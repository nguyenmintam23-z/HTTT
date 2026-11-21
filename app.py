import os
from sys import float_info
from flask import Flask, jsonify, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from admin import create_admin_blueprint

app = Flask(__name__)
app.secret_key = 'kho_sach_secret_key'  # Khóa bí mật cho session

# Cấu hình SQLite Database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    BASE_DIR, 'bookstore.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- ORM MODELS ---
class NguoiDung(db.Model):
  __tablename__ = 'nguoi_dung'
  username = db.Column(db.String(50), primary_key=True)
  password = db.Column(db.String(255), nullable=False)
  role = db.Column(
      db.String(20), nullable=False
  )  # 'staff' (Nhân viên), 'manager' (Quản lý) hoặc 'admin'
  ho_ten = db.Column(db.String(100))
  chuc_vu = db.Column(db.String(50))


class ChucVu(db.Model):
  __tablename__ = 'chuc_vu'
  ten_chuc_vu = db.Column(db.String(50), primary_key=True)


app.register_blueprint(create_admin_blueprint(db, NguoiDung, ChucVu))


class NhaCungCap(db.Model):
  __tablename__ = 'nha_cung_cap'
  ma_ncc = db.Column(db.String(20), primary_key=True)
  ten_ncc = db.Column(db.String(100), nullable=False)
  dia_chi = db.Column(db.String(200))
  so_dien_thoai = db.Column(db.String(20))
  email = db.Column(db.String(100))

  def to_dict(self):
    return {
        'ma_ncc': self.ma_ncc,
        'ten_ncc': self.ten_ncc,
        'dia_chi': self.dia_chi,
        'so_dien_thoai': self.so_dien_thoai,
        'email': self.email,
    }


class Sach(db.Model):
  __tablename__ = 'sach'
  ma_sach = db.Column(db.String(20), primary_key=True)
  ten_sach = db.Column(db.String(150), nullable=False)
  the_loai = db.Column(db.String(50))
  tac_gia = db.Column(db.String(100))
  nha_xuat_ban = db.Column(db.String(100))
  ma_ncc = db.Column(
      db.String(20), db.ForeignKey('nha_cung_cap.ma_ncc'), nullable=False
  )
  gia_nhap = db.Column(db.Float, default=0.0)
  gia_ban = db.Column(db.Float, default=0.0)
  so_luong_ton = db.Column(db.Integer, default=0)
  vi_tri = db.Column(db.String(50))

  def to_dict(self):
    return {
        'ma_sach': self.ma_sach,
        'ten_sach': self.ten_sach,
        'the_loai': self.the_loai,
        'tac_gia': self.tac_gia,
        'nha_xuat_ban': self.nha_xuat_ban,
        'ma_ncc': self.ma_ncc,
        'gia_nhap': self.gia_nhap,
        'gia_ban': self.gia_ban,
        'so_luong_ton': self.so_luong_ton,
        'vi_tri': self.vi_tri,
    }


class PhieuNhap(db.Model):
  __tablename__ = 'phieu_nhap'
  ma_phieu_nhap = db.Column(db.String(20), primary_key=True)
  ngay_nhap = db.Column(db.String(10), nullable=False)
  ma_ncc = db.Column(
      db.String(20), db.ForeignKey('nha_cung_cap.ma_ncc'), nullable=False
  )
  nguoi_lap = db.Column(db.String(50))
  tong_tien = db.Column(db.Float, default=0.0)
  chi_tiet = db.relationship(
      'ChiTietPhieuNhap',
      back_populates='phieu_nhap_ref',
      cascade='all, delete-orphan',
  )

  def to_dict(self):
    return {
        'ma_phieu_nhap': self.ma_phieu_nhap,
        'ngay_nhap': self.ngay_nhap,
        'ma_ncc': self.ma_ncc,
        'nguoi_lap': self.nguoi_lap,
        'tong_tien': self.tong_tien,
        'chi_tiet': [item.to_dict() for item in self.chi_tiet],
    }


class ChiTietPhieuNhap(db.Model):
  __tablename__ = 'chi_tiet_phieu_nhap'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  ma_phieu_nhap = db.Column(
      db.String(20), db.ForeignKey('phieu_nhap.ma_phieu_nhap'), nullable=False
  )
  ma_sach = db.Column(
      db.String(20), db.ForeignKey('sach.ma_sach'), nullable=False
  )
  so_luong_nhap = db.Column(db.Integer, nullable=False)
  don_gia_nhap = db.Column(db.Float, nullable=False)
  thanh_tien = db.Column(db.Float, nullable=False)

  phieu_nhap_ref = db.relationship('PhieuNhap', back_populates='chi_tiet')

  def to_dict(self):
    return {
        'ma_sach': self.ma_sach,
        'so_luong_nhap': self.so_luong_nhap,
        'don_gia_nhap': self.don_gia_nhap,
        'thanh_tien': self.thanh_tien,
    }


class PhieuXuat(db.Model):
  __tablename__ = 'phieu_xuat'
  ma_phieu_xuat = db.Column(db.String(20), primary_key=True)
  ngay_xuat = db.Column(db.String(10), nullable=False)
  nguoi_nhan = db.Column(db.String(100))
  ly_do = db.Column(db.String(200))
  nguoi_lap = db.Column(db.String(50))
  chi_tiet = db.relationship(
      'ChiTietPhieuXuat',
      back_populates='phieu_xuat_ref',
      cascade='all, delete-orphan',
  )

  def to_dict(self):
    return {
        'ma_phieu_xuat': self.ma_phieu_xuat,
        'ngay_xuat': self.ngay_xuat,
        'nguoi_nhan': self.nguoi_nhan,
        'ly_do': self.ly_do,
        'nguoi_lap': self.nguoi_lap,
        'chi_tiet': [item.to_dict() for item in self.chi_tiet],
    }


class ChiTietPhieuXuat(db.Model):
  __tablename__ = 'chi_tiet_phieu_xuat'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  ma_phieu_xuat = db.Column(
      db.String(20), db.ForeignKey('phieu_xuat.ma_phieu_xuat'), nullable=False
  )
  ma_sach = db.Column(
      db.String(20), db.ForeignKey('sach.ma_sach'), nullable=False
  )
  so_luong_xuat = db.Column(db.Integer, nullable=False)

  phieu_xuat_ref = db.relationship('PhieuXuat', back_populates='chi_tiet')

  def to_dict(self):
    return {'ma_sach': self.ma_sach, 'so_luong_xuat': self.so_luong_xuat}


# --- AUTHENTICATION API ROUTES ---
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


@app.route('/api/sach', methods=['GET'])
def get_sach():
  if 'user' not in session:
    return jsonify({'error': 'Chưa đăng nhập!'}), 401
  keyword = request.args.get('q', '').lower()
  ncc = request.args.get('ncc', '')
  sort_by = request.args.get('sort', '')
  query = Sach.query
  if keyword:
    query = query.filter(
        (Sach.ten_sach.ilike(f'%{keyword}%'))
        | (Sach.the_loai.ilike(f'%{keyword}%'))
    )
  if ncc:
    query = query.filter_by(ma_ncc=ncc)
  if sort_by == 'ten':
    query = query.order_by(Sach.ten_sach.asc())
  elif sort_by == 'gia':
    query = query.order_by(Sach.gia_ban.asc())
  return jsonify([s.to_dict() for s in query.all()])


@app.route('/api/sach', methods=['POST'])
def add_sach():
  if session.get('role') != 'manager':
    return (
        jsonify({'error': 'Truy cập bị từ chối! Chỉ Quản lý mới được thêm sách.'}),
        403,
    )
  data = request.json
  if db.session.get(Sach, data.get('ma_sach')):
    return jsonify({'error': 'Mã sách đã tồn tại!'}), 400
  db.session.add(Sach(**data))
  db.session.commit()
  return jsonify({'message': 'Thêm sách thành công!'}), 201


@app.route('/api/sach/<ma_sach>', methods=['PUT'])
def update_sach(ma_sach):
  if session.get('role') != 'manager':
    return jsonify({'error': 'Chỉ quản lý được cập nhật.'}), 403
  record = db.session.get(Sach, ma_sach)
  if record is None:
    return jsonify({'error': 'Không tìm thấy bản ghi.'}), 404
  data = request.get_json(silent=True)
  if not isinstance(data, dict) or data.get('ma_sach', ma_sach) != ma_sach:
    return jsonify({'error': 'Dữ liệu hoặc mã bản ghi không hợp lệ.'}), 400
  changes = {}
  for field in ('ten_sach', 'the_loai', 'tac_gia', 'nha_xuat_ban', 'ma_ncc', 'vi_tri'):
    if field in data:
      if not isinstance(data[field], str):
        return jsonify({'error': f'Trường {field} phải là văn bản.'}), 400
      changes[field] = data[field].strip()
  if not changes.get('ten_sach', record.ten_sach):
    return jsonify({'error': 'Vui lòng nhập tên.'}), 400

  if 'ma_ncc' in changes and db.session.get(NhaCungCap, changes['ma_ncc']) is None:
    return jsonify({'error': 'Nhà cung cấp không tồn tại.'}), 400
  for field in ('gia_nhap', 'gia_ban'):
    if field in data:
      value = data[field]
      if type(value) not in (int, float) or not 0 <= value <= float_info.max:
        return jsonify({'error': 'Giá phải là số hữu hạn và không âm.'}), 400
      changes[field] = value

  for field, value in changes.items():
    setattr(record, field, value)
  db.session.commit()
  return jsonify({'message': 'Cập nhật thành công!'})


@app.route('/api/sach/<ma_sach>', methods=['DELETE'])
def delete_sach(ma_sach):
  if session.get('role') != 'manager':
    return (
        jsonify({'error': 'Truy cập bị từ chối! Chỉ Quản lý mới được xóa sách.'}),
        403,
    )
  sach = db.session.get(Sach, ma_sach)
  if not sach:
    return jsonify({'error': 'Không tìm thấy sách!'}), 404
  db.session.delete(sach)
  db.session.commit()
  return jsonify({'message': 'Xóa sách thành công!'})


@app.route('/api/ncc', methods=['GET'])
def get_ncc():
  if 'user' not in session:
    return jsonify({'error': 'Chưa đăng nhập!'}), 401
  return jsonify([n.to_dict() for n in NhaCungCap.query.all()])


@app.route('/api/ncc', methods=['POST'])
def add_ncc():
  if session.get('role') != 'manager':
    return (
        jsonify({'error': 'Truy cập bị từ chối! Chỉ Quản lý mới được thao tác NCC.'}),
        403,
    )
  data = request.json
  if db.session.get(NhaCungCap, data.get('ma_ncc')):
    return jsonify({'error': 'Mã nhà cung cấp đã tồn tại!'}), 400
  db.session.add(NhaCungCap(**data))
  db.session.commit()
  return jsonify({'message': 'Thêm nhà cung cấp thành công!'}), 201


@app.route('/api/ncc/<ma_ncc>', methods=['PUT'])
def update_ncc(ma_ncc):
  if session.get('role') != 'manager':
    return jsonify({'error': 'Chỉ quản lý được cập nhật.'}), 403
  record = db.session.get(NhaCungCap, ma_ncc)
  if record is None:
    return jsonify({'error': 'Không tìm thấy bản ghi.'}), 404
  data = request.get_json(silent=True)
  if not isinstance(data, dict) or data.get('ma_ncc', ma_ncc) != ma_ncc:
    return jsonify({'error': 'Dữ liệu hoặc mã bản ghi không hợp lệ.'}), 400
  changes = {}
  for field in ('ten_ncc', 'dia_chi', 'so_dien_thoai', 'email'):
    if field in data:
      if not isinstance(data[field], str):
        return jsonify({'error': f'Trường {field} phải là văn bản.'}), 400
      changes[field] = data[field].strip()
  if not changes.get('ten_ncc', record.ten_ncc):
    return jsonify({'error': 'Vui lòng nhập tên.'}), 400

  for field, value in changes.items():
    setattr(record, field, value)
  db.session.commit()
  return jsonify({'message': 'Cập nhật thành công!'})


@app.route('/api/ncc/<ma_ncc>', methods=['DELETE'])
def delete_ncc(ma_ncc):
  if session.get('role') != 'manager':
    return (
        jsonify({'error': 'Truy cập bị từ chối! Chỉ Quản lý mới được xóa NCC.'}),
        403,
    )
  ncc = db.session.get(NhaCungCap, ma_ncc)
  if not ncc:
    return jsonify({'error': 'Không tìm thấy nhà cung cấp!'}), 404
  db.session.delete(ncc)
  db.session.commit()
  return jsonify({'message': 'Xóa nhà cung cấp thành công!'})


@app.route('/api/phieu-nhap', methods=['POST'])
def create_phieu_nhap():
  # Chỉ Nhân viên kho mới được phép lập phiếu nhập
  if session.get('role') != 'staff':
    return (
        jsonify({
            'error': (
                'Truy cập bị từ chối! Chức năng lập phiếu chỉ dành cho Nhân'
                ' viên kho.'
            )
        }),
        403,
    )

  data = request.json
  if db.session.get(PhieuNhap, data.get('ma_phieu_nhap')):
    return jsonify({'error': 'Mã phiếu nhập đã tồn tại!'}), 400

  tong_tien = 0
  chi_tiet_objs = []
  for item in data.get('chi_tiet', []):
    thanh_tien = item['so_luong_nhap'] * item['don_gia_nhap']
    tong_tien += thanh_tien
    sach = db.session.get(Sach, item['ma_sach'])
    if sach:
      sach.so_luong_ton += item['so_luong_nhap']
    chi_tiet_objs.append(
        ChiTietPhieuNhap(
            ma_sach=item['ma_sach'],
            so_luong_nhap=item['so_luong_nhap'],
            don_gia_nhap=item['don_gia_nhap'],
            thanh_tien=thanh_tien,
        )
    )

  phieu = PhieuNhap(
      ma_phieu_nhap=data['ma_phieu_nhap'],
      ngay_nhap=data['ngay_nhap'],
      ma_ncc=data['ma_ncc'],
      nguoi_lap=session.get('ho_ten', 'Nhân viên kho'),
      tong_tien=tong_tien,
      chi_tiet=chi_tiet_objs,
  )
  db.session.add(phieu)
  db.session.commit()
  return jsonify({'message': 'Lập phiếu nhập thành công!'}), 201


@app.route('/api/phieu-nhap', methods=['GET'])
def get_phieu_nhap():
  if session.get('role') != 'manager':
    return (
        jsonify(
            {'error': 'Truy cập bị từ chối! Chỉ Quản lý mới xem được thống kê.'}
        ),
        403,
    )
  thang, nam = request.args.get('thang', ''), request.args.get('nam', '')

  def valid_period(value, maximum):
    return not value or (
        value.isascii() and value.isdecimal() and len(value) <= 4
        and 1 <= int(value) <= maximum
    )

  if not valid_period(thang, 12) or not valid_period(nam, 9999):
    return jsonify({'error': 'Tháng phải từ 1 đến 12 và năm từ 1 đến 9999.'}), 400

  query = PhieuNhap.query
  if thang:
    query = query.filter(db.func.substr(PhieuNhap.ngay_nhap, 6, 2) == f'{int(thang):02d}')
  if nam:
    query = query.filter(db.func.substr(PhieuNhap.ngay_nhap, 1, 4) == f'{int(nam):04d}')
  receipts = query.order_by(PhieuNhap.ngay_nhap.desc(), PhieuNhap.ma_phieu_nhap).all()
  return jsonify([receipt.to_dict() for receipt in receipts])


@app.route('/api/phieu-xuat', methods=['POST'])
def create_phieu_xuat():
  # Chỉ Nhân viên kho mới được phép lập phiếu xuất
  if session.get('role') != 'staff':
    return (
        jsonify({
            'error': (
                'Truy cập bị từ chối! Chức năng lập phiếu chỉ dành cho Nhân'
                ' viên kho.'
            )
        }),
        403,
    )

  data = request.json
  if db.session.get(PhieuXuat, data.get('ma_phieu_xuat')):
    return jsonify({'error': 'Mã phiếu xuất đã tồn tại!'}), 400

  for item in data.get('chi_tiet', []):
    sach = db.session.get(Sach, item['ma_sach'])
    if not sach:
      return jsonify({'error': f"Không tìm thấy sách {item['ma_sach']}"}), 400
    if sach.so_luong_ton < item['so_luong_xuat']:
      return (
          jsonify({
              'error': (
                  f'Sách [{sach.ten_sach}] không đủ tồn kho! Tồn:'
                  f' {sach.so_luong_ton}'
              )
          }),
          400,
      )

  chi_tiet_objs = []
  for item in data.get('chi_tiet', []):
    sach = db.session.get(Sach, item['ma_sach'])
    sach.so_luong_ton -= item['so_luong_xuat']
    chi_tiet_objs.append(
        ChiTietPhieuXuat(
            ma_sach=item['ma_sach'], so_luong_xuat=item['so_luong_xuat']
        )
    )

  phieu = PhieuXuat(
      ma_phieu_xuat=data['ma_phieu_xuat'],
      ngay_xuat=data['ngay_xuat'],
      nguoi_nhan=data.get('nguoi_nhan', ''),
      ly_do=data.get('ly_do', ''),
      nguoi_lap=session.get('ho_ten', 'Nhân viên kho'),
      chi_tiet=chi_tiet_objs,
  )
  db.session.add(phieu)
  db.session.commit()
  return jsonify({'message': 'Lập phiếu xuất thành công!'}), 201


def init_db():
  with app.app_context():
    db.create_all()
    with db.engine.begin() as connection:
      user_columns = {
          row[1] for row in connection.exec_driver_sql('PRAGMA table_info(nguoi_dung)')
      }
      if 'chuc_vu' not in user_columns:
        connection.exec_driver_sql(
            "ALTER TABLE nguoi_dung ADD COLUMN chuc_vu VARCHAR(50)"
        )
      connection.exec_driver_sql(
          "UPDATE nguoi_dung SET chuc_vu = CASE "
          "WHEN role = 'manager' THEN 'Quản lý kho' "
          "WHEN role = 'admin' THEN 'Quản trị hệ thống' "
          "ELSE 'Nhân viên kho' END "
          "WHERE chuc_vu IS NULL OR TRIM(chuc_vu) = ''"
      )

    if not ChucVu.query.first():
      db.session.add_all([
          ChucVu(ten_chuc_vu='Nhân viên kho'),
          ChucVu(ten_chuc_vu='Quản lý kho'),
      ])

    # Tạo tài khoản mặc định nếu chưa có
    if not NguoiDung.query.first():
      u1 = NguoiDung(
          username='manager',
          password=generate_password_hash('123456'),
          role='manager',
          ho_ten='Nguyễn Quản Lý',
            chuc_vu='Quản lý kho',
      )
      u2 = NguoiDung(
          username='staff',
          password=generate_password_hash('123456'),
          role='staff',
          ho_ten='Trần Nhân Viên',
            chuc_vu='Nhân viên kho',
      )
      db.session.add_all([u1, u2])

    if db.session.get(NguoiDung, 'admin') is None:
      db.session.add(NguoiDung(
          username='admin',
          password=generate_password_hash('123456'),
          role='admin',
          ho_ten='Quản trị viên',
      ))

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
    db.session.commit()


if __name__ == '__main__':
  init_db()
  app.run(debug=True, port=5000)