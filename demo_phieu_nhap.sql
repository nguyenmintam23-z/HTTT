-- Chỉ sử dụng trên CSDL DEMO sau khi nhóm xác nhận ba mã phiếu là giao dịch mẫu.
-- Không gán người lập cho phiếu thật hoặc ghi đè người lập đã có.
PRAGMA foreign_keys = ON;
BEGIN;
UPDATE phieu_nhap SET nguoi_lap = 'staff'
WHERE nguoi_lap IS NULL
  AND ma_phieu_nhap IN ('PN-DEMO-01', 'PN-DEMO-02', 'PN-DEMO-03')
  AND EXISTS (SELECT 1 FROM nguoi_dung WHERE username = 'staff' AND role = 'staff');
COMMIT;
