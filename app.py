import os
import hmac
import secrets
import sqlite3
from contextlib import closing
from pathlib import Path
from flask import Flask, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from admin import create_admin_blueprint
from models import db, NguoiDung, ChucVu
from b3 import b3
from b4 import b4
from sqlalchemy import event, inspect
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException
from models import ensure_sqlite_guards

app = Flask(__name__)
# Không ghi khóa bí mật vào source. Khóa ngẫu nhiên dùng cho demo một tiến trình.
app.secret_key = os.environ.get('BOOKSTORE_SECRET_KEY') or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
                  SESSION_COOKIE_SECURE=os.environ.get('BOOKSTORE_HTTPS') == '1')
DEMO_MODE = os.environ.get('BOOKSTORE_DEMO', '1') == '1'
if not DEMO_MODE and not os.environ.get('BOOKSTORE_SECRET_KEY'):
  raise RuntimeError('Cần BOOKSTORE_SECRET_KEY riêng khi tắt chế độ demo.')

# Cấu hình SQLite Database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Cho phép kiểm thử trên bản sao CSDL, mặc định vẫn dùng bookstore.db.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.environ.get(
    'BOOKSTORE_DB_PATH', os.path.join(BASE_DIR, 'bookstore.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Bật khóa ngoại cho mọi kết nối, kể cả khi import app để chạy kiểm thử.
with app.app_context():
  @event.listens_for(db.engine, 'connect')
  def enable_sqlite_foreign_keys(sqlite_connection, _connection_record):
    cursor = sqlite_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


# Đăng ký các module dùng chung một SQLAlchemy instance.
app.register_blueprint(create_admin_blueprint(db, NguoiDung, ChucVu))
app.register_blueprint(b3)
app.register_blueprint(b4)


# Kiểm tra tài khoản thật trước tất cả API, không tin role cũ trong cookie.
def auth_stamp(user):
  value = f'{user.username}\0{user.role}\0{user.password}\0{user.session_version}'.encode('utf-8')
  key = app.secret_key.encode('utf-8') if isinstance(app.secret_key, str) else app.secret_key
  return hmac.digest(key, value, 'sha256').hex()


@app.before_request
def validate_session():
  if not request.path.startswith('/api/') or request.endpoint == 'login':
    return
  username = session.get('user')
  if not username:
    # Không giữ role nếu thiếu danh tính.
    if session.get('role'):
      session.clear()
    return
  user = db.session.get(NguoiDung, username) if isinstance(username, str) else None
  stamp = session.get('auth_stamp')
  if (user is None or user.role not in ('staff', 'manager', 'admin')
      or not isinstance(stamp, str) or not hmac.compare_digest(stamp, auth_stamp(user))):
    session.clear()
    if request.endpoint not in ('check_session', 'logout'):
      return jsonify({'error': 'Phiên đăng nhập đã hết hiệu lực. Vui lòng đăng nhập lại.'}), 401
    return
  session.update(role=user.role, ho_ten=user.ho_ten)


@app.after_request
def no_cache_api(response):
  if request.path.startswith('/api/'):
    response.headers['Cache-Control'] = 'no-store'
  return response


@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):
  db.session.rollback()
  if isinstance(error, IntegrityError):
    return jsonify({'error': 'Không thể lưu dữ liệu: trùng mã, dữ liệu không hợp lệ hoặc đang được tham chiếu.'}), 409
  app.logger.error('Lỗi cơ sở dữ liệu', exc_info=error)
  return jsonify({'error': 'Không thể xử lý dữ liệu. Vui lòng thử lại.'}), 500


@app.errorhandler(HTTPException)
def handle_http_error(error):
  if request.path.startswith('/api/'):
    return jsonify({'error': error.description}), error.code
  return error


@app.errorhandler(Exception)
def handle_unexpected_error(error):
  db.session.rollback()
  app.logger.error('Lỗi chưa được xử lý', exc_info=error)
  if request.path.startswith('/api/'):
    return jsonify({'error': 'Máy chủ gặp lỗi. Vui lòng thử lại.'}), 500
  return 'Máy chủ gặp lỗi.', 500


@app.route('/api/login', methods=['POST'])
def login():
  data = request.get_json(silent=True)
  if not isinstance(data, dict):
    return jsonify({'error': 'Dữ liệu đăng nhập không hợp lệ.'}), 400
  username, password = data.get('username'), data.get('password')
  if (not isinstance(username, str) or not username.strip() or len(username.strip()) > 50
      or not isinstance(password, str) or not password or len(password) > 128):
    return jsonify({'error': 'Tên đăng nhập hoặc mật khẩu không hợp lệ.'}), 400
  user = db.session.get(NguoiDung, username.strip())
  if user and user.role in ('staff', 'manager', 'admin') and check_password_hash(user.password, password):
    session.clear()
    session.update(user=user.username, role=user.role, ho_ten=user.ho_ten, auth_stamp=auth_stamp(user))
    return jsonify({'message': 'Đăng nhập thành công!', 'username': user.username,
                    'role': user.role, 'ho_ten': user.ho_ten})
  return jsonify({'error': 'Sai tên đăng nhập hoặc mật khẩu!'}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
  session.clear()
  return jsonify({'message': 'Đăng xuất thành công!'})


@app.route('/api/check-session', methods=['GET'])
def check_session():
  if 'user' in session:
    return jsonify({
        'logged_in': True,
        'username': session['user'],
        'role': session['role'],
        'ho_ten': session['ho_ten'],
    })
  return jsonify({'logged_in': False})


# --- ROUTES & API ENDPOINTS ---
@app.route('/')
def index():
  return render_template('index.html')


def init_db():
  with app.app_context():
    # Chỉ nạp seed khi CSDL hoàn toàn mới; tuyệt đối không ghi đè dữ liệu đang có.
    if not inspect(db.engine).get_table_names() and DEMO_MODE:
      db.session.remove()
      db.engine.dispose()
      with closing(sqlite3.connect(db.engine.url.database)) as con:
        con.executescript(Path(BASE_DIR, 'database.sql').read_text(encoding='utf-8'))
    db.create_all()
    with db.engine.begin() as connection:
      columns = {row[1] for row in connection.exec_driver_sql('PRAGMA table_info(nguoi_dung)')}
      if 'chuc_vu' not in columns:
        connection.exec_driver_sql(
            'ALTER TABLE nguoi_dung ADD COLUMN chuc_vu VARCHAR(50) '
            'REFERENCES chuc_vu(ten_chuc_vu) ON UPDATE CASCADE ON DELETE RESTRICT')
      if 'session_version' not in columns:
        connection.exec_driver_sql("ALTER TABLE nguoi_dung ADD COLUMN session_version VARCHAR(32) NOT NULL DEFAULT ''")
      connection.exec_driver_sql("UPDATE nguoi_dung SET session_version=lower(hex(randomblob(16))) WHERE session_version='' OR session_version IS NULL")
      # Bảo đảm bản ghi cha tồn tại trước khi gán chức vụ; không đổi tên đã thiết lập.
      positions = {'staff': 'Nhân viên kho', 'manager': 'Quản lý kho', 'admin': 'Quản trị hệ thống'}
      for role, title in positions.items():
        missing = connection.exec_driver_sql(
            "SELECT 1 FROM nguoi_dung WHERE role=? AND (chuc_vu IS NULL OR TRIM(chuc_vu)='') LIMIT 1", (role,)).first()
        empty_users = not connection.exec_driver_sql('SELECT 1 FROM nguoi_dung LIMIT 1').first()
        if missing or empty_users:
          connection.exec_driver_sql('INSERT OR IGNORE INTO chuc_vu(ten_chuc_vu) VALUES (?)', (title,))
          connection.exec_driver_sql(
              "UPDATE nguoi_dung SET chuc_vu=? WHERE role=? AND (chuc_vu IS NULL OR TRIM(chuc_vu)='')", (title, role))
      ensure_sqlite_guards(connection)
      if connection.exec_driver_sql('PRAGMA foreign_key_check').first():
        raise RuntimeError('CSDL có tham chiếu không hợp lệ. Hãy sao lưu và xử lý trước khi chạy.')
    # Ngoài chế độ demo, quản trị viên phải được cấp mật khẩu riêng khi khởi tạo.
    if not NguoiDung.query.first() and not DEMO_MODE:
      password = os.environ.get('BOOKSTORE_ADMIN_PASSWORD', '')
      if len(password) < 12 or len(password) > 128:
        raise RuntimeError('Cần BOOKSTORE_ADMIN_PASSWORD từ 12–128 ký tự để tạo admin đầu tiên.')
      db.session.add(NguoiDung(username='admin', password=generate_password_hash(password),
                               role='admin', ho_ten='Quản trị viên', chuc_vu='Quản trị hệ thống'))
      db.session.commit()


# Khoi tao va nang cap CSDL truoc khi Flask phuc vu request.
init_db()

if __name__ == '__main__':
  app.run(debug=False, host='127.0.0.1', port=5000)
