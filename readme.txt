========================================================================
BÁO CÁO ĐỒ ÁN MÔN HỌC: PHÂN TÍCH THIẾT KẾ HỆ THỐNG THÔNG TIN
ĐỀ TÀI: XÂY DỰNG HỆ THỐNG THÔNG TIN QUẢN LÝ KHO SÁCH
(TRIỂN KHAI PHÂN HỆ B: NHẬP - XUẤT KHO)
========================================================================

I. THÔNG TIN CHUNG
- Giảng viên hướng dẫn: Lê Nhị Lãm Thúy
- Trường Đại học Sài Gòn - Bộ môn Hệ thống Thông tin
- Năm học: 2026 - 2027 (Học kỳ 1)

II. DANH SÁCH THÀNH VIÊN NHÓM THỰC HIỆN
STT   Họ và tên                     MSSV          Phân công chính
1     Lê Phước Đại                  3123480012    Khảo sát yêu cầu, Thiết kế CSDL (RDM, mô tả bảng)
2     Phạm Nguyễn Tuấn Kiệt         3123480026    Hệ thống sơ đồ (BFD, DFD), Thiết kế giao diện, Ghép báo cáo
3     Huỳnh Hữu Phúc                3123480046    Lập trình phân hệ B3 (Nhập/xuất kho, tồn kho, lọc giá), Kiểm thử B3
4     Nguyễn Thanh Hoàng Phúc       3123480047    Lập trình phân hệ Admin (Quản trị user, phân quyền), Tích hợp CSDL
5     Nguyễn Minh Tâm               3123480058    Lập trình phân hệ B4 (Quản lý sách, NCC, in PDF, thống kê), Kiểm thử B4

III. HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY CHƯƠNG TRÌNH

1. Yêu cầu hệ thống:
   - Hệ điều hành: Windows / macOS / Linux
   - Python: Phiên bản 3.10 trở lên
   - Trình duyệt web: Google Chrome, Microsoft Edge, Mozilla Firefox...

2. Cài đặt các thư viện phụ thuộc:
   Mở terminal / command prompt tại thư mục dự án và chạy lệnh:
   pip install -r requirements.txt

   (Các gói chính bao gồm: Flask, Flask-SQLAlchemy, Werkzeug...)

3. Khởi chạy máy chủ:
   Tại thư mục gốc, thực thi lệnh:
   python app.py

   Hệ thống sẽ khởi động máy chủ cục bộ tại:
   * Running on http://127.0.0.1:5000 / http://localhost:5000

4. Truy cập ứng dụng:
   Mở trình duyệt web và điều hướng tới địa chỉ:
   http://127.0.0.1:5000

IV. DANH SÁCH TÀI KHOẢN KIỂM THỬ DEMO (MẶT ĐỊNH)

1. Tài khoản Quản trị viên (Admin Server):
   - Tên đăng nhập: admin
   - Mật khẩu: 123456
   - Quyền hạn: Quản trị tài khoản người dùng, phân quyền (manager/staff), quản lý danh mục chức vụ.

2. Tài khoản Quản lý kho (Manager - Phân hệ B4):
   - Tên đăng nhập: manager
   - Mật khẩu: 123456
   - Quyền hạn: Thêm/sửa/xóa sách, thêm/sửa/xóa nhà cung cấp, tìm kiếm & sắp xếp, thống kê lịch sử nhập kho theo tháng/năm, xem chi tiết và in phiếu nhập dạng PDF.

3. Tài khoản Nhân viên kho (Staff - Phân hệ B3):
   - Tên đăng nhập: staff
   - Mật khẩu: 123456
   - Quyền hạn: Tra cứu danh mục sách & tồn kho khả dụng, lọc sách theo khoảng giá bán và từ khóa, lập phiếu nhập kho (+ tồn kho), lập phiếu xuất kho (- tồn kho), kiểm soát ngăn chặn xuất vượt tồn kho.

V. CẤU TRÚC GÓI NỘP BÀI
- readme.txt                      : Tệp thuyết minh thông tin nhóm và hướng dẫn vận hành
- Source code                     : Toàn bộ mã nguồn ứng dụng (app.py, admin.py, b3.py, b4.py, templates/, static/)
- database.sql                    : Kịch bản khởi tạo cơ sở dữ liệu và dữ liệu thử nghiệm
- bookstore.db                    : Cơ sở dữ liệu SQLite đã nạp sẵn dữ liệu demo
- Báo cáo đồ án                   : File PDF báo cáo kỹ thuật hoàn chỉnh (báo cáo HTTT.pdf)
========================================================================
