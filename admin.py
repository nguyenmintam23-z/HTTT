import re
from secrets import token_hex
from functools import wraps

from flask import Blueprint, jsonify, request, session
from werkzeug.security import generate_password_hash


def create_admin_blueprint(db, NguoiDung, ChucVu):
  admin = Blueprint('admin', __name__)

  def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
      if session.get('role') != 'admin':
        return jsonify({'error': 'Chỉ quản trị viên mới được sử dụng chức năng này.'}), 403
      return view(*args, **kwargs)
    return wrapped

  def validate_position(name):
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 50:
      return None
    return name.strip()

  @admin.route('/api/admin/users', methods=['GET'])
  @admin_required
  def get_admin_users():
    users = NguoiDung.query.filter(
        NguoiDung.role.in_(('staff', 'manager'))
    ).order_by(NguoiDung.username).all()
    return jsonify([{
        'username': user.username,
        'ho_ten': user.ho_ten,
        'role': user.role,
        'chuc_vu': user.chuc_vu,
    } for user in users])

  @admin.route('/api/admin/users', methods=['POST'])
  @admin_required
  def add_admin_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
      return jsonify({'error': 'Dữ liệu tài khoản không hợp lệ.'}), 400
    username = data.get('username')
    ho_ten = data.get('ho_ten')
    role = data.get('role')
    password = data.get('password')
    chuc_vu = validate_position(data.get('chuc_vu'))
    if not isinstance(username, str) or not re.fullmatch(r'[A-Za-z0-9._-]{3,50}', username):
      return jsonify({'error': 'Tên đăng nhập cần từ 3 đến 50 ký tự (chữ, số, ., _, -).'}), 400
    if not isinstance(ho_ten, str) or not ho_ten.strip() or len(ho_ten.strip()) > 100:
      return jsonify({'error': 'Vui lòng nhập họ tên hợp lệ (tối đa 100 ký tự).'}), 400
    if role not in ('staff', 'manager'):
      return jsonify({'error': 'Loại tài khoản không hợp lệ.'}), 400
    if not isinstance(password, str) or not 6 <= len(password) <= 128:
      return jsonify({'error': 'Mật khẩu cần từ 6 đến 128 ký tự.'}), 400
    if chuc_vu is None or db.session.get(ChucVu, chuc_vu) is None:
      return jsonify({'error': 'Vui lòng chọn chức vụ đã được khai báo.'}), 400
    if db.session.get(NguoiDung, username):
      return jsonify({'error': 'Tên đăng nhập đã tồn tại.'}), 400
    db.session.add(NguoiDung(
        username=username,
        password=generate_password_hash(password),
        role=role,
        ho_ten=ho_ten.strip(),
        chuc_vu=chuc_vu,
    ))
    db.session.commit()
    return jsonify({'message': 'Tạo tài khoản thành công.'}), 201

  @admin.route('/api/admin/users/<username>', methods=['PUT'])
  @admin_required
  def update_admin_user(username):
    user = db.session.get(NguoiDung, username)
    if user is None or user.role not in ('staff', 'manager'):
      return jsonify({'error': 'Không tìm thấy tài khoản nhân viên.'}), 404
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or data.get('username', username) != username:
      return jsonify({'error': 'Dữ liệu hoặc tên tài khoản không hợp lệ.'}), 400
    ho_ten = data.get('ho_ten')
    role = data.get('role')
    chuc_vu = validate_position(data.get('chuc_vu'))
    if not isinstance(ho_ten, str) or not ho_ten.strip() or len(ho_ten.strip()) > 100:
      return jsonify({'error': 'Vui lòng nhập họ tên hợp lệ (tối đa 100 ký tự).'}), 400
    if role not in ('staff', 'manager'):
      return jsonify({'error': 'Loại tài khoản không hợp lệ.'}), 400
    if chuc_vu is None or db.session.get(ChucVu, chuc_vu) is None:
      return jsonify({'error': 'Vui lòng chọn chức vụ đã được khai báo.'}), 400
    password = data.get('password', '')
    if not isinstance(password, str) or (password != '' and not 6 <= len(password) <= 128):
      return jsonify({'error': 'Mật khẩu mới cần từ 6 đến 128 ký tự.'}), 400
    if user.role != role or password:
      user.session_version = token_hex(16)
    user.ho_ten = ho_ten.strip()
    user.role = role
    user.chuc_vu = chuc_vu
    if password:
      user.password = generate_password_hash(password)
    db.session.commit()
    return jsonify({'message': 'Cập nhật tài khoản thành công.'})

  @admin.route('/api/admin/users/<username>', methods=['DELETE'])
  @admin_required
  def delete_admin_user(username):
    user = db.session.get(NguoiDung, username)
    if user is None or user.role not in ('staff', 'manager'):
      return jsonify({'error': 'Không tìm thấy tài khoản nhân viên.'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Xóa tài khoản thành công.'})

  @admin.route('/api/admin/positions', methods=['GET'])
  @admin_required
  def get_admin_positions():
    positions = ChucVu.query.order_by(ChucVu.ten_chuc_vu).all()
    return jsonify([position.ten_chuc_vu for position in positions])

  @admin.route('/api/admin/positions', methods=['POST'])
  @admin_required
  def add_admin_position():
    data = request.get_json(silent=True)
    name = validate_position(data.get('ten_chuc_vu')) if isinstance(data, dict) else None
    if name is None:
      return jsonify({'error': 'Tên chức vụ không hợp lệ (tối đa 50 ký tự).'}), 400
    if db.session.get(ChucVu, name):
      return jsonify({'error': 'Chức vụ đã tồn tại.'}), 400
    db.session.add(ChucVu(ten_chuc_vu=name))
    db.session.commit()
    return jsonify({'message': 'Thêm chức vụ thành công.'}), 201

  @admin.route('/api/admin/positions/<path:old_name>', methods=['PUT'])
  @admin_required
  def update_admin_position(old_name):
    position = db.session.get(ChucVu, old_name)
    if position is None:
      return jsonify({'error': 'Không tìm thấy chức vụ.'}), 404
    data = request.get_json(silent=True)
    new_name = validate_position(data.get('ten_chuc_vu')) if isinstance(data, dict) else None
    if new_name is None:
      return jsonify({'error': 'Tên chức vụ không hợp lệ (tối đa 50 ký tự).'}), 400
    if new_name != old_name and db.session.get(ChucVu, new_name):
      return jsonify({'error': 'Chức vụ đã tồn tại.'}), 400
    if new_name != old_name:
      # Tạo bảng cha trước, sau đó chuyển tham chiếu và xóa tên cũ.
      db.session.add(ChucVu(ten_chuc_vu=new_name))
      db.session.flush()
      NguoiDung.query.filter_by(chuc_vu=old_name).update(
          {NguoiDung.chuc_vu: new_name}, synchronize_session=False
      )
      db.session.delete(position)
    db.session.commit()
    return jsonify({'message': 'Cập nhật chức vụ thành công.'})

  @admin.route('/api/admin/positions/<path:name>', methods=['DELETE'])
  @admin_required
  def delete_admin_position(name):
    position = db.session.get(ChucVu, name)
    if position is None:
      return jsonify({'error': 'Không tìm thấy chức vụ.'}), 404
    if NguoiDung.query.filter_by(chuc_vu=name).first():
      return jsonify({'error': 'Không thể xóa chức vụ đang được tài khoản sử dụng.'}), 400
    db.session.delete(position)
    db.session.commit()
    return jsonify({'message': 'Xóa chức vụ thành công.'})

  return admin
