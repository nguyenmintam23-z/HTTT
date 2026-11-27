from flask_sqlalchemy import SQLAlchemy
from datetime import date
from secrets import token_hex

db = SQLAlchemy()

# --- ORM MODELS ---
class NguoiDung(db.Model):
  __tablename__ = 'nguoi_dung'
  username = db.Column(db.String(50), primary_key=True)
  password = db.Column(db.String(255), nullable=False)
  role = db.Column(db.String(20), nullable=False, default='staff', server_default='staff')
  ho_ten = db.Column(db.String(100))
  session_version = db.Column(db.String(32), nullable=False, default=lambda: token_hex(16), server_default='')
  chuc_vu = db.Column(
      db.String(50),
      db.ForeignKey('chuc_vu.ten_chuc_vu', onupdate='CASCADE', ondelete='RESTRICT'),
  )
  __table_args__ = (
      db.CheckConstraint("role IN ('staff', 'manager', 'admin')", name='chk_nguoi_dung_role'),
  )


class ChucVu(db.Model):
  __tablename__ = 'chuc_vu'
  ten_chuc_vu = db.Column(db.String(50), primary_key=True)


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
      db.String(20),
      db.ForeignKey(
          'nha_cung_cap.ma_ncc', onupdate='CASCADE', ondelete='RESTRICT'
      ),
      nullable=False,
  )
  gia_nhap = db.Column(db.Numeric(15, 2, asdecimal=False), nullable=False, default=0, server_default='0')
  gia_ban = db.Column(db.Numeric(15, 2, asdecimal=False), nullable=False, default=0, server_default='0')
  so_luong_ton = db.Column(db.Integer, nullable=False, default=0, server_default='0')
  vi_tri = db.Column(db.String(50))
  __table_args__ = (
      db.Index('idx_sach_ten', 'ten_sach'),
      db.Index('idx_sach_ma_ncc', 'ma_ncc'),
      db.CheckConstraint('gia_nhap >= 0', name='chk_sach_gia_nhap'),
      db.CheckConstraint('gia_ban >= 0', name='chk_sach_gia_ban'),
      db.CheckConstraint("typeof(so_luong_ton) = 'integer' AND so_luong_ton >= 0", name='chk_sach_ton'),
  )

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
  ngay_nhap = db.Column(db.Date, nullable=False, server_default=db.text("(DATE('now', 'localtime'))"))
  ma_ncc = db.Column(
      db.String(20),
      db.ForeignKey(
          'nha_cung_cap.ma_ncc', onupdate='CASCADE', ondelete='RESTRICT'
      ),
      nullable=False,
  )
  nguoi_lap = db.Column(
      db.String(50),
      db.ForeignKey(
          'nguoi_dung.username', onupdate='CASCADE', ondelete='SET NULL'
      ),
  )
  tong_tien = db.Column(db.Numeric(15, 2, asdecimal=False), nullable=False, default=0, server_default='0')
  __table_args__ = (
      db.Index('idx_phieu_nhap_ngay', 'ngay_nhap'),
      db.CheckConstraint('tong_tien >= 0', name='chk_phieu_nhap_tong_tien'),
  )
  chi_tiet = db.relationship(
      'ChiTietPhieuNhap',
      back_populates='phieu_nhap_ref',
      cascade='all, delete-orphan',
  )

  def to_dict(self):
    return {
        'ma_phieu_nhap': self.ma_phieu_nhap,
        'ngay_nhap': self.ngay_nhap.isoformat() if isinstance(self.ngay_nhap, date) else self.ngay_nhap,
        'ma_ncc': self.ma_ncc,
        'nguoi_lap': self.nguoi_lap,
        'tong_tien': self.tong_tien,
        'chi_tiet': [item.to_dict() for item in self.chi_tiet],
    }


class ChiTietPhieuNhap(db.Model):
  __tablename__ = 'chi_tiet_phieu_nhap'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  ma_phieu_nhap = db.Column(
      db.String(20),
      db.ForeignKey(
          'phieu_nhap.ma_phieu_nhap',
          onupdate='CASCADE',
          ondelete='CASCADE',
      ),
      nullable=False,
  )
  ma_sach = db.Column(
      db.String(20),
      db.ForeignKey(
          'sach.ma_sach', onupdate='CASCADE', ondelete='RESTRICT'
      ),
      nullable=False,
  )
  so_luong_nhap = db.Column(db.Integer, nullable=False)
  don_gia_nhap = db.Column(db.Numeric(15, 2, asdecimal=False), nullable=False)
  thanh_tien = db.Column(db.Numeric(15, 2, asdecimal=False), nullable=False)
  __table_args__ = (
      db.Index('idx_ct_nhap_ma_phieu', 'ma_phieu_nhap'),
      db.Index('idx_ct_nhap_ma_sach', 'ma_sach'),
      db.CheckConstraint("typeof(so_luong_nhap) = 'integer' AND so_luong_nhap > 0", name='chk_ct_nhap_so_luong'),
      db.CheckConstraint('don_gia_nhap >= 0', name='chk_ct_nhap_don_gia'),
      db.CheckConstraint('thanh_tien >= 0', name='chk_ct_nhap_thanh_tien'),
      {'sqlite_autoincrement': True},
  )

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
  ngay_xuat = db.Column(db.Date, nullable=False, server_default=db.text("(DATE('now', 'localtime'))"))
  nguoi_nhan = db.Column(db.String(100))
  ly_do = db.Column(db.String(200))
  nguoi_lap = db.Column(
      db.String(50),
      db.ForeignKey(
          'nguoi_dung.username', onupdate='CASCADE', ondelete='SET NULL'
      ),
  )
  __table_args__ = (
      db.Index('idx_phieu_xuat_ngay', 'ngay_xuat'),
  )
  chi_tiet = db.relationship(
      'ChiTietPhieuXuat',
      back_populates='phieu_xuat_ref',
      cascade='all, delete-orphan',
  )

  def to_dict(self):
    return {
        'ma_phieu_xuat': self.ma_phieu_xuat,
        'ngay_xuat': self.ngay_xuat.isoformat() if isinstance(self.ngay_xuat, date) else self.ngay_xuat,
        'nguoi_nhan': self.nguoi_nhan,
        'ly_do': self.ly_do,
        'nguoi_lap': self.nguoi_lap,
        'chi_tiet': [item.to_dict() for item in self.chi_tiet],
    }


class ChiTietPhieuXuat(db.Model):
  __tablename__ = 'chi_tiet_phieu_xuat'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  ma_phieu_xuat = db.Column(
      db.String(20),
      db.ForeignKey(
          'phieu_xuat.ma_phieu_xuat',
          onupdate='CASCADE',
          ondelete='CASCADE',
      ),
      nullable=False,
  )
  ma_sach = db.Column(
      db.String(20),
      db.ForeignKey(
          'sach.ma_sach', onupdate='CASCADE', ondelete='RESTRICT'
      ),
      nullable=False,
  )
  so_luong_xuat = db.Column(db.Integer, nullable=False)
  __table_args__ = (
      db.Index('idx_ct_xuat_ma_phieu', 'ma_phieu_xuat'),
      db.Index('idx_ct_xuat_ma_sach', 'ma_sach'),
      db.CheckConstraint("typeof(so_luong_xuat) = 'integer' AND so_luong_xuat > 0", name='chk_ct_xuat_so_luong'),
      {'sqlite_autoincrement': True},
  )

  phieu_xuat_ref = db.relationship('PhieuXuat', back_populates='chi_tiet')

  def to_dict(self):
    return {'ma_sach': self.ma_sach, 'so_luong_xuat': self.so_luong_xuat}


# --- AUTHENTICATION API ROUTES ---


# Bảo vệ dữ liệu cũ mà không tái tạo bảng hoặc làm mất lịch sử.
SQLITE_INDEXES = [('sach', 'ten_sach', 'idx_sach_ten'), ('sach', 'ma_ncc', 'idx_sach_ma_ncc'), ('phieu_nhap', 'ngay_nhap', 'idx_phieu_nhap_ngay'), ('phieu_xuat', 'ngay_xuat', 'idx_phieu_xuat_ngay'), ('chi_tiet_phieu_nhap', 'ma_phieu_nhap', 'idx_ct_nhap_ma_phieu'), ('chi_tiet_phieu_nhap', 'ma_sach', 'idx_ct_nhap_ma_sach'), ('chi_tiet_phieu_xuat', 'ma_phieu_xuat', 'idx_ct_xuat_ma_phieu'), ('chi_tiet_phieu_xuat', 'ma_sach', 'idx_ct_xuat_ma_sach')]
SQLITE_INTEGER_RULES = [('sach', 'so_luong_ton', '>=', '0', 'chk_sach_ton'), ('chi_tiet_phieu_nhap', 'so_luong_nhap', '>', '0', 'chk_ct_nhap_so_luong'), ('chi_tiet_phieu_xuat', 'so_luong_xuat', '>', '0', 'chk_ct_xuat_so_luong')]


def ensure_sqlite_guards(connection):
  for table, column, name in SQLITE_INDEXES:
    connection.exec_driver_sql(f'CREATE INDEX IF NOT EXISTS {name} ON {table} ({column})')
  for table, column, op, number, name in SQLITE_INTEGER_RULES:
    condition = f"typeof({column}) = 'integer' AND {column} {op} {number}"
    if connection.exec_driver_sql(f'SELECT 1 FROM {table} WHERE NOT ({condition}) OR {column} IS NULL LIMIT 1').first():
      raise RuntimeError(f'Dữ liệu cũ không hợp lệ: {table}.{column}. Hãy sao lưu và kiểm tra thủ công.')
    for action in ('INSERT', 'UPDATE'):
      connection.exec_driver_sql(f"CREATE TRIGGER IF NOT EXISTS guard_{name}_{action.lower()} BEFORE {action} ON {table} "
          f"WHEN typeof(NEW.{column}) <> 'integer' OR NOT (NEW.{column} {op} {number}) "
          f"BEGIN SELECT RAISE(ABORT, '{name}'); END")
