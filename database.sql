-- Chỉ chạy trên CSDL mới/rỗng. Dữ liệu bên dưới là dữ liệu DEMO cục bộ.
PRAGMA foreign_keys = ON;
BEGIN;

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
    session_version VARCHAR(32) NOT NULL DEFAULT '',
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

-- 4. Bảng sách
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
    CONSTRAINT chk_sach_ton CHECK (typeof(so_luong_ton) = 'integer' AND so_luong_ton >= 0)
);

-- 5. Bảng phiếu nhập
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

-- 6. Bảng phiếu xuất
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

-- 7. Bảng chi tiết phiếu nhập
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
    CONSTRAINT chk_ct_nhap_so_luong CHECK (typeof(so_luong_nhap) = 'integer' AND so_luong_nhap > 0),
    CONSTRAINT chk_ct_nhap_don_gia CHECK (don_gia_nhap >= 0),
    CONSTRAINT chk_ct_nhap_thanh_tien CHECK (thanh_tien >= 0)
);

-- 8. Bảng chi tiết phiếu xuất
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
    CONSTRAINT chk_ct_xuat_so_luong CHECK (typeof(so_luong_xuat) = 'integer' AND so_luong_xuat > 0)
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

-- 9. Dữ liệu mẫu; ba phiếu PN-DEMO được gán nhân viên demo staff.

-- chuc_vu
INSERT INTO chuc_vu (ten_chuc_vu) VALUES ('Nhân viên kho');
INSERT INTO chuc_vu (ten_chuc_vu) VALUES ('Quản lý kho');
INSERT INTO chuc_vu (ten_chuc_vu) VALUES ('Quản trị hệ thống');

-- nguoi_dung
INSERT INTO nguoi_dung (username, password, role, ho_ten, chuc_vu) VALUES ('manager', 'scrypt:32768:8:1$cTxsHy4PZIP4VNIy$ca2edb62a9c7dec786d5c1b0917675f676d0891eaa7dab8b69955121867391e89992687f11985fbd14bfe30fc0e5e225e8dd414a005f415b8dc2ca0c6c15899d', 'manager', 'Nguyễn Quản Lý', 'Quản lý kho');
INSERT INTO nguoi_dung (username, password, role, ho_ten, chuc_vu) VALUES ('staff', 'scrypt:32768:8:1$78LTFYXgBvkDmXPH$5c4ffaa3ef59a1ea3222f9c2ada85130cc9f48824a0ec86454ce4ffce1ace27cee105b72b6e631d5119ae0f801cd31cd40836a288c317430e9050ae9021e0856', 'staff', 'Trần Nhân Viên', 'Nhân viên kho');
INSERT INTO nguoi_dung (username, password, role, ho_ten, chuc_vu) VALUES ('admin', 'scrypt:32768:8:1$AFakc9lqfbNdToOL$084d1756d7163e8e51ae3eafae71ddf829dd8d1521ff9d22e9fa1feca02eb4143ec989dccbb7ca97764ef107f0ec4ebc7c272f0f6d4455503e60611af0dc6d2b', 'admin', 'Quản trị viên', 'Quản trị hệ thống');

-- nha_cung_cap
INSERT INTO nha_cung_cap (ma_ncc, ten_ncc, dia_chi, so_dien_thoai, email) VALUES ('NCC01', 'Công ty Sách Trí Tuệ', '125 An Dương Vương, Q.6, TP.HCM', '0901234567', 'contact@tritue.com');
INSERT INTO nha_cung_cap (ma_ncc, ten_ncc, dia_chi, so_dien_thoai, email) VALUES ('NCC02', 'Nhà Xuất Bản Xã Hội', '45 Tôn Đức Thắng, Q.1, TP.HCM', '0987654321', 'info@nxbxahoi.vn');
INSERT INTO nha_cung_cap (ma_ncc, ten_ncc, dia_chi, so_dien_thoai, email) VALUES ('NCC03', 'Nhà Xuất Bản Đại Học Quốc Gia', '123 Nguyễn Văn Linh, Thành Phố Thủ Đức', '0912317516', 'dhqg@gmail.com');
INSERT INTO nha_cung_cap (ma_ncc, ten_ncc, dia_chi, so_dien_thoai, email) VALUES ('NCC04', 'Nhà cung cấp Sách Ánh Dương', '123 Tôn Đức Thắng, quận 1, TP.HCM', '0987123412', 'contact@nxbad.com');
INSERT INTO nha_cung_cap (ma_ncc, ten_ncc, dia_chi, so_dien_thoai, email) VALUES ('NCC05', 'Nhà cung cấp Tri Thức Xanh', '56 Nguyễn Trãi, quận 5, TP.HCM', '0363636363', 'contact@nxbttx.com');
INSERT INTO nha_cung_cap (ma_ncc, ten_ncc, dia_chi, so_dien_thoai, email) VALUES ('NCC06', 'Nhà cung cấp Sách Sao Mai', '15 Lý Thường Kiệt, quận Tân Phú, TP.HCM', '0383838383', 'contact@nxbsm.com');

-- sach
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S001', 'Lập trình Python', 'Công nghệ thông tin', 'Nguyễn Minh Thanh', 'NXB Khoa Học', 'NCC01', 65000, 100000, 15, 'B2');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S002', 'Python cơ bản', 'Công nghệ thông tin', 'Nguyễn Minh Anh', NULL, 'NCC01', 65000, 99000, 21, 'A2');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S003', 'Thiết kế hệ thống thông tin', 'Công nghệ thông tin', 'Trần Hải Nam', NULL, 'NCC02', 92000, 145000, 15, 'A3');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S004', 'Dế Mèn phiêu lưu ký', 'Văn học', 'Tô Hoài', NULL, 'NCC03', 35000, 59000, 31, 'B1');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S005', 'Đất rừng phương Nam', 'Văn học', 'Đoàn Giỏi', NULL, 'NCC01', 47000, 79000, 16, 'B2');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S006', 'Toán ứng dụng', 'Giáo trình', 'Lê Thanh Bình', NULL, 'NCC02', 105000, 169000, 9, 'C1');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S007', 'Kỹ năng làm việc nhóm', 'Kỹ năng', 'Phạm Thảo Vy', NULL, 'NCC03', 41000, 69000, 23, 'D1');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S008', 'Việt Bắc', 'Văn học', 'Tố Hữu', 'Nhà xuất bản Hà Nội', 'NCC02', 40000, 60000, 34, 'B2');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S009', 'Nhập môn JavaScript', 'Công nghệ thông tin', 'Tác giả mẫu', 'NXB mẫu', 'NCC04', 43500, 70000, 12, 'A1');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S010', 'Cơ sở dữ liệu SQL', 'Công nghệ thông tin', 'Tác giả mẫu', 'NXB mẫu', 'NCC05', 47000, 75000, 14, 'A2');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S011', 'Lập trình hướng đối tượng', 'Công nghệ thông tin', 'Tác giả mẫu', 'NXB mẫu', 'NCC06', 50500, 80000, 16, 'A3');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S012', 'Mạng máy tính cơ bản', 'Công nghệ thông tin', 'Tác giả mẫu', 'NXB mẫu', 'NCC04', 54000, 85000, 18, 'A4');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S013', 'Cấu trúc dữ liệu và giải thuật', 'Công nghệ thông tin', 'Tác giả mẫu', 'NXB mẫu', 'NCC05', 57500, 90000, 20, 'A5');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S014', 'Tiếng Anh giao tiếp', 'Ngoại ngữ', 'Tác giả mẫu', 'NXB mẫu', 'NCC06', 61000, 95000, 22, 'B1');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S015', 'Ngữ pháp tiếng Anh', 'Ngoại ngữ', 'Tác giả mẫu', 'NXB mẫu', 'NCC04', 64500, 100000, 24, 'B2');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S016', 'Đại số tuyến tính', 'Giáo trình', 'Tác giả mẫu', 'NXB mẫu', 'NCC05', 68000, 105000, 26, 'B3');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S017', 'Xác suất thống kê', 'Giáo trình', 'Tác giả mẫu', 'NXB mẫu', 'NCC06', 71500, 110000, 28, 'B4');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S018', 'Kinh tế học đại cương', 'Giáo trình', 'Tác giả mẫu', 'NXB mẫu', 'NCC04', 75000, 115000, 30, 'B5');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S019', 'Kỹ năng thuyết trình', 'Kỹ năng', 'Tác giả mẫu', 'NXB mẫu', 'NCC05', 78500, 120000, 32, 'C1');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S020', 'Quản lý thời gian', 'Kỹ năng', 'Tác giả mẫu', 'NXB mẫu', 'NCC06', 82000, 125000, 34, 'C2');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S021', 'Tư duy sáng tạo', 'Kỹ năng', 'Tác giả mẫu', 'NXB mẫu', 'NCC04', 85500, 130000, 36, 'C3');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S022', 'Những câu chuyện tuổi trẻ', 'Văn học', 'Tác giả mẫu', 'NXB mẫu', 'NCC05', 89000, 135000, 38, 'C4');
INSERT INTO sach (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri) VALUES ('S023', 'Hành trình khám phá thiên nhiên', 'Khoa học', 'Tác giả mẫu', 'NXB mẫu', 'NCC06', 92500, 140000, 40, 'C5');

-- phieu_nhap
INSERT INTO phieu_nhap (ma_phieu_nhap, ngay_nhap, ma_ncc, nguoi_lap, tong_tien) VALUES ('PN-DEMO-01', '2025-09-15', 'NCC01', 'staff', 289000);
INSERT INTO phieu_nhap (ma_phieu_nhap, ngay_nhap, ma_ncc, nguoi_lap, tong_tien) VALUES ('PN-DEMO-02', '2026-09-15', 'NCC02', 'staff', 473000);
INSERT INTO phieu_nhap (ma_phieu_nhap, ngay_nhap, ma_ncc, nguoi_lap, tong_tien) VALUES ('PN-DEMO-03', '2026-10-22', 'NCC03', 'staff', 257000);

-- phieu_xuat
INSERT INTO phieu_xuat (ma_phieu_xuat, ngay_xuat, nguoi_nhan, ly_do, nguoi_lap) VALUES ('PX001', '2026-11-19', 'Nguyễn Văn A', 'Khách mua', 'staff');

-- chi_tiet_phieu_nhap
INSERT INTO chi_tiet_phieu_nhap (id, ma_phieu_nhap, ma_sach, so_luong_nhap, don_gia_nhap, thanh_tien) VALUES (1, 'PN-DEMO-01', 'S002', 3, 65000, 195000);
INSERT INTO chi_tiet_phieu_nhap (id, ma_phieu_nhap, ma_sach, so_luong_nhap, don_gia_nhap, thanh_tien) VALUES (2, 'PN-DEMO-01', 'S005', 2, 47000, 94000);
INSERT INTO chi_tiet_phieu_nhap (id, ma_phieu_nhap, ma_sach, so_luong_nhap, don_gia_nhap, thanh_tien) VALUES (3, 'PN-DEMO-02', 'S003', 4, 92000, 368000);
INSERT INTO chi_tiet_phieu_nhap (id, ma_phieu_nhap, ma_sach, so_luong_nhap, don_gia_nhap, thanh_tien) VALUES (4, 'PN-DEMO-02', 'S006', 1, 105000, 105000);
INSERT INTO chi_tiet_phieu_nhap (id, ma_phieu_nhap, ma_sach, so_luong_nhap, don_gia_nhap, thanh_tien) VALUES (5, 'PN-DEMO-03', 'S004', 5, 35000, 175000);
INSERT INTO chi_tiet_phieu_nhap (id, ma_phieu_nhap, ma_sach, so_luong_nhap, don_gia_nhap, thanh_tien) VALUES (6, 'PN-DEMO-03', 'S007', 2, 41000, 82000);

-- chi_tiet_phieu_xuat
INSERT INTO chi_tiet_phieu_xuat (id, ma_phieu_xuat, ma_sach, so_luong_xuat) VALUES (1, 'PX001', 'S003', 1);

UPDATE nguoi_dung SET session_version=lower(hex(randomblob(16))) WHERE session_version='';
COMMIT;
