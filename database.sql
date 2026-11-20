PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS nguoi_dung (
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    ho_ten VARCHAR(100),
    CONSTRAINT pk_nguoi_dung PRIMARY KEY (username)
);

CREATE TABLE IF NOT EXISTS nha_cung_cap (
    ma_ncc VARCHAR(20) NOT NULL,
    ten_ncc VARCHAR(100) NOT NULL,
    dia_chi VARCHAR(200),
    so_dien_thoai VARCHAR(20),
    email VARCHAR(100),
    CONSTRAINT pk_nha_cung_cap PRIMARY KEY (ma_ncc)
);

CREATE TABLE IF NOT EXISTS sach (
    ma_sach VARCHAR(20) NOT NULL,
    ten_sach VARCHAR(150) NOT NULL,
    the_loai VARCHAR(50),
    tac_gia VARCHAR(100),
    nha_xuat_ban VARCHAR(100),
    ma_ncc VARCHAR(20) NOT NULL,
    gia_nhap FLOAT,
    gia_ban FLOAT,
    so_luong_ton INTEGER,
    vi_tri VARCHAR(50),
    CONSTRAINT pk_sach PRIMARY KEY (ma_sach),
    CONSTRAINT fk_sach_nha_cung_cap
        FOREIGN KEY (ma_ncc) REFERENCES nha_cung_cap (ma_ncc)
);

CREATE TABLE IF NOT EXISTS phieu_nhap (
    ma_phieu_nhap VARCHAR(20) NOT NULL,
    ngay_nhap VARCHAR(10) NOT NULL,
    ma_ncc VARCHAR(20) NOT NULL,
    nguoi_lap VARCHAR(50),
    tong_tien FLOAT,
    CONSTRAINT pk_phieu_nhap PRIMARY KEY (ma_phieu_nhap),
    CONSTRAINT fk_phieu_nhap_nha_cung_cap
        FOREIGN KEY (ma_ncc) REFERENCES nha_cung_cap (ma_ncc)
);

CREATE TABLE IF NOT EXISTS phieu_xuat (
    ma_phieu_xuat VARCHAR(20) NOT NULL,
    ngay_xuat VARCHAR(10) NOT NULL,
    nguoi_nhan VARCHAR(100),
    ly_do VARCHAR(200),
    nguoi_lap VARCHAR(50),
    CONSTRAINT pk_phieu_xuat PRIMARY KEY (ma_phieu_xuat)
);

CREATE TABLE IF NOT EXISTS chi_tiet_phieu_nhap (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_phieu_nhap VARCHAR(20) NOT NULL,
    ma_sach VARCHAR(20) NOT NULL,
    so_luong_nhap INTEGER NOT NULL,
    don_gia_nhap FLOAT NOT NULL,
    thanh_tien FLOAT NOT NULL,
    CONSTRAINT fk_ct_phieu_nhap_phieu_nhap
        FOREIGN KEY (ma_phieu_nhap) REFERENCES phieu_nhap (ma_phieu_nhap),
    CONSTRAINT fk_ct_phieu_nhap_sach
        FOREIGN KEY (ma_sach) REFERENCES sach (ma_sach)
);

CREATE TABLE IF NOT EXISTS chi_tiet_phieu_xuat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_phieu_xuat VARCHAR(20) NOT NULL,
    ma_sach VARCHAR(20) NOT NULL,
    so_luong_xuat INTEGER NOT NULL,
    CONSTRAINT fk_ct_phieu_xuat_phieu_xuat
        FOREIGN KEY (ma_phieu_xuat) REFERENCES phieu_xuat (ma_phieu_xuat),
    CONSTRAINT fk_ct_phieu_xuat_sach
        FOREIGN KEY (ma_sach) REFERENCES sach (ma_sach)
);
