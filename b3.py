from datetime import date
from decimal import Decimal, DecimalException
import json
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, jsonify, request, session
from models import (db, NhaCungCap, Sach, PhieuNhap, ChiTietPhieuNhap,
                    PhieuXuat, ChiTietPhieuXuat)

b3 = Blueprint('b3', __name__)

MAX_STOCK = 9223372036854775807
# DECIMAL(15, 2): tối đa 13 chữ số phần nguyên.
MAX_MONEY = Decimal('9999999999999.99')


@b3.route('/api/phieu-nhap', methods=['POST'])
def create_phieu_nhap():
  # B3: Chỉ nhân viên kho được lập phiếu.
  if session.get('role') != 'staff':
    return jsonify({'error': 'Chỉ nhân viên kho được lập phiếu nhập.'}), 403

  # Đọc số thập phân trực tiếp từ JSON, tránh làm tròn qua float.
  if not request.is_json:
    return jsonify({'error': 'Dữ liệu phiếu nhập không hợp lệ.'}), 400
  try:
    data = json.loads(request.get_data(as_text=True), parse_float=Decimal,
                      parse_constant=Decimal)
  except (ValueError, UnicodeError, DecimalException):
    return jsonify({'error': 'Dữ liệu phiếu nhập không hợp lệ.'}), 400
  if not isinstance(data, dict):
    return jsonify({'error': 'Dữ liệu phiếu nhập không hợp lệ.'}), 400

  ma_phieu = data.get('ma_phieu_nhap')
  ngay_nhap = data.get('ngay_nhap')
  ma_ncc = data.get('ma_ncc')
  chi_tiet = data.get('chi_tiet')
  if not isinstance(ma_phieu, str) or not ma_phieu.strip():
    return jsonify({'error': 'Thiếu mã phiếu nhập.'}), 400
  ma_phieu = ma_phieu.strip()
  if len(ma_phieu) > 20:
    return jsonify({'error': 'Mã phiếu không được dài quá 20 ký tự.'}), 400
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
    if type(so_luong) is not int or not (0 < so_luong <= MAX_STOCK):
      return jsonify({'error': 'Số lượng nhập phải là số nguyên dương hợp lệ.'}), 400
    if type(don_gia) not in (int, Decimal):
      return jsonify({'error': 'Đơn giá nhập phải là số không âm, hữu hạn.'}), 400
    don_gia = Decimal(don_gia)
    if not don_gia.is_finite() or don_gia < 0 or don_gia > MAX_MONEY:
      return jsonify({'error': 'Đơn giá nhập vượt giới hạn cho phép hoặc không hữu hạn.'}), 400
    don_gia_2 = don_gia.quantize(Decimal('0.01'))
    if don_gia != don_gia_2:
      return jsonify({'error': 'Đơn giá nhập chỉ được có tối đa 2 chữ số thập phân.'}), 400
    don_gia = don_gia_2
    thanh_tien = so_luong * don_gia
    if thanh_tien > MAX_MONEY:
      return jsonify({'error': 'Thành tiền vượt giới hạn cho phép.'}), 400
    validated.append((sach, so_luong, don_gia, thanh_tien))

  # Tính toán bằng Decimal trước khi sửa tồn kho.
  tong_tien = sum((row[3] for row in validated), Decimal('0.00'))
  if tong_tien > MAX_MONEY:
    return jsonify({'error': 'Tổng tiền vượt giới hạn cho phép.'}), 400
  tong_nhap = {}
  for sach, so_luong, _, _ in validated:
    tong_nhap[sach.ma_sach] = tong_nhap.get(sach.ma_sach, 0) + so_luong
  for ma_sach, so_luong in tong_nhap.items():
    if db.session.get(Sach, ma_sach).so_luong_ton + so_luong > MAX_STOCK:
      return jsonify({'error': f'Tồn kho sách {ma_sach} vượt giới hạn.'}), 400

  chi_tiet_objs = []
  for sach, so_luong, don_gia, thanh_tien in validated:
    chi_tiet_objs.append(ChiTietPhieuNhap(
        ma_sach=sach.ma_sach,
        so_luong_nhap=so_luong,
        don_gia_nhap=don_gia,
        thanh_tien=thanh_tien,
    ))
  phieu = PhieuNhap(
      ma_phieu_nhap=ma_phieu,
      ngay_nhap=date.fromisoformat(ngay_nhap),
      ma_ncc=ma_ncc,
      nguoi_lap=session.get('user'),
      tong_tien=tong_tien,
      chi_tiet=chi_tiet_objs,
  )
  try:
    # Cộng tồn trực tiếp trong SQL, không ghi đè tồn của giao dịch khác.
    for ma_sach, so_luong in tong_nhap.items():
      changed = db.session.query(Sach).filter(
          Sach.ma_sach == ma_sach, Sach.so_luong_ton <= MAX_STOCK - so_luong
      ).update({Sach.so_luong_ton: Sach.so_luong_ton + so_luong}, synchronize_session=False)
      if changed != 1:
        db.session.rollback()
        return jsonify({'error': 'Tồn kho đã thay đổi hoặc vượt giới hạn; vui lòng thử lại.'}), 400
    db.session.add(phieu)
    db.session.commit()
  except SQLAlchemyError:
    db.session.rollback()
    return jsonify({'error': 'Không lưu được phiếu nhập; dữ liệu chưa được cập nhật.'}), 500
  return jsonify({'message': 'Lập phiếu nhập thành công!'}), 201


@b3.route('/api/phieu-xuat', methods=['POST'])
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
  if len(ma_phieu) > 20:
    return jsonify({'error': 'Mã phiếu không được dài quá 20 ký tự.'}), 400
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

  if len(nguoi_nhan.strip()) > 100 or len(ly_do.strip()) > 200:
    return jsonify({'error': 'Người nhận tối đa 100 ký tự, lý do tối đa 200 ký tự.'}), 400

  tong_xuat = {}
  validated = []
  for item in chi_tiet:
    if not isinstance(item, dict):
      return jsonify({'error': 'Chi tiết phiếu không hợp lệ.'}), 400
    ma_sach = item.get('ma_sach')
    so_luong = item.get('so_luong_xuat')
    if not isinstance(ma_sach, str) or not ma_sach.strip():
      return jsonify({'error': 'Mã sách không hợp lệ.'}), 400
    if type(so_luong) is not int or not (0 < so_luong <= MAX_STOCK):
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
  chi_tiet_objs = [ChiTietPhieuXuat(
      ma_sach=ma_sach, so_luong_xuat=so_luong
  ) for ma_sach, so_luong in validated]

  phieu = PhieuXuat(
      ma_phieu_xuat=ma_phieu,
      ngay_xuat=date.fromisoformat(ngay_xuat),
      nguoi_nhan=nguoi_nhan.strip(),
      ly_do=ly_do.strip(),
      nguoi_lap=session.get('user'),
      chi_tiet=chi_tiet_objs,
  )
  try:
    # Điều kiện tồn kho được kiểm tra lại ngay tại câu lệnh UPDATE.
    for ma_sach, so_luong in tong_xuat.items():
      changed = db.session.query(Sach).filter(
          Sach.ma_sach == ma_sach, Sach.so_luong_ton >= so_luong
      ).update({Sach.so_luong_ton: Sach.so_luong_ton - so_luong}, synchronize_session=False)
      if changed != 1:
        db.session.rollback()
        return jsonify({'error': 'Tồn kho đã thay đổi; không đủ sách để xuất.'}), 400
    db.session.add(phieu)
    db.session.commit()
  except SQLAlchemyError:
    db.session.rollback()
    return jsonify({'error': 'Không lưu được phiếu xuất; dữ liệu chưa được cập nhật.'}), 500
  return jsonify({'message': 'Lập phiếu xuất thành công!'}), 201


@b3.route('/api/phieu-xuat', methods=['GET'])
def get_phieu_xuat():
  # Nhân viên chỉ xem phiếu mình lập; quản lý xem tất cả. Không cấp quyền cho Admin.
  if not session.get('user'):
    return jsonify({'error': 'Chưa đăng nhập!'}), 401
  role = session.get('role')
  if role not in ('staff', 'manager'):
    return jsonify({'error': 'Không có quyền xem lịch sử xuất kho.'}), 403

  thang, nam = request.args.get('thang', ''), request.args.get('nam', '')

  def valid_period(value, maximum):
    return not value or (value.isascii() and value.isdecimal()
                         and len(value) <= 4 and 1 <= int(value) <= maximum)

  if not valid_period(thang, 12) or not valid_period(nam, 9999):
    return jsonify({'error': 'Tháng phải từ 1 đến 12 và năm từ 1 đến 9999.'}), 400

  query = PhieuXuat.query
  if role == 'staff':
    query = query.filter(PhieuXuat.nguoi_lap == session['user'])
  if thang:
    query = query.filter(db.func.substr(PhieuXuat.ngay_xuat, 6, 2) == f'{int(thang):02d}')
  if nam:
    query = query.filter(db.func.substr(PhieuXuat.ngay_xuat, 1, 4) == f'{int(nam):04d}')
  receipts = query.order_by(PhieuXuat.ngay_xuat.desc(), PhieuXuat.ma_phieu_xuat).all()
  result = [receipt.to_dict() for receipt in receipts]
  codes = {item['ma_sach'] for receipt in result for item in receipt['chi_tiet']}
  names = dict(db.session.query(Sach.ma_sach, Sach.ten_sach).filter(Sach.ma_sach.in_(codes)).all()) if codes else {}
  for receipt in result:
    for item in receipt['chi_tiet']:
      item['ten_sach'] = names.get(item['ma_sach'])
  return jsonify(result)
