import re
from math import isfinite
from sys import float_info
from models import db, Sach, NhaCungCap, PhieuNhap, ChiTietPhieuNhap, ChiTietPhieuXuat
from flask import Blueprint, jsonify, request, session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
b4 = Blueprint('b4', __name__)

def validate_payload(model, payload, creating):
  if not isinstance(payload, dict):
    return None, 'Dữ liệu phải là một đối tượng JSON.'
  is_book = model is Sach
  code = 'ma_sach' if is_book else 'ma_ncc'
  name = 'ten_sach' if is_book else 'ten_ncc'
  fields = (
      ('ma_sach', 'ten_sach', 'the_loai', 'tac_gia', 'nha_xuat_ban',
       'ma_ncc', 'gia_nhap', 'gia_ban', 'so_luong_ton', 'vi_tri')
      if is_book else ('ma_ncc', 'ten_ncc', 'dia_chi', 'so_dien_thoai', 'email')
  )
  if set(payload) - set(fields):
    return None, 'Dữ liệu chứa trường không được hỗ trợ.'
  required = (code, name, 'ma_ncc') if is_book else (code, name)
  if creating and any(field not in payload for field in required):
    return None, 'Vui lòng nhập đầy đủ mã, tên và nhà cung cấp nếu là sách.'
  result = {}
  for field, value in payload.items():
    if field in ('gia_nhap', 'gia_ban'):
      if type(value) not in (int, float) or not 0 <= value <= float_info.max:
        return None, 'Giá phải là số hữu hạn, không âm.'
    elif field == 'so_luong_ton':
      if type(value) is not int or not 0 <= value <= 2147483647:
        return None, 'Tồn kho phải là số nguyên không âm và không vượt 2147483647.'
    else:
      if not isinstance(value, str):
        return None, f'Trường {field} phải là văn bản.'
      value = value.strip()
      limit = model.__table__.columns[field].type.length
      if limit and len(value) > limit:
        return None, f'Trường {field} tối đa {limit} ký tự.'
      if field in required and not value:
        return None, 'Mã, tên và nhà cung cấp không được để trống.'
      if field in (code, 'ma_ncc') and ('/' in value or any(ord(c) < 32 for c in value)):
        return None, 'Mã không được chứa dấu / hoặc ký tự điều khiển.'
      if field == 'email' and value and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
        return None, 'Email không hợp lệ.'
      if field == 'so_dien_thoai' and value:
        digits = re.sub(r'[^0-9]', '', value)
        if (not 6 <= len(digits) <= 15
            or not re.fullmatch(r'\+?(?:[0-9]+|\([0-9]+\))(?:[ -]?(?:[0-9]+|\([0-9]+\)))*', value)):
          return None, 'Số điện thoại phải có 6–15 chữ số và định dạng hợp lệ.'
    result[field] = value
  if is_book and 'ma_ncc' in result and db.session.get(NhaCungCap, result['ma_ncc']) is None:
    return None, 'Nhà cung cấp không tồn tại.'
  return result, None


def save_changes(message, status=200):
  try:
    db.session.commit()
  except IntegrityError:
    db.session.rollback()
    return jsonify({'error': 'Dữ liệu trùng hoặc đang được tham chiếu, không thể lưu thay đổi.'}), 409
  except SQLAlchemyError:
    db.session.rollback()
    return jsonify({'error': 'Không lưu được dữ liệu. Vui lòng thử lại.'}), 500
  return jsonify({'message': message}), status



@b4.route('/api/sach', methods=['GET'])
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
    query = query.order_by(Sach.ten_sach.asc(), Sach.ma_sach.asc())
  elif sort_by == 'gia':
    query = query.order_by(Sach.gia_ban.asc(), Sach.ma_sach.asc())
  if sort_by not in ('ten', 'gia'):
    query = query.order_by(Sach.ma_sach.asc())
  return jsonify([s.to_dict() for s in query.all()])


@b4.route('/api/sach', methods=['POST'])
def add_sach():
  if session.get('role') != 'manager':
    return jsonify({'error': 'Chỉ quản lý được thêm sách.'}), 403
  data, error = validate_payload(Sach, request.get_json(silent=True), creating=True)
  if error:
    return jsonify({'error': error}), 400
  if db.session.get(Sach, data['ma_sach']):
    return jsonify({'error': 'Mã sách đã tồn tại!'}), 409
  db.session.add(Sach(**data))
  return save_changes('Thêm sách thành công!', 201)


@b4.route('/api/sach/<ma_sach>', methods=['PUT'])
def update_sach(ma_sach):
  if session.get('role') != 'manager':
    return jsonify({'error': 'Chỉ quản lý được cập nhật.'}), 403
  record = db.session.get(Sach, ma_sach)
  if record is None:
    return jsonify({'error': 'Không tìm thấy bản ghi.'}), 404
  changes, error = validate_payload(Sach, request.get_json(silent=True), creating=False)
  if error:
    return jsonify({'error': error}), 400
  new_code = changes.pop('ma_sach', ma_sach)
  # Stock changes belong to receipt workflows once the book exists.
  changes.pop('so_luong_ton', None)
  if new_code != ma_sach and db.session.get(Sach, new_code) is not None:
    return jsonify({'error': 'Mã sách đã tồn tại!'}), 409

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
  except SQLAlchemyError:
    db.session.rollback()
    return jsonify({'error': 'Không lưu được dữ liệu. Vui lòng thử lại.'}), 500
  return jsonify({'message': 'Cập nhật thành công!'})



@b4.route('/api/sach/<ma_sach>', methods=['DELETE'])
def delete_sach(ma_sach):
  if session.get('role') != 'manager':
    return (
        jsonify({'error': 'Truy cập bị từ chối! Chỉ Quản lý mới được xóa sách.'}),
        403,
    )
  sach = db.session.get(Sach, ma_sach)
  if not sach:
    return jsonify({'error': 'Không tìm thấy sách!'}), 404
  if (ChiTietPhieuNhap.query.filter_by(ma_sach=ma_sach).first()
      or ChiTietPhieuXuat.query.filter_by(ma_sach=ma_sach).first()):
    return jsonify({'error': 'Sách đã có lịch sử nhập/xuất nên không thể xóa.'}), 409
  db.session.delete(sach)
  return save_changes('Xóa sách thành công!')


@b4.route('/api/ncc', methods=['GET'])
def get_ncc():
  if 'user' not in session:
    return jsonify({'error': 'Chưa đăng nhập!'}), 401
  return jsonify([n.to_dict() for n in NhaCungCap.query.all()])


@b4.route('/api/ncc', methods=['POST'])
def add_ncc():
  if session.get('role') != 'manager':
    return (
        jsonify({'error': 'Truy cập bị từ chối! Chỉ Quản lý mới được thao tác NCC.'}),
        403,
    )
  data, error = validate_payload(NhaCungCap, request.get_json(silent=True), creating=True)
  if error:
    return jsonify({'error': error}), 400
  if db.session.get(NhaCungCap, data['ma_ncc']):
    return jsonify({'error': 'Mã nhà cung cấp đã tồn tại!'}), 409
  db.session.add(NhaCungCap(**data))
  return save_changes('Thêm nhà cung cấp thành công!', 201)


@b4.route('/api/ncc/<ma_ncc>', methods=['PUT'])
def update_ncc(ma_ncc):
  if session.get('role') != 'manager':
    return jsonify({'error': 'Chỉ quản lý được cập nhật.'}), 403
  record = db.session.get(NhaCungCap, ma_ncc)
  if record is None:
    return jsonify({'error': 'Không tìm thấy bản ghi.'}), 404
  changes, error = validate_payload(NhaCungCap, request.get_json(silent=True), creating=False)
  if error:
    return jsonify({'error': error}), 400
  if changes.get('ma_ncc', ma_ncc) != ma_ncc:
    return jsonify({'error': 'Không thể đổi mã nhà cung cấp.'}), 400
  for field, value in changes.items():
    setattr(record, field, value)
  return save_changes('Cập nhật nhà cung cấp thành công!')


@b4.route('/api/ncc/<ma_ncc>', methods=['DELETE'])
def delete_ncc(ma_ncc):
  if session.get('role') != 'manager':
    return (
        jsonify({'error': 'Truy cập bị từ chối! Chỉ Quản lý mới được xóa NCC.'}),
        403,
    )
  ncc = db.session.get(NhaCungCap, ma_ncc)
  if not ncc:
    return jsonify({'error': 'Không tìm thấy nhà cung cấp!'}), 404
  if (Sach.query.filter_by(ma_ncc=ma_ncc).first()
      or PhieuNhap.query.filter_by(ma_ncc=ma_ncc).first()):
    return jsonify({'error': 'Nhà cung cấp đang được sách hoặc phiếu nhập sử dụng nên không thể xóa.'}), 409
  db.session.delete(ncc)
  return save_changes('Xóa nhà cung cấp thành công!')


@b4.route('/api/phieu-nhap', methods=['GET'])
def get_phieu_nhap():
  # Nhân viên chỉ được xem phiếu do chính mình lập; quản lý xem toàn kho.
  if not session.get('user'):
    return jsonify({'error': 'Chưa đăng nhập!'}), 401
  role = session.get('role')
  if role not in ('staff', 'manager'):
    return jsonify({'error': 'Không có quyền xem lịch sử nhập kho.'}), 403
  thang, nam = request.args.get('thang', ''), request.args.get('nam', '')

  def valid_period(value, maximum):
    return not value or (
        value.isascii() and value.isdecimal() and len(value) <= 4
        and 1 <= int(value) <= maximum
    )

  if not valid_period(thang, 12) or (nam and not re.fullmatch(r'[1-9][0-9]{3}', nam)):
    return jsonify({'error': 'Tháng phải từ 1 đến 12, năm phải có đúng 4 chữ số (1000–9999).'}), 400

  query = PhieuNhap.query
  if role == 'staff':
    query = query.filter(PhieuNhap.nguoi_lap == session['user'])
  if thang:
    query = query.filter(db.func.substr(PhieuNhap.ngay_nhap, 6, 2) == f'{int(thang):02d}')
  if nam:
    query = query.filter(db.func.substr(PhieuNhap.ngay_nhap, 1, 4) == f'{int(nam):04d}')
  receipts = query.order_by(PhieuNhap.ngay_nhap.desc(), PhieuNhap.ma_phieu_nhap).all()
  result = [receipt.to_dict() for receipt in receipts]
  codes = {item['ma_sach'] for receipt in result for item in receipt['chi_tiet']}
  names = dict(db.session.query(Sach.ma_sach, Sach.ten_sach).filter(Sach.ma_sach.in_(codes)).all()) if codes else {}
  supplier_codes = {receipt['ma_ncc'] for receipt in result}
  suppliers = dict(db.session.query(NhaCungCap.ma_ncc, NhaCungCap.ten_ncc).filter(NhaCungCap.ma_ncc.in_(supplier_codes)).all()) if supplier_codes else {}
  for receipt in result:
    receipt['ten_ncc'] = suppliers.get(receipt['ma_ncc'])
    for item in receipt['chi_tiet']:
      item['ten_sach'] = names.get(item['ma_sach'])
  return jsonify(result)
