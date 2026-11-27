HỆ THỐNG QUẢN LÝ KHO SÁCH
Đồ án Phân tích thiết kế hệ thống thông tin – Mục B: Nhập xuất kho

Thông tin nhóm (theo bảng phân công): Đại, Kiệt, Hữu Phúc, Hoàng Phúc, Tâm.
Nhóm bổ sung họ tên đầy đủ, MSSV, lớp và thông tin liên hệ theo yêu cầu nộp bài.

1. Cài đặt và chạy trên Windows
- Cài Python 3 và mở Terminal tại thư mục chứa app.py.
- py -m pip install -r requirements.txt
- Sao lưu bookstore.db khi Flask đã dừng, trước khi nâng cấp.
- py app.py
- Truy cập http://127.0.0.1:5000
- CSDL hiện có không bị nạp lại seed. Khi DB mới chưa có bảng, chương trình nạp database.sql trong chế độ demo.
- Khi nâng cấp DB cũ, init_db bổ sung session_version, chỉ mục và trigger kiểm tra số lượng nguyên; không tái tạo bảng. Nếu báo dữ liệu cũ không hợp lệ, giữ bản sao lưu và xử lý thủ công.

2. Tài khoản demo (chỉ dùng cục bộ)
- admin / 123456: Quản lý tài khoản, chức vụ và phân quyền.
- manager / 123456: Quản lý sách, nhà cung cấp, lịch sử và thống kê nhập kho.
- staff / 123456: Tra cứu sách, lập phiếu nhập/xuất, xem phiếu cá nhân.
Các mật khẩu này chỉ đúng với seed demo trong database.sql; DB đang sử dụng có thể đã đổi mật khẩu.
role quyết định quyền thực tế; chuc_vu là tên chức vụ nghiệp vụ độc lập, không cấp quyền.
Sau khi đổi quyền, đổi mật khẩu hoặc xóa tài khoản, phiên cũ bị thu hồi và người dùng cần đăng nhập lại.

3. Script SQL
- database.sql: tạo 8 bảng, 8 index, các ràng buộc và dữ liệu mẫu (3 tài khoản, 6 NCC, 23 sách, 3 phiếu nhập, 1 phiếu xuất). Chạy trên CSDL mới, không chạy đè CSDL đã có.
- Ba phiếu PN-DEMO-01/02/03 trong seed được quy ước người lập là staff, chỉ nhằm demo. Với DB đang dùng, chỉ chạy demo_phieu_nhap.sql nếu nhóm xác nhận các mã này là dữ liệu mẫu; script chỉ cập nhật người lập còn NULL.
- Cột nguoi_dung.session_version là mã phiên nội bộ (VARCHAR(32), NOT NULL), dùng thu hồi phiên. Cập nhật lược đồ và đặc tả bảng trong báo cáo.
- Dữ liệu mẫu giữ nguyên tồn kho của bản snapshot; không tính lại tồn từ giao dịch mẫu vì lịch sử mẫu không phải toàn bộ giao dịch.
- Khởi tạo DB mới riêng bằng lệnh: py -c "import sqlite3,pathlib; p=pathlib.Path('bookstore_demo_new.db'); assert not p.exists(); c=sqlite3.connect(p); c.executescript(pathlib.Path('database.sql').read_text(encoding='utf-8')); c.close()"
- Chạy kiểm thử với DB mới: trong CMD, set BOOKSTORE_DB_PATH=%CD%\bookstore_demo_new.db rồi py app.py. Dừng và set BOOKSTORE_DB_PATH= để trở về DB mặc định.

4. Kiểm thử
- py -m unittest discover -s tests -v
- Cần cài Flask và Flask-SQLAlchemy để không bỏ qua HTTP integration tests.
- Kiểm tra đăng nhập, đổi role ở Admin khi tài khoản đang mở trong Chrome ẩn danh, thử API quản lý với phiên cũ, đăng nhập lại và xác nhận quyền mới. Kiểm tra đổi tên chức vụ đang sử dụng.
- Thử nhập/xuất, lọc giá, lịch sử, in phiếu, CRUD sách/NCC và giao diện của cả 3 vai trò.

5. Bảo mật
- Chương trình mặc định chạy cục bộ, debug tắt. Nếu không cấu hình BOOKSTORE_SECRET_KEY, ứng dụng tạo khóa ngẫu nhiên mỗi lần chạy; phiên trước bị mất khi khởi động lại.
- Không dùng dữ liệu và mật khẩu demo để triển khai công khai. BOOKSTORE_DEMO=0, BOOKSTORE_SECRET_KEY riêng và BOOKSTORE_ADMIN_PASSWORD riêng (12–128 ký tự) dành cho khởi tạo CSDL mới ngoài demo. Không công bố khóa hoặc mật khẩu thật.
- BOOKSTORE_HTTPS=1 chỉ dùng khi thực sự triển khai HTTPS. Cần máy chủ WSGI, HTTPS, kiểm soát truy cập, giới hạn thử đăng nhập và rà soát bảo mật bổ sung trước khi triển khai công khai.
