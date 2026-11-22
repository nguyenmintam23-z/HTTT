PRAGMA foreign_keys = ON;

-- 1. Bảng chức vụ
CREATE TABLE IF NOT EXISTS chuc_vu (
    ten_chuc_vu VARCHAR(50) NOT NULL,
    CONSTRAINT pk_chuc_vu PRIMARY KEY (ten_chuc_vu)
);

-- 2. Bảng người dùng
CREATE TABLE IF NOT EXISTS nguoi_dung (
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'staff',
    ho_ten VARCHAR(100),
    chuc_vu VARCHAR(50),
    CONSTRAINT pk_nguoi_dung PRIMARY KEY (username),
    CONSTRAINT fk_nguoi_dung_chuc_vu
        FOREIGN KEY (chuc_vu) REFERENCES chuc_vu (ten_chuc_vu)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_nguoi_dung_role
        CHECK (role IN ('staff', 'manager', 'admin'))
);

-- 3. Bảng nhà cung cấp
CREATE TABLE IF NOT EXISTS nha_cung_cap (
    ma_ncc VARCHAR(20) NOT NULL,
    ten_ncc VARCHAR(100) NOT NULL,
    dia_chi VARCHAR(200),
    so_dien_thoai VARCHAR(20),
    email VARCHAR(100),
    CONSTRAINT pk_nha_cung_cap PRIMARY KEY (ma_ncc)
);

-- 3. Bảng sách
CREATE TABLE IF NOT EXISTS sach (
    ma_sach VARCHAR(20) NOT NULL,
    ten_sach VARCHAR(150) NOT NULL,
    the_loai VARCHAR(50),
    tac_gia VARCHAR(100),
    nha_xuat_ban VARCHAR(100),
    ma_ncc VARCHAR(20) NOT NULL,
    gia_nhap DECIMAL(15, 2) NOT NULL DEFAULT 0,
    gia_ban DECIMAL(15, 2) NOT NULL DEFAULT 0,
    so_luong_ton INTEGER NOT NULL DEFAULT 0,
    vi_tri VARCHAR(50),
    CONSTRAINT pk_sach PRIMARY KEY (ma_sach),
    CONSTRAINT fk_sach_nha_cung_cap
        FOREIGN KEY (ma_ncc) REFERENCES nha_cung_cap (ma_ncc)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_sach_gia_nhap CHECK (gia_nhap >= 0),
    CONSTRAINT chk_sach_gia_ban CHECK (gia_ban >= 0),
    CONSTRAINT chk_sach_ton CHECK (so_luong_ton >= 0)
);

-- 4. Bảng phiếu nhập
CREATE TABLE IF NOT EXISTS phieu_nhap (
    ma_phieu_nhap VARCHAR(20) NOT NULL,
    ngay_nhap DATE NOT NULL DEFAULT (DATE('now', 'localtime')),
    ma_ncc VARCHAR(20) NOT NULL,
    nguoi_lap VARCHAR(50),
    tong_tien DECIMAL(15, 2) NOT NULL DEFAULT 0,
    CONSTRAINT pk_phieu_nhap PRIMARY KEY (ma_phieu_nhap),
    CONSTRAINT fk_phieu_nhap_nha_cung_cap
        FOREIGN KEY (ma_ncc) REFERENCES nha_cung_cap (ma_ncc)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_phieu_nhap_nguoi_dung
        FOREIGN KEY (nguoi_lap) REFERENCES nguoi_dung (username)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT chk_phieu_nhap_tong_tien CHECK (tong_tien >= 0)
);

-- 5. Bảng phiếu xuất
CREATE TABLE IF NOT EXISTS phieu_xuat (
    ma_phieu_xuat VARCHAR(20) NOT NULL,
    ngay_xuat DATE NOT NULL DEFAULT (DATE('now', 'localtime')),
    nguoi_nhan VARCHAR(100),
    ly_do VARCHAR(200),
    nguoi_lap VARCHAR(50),
    CONSTRAINT pk_phieu_xuat PRIMARY KEY (ma_phieu_xuat),
    CONSTRAINT fk_phieu_xuat_nguoi_dung
        FOREIGN KEY (nguoi_lap) REFERENCES nguoi_dung (username)
        ON UPDATE CASCADE
        ON DELETE SET NULL
);

-- 6. Bảng chi tiết phiếu nhập
CREATE TABLE IF NOT EXISTS chi_tiet_phieu_nhap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_phieu_nhap VARCHAR(20) NOT NULL,
    ma_sach VARCHAR(20) NOT NULL,
    so_luong_nhap INTEGER NOT NULL,
    don_gia_nhap DECIMAL(15, 2) NOT NULL,
    thanh_tien DECIMAL(15, 2) NOT NULL,
    CONSTRAINT fk_ct_phieu_nhap_phieu_nhap
        FOREIGN KEY (ma_phieu_nhap) REFERENCES phieu_nhap (ma_phieu_nhap)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_ct_phieu_nhap_sach
        FOREIGN KEY (ma_sach) REFERENCES sach (ma_sach)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_ct_nhap_so_luong CHECK (so_luong_nhap > 0),
    CONSTRAINT chk_ct_nhap_don_gia CHECK (don_gia_nhap >= 0),
    CONSTRAINT chk_ct_nhap_thanh_tien CHECK (thanh_tien >= 0)
);

-- 7. Bảng chi tiết phiếu xuất
CREATE TABLE IF NOT EXISTS chi_tiet_phieu_xuat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_phieu_xuat VARCHAR(20) NOT NULL,
    ma_sach VARCHAR(20) NOT NULL,
    so_luong_xuat INTEGER NOT NULL,
    CONSTRAINT fk_ct_phieu_xuat_phieu_xuat
        FOREIGN KEY (ma_phieu_xuat) REFERENCES phieu_xuat (ma_phieu_xuat)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_ct_phieu_xuat_sach
        FOREIGN KEY (ma_sach) REFERENCES sach (ma_sach)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT chk_ct_xuat_so_luong CHECK (so_luong_xuat > 0)
);

-- Chỉ mục (Index) tăng tốc độ tìm kiếm & join
CREATE INDEX IF NOT EXISTS idx_sach_ten ON sach (ten_sach);
CREATE INDEX IF NOT EXISTS idx_sach_ma_ncc ON sach (ma_ncc);
CREATE INDEX IF NOT EXISTS idx_phieu_nhap_ngay ON phieu_nhap (ngay_nhap);
CREATE INDEX IF NOT EXISTS idx_phieu_xuat_ngay ON phieu_xuat (ngay_xuat);
CREATE INDEX IF NOT EXISTS idx_ct_nhap_ma_phieu ON chi_tiet_phieu_nhap (ma_phieu_nhap);
CREATE INDEX IF NOT EXISTS idx_ct_nhap_ma_sach ON chi_tiet_phieu_nhap (ma_sach);
CREATE INDEX IF NOT EXISTS idx_ct_xuat_ma_phieu ON chi_tiet_phieu_xuat (ma_phieu_xuat);
CREATE INDEX IF NOT EXISTS idx_ct_xuat_ma_sach ON chi_tiet_phieu_xuat (ma_sach);