import os
from datetime import date
from math import isfinite
from sqlalchemy.exc import SQLAlchemyError
from sys import float_info
from flask import Flask, jsonify, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

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
  )  # 'staff' (Nhân viên) hoặc 'manager' (Quản lý)
  ho_ten = db.Column(db.String(100))


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

  keyword = request.args.get('q', '').strip()
  ncc = request.args.get('ncc', '')
  sort_by = request.args.get('sort', '')
  query = Sach.query

  if keyword:
    query = query.filter(
        Sach.ten_sach.ilike(f'%{keyword}%') |
        Sach.ma_sach.ilike(f'%{keyword}%') |
        Sach.the_loai.ilike(f'%{keyword}%')
    )
  if ncc:
    query = query.filter_by(ma_ncc=ncc)

  # B3 - Bổ sung lọc theo khoảng giá bán.
  min_price = request.args.get('min_price', '').strip()
  max_price = request.args.get('max_price', '').strip()
  try:
    min_value = float(min_price) if min_price else None
    max_value = float(max_price) if max_price else None
  except ValueError:
    return jsonify({'error': 'Khoảng giá phải là số.'}), 400

  for value in (min_value, max_value):
    if value is not None and (not isfinite(value) or value < 0):
      return jsonify({'error': 'Giá phải là số hữu hạn, không âm.'}), 400
  if min_value is not None and max_value is not None and min_value > max_value:
    return jsonify({'error': 'Giá từ không được lớn hơn giá đến.'}), 400
  if min_value is not None:
    query = query.filter(Sach.gia_ban >= min_value)
  if max_value is not None:
    query = query.filter(Sach.gia_ban <= max_value)

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
  if not isinstance(data, dict):
    return jsonify({'error': 'Dữ liệu hoặc mã bản ghi không hợp lệ.'}), 400
  new_code = data.get('ma_sach', ma_sach)
  if not isinstance(new_code, str) or not new_code.strip() or len(new_code.strip()) > 20 or '/' in new_code:
    return jsonify({'error': 'Mã sách phải có từ 1 đến 20 ký tự và không chứa dấu /.'}), 400
  new_code = new_code.strip()
  if new_code != ma_sach and db.session.get(Sach, new_code) is not None:
    return jsonify({'error': 'Mã sách đã tồn tại!'}), 409
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

  try:
    if new_code != ma_sach:
      # Defer foreign-key checks until the parent and all receipt lines agree.
      db.session.execute(text('PRAGMA defer_foreign_keys = ON'))
      db.session.query(ChiTietPhieuNhap).filter_by(ma_sach=ma_sach).update(
          {'ma_sach': new_code}, synchronize_session=False
      )
      db.session.query(ChiTietPhieuXuat).filter_by(ma_sach=ma_sach).update(
          {'ma_sach': new_code}, synchronize_session=False
      )
      record.ma_sach = new_code
    for field, value in changes.items():
      setattr(record, field, value)
    db.session.commit()
  except IntegrityError:
    db.session.rollback()
    return jsonify({'error': 'Không thể lưu mã sách. Mã có thể đã được sử dụng, vui lòng tải lại và thử lại.'}), 409
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
  # B3: Chỉ nhân viên kho được lập phiếu.
  if session.get('role') != 'staff':
    return jsonify({'error': 'Chỉ nhân viên kho được lập phiếu nhập.'}), 403

  data = request.get_json(silent=True)
  if not isinstance(data, dict):
    return jsonify({'error': 'Dữ liệu phiếu nhập không hợp lệ.'}), 400

  ma_phieu = data.get('ma_phieu_nhap')
  ngay_nhap = data.get('ngay_nhap')
  ma_ncc = data.get('ma_ncc')
  chi_tiet = data.get('chi_tiet')
  if not isinstance(ma_phieu, str) or not ma_phieu.strip():
    return jsonify({'error': 'Thiếu mã phiếu nhập.'}), 400
  ma_phieu = ma_phieu.strip()
  if db.session.get(PhieuNhap, ma_phieu):
    return jsonify({'error': 'Mã phiếu nhập đã tồn tại!'}), 400
  if not isinstance(ngay_nhap, str):
    return jsonify({'error': 'Ngày nhập không hợp lệ.'}), 400
  try:
    ngay_hop_le = date.fromisoformat(ngay_nhap)
    if ngay_hop_le.isoformat() != ngay_nhap:
      raise ValueError('Sai định dạng')
  except ValueError:
    return jsonify({'error': 'Ngày nhập phải có dạng YYYY-MM-DD hợp lệ.'}), 400
  if not isinstance(ma_ncc, str) or db.session.get(NhaCungCap, ma_ncc.strip()) is None:
    return jsonify({'error': 'Nhà cung cấp không tồn tại.'}), 400
  ma_ncc = ma_ncc.strip()
  if not isinstance(chi_tiet, list) or not chi_tiet:
    return jsonify({'error': 'Phiếu nhập phải có ít nhất một dòng sách.'}), 400

  # Kiểm tra TẤT CẢ dòng trước khi thay đổi bất kỳ số lượng tồn nào.
  validated = []
  for item in chi_tiet:
    if not isinstance(item, dict):
      return jsonify({'error': 'Chi tiết phiếu không hợp lệ.'}), 400
    ma_sach = item.get('ma_sach')
    so_luong = item.get('so_luong_nhap')
    don_gia = item.get('don_gia_nhap')
    if not isinstance(ma_sach, str) or not ma_sach.strip():
      return jsonify({'error': 'Mã sách không hợp lệ.'}), 400
    ma_sach = ma_sach.strip()
    sach = db.session.get(Sach, ma_sach)
    if sach is None:
      return jsonify({'error': f'Không tìm thấy sách {ma_sach}.'}), 400
    if type(so_luong) is not int or not (0 < so_luong <= 9223372036854775807):
      return jsonify({'error': 'Số lượng nhập phải là số nguyên dương hợp lệ.'}), 400
    if type(don_gia) not in (int, float) or don_gia < 0:
      return jsonify({'error': 'Đơn giá nhập phải là số không âm, hữu hạn.'}), 400
    try:
      don_gia = float(don_gia)
    except (ValueError, OverflowError):
      return jsonify({'error': 'Đơn giá nhập vượt giới hạn cho phép.'}), 400
    if not isfinite(don_gia):
      return jsonify({'error': 'Đơn giá nhập phải là số hữu hạn.'}), 400
    thanh_tien = so_luong * don_gia
    if not isfinite(thanh_tien):
      return jsonify({'error': 'Thành tiền vượt giới hạn cho phép.'}), 400
    validated.append((sach, so_luong, don_gia, thanh_tien))

  # Tính toán và kiểm tra toàn bộ trước khi sửa tồn kho.
  tong_tien = sum(row[3] for row in validated)
  if not isfinite(tong_tien):
    return jsonify({'error': 'Tổng tiền vượt giới hạn cho phép.'}), 400
  tong_nhap = {}
  for sach, so_luong, _, _ in validated:
    tong_nhap[sach.ma_sach] = tong_nhap.get(sach.ma_sach, 0) + so_luong
  for ma_sach, so_luong in tong_nhap.items():
    if db.session.get(Sach, ma_sach).so_luong_ton + so_luong > 9223372036854775807:
      return jsonify({'error': f'Tồn kho sách {ma_sach} vượt giới hạn.'}), 400

  chi_tiet_objs = []
  for sach, so_luong, don_gia, thanh_tien in validated:
    chi_tiet_objs.append(ChiTietPhieuNhap(
        ma_sach=sach.ma_sach,
        so_luong_nhap=so_luong,
        don_gia_nhap=don_gia,
        thanh_tien=thanh_tien,
    ))
  for ma_sach, so_luong in tong_nhap.items():
    db.session.get(Sach, ma_sach).so_luong_ton += so_luong

  phieu = PhieuNhap(
      ma_phieu_nhap=ma_phieu,
      ngay_nhap=ngay_nhap,
      ma_ncc=ma_ncc,
      nguoi_lap=session.get('ho_ten', 'Nhân viên kho'),
      tong_tien=tong_tien,
      chi_tiet=chi_tiet_objs,
  )
  try:
    db.session.add(phieu)
    db.session.commit()
  except SQLAlchemyError:
    db.session.rollback()
    return jsonify({'error': 'Không lưu được phiếu nhập; dữ liệu chưa được cập nhật.'}), 500
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
  if session.get('role') != 'staff':
    return jsonify({'error': 'Chỉ nhân viên kho được lập phiếu xuất.'}), 403

  data = request.get_json(silent=True)
  if not isinstance(data, dict):
    return jsonify({'error': 'Dữ liệu phiếu xuất không hợp lệ.'}), 400
  ma_phieu = data.get('ma_phieu_xuat')
  ngay_xuat = data.get('ngay_xuat')
  chi_tiet = data.get('chi_tiet')
  if not isinstance(ma_phieu, str) or not ma_phieu.strip():
    return jsonify({'error': 'Thiếu mã phiếu xuất.'}), 400
  ma_phieu = ma_phieu.strip()
  if db.session.get(PhieuXuat, ma_phieu):
    return jsonify({'error': 'Mã phiếu xuất đã tồn tại!'}), 400
  if not isinstance(ngay_xuat, str):
    return jsonify({'error': 'Ngày xuất không hợp lệ.'}), 400
  try:
    ngay_hop_le = date.fromisoformat(ngay_xuat)
    if ngay_hop_le.isoformat() != ngay_xuat:
      raise ValueError('Sai định dạng')
  except ValueError:
    return jsonify({'error': 'Ngày xuất phải có dạng YYYY-MM-DD hợp lệ.'}), 400
  if not isinstance(chi_tiet, list) or not chi_tiet:
    return jsonify({'error': 'Phiếu xuất phải có ít nhất một dòng sách.'}), 400
  nguoi_nhan = data.get('nguoi_nhan', '')
  ly_do = data.get('ly_do', '')
  if not isinstance(nguoi_nhan, str) or not isinstance(ly_do, str):
    return jsonify({'error': 'Người nhận và lý do phải là văn bản.'}), 400

  tong_xuat = {}
  validated = []
  for item in chi_tiet:
    if not isinstance(item, dict):
      return jsonify({'error': 'Chi tiết phiếu không hợp lệ.'}), 400
    ma_sach = item.get('ma_sach')
    so_luong = item.get('so_luong_xuat')
    if not isinstance(ma_sach, str) or not ma_sach.strip():
      return jsonify({'error': 'Mã sách không hợp lệ.'}), 400
    if type(so_luong) is not int or not (0 < so_luong <= 9223372036854775807):
      return jsonify({'error': 'Số lượng xuất phải là số nguyên dương hợp lệ.'}), 400
    ma_sach = ma_sach.strip()
    tong_xuat[ma_sach] = tong_xuat.get(ma_sach, 0) + so_luong
    validated.append((ma_sach, so_luong))

  # Gộp số lượng của các dòng có cùng mã sách để chống xuất vượt tồn.
  for ma_sach, so_luong in tong_xuat.items():
    sach = db.session.get(Sach, ma_sach)
    if sach is None:
      return jsonify({'error': f'Không tìm thấy sách {ma_sach}.'}), 400
    if so_luong > sach.so_luong_ton:
      return jsonify({
          'error': f'Sách [{sach.ten_sach}] không đủ tồn. Có {sach.so_luong_ton}, cần {so_luong}.'
      }), 400

  # Tất cả dòng đạt kiểm tra, mới giảm tồn và lưu phiếu.
  for ma_sach, so_luong in tong_xuat.items():
    db.session.get(Sach, ma_sach).so_luong_ton -= so_luong
  chi_tiet_objs = [ChiTietPhieuXuat(
      ma_sach=ma_sach, so_luong_xuat=so_luong
  ) for ma_sach, so_luong in validated]

  phieu = PhieuXuat(
      ma_phieu_xuat=ma_phieu,
      ngay_xuat=ngay_xuat,
      nguoi_nhan=nguoi_nhan.strip(),
      ly_do=ly_do.strip(),
      nguoi_lap=session.get('ho_ten', 'Nhân viên kho'),
      chi_tiet=chi_tiet_objs,
  )
  try:
    db.session.add(phieu)
    db.session.commit()
  except SQLAlchemyError:
    db.session.rollback()
    return jsonify({'error': 'Không lưu được phiếu xuất; dữ liệu chưa được cập nhật.'}), 500
  return jsonify({'message': 'Lập phiếu xuất thành công!'}), 201


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


if __name__ == '__main__':
  init_db()
  app.run(debug=True, port=5000)