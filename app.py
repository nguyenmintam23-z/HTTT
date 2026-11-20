import os
from flask import Flask, jsonify, render_template, request, session
from models import db, NguoiDung, NhaCungCap, Sach
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'kho_sach_secret_key'  # Khóa bí mật cho session

# Cấu hình SQLite Database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    BASE_DIR, 'bookstore.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/api/login', methods=['POST'])
def login():
  data = request.json
  user = db.session.get(NguoiDung, data.get('username'))
  if user and check_password_hash(user.password, data.get('password')):
    session['user'] = user.username
    session['role'] = user.role
    session['ho_ten'] = user.ho_ten
    return jsonify({
        'message': 'Đăng nhập thành công!',
        'username': user.username,
        'role': user.role,
        'ho_ten': user.ho_ten,
    })
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
    db.create_all()
    # Tạo tài khoản mặc định nếu chưa có
    if not NguoiDung.query.first():
      u1 = NguoiDung(
          username='manager',
          password=generate_password_hash('123456'),
          role='manager',
          ho_ten='Nguyễn Quản Lý',
      )
      u2 = NguoiDung(
          username='staff',
          password=generate_password_hash('123456'),
          role='staff',
          ho_ten='Trần Nhân Viên',
      )
      db.session.add_all([u1, u2])

    if not NhaCungCap.query.first():
      n1 = NhaCungCap(
          ma_ncc='NCC01',
          ten_ncc='Công ty Sách Trí Tuệ',
          dia_chi='123 Nguyễn Văn Cừ, Q.5, TP.HCM',
          so_dien_thoai='0901234567',
          email='contact@tritue.com',
      )
      n2 = NhaCungCap(
          ma_ncc='NCC02',
          ten_ncc='Nhà Xuất Bản Khoa Học',
          dia_chi='45 Lê Duẩn, Q.1, TP.HCM',
          so_dien_thoai='0988888888',
          email='info@nxbkhoahoc.vn',
      )
      db.session.add_all([n1, n2])
      s1 = Sach(
          ma_sach='S001',
          ten_sach='Nhập môn Phân tích Thiết kế Hệ thống',
          the_loai='Giáo khoa',
          tac_gia='Nguyễn Văn A',
          nha_xuat_ban='NXB Đại học Sài Gòn',
          ma_ncc='NCC01',
          gia_nhap=50000,
          gia_ban=75000,
          so_luong_ton=25,
          vi_tri='Kệ A1',
      )
      s2 = Sach(
          ma_sach='S002',
          ten_sach='Lập trình Web Flask Python',
          the_loai='Công nghệ thông tin',
          tac_gia='Trần Văn B',
          nha_xuat_ban='NXB Khoa Học',
          ma_ncc='NCC02',
          gia_nhap=60000,
          gia_ban=90000,
          so_luong_ton=15,
          vi_tri='Kệ B2',
      )
      db.session.add_all([s1, s2])
      db.session.commit()


from b3 import b3
from b4 import b4
app.register_blueprint(b3)
app.register_blueprint(b4)


if __name__ == '__main__':
  init_db()
  app.run(debug=True, port=5000)