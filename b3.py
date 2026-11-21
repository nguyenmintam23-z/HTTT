from datetime import date
from math import isfinite
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, jsonify, request, session
from models import (db, NhaCungCap, Sach, PhieuNhap, ChiTietPhieuNhap,
                    PhieuXuat, ChiTietPhieuXuat)

b3 = Blueprint('b3', __name__)


@b3.route('/api/phieu-nhap', methods=['POST'])
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
