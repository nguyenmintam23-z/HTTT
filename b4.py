from math import isfinite
from sys import float_info
from flask import Blueprint, jsonify, request, session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from models import (db, Sach, NhaCungCap, PhieuNhap,
                    ChiTietPhieuNhap, ChiTietPhieuXuat)

b4 = Blueprint('b4', __name__)

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
    query = query.order_by(Sach.ten_sach.asc())
  elif sort_by == 'gia':
    query = query.order_by(Sach.gia_ban.asc())
  if not sort_by:
    query = query.order_by(Sach.ma_sach.asc())
  return jsonify([s.to_dict() for s in query.all()])


@b4.route('/api/sach', methods=['POST'])
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


@b4.route('/api/sach/<ma_sach>', methods=['PUT'])
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
  db.session.delete(sach)
  db.session.commit()
  return jsonify({'message': 'Xóa sách thành công!'})


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
  data = request.json
  if db.session.get(NhaCungCap, data.get('ma_ncc')):
    return jsonify({'error': 'Mã nhà cung cấp đã tồn tại!'}), 400
  db.session.add(NhaCungCap(**data))
  db.session.commit()
  return jsonify({'message': 'Thêm nhà cung cấp thành công!'}), 201


@b4.route('/api/ncc/<ma_ncc>', methods=['PUT'])
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
  db.session.delete(ncc)
  db.session.commit()
  return jsonify({'message': 'Xóa nhà cung cấp thành công!'})


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

  if not valid_period(thang, 12) or not valid_period(nam, 9999):
    return jsonify({'error': 'Tháng phải từ 1 đến 12 và năm từ 1 đến 9999.'}), 400

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


