# BÁO CÁO ĐÁNH GIÁ, PHÂN TÍCH VÀ ĐỀ XUẤT ĐIỀU CHỈNH HỆ THỐNG SƠ ĐỒ
## Đồ án Phân tích & Thiết kế Hệ thống Thông tin - Quản lý Kho Sách

---

### TỔNG QUAN THƯ MỤC `so_do_de_xuat`
Thư mục này chứa toàn bộ các sơ đồ được rà soát, phát hiện sai sót, chuẩn hóa và bổ sung mới nhằm đồng bộ 100% với:
1. **Cơ sở dữ liệu 8 bảng thực thể** (đã bổ sung bảng `chuc_vu`, liên kết khóa ngoại với `nguoi_dung`).
2. **Backend API thực tế** (`admin.py` đã hiện thực hóa quản lý tài khoản và danh mục chức vụ).
3. **Chuẩn học thuật PTTK HTTT** (Ký pháp Gane & Sarson, quy tắc đánh số thứ tự phân rã DFD mức 0, 1, 2).

Mỗi sơ đồ bao gồm **cặp 2 tệp**:
- Tệp `.drawio`: Tệp mã nguồn vector XML, mở trực tiếp bằng Draw.io (desktop app, web `app.diagrams.net`, hoặc VS Code Draw.io Integration) để chỉnh sửa tự do.
- Tệp `.drawio.png`: Tệp hình ảnh hiển thị độ phân giải cao, **đã nhúng sẵn metadata `mxfile`**, vừa có thể xem như ảnh thông thường, vừa có thể kéo thả vào Draw.io để chỉnh sửa tiếp.

---

### BẢNG ĐỐI CHIẾU VÀ TỔNG HỢP SAI SÓT TỪNG SƠ ĐỒ

| STT | Tên sơ đồ | Tình trạng ban đầu | Sai sót / Bất cập phát hiện | Phương án xử lý trong `so_do_de_xuat` |
|:---:|:---|:---|:---|:---|
| 1 | `BFD.drawio.png` | Nhánh 1 chỉ có 1.1, 1.2, 1.3 | Thiếu chức năng quản lý danh mục chức vụ (Bảng `chuc_vu` mới thêm). Chưa cân xứng với backend `admin.py`. | **Đã bổ sung node `1.4 Quản lý danh mục chức vụ`** thẳng hàng với 1.1, 1.2, 1.3; nối nhánh từ trục dọc chính. |
| 2 | `DFD0.drawio.png` | Luồng với Admin chỉ ghi "tài khoản, phân quyền" | Chưa phản ánh việc luân chuyển dữ liệu danh mục chức vụ giữa Quản trị viên và hệ thống. | **Cập nhật luồng vào:** `Thông tin tài khoản, phân quyền & chức vụ`.<br>**Cập nhật luồng ra:** `DS tài khoản, danh mục chức vụ & kết quả`. |
| 3 | `DFD1.drawio.png` | Tiến trình 1.0 ghi `Đăng nhập & Quản lý User`; Kho mang tên `NHANVIEN` | 1. Tên tiến trình 1.0 quá hẹp.<br>2. Kho `NHANVIEN` không khớp bảng `nguoi_dung` & `chuc_vu` (vì có cả Admin, Manager).<br>3. Thiếu mã định danh kho (`D1..D5`). | **Đổi tên 1.0:** `1.0 Quản trị hệ thống & Phân quyền`.<br>**Đổi tên kho:** `D1: NGUOI_DUNG & CHUC_VU`.<br>**Chuẩn hóa mã kho:** `D1`, `D2: SACH`, `D3: NHACUNGCAP`, `D4: PHIEUNHAP & CT`, `D5: PHIEUXUAT & CT`. |
| 4 | `DFD2_1.0.drawio.png` | **Chưa có trong bài báo cáo** | Báo cáo có DFD mức 2 cho 2.0, 3.0, 4.0 nhưng thiếu hẳn DFD mức 2 cho 1.0 (Quản trị hệ thống & Phân quyền). | **Xây dựng mới hoàn chỉnh `DFD2_1.0`** gồm: Tác nhân Admin & Nhân sự; các tiến trình 1.1 (Đăng nhập), 1.2 (CRUD User), 1.3 (Phân quyền & Chức vụ); kết nối kho `D1`. |
| 5 | `DFD2_2.0.drawio.png` | Tiến trình 2.1, 2.2, 2.3; Kho `SACH`, `NHACUNGCAP` | Ký hiệu kho vẽ dạng hình trụ CSDL vật lý (cylinder); thiếu mã hiệu kho `D2`, `D3`. | Giữ cấu trúc luồng chuẩn xác; chuẩn hóa nhãn mã định danh `D2: SACH` và `D3: NHACUNGCAP` trong XML để tương thích Draw.io. |
| 6 | `DFD2_3.0.drawio.png` | Tiến trình 3.1, 3.2, 3.3; Kho dữ liệu dạng cylinder | Các kho thiếu mã định danh `D2`, `D3`, `D4`, `D5` theo chuẩn DFD mức 1. | Giữ cấu trúc luồng nghiệp vụ kho chuẩn xác; cập nhật định danh `D2..D5` trong XML phục vụ xuất bản. |
| 7 | `DFD2_4.0.drawio.png` | **LỖI NGHIÊM TRỌNG:** Số hiệu 3 tiến trình là `1`, `2`, `3` | 1. Sai quy tắc đánh số DFD mức 2 (phải là `4.1`, `4.2`, `4.3`).<br>2. Kho ghi `PHIEUNHAP & CHITIET_NHAP` (không đồng nhất với DFD mức 1 là `PHIEUNHAP & CT`). | **Sửa số hiệu tiến trình thành `4.1`, `4.2`, `4.3`**.<br>**Chuẩn hóa tên kho thành `D4: PHIEUNHAP & CT`**, `D2: SACH`, `D3: NHACUNGCAP`. |

---

### CHI TIẾT ĐIỀU CHỈNH TỪNG SƠ ĐỒ

#### 1. Sơ đồ BFD (`BFD.drawio.png` / `BFD.drawio`)
- **Vấn đề cũ:** Nhánh `1. Quản trị hệ thống (Admin)` chỉ có 3 ô tác nghiệp (1.1 Đăng nhập/Đăng xuất, 1.2 Quản lý tài khoản, 1.3 Phân quyền hệ thống). Khi cơ sở dữ liệu bổ sung bảng `chuc_vu` và module `admin.py` cung cấp các API thêm/sửa/xóa chức vụ nhân viên, sơ đồ BFD bị thiếu một chức năng nghiệp vụ độc lập.
- **Giải pháp đề xuất:**
  - Bổ sung khối chức năng: `1.4 Quản lý danh mục chức vụ` ngay dưới khối 1.3.
  - Kéo dài trục dọc (spine) của nhánh 1 và nối nhánh ngang vào khối 1.4.
  - Kích thước canvas mở rộng theo chiều dọc để bảo toàn khoảng cách thoáng đãng giữa các khối.

#### 2. Sơ đồ Ngữ cảnh DFD Mức 0 (`DFD0.drawio.png` / `DFD0.drawio`)
- **Vấn đề cũ:** Nhãn luồng giữa Admin và hệ thống chỉ nhắc đến "tài khoản, phân quyền", chưa bao quát danh mục chức vụ.
- **Giải pháp đề xuất:**
  - Luồng vào (Admin $\rightarrow$ Hệ thống): `Thông tin tài khoản, phân quyền & chức vụ`.
  - Luồng ra (Hệ thống $\rightarrow$ Admin): `DS tài khoản, danh mục chức vụ & kết quả`.

#### 3. Sơ đồ DFD Mức 1 (`DFD1.drawio.png` / `DFD1.drawio`)
- **Vấn đề cũ:**
  - Tiến trình 1.0 mang tên `Đăng nhập & Quản lý User` quá hẹp so với thực tế phân quyền quản trị.
  - Kho dữ liệu mang tên `NHANVIEN` không chuẩn vì trong CSDL bảng là `nguoi_dung`, lưu trữ cả tài khoản quản trị và quản lý.
  - Các kho dữ liệu chưa gắn mã định danh chuẩn Gane & Sarson (`D1..D5`).
- **Giải pháp đề xuất:**
  - Đổi tên tiến trình 1.0 thành: `1.0 Quản trị hệ thống & Phân quyền`.
  - Đổi tên kho dữ liệu thành: `D1: NGUOI_DUNG & CHUC_VU`.
  - Bổ sung mã định danh kho vào ngăn trái (left compartment): `D1`, `D2`, `D3`.
  - Cập nhật luồng dữ liệu truy vấn giữa 1.0 và kho D1 thành: `Đọc / Cập nhật tài khoản & chức vụ`.

#### 4. Sơ đồ DFD Mức 2 - Tiến trình 1.0 (`DFD2_1.0.drawio.png` / `DFD2_1.0.drawio`) - *MỚI BỔ SUNG*
- **Ý nghĩa:** Hoàn thiện sự thiếu hụt lớn nhất của bộ tài liệu thiết kế hệ thống.
- **Cấu trúc sơ đồ:**
  - **Tác nhân:** `Quản trị viên (Admin)` và `Người dùng hệ thống (Thủ kho / Quản lý)`.
  - **Tiến trình 1.1:** `Đăng nhập / Đăng xuất & Xác thực phiên (Session)`.
  - **Tiến trình 1.2:** `Quản lý tài khoản người dùng (CRUD)`.
  - **Tiến trình 1.3:** `Quản lý danh mục chức vụ & Phân quyền vai trò`.
  - **Kho dữ liệu:** `D1: NGUOI_DUNG & CHUC_VU`.
  - **Các luồng dữ liệu:** Đặc tả đầy đủ luồng băm mật khẩu, cấp phiên làm việc, cập nhật tài khoản và phân bổ chức vụ/vai trò.

#### 5. Sơ đồ DFD Mức 2 - Tiến trình 4.0 (`DFD2_4.0.drawio.png` / `DFD2_4.0.drawio`)
- **Vấn đề cũ:** Đầu process box hiển thị con số `1`, `2`, `3` thay vì mã số phân rã `4.1`, `4.2`, `4.3`. Kho dữ liệu đặt tên `PHIEUNHAP & CHITIET_NHAP` lệch chuẩn so với DFD mức 1 (`PHIEUNHAP & CT`).
- **Giải pháp đề xuất:**
  - Thay số `1` $\rightarrow$ `4.1` (Lọc lịch sử nhập theo tháng/năm).
  - Thay số `2` $\rightarrow$ `4.2` (Xem chi tiết phiếu nhập).
  - Thay số `3` $\rightarrow$ `4.3` (In / Lưu trữ phiếu nhập PDF).
  - Thay nhãn kho thành `D4: PHIEUNHAP & CT`, `D2: SACH`, `D3: NHACUNGCAP`.

---

### HƯỚNG DẪN DUYỆT VÀ ÁP DỤNG VÀO BÁO CÁO LATEX

1. **Kiểm tra trực quan:**
   Người dùng có thể mở trực tiếp các tệp `.drawio.png` trong thư mục `so_do_de_xuat` bằng bất kỳ trình xem ảnh nào trên máy để đánh giá bố cục, màu sắc và kiểu chữ.
2. **Kiểm tra / Tùy biến mã nguồn Draw.io:**
   Mở tệp `.drawio` hoặc kéo thả trực tiếp tệp `.drawio.png` vào trang [app.diagrams.net](https://app.diagrams.net) để chỉnh sửa các chi tiết nếu muốn thay đổi theo sở thích cá nhân.
3. **Áp dụng vào báo cáo Latex:**
   Khi đã ưng ý với các sơ đồ đề xuất:
   - Sao chép đè các tệp `.drawio.png` từ `so_do_de_xuat` ra thư mục gốc `file tổng hợp cho báo cáo\Báo cáo HTTT\`.
   - Đối với sơ đồ mới `DFD2_1.0.drawio.png`, có thể chèn thêm mục `\subsection{Sơ đồ DFD Mức 2 - Tiến trình 1.0: Quản trị hệ thống & Phân quyền}` vào trước Mục 2.0 trong tệp `báo cáo HTTT.tex` để bài báo cáo đạt điểm tuyệt đối.
