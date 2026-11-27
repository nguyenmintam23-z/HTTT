# TỔNG HỢP MÃ NGUỒN UML & SƠ ĐỒ HỆ THỐNG QUẢN LÝ KHO SÁCH

Thư mục này chứa toàn bộ mã nguồn sơ đồ phân tích hệ thống được thiết kế chuẩn hóa cho **Đồ án Phân tích Thiết kế Hệ thống Thông tin - Phân hệ B: Nhập - Xuất kho**.

---

## 1. Hướng dẫn sử dụng nhanh trên draw.io

Để chèn mã sơ đồ và tự động sinh hình vẽ trên [draw.io](https://app.diagrams.net/):
1. Mở phần mềm hoặc trang web **draw.io**.
2. Trên thanh menu, chọn: **Arrange** $\rightarrow$ **Insert** $\rightarrow$ **Advanced**:
   * Nếu dùng mã PlantUML: Chọn **PlantUML...** $\rightarrow$ Dán nội dung tệp `.puml` tương ứng $\rightarrow$ Nhấn **Insert**.
   * Nếu dùng mã Mermaid: Chọn **Mermaid...** $\rightarrow$ Dán nội dung tệp `.mmd` tương ứng $\rightarrow$ Nhấn **Insert**.
3. Căn chỉnh giao diện theo ý muốn, sau đó xuất file:
   * Chọn **File** $\rightarrow$ **Export as** $\rightarrow$ **PNG...**.
   * Lưu tệp vào thư mục `Báo cáo HTTT` với tên trùng khớp (ví dụ: `BFD.drawio.png`, `DFD0.drawio.png`,...) để báo cáo LaTeX tự động cập nhật.

---

## 2. Danh mục các tệp mã nguồn trong thư mục

| STT | Tên sơ đồ | Tệp PlantUML | Tệp Mermaid | Tệp ảnh tương ứng trong TeX |
| :---: | :--- | :--- | :--- | :--- |
| 1 | Sơ đồ Phân rã Chức năng (BFD) | `01_BFD.puml` | `01_BFD.mmd` | `BFD.drawio.png` |
| 2 | Sơ đồ Ngữ cảnh (Context - DFD Mức 0) | `02_DFD0_NguCanh.puml` | `02_DFD0_NguCanh.mmd` | `DFD0.drawio.png` |
| 3 | Sơ đồ Luồng Dữ liệu Mức Đỉnh (DFD Mức 1) | `03_DFD1_MucDinh.puml` | `03_DFD1_MucDinh.mmd` | `DFD1.drawio.png` |
| 4 | DFD Mức 2 - Tiến trình 2.0 (Danh mục & NCC - B4) | `04_DFD2_2.0_DanhMuc_DoiTac.puml` | `04_DFD2_2.0_DanhMuc_DoiTac.mmd` | `DFD2_2.0.drawio.png` |
| 5 | DFD Mức 2 - Tiến trình 3.0 (Nhập - Xuất kho - B3) | `05_DFD2_3.0_NhapXuatKho.puml` | `05_DFD2_3.0_NhapXuatKho.mmd` | `DFD2_3.0.drawio.png` |
| 6 | DFD Mức 2 - Tiến trình 4.0 (Báo cáo & Thống kê - B4) | `06_DFD2_4.0_BaoCao_ThongKe.puml` | `06_DFD2_4.0_BaoCao_ThongKe.mmd` | `DFD2_4.0.drawio.png` |
| 7 | Sơ đồ Thực thể - Liên kết (ERD) | `07_ERD_ThucTheLienKet.puml` | `07_ERD_ThucTheLienKet.mmd` | `ERD.drawio.png` |
| 8 | Lược đồ Cơ sở Dữ liệu Quan hệ (RDM) | `08_RDM_LuocDoQuanHe.puml` | `08_RDM_LuocDoQuanHe.mmd` | `RDM.drawio.png` |

---

## 3. Quy chuẩn Kho dữ liệu bám sát CSDL (RDM)
* `D1: NGUOI_DUNG & CHUC_VU` (username, password, role, ho_ten, chuc_vu / ten_chuc_vu)
* `D2: SACH` (ma_sach, ten_sach, the_loai, tac_gia, nha_xuat_ban, ma_ncc, gia_nhap, gia_ban, so_luong_ton, vi_tri)
* `D3: NHA_CUNG_CAP` (ma_ncc, ten_ncc, dia_chi, so_dien_thoai, email)
* `D4: PHIEU_NHAP & CHI_TIET_PHIEU_NHAP` (ma_phieu_nhap, ngay_nhap, ma_ncc, nguoi_lap, tong_tien / id, ma_sach, so_luong_nhap, don_gia_nhap, thanh_tien)
* `D5: PHIEU_XUAT & CHI_TIET_PHIEU_XUAT` (ma_phieu_xuat, ngay_xuat, nguoi_nhan, ly_do, nguoi_lap / id, ma_sach, so_luong_xuat)
