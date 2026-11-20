### **1\. GIỚI THIỆU HỆ THỐNG QUẢN LÝ KHO SÁCH**

#### **1.1. Bối cảnh và lý do chọn đề tài**

Trong hoạt động kinh doanh và phân phối sách, công tác quản lý kho đóng vai trò then chốt giúp đảm bảo nguồn hàng ổn định, kiểm soát chính xác số lượng tồn kho và tối ưu hóa quy trình nhập – xuất hàng hóa. Tuy nhiên, nếu thực hiện quản lý theo phương pháp thủ công (ghi chép sổ sách hoặc lưu trữ rời rạc trên các bảng tính riêng lẻ), đơn vị thường gặp nhiều khó khăn như: dễ xảy ra sai sót khi cộng trừ số lượng tồn kho, khó tra cứu nhanh thông tin đầu sách theo nhà cung cấp hoặc mức giá, mất nhiều thời gian tổng hợp lịch sử nhập hàng theo kỳ, và thiếu cơ chế phân quyền rõ ràng giữa các bộ phận.

Xuất phát từ thực tế đó, nhóm thực hiện đề tài **“Ứng dụng Quản lý kho sách”** (tập trung vào nghiệp vụ Nhập – Xuất kho) nhằm xây dựng một giải pháp phần mềm hỗ trợ quy trình vận hành kho, đảm bảo tính nhất quán dữ liệu và nâng cao hiệu quả quản lý.

#### **1.2. Mục tiêu của hệ thống**

Hệ thống được phân tích, thiết kế và xây dựng hướng tới các mục tiêu chính sau:

* **Tin học hóa quy trình nhập – xuất kho:** Cho phép lập phiếu nhập sách từ nhà cung cấp và lập phiếu xuất sách từ kho một cách nhanh chóng, chính xác.

* **Kiểm soát chặt chẽ biến động tồn kho:** Tự động cập nhật số lượng sách tồn kho ngay khi phát sinh giao dịch nhập hoặc xuất; đồng thời kiểm tra ràng buộc dữ liệu đầu vào nhằm ngăn chặn tình trạng xuất vượt quá số lượng tồn kho hiện có hoặc nhập dữ liệu không hợp lệ.

* **Hỗ trợ tra cứu và quản lý danh mục:** Cung cấp các chức năng thêm, sửa, xóa, tìm kiếm, lọc và sắp xếp thông tin sách cũng như nhà cung cấp.

* **Phân quyền người dùng rõ ràng:** Tách biệt quyền hạn và giao diện thao tác giữa Quản trị viên hệ thống (Admin), Quản lý kho và Nhân viên kho để đảm bảo tính bảo mật và đúng trách nhiệm nghiệp vụ.

* **Hỗ trợ lưu trữ và thống kê:** Cho phép in/lưu phiếu nhập và thống kê lịch sử nhập hàng theo tháng, năm phục vụ công tác theo dõi và đối soát.

#### **1.3. Phạm vi chức năng của hệ thống**

Hệ thống tập trung giải quyết bài toán nghiệp vụ nhập – xuất kho sách, bao gồm ba nhóm chức năng chính tương ứng với ba vai trò sử dụng:

1. **Phân hệ Quản trị hệ thống:**

   * Quản lý tài khoản người dùng trong hệ thống: thêm mới, cập nhật thông tin, xóa tài khoản và thiết lập phân quyền truy cập theo từng vai trò.

   * Kiểm soát đăng nhập và xác thực quyền hạn trước khi thực hiện các chức năng nghiệp vụ.

2. **Phân hệ Nhân viên kho (Nghiệp vụ nhập – xuất kho):**

   * Xem thông tin chi tiết và số lượng tồn kho hiện tại của các đầu sách.

   * Tìm kiếm sách theo tên sản phẩm và lọc danh sách sách theo khoảng giá bán.

   * Lập phiếu nhập kho (nhập sách từ nhà cung cấp) và phiếu xuất kho (xuất sách khỏi kho), hệ thống tự động tăng hoặc giảm số lượng tồn kho tương ứng.

   * Kiểm tra tính hợp lệ của dữ liệu phiếu (số lượng nguyên dương, đơn giá hợp lệ, không xuất quá số lượng tồn kể cả khi trùng mã sách trên nhiều dòng).

3. **Phân hệ Quản lý kho:**

   * Quản lý danh mục sách: thêm mới, chỉnh sửa thông tin, xóa đầu sách.

   * Quản lý danh mục nhà cung cấp: thêm mới, chỉnh sửa thông tin, xóa nhà cung cấp.

   * Tìm kiếm và sắp xếp dữ liệu theo sách và nhà cung cấp.

   * Thực hiện in hoặc lưu trữ phiếu nhập kho.

   * Xem báo cáo, thống kê lịch sử nhập sách theo tháng và năm.

#### **1.4. Dữ liệu đầu vào, xử lý và đầu ra của hệ thống**

| Thành phần | Mô tả chi tiết trong hệ thống |
| :---- | :---- |
| **Dữ liệu đầu vào (Input)** | • Thông tin đăng nhập (tên đăng nhập, mật khẩu) và thông tin quản lý tài khoản, phân quyền người dùng. • Thông tin danh mục sách (mã sách, tên sách, thể loại, tác giả, giá bán, vị trí lưu kho, số lượng tồn...) . • Thông tin nhà cung cấp (mã nhà cung cấp, tên nhà cung cấp, địa chỉ, số điện thoại/liên hệ...). • Thông tin giao dịch nhập kho (ngày nhập, nhà cung cấp, danh sách mã sách, số lượng nhập, đơn giá nhập). • Thông tin giao dịch xuất kho (ngày xuất, thông tin phiếu xuất, danh sách mã sách, số lượng xuất). • Các tiêu chí tìm kiếm, lọc theo khoảng giá, sắp xếp và mốc thời gian (tháng/năm) cần thống kê. |
| **Quá trình xử lý (Process)** | • Xác thực tài khoản và kiểm tra phân quyền truy cập theo vai trò (Admin, Quản lý kho, Nhân viên kho). • Kiểm tra tính hợp lệ và toàn vẹn dữ liệu: từ chối số lượng $\leq 0$, đơn giá không hợp lệ, thiếu trường bắt buộc, kiểm tra ràng buộc khóa ngoại khi xóa sách/nhà cung cấp đã có giao dịch. • Kiểm tra tồn kho khả dụng khi xuất hàng (cộng dồn số lượng nếu một mã sách xuất hiện ở nhiều dòng trong cùng phiếu) và cập nhật tự động số lượng tồn kho sau khi lưu phiếu nhập/xuất. • Truy vấn, lọc, sắp xếp danh mục và tổng hợp dữ liệu nhập kho theo tháng/năm. |
| **Dữ liệu đầu ra (Output)** | • Danh sách tài khoản người dùng và trạng thái phân quyền. •Danh sách sách kèm thông tin chi tiết (thể loại, tác giả, vị trí, giá bán) và số lượng tồn kho cập nhật. • Phiếu nhập kho, phiếu xuất kho hoàn chỉnh và bản in/lưu phiếu nhập. • Bảng thống kê lịch sử nhập kho theo tháng/năm. • Các thông báo xác nhận thao tác thành công hoặc cảnh báo lỗi nghiệp vụ (vượt tồn kho, sai định dạng, vướng ràng buộc dữ liệu). |

### **2\. KHẢO SÁT VÀ PHÂN TÍCH YÊU CẦU**

#### **2.1. Tổng quan khảo sát hiện trạng**

* **Đơn vị / đối tượng khảo sát:**

  \[Cần bổ sung: ghi rõ tên đơn vị/cửa hàng/kho sách khảo sát thực tế nếu có, hoặc nêu rõ phạm vi khảo sát dựa trên yêu cầu đề đồ án mục B – Nhập xuất kho\].

* **Phương pháp thực hiện:** 

  \[Cần bổ sung: nêu hình thức đã áp dụng nếu có, ví dụ phỏng vấn, quan sát quy trình hoặc đối chiếu tài liệu/yêu cầu bài toán\].

* **Hiện trạng vận hành & các vấn đề tồn tại:**

  * Việc theo dõi số lượng nhập, xuất và tồn kho của từng đầu sách có thể thiếu đồng bộ nếu cập nhật rời rạc hoặc chưa kiểm soát chặt chẽ các ràng buộc dữ liệu đầu vào.

  * Khi lập phiếu xuất có nhiều dòng hoặc trùng mã sách, nếu thiếu bước kiểm tra tổng số lượng xuất so với tồn kho hiện tại dễ dẫn đến nguy cơ xuất vượt tồn hoặc sai lệch tồn kho.

  * Việc tìm kiếm, lọc theo tên/giá bán, sắp xếp theo sách/nhà cung cấp, cũng như tra cứu lịch sử nhập theo tháng/năm cần được tổ chức rõ ràng theo từng vai trò.

  * Cần phân định rạch ròi quyền thao tác và phạm vi hiển thị giữa Quản trị viên hệ thống (Admin), Nhân viên kho (phân hệ B3) và Quản lý kho (phân hệ B4), đồng thời bảo đảm tính toàn vẹn dữ liệu khi xóa danh mục đã phát sinh phiếu.

  * \[Cần bổ sung: các số liệu cụ thể, thời gian xử lý trung bình hoặc vấn đề đặc thù thực tế nếu nhóm có khảo sát đơn vị ngoài\].

#### **2.2. Phân tích yêu cầu chức năng**

Hệ thống đáp ứng các nhóm yêu cầu chức năng chính sau:

* **Quản trị hệ thống và phân quyền (Admin):**

  * Đăng nhập, xác thực tài khoản và kiểm soát quyền truy cập theo vai trò.

  * Quản lý người dùng trên giao diện quản trị tách biệt: thêm, sửa, xóa tài khoản và thiết lập phân quyền.

* **Nghiệp vụ của Nhân viên kho (Phân hệ B3):**

  * Xem thông tin sản phẩm và số lượng tồn kho hiện có.

  * Tìm kiếm theo tên sản phẩm và lọc hàng hóa theo khoảng giá bán.

  * Lập phiếu nhập kho và phiếu xuất kho; cập nhật đúng số lượng tồn kho.

  * Kiểm tra tính hợp lệ của dữ liệu phiếu (số lượng nguyên dương, đơn giá hợp lệ, đầy đủ trường bắt buộc, không cho phép xuất vượt tồn kho kể cả trường hợp trùng mã sách trên nhiều dòng).

* **Nghiệp vụ của Quản lý kho (Phân hệ B4):**

  * Quản lý danh mục sách (thêm, sửa, xóa) và danh mục nhà cung cấp (thêm, sửa, xóa).

  * Tìm kiếm và sắp xếp thông tin theo sách và nhà cung cấp.

  * In hoặc lưu trữ phiếu nhập kho.

  * Xem thống kê lịch sử nhập hàng theo tháng và năm.

* **Tính toàn vẹn dữ liệu và dữ liệu mẫu:**

  * Kiểm tra ràng buộc khóa ngoại khi xóa sách hoặc nhà cung cấp đã có lịch sử phiếu.

  * Có dữ liệu mẫu trên cơ sở dữ liệu phục vụ kiểm thử và demo các luồng nghiệp vụ.

#### **2.3. Phân tích yêu cầu phi chức năng**

* **Tính đúng đắn và toàn vẹn dữ liệu:** Từ chối dữ liệu phiếu không hợp lệ (số lượng âm, bằng 0 hoặc không phải số nguyên; đơn giá sai; thiếu trường bắt buộc; xuất vượt tồn kho); giữ tính nhất quán giữa giao diện, mã xử lý và cơ sở dữ liệu.

* **Tính bảo mật và kiểm soát truy cập:** Phân tách quyền hạn theo vai trò người dùng; cấu hình hệ thống phù hợp cho môi trường chạy chính thức, tránh để lộ thông tin hoặc cấu hình debug mặc định trên bản nộp.

* **Tính khả dụng và giao diện:** Giao diện trực quan, thông báo lỗi rõ ràng khi thao tác sai hoặc vi phạm ràng buộc; các bảng hiển thị khớp số cột với tiêu đề và xử lý an toàn dữ liệu hiển thị trên giao diện.

* **Khả năng bảo trì và triển khai:** Cấu trúc cơ sở dữ liệu rõ ràng (7 bảng cốt lõi), có script khởi tạo CSDL, hướng dẫn cài đặt/sử dụng và tệp thông tin nhóm (readme.txt) để triển khai và kiểm thử lại được.

### **3\. THIẾT KẾ CƠ SỞ DỮ LIỆU**

#### **3.1. Tổng quan mô hình dữ liệu và các mối quan hệ chính**

### **4\. KẾ HOẠCH THỰC HIỆN VÀ PHÂN CÔNG CÔNG VIỆC**

#### **4.1. Bảng phân công nhiệm vụ và tiến độ thực hiện**

***BẢNG CHƯA HOÀN THIỆN, CÒN CHỈNH SỬA***

| Giai đoạn | Nhiệm v | Thành viên phụ trách | Đầu ra / Sản phẩm bàn giao | Thời hạn dự kiến | Trạng thái |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Giai đoạn 1** *(Chuẩn hóa nền tảng & sửa lỗi lõi)* | • Chuẩn bị nhánh tích hợp, thống nhất cấu trúc CSDL và quy ước thay đổi dữ liệu. • Khắc phục các lỗi logic phiếu nhập/xuất (số lượng âm/0, đơn giá sai, trùng mã sách vượt tồn kho, thiếu trường bắt buộc). • Khắc phục lỗi hiển thị giao diện chung (hàm trùng lặp, lệch cột bảng, xử lý chuỗi HTML an toàn). | Nguyễn Thanh Hoàng Phúc Huỳnh Hữu Phúc Nguyễn Minh Tâm | • Cấu trúc CSDL thống nhất. • Mã nguồn xử lý lỗi nghiệp vụ B3 và hiển thị B4 ổn định. |  | Đã hoàn thành |
| **Giai đoạn 2** *(Hoàn thiện chức năng & kiểm thử)* | • **Phân hệ Admin:** Xây dựng giao diện và API Admin tách biệt; quản lý user (thêm, sửa, xóa, phân quyền); xử lý ràng buộc khóa ngoại và cấu hình bảo mật bản chạy. • **Phân hệ B3 (Nhân viên kho):** Hoàn thiện tìm kiếm theo tên, lọc theo khoảng giá bán, kiểm thử luồng lập phiếu nhập/xuất và cập nhật tồn kho. • **Phân hệ B4 (Quản lý kho):** Bổ sung chức năng sửa sách và sửa nhà cung cấp; hoàn thiện tìm kiếm/sắp xếp; kiểm tra in/lưu phiếu nhập và thống kê theo tháng/năm. • Nạp dữ liệu demo thực tế vào CSDL, kiểm thử tích hợp toàn hệ thống. | Nguyễn Thanh Hoàng Phúc Huỳnh Hữu Phúc Nguyễn Minh Tâm | • Bản ứng dụng chạy hoàn chỉnh đủ 3 vai trò (Admin, B3, B4). • CSDL demo có tài khoản mẫu và giao dịch nhập/xuất thực. • Bảng kịch bản kiểm thử và ảnh chụp màn hình bản chạy cuối. |  | Đã hoàn thành |
| **Giai đoạn 3** *(Hoàn thiện lý thuyết, sơ đồ & tài liệu)* | • **Giới thiệu, khảo sát & CSDL:** Hoàn thiện phần giới thiệu, phân tích yêu cầu; cập nhật lược đồ và mô tả chi tiết 7 bảng CSDL khớp với bản code cuối; lập kế hoạch và biểu mẫu đánh giá. • **Sơ đồ & giao diện:** Vẽ sơ đồ chức năng (BFD), sơ đồ ngữ cảnh, DFD các mức; tổng hợp hình ảnh giao diện cuối và thuyết minh. • **Thuyết minh nghiệp vụ:** Hoàn thiện mô tả quy trình, đầu vào/ra, kịch bản kiểm thử B3 và B4 gửi ghép báo cáo. | Lê Phước Đại Phạm Nguyễn Tuấn Kiệt Huỳnh Hữu Phúc Nguyễn Minh Tâm | • Bộ sơ đồ BFD, ngữ cảnh, DFD đúng chuẩn. • Lược đồ CSDL và bảng mô tả 7 bảng hoàn chỉnh. • Phần thuyết minh B3, B4 và minh chứng giao diện. |  | Đã hoàn thành |
| **Giai đoạn 4** *(Tổng kết, đóng gói & nghiệm thu)* | • Viết hướng dẫn cài đặt, hướng dẫn sử dụng và phần tổng kết (ưu/nhược điểm, hướng phát triển). • Chuẩn bị script SQL, tệp readme.txt và gói mã nguồn. • Ghép toàn bộ bản báo cáo in; cả nhóm rà soát đối chiếu tiêu chí chấm điểm và chốt tỷ lệ % đóng góp. | Phạm Nguyễn Tuấn Kiệt Nguyễn Thanh Hoàng Phúc Lê Phước Đại Huỳnh Hữu Phúc Nguyễn Minh Tâm | • Bản báo cáo in hoàn chỉnh. • Gói nộp gồm: source code, script SQL, báo cáo, readme.txt. • Bảng đánh giá % đóng góp có xác nhận của 5 thành viên. |  | Đã hoàn thành |

#### **4.2. Bảng phân công chi tiết và tỷ lệ đóng góp**

| STT | Họ tên  | MSSV | Nhiệm vụ | Tỷ lệ đóng góp (%) | Ký xác nhận |
| ----- | ----- | ----- | ----- | ----- | ----- |
| 1 | Lê Phước Đại | 3123480012 | **Tài liệu / Lý thuyết:** Viết phần giới thiệu hệ thống, khảo sát và phân tích yêu cầu; thiết kế lược đồ CSDL; lập bảng kế hoạch công việc và biểu mẫu đánh giá đóng góp; rà soát đối chiếu báo cáo với bản chạy cuối. |  |  |
| 2 | Phạm Nguyễn Tuấn Kiệt | 31234800\_\_ | **Tài liệu / Lý thuyết:** Vẽ sơ đồ chức năng (BFD), sơ đồ ngữ cảnh, DFD mức đỉnh và dưới đỉnh; tổng hợp phần thiết kế giao diện; viết hướng dẫn cài đặt, hướng dẫn sử dụng, phần tổng kết và ghép hoàn chỉnh bản báo cáo. |  |  |
| 3 | Huỳnh Hữu Phúc | 31234800\_\_ | **Lập trình & Tài liệu (Phân hệ B3 – Nhân viên kho):** Sửa lỗi logic và hoàn thiện chức năng tìm kiếm/lọc giá bán, lập phiếu nhập/xuất, kiểm tra và cập nhật tồn kho; kiểm thử nghiệp vụ B3, chụp ảnh minh chứng và viết thuyết minh quy trình B3. |  |  |
| 4 | Nguyễn Minh Tâm | 31234800\_\_ | **Lập trình & Tài liệu (Phân hệ B4 – Quản lý kho):** Bổ sung chức năng sửa sách và nhà cung cấp; hoàn thiện tìm kiếm/sắp xếp, in/lưu phiếu nhập và thống kê lịch sử nhập theo tháng/năm; sửa lỗi bảng giao diện; kiểm thử và viết thuyết minh B4. |  |  |
| 5 | Nguyễn Thanh Hoàng Phúc | 31234800\_\_ | **Lập trình chính & Tích hợp:** Xây dựng giao diện và API Admin tách biệt (quản lý user, phân quyền); xử lý toàn vẹn dữ liệu/khóa ngoại và bảo mật; tích hợp mã nguồn nhóm; chuẩn bị dữ liệu demo, script SQL, readme.txt và kiểm thử tích hợp. |  |  |

### **3\. THIẾT KẾ CƠ SỞ DỮ LIỆU**

#### **3.1. Tổng quan mô hình dữ liệu và các mối quan hệ chính**

Hệ thống quản lý kho sách sử dụng cơ sở dữ liệu quan hệ gồm 7 bảng chính, phục vụ lưu trữ thông tin tài khoản/phân quyền, danh mục hàng hóa, nhà cung cấp và các chứng từ nhập – xuất kho cùng chi tiết từng dòng hàng:

* **NGUOI\_DUNG (Người dùng)**: Lưu trữ tài khoản đăng nhập, thông tin người dùng và vai trò/quyền hạn trong hệ thống (Admin, Nhân viên kho, Quản lý kho).

* **NHA\_CUNG\_CAP (Nhà cung cấp)**: Lưu trữ thông tin các đơn vị cung cấp sách phục vụ nghiệp vụ nhập hàng và quản lý danh mục.

* **SACH (Sách)**: Lưu trữ thông tin đầu sách và số lượng tồn kho hiện tại.

* **PHIEU\_NHAP (Phiếu nhập)**: Lưu thông tin chung của từng lần nhập kho (mã phiếu, ngày lập/nhập, nhà cung cấp, người lập phiếu...).

* **CHI\_TIET\_PHIEU\_NHAP (Chi tiết phiếu nhập)**: Lưu từng dòng sách nhập theo phiếu nhập (mã phiếu nhập, mã sách, số lượng nhập, đơn giá nhập...).

* **PHIEU\_XUAT (Phiếu xuất)**: Lưu thông tin chung của từng lần xuất kho (mã phiếu, ngày lập/xuất, người lập phiếu...).

* **CHI\_TIET\_PHIEU\_XUAT (Chi tiết phiếu xuất)**: Lưu từng dòng sách xuất theo phiếu xuất (mã phiếu xuất, mã sách, số lượng xuất...).

**Các mối quan hệ cốt lõi giữa các bảng:**

* **1 – N giữa NHA\_CUNG\_CAP và PHIEU\_NHAP:** Một nhà cung cấp có thể cung cấp hàng cho nhiều phiếu nhập; mỗi phiếu nhập thuộc về một nhà cung cấp.

* **1 – N giữa PHIEU\_NHAP và CHI\_TIET\_PHIEU\_NHAP:** Một phiếu nhập có thể gồm một hoặc nhiều dòng chi tiết sách nhập.

* **1 – N giữa SACH và CHI\_TIET\_PHIEU\_NHAP:** Một đầu sách có thể xuất hiện ở nhiều dòng chi tiết phiếu nhập theo thời gian.

* **1 – N giữa PHIEU\_XUAT và CHI\_TIET\_PHIEU\_XUAT:** Một phiếu xuất có thể gồm một hoặc nhiều dòng chi tiết sách xuất.

* **1 – N giữa SACH và CHI\_TIET\_PHIEU\_XUAT:** Một đầu sách có thể xuất hiện ở nhiều dòng chi tiết phiếu xuất.

* **Liên kết với NGUOI\_DUNG (nếu có lưu người lập/thao tác):** Một người dùng có thể lập hoặc gắn với nhiều phiếu nhập/phiếu xuất hoặc thao tác trong hệ thống (cần đối chiếu với lược đồ CSDL thực tế của Hoàng Phúc).

**Lưu ý về tính toàn vẹn dữ liệu:** Khi thực hiện xóa một đầu sách (SACH) hoặc một nhà cung cấp (NHA\_CUNG\_CAP) đã có dữ liệu phát sinh trên các phiếu liên quan, hệ thống cần kiểm tra ràng buộc khóa ngoại để tránh tạo bản ghi tham chiếu mồ côi hoặc mất dữ liệu lịch sử.

#### **3.2. Mô tả chi tiết các bảng và thuộc tính**

(Lưu ý: Tên cột chính xác, kiểu dữ liệu và ràng buộc cụ thể dưới đây là khung đối chiếu theo nghiệp vụ đề và giao diện hiện tại; Đại cần xác nhận/cập nhật lại theo script SQL và bản CSDL cuối cùng của Hoàng Phúc.)

##### **Bảng 1: NGUOI\_DUNG (Người dùng)**

| Tên thuộc tính (khung đối chiếu) | Kiểu dữ liệu (dự kiến) | Khóa / Ràng buộc | Diễn giải |
| :---- | :---- | :---- | :---- |
| ma\_nguoi\_dung | \[Kiểu số/chuỗi\] | PRIMARY KEY, NOT NULL | Định danh duy nhất tài khoản người dùng |
| ten\_dang\_nhap | \[VARCHAR\] | UNIQUE, NOT NULL | Tên đăng nhập vào hệ thống |
| mat\_khau | \[VARCHAR\] | NOT NULL | Mật khẩu tài khoản (được lưu trữ an toàn theo cấu hình hệ thống) |
| ho\_ten | \[VARCHAR\] | \[Cần đối chiếu CSDL cuối\] | Tên hiển thị của người dùng |
| vai\_tro | \[VARCHAR\] | NOT NULL | Vai trò/quyền hạn (ví dụ: Admin, Nhân viên kho, Quản lý kho) |
| \[Các cột khác nếu có\] | \[Cần đối chiếu CSDL cuối\] | \[Cần đối chiếu CSDL cuối\] | Bổ sung theo CSDL thực tế của Hoàng Phúc |

##### **Bảng 2: NHA\_CUNG\_CAP (Nhà cung cấp)**

| Tên thuộc tính (khung đối chiếu) | Kiểu dữ liệu (dự kiến) | Khóa / Ràng buộc | Diễn giải |
| :---- | :---- | :---- | :---- |
| ma\_ncc | \[VARCHAR/INT\] | PRIMARY KEY, NOT NULL | Mã định danh nhà cung cấp |
| ten\_ncc | \[VARCHAR\] | NOT NULL | Tên nhà cung cấp sách |
| dia\_chi | \[VARCHAR\] | \[Cần đối chiếu CSDL cuối\] | Địa chỉ nhà cung cấp |
| so\_dien\_thoai | \[VARCHAR\] | \[Cần đối chiếu CSDL cuối\] | Số điện thoại liên hệ |
| \[Các cột khác nếu có\] | \[Cần đối chiếu CSDL cuối\] | \[Cần đối chiếu CSDL cuối\] | Đối chiếu với code/CSDL bản cuối |

##### **Bảng 3: SACH (Sách)**

| Tên thuộc tính (khung đối chiếu) | Kiểu dữ liệu (dự kiến) | Khóa / Ràng buộc | Diễn giải |
| :---- | :---- | :---- | :---- |
| ma\_sach | \[VARCHAR\] | PRIMARY KEY, NOT NULL | Mã định danh đầu sách (ví dụ: S002, DEMO101...) |
| ten\_sach | \[VARCHAR\] | NOT NULL | Tên sách |
| the\_loai | \[VARCHAR\] | \[Cần đối chiếu CSDL cuối\] | Thể loại sách |
| tac\_gia | \[VARCHAR\] | \[Cần đối chiếu CSDL cuối\] | Tên tác giả |
| gia\_ban | \[DECIMAL/INT\] | NOT NULL, kiểm tra hợp lệ | Giá bán của sách |
| so\_luong\_ton | \[INT\] | NOT NULL, $\geq 0$ | Số lượng tồn kho hiện tại (không âm) |
| vi\_tri | \[VARCHAR\] | \[Cần đối chiếu CSDL cuối\] | Vị trí lưu sách trong kho (ví dụ: Kệ B2, A2...) |

##### **Bảng 4: PHIEU\_NHAP (Phiếu nhập)**

| Tên thuộc tính (khung đối chiếu) | Kiểu dữ liệu (dự kiến) | Khóa / Ràng buộc | Diễn giải |
| :---- | :---- | :---- | :---- |
| ma\_phieu\_nhap | \[VARCHAR/INT\] | PRIMARY KEY, NOT NULL | Mã định danh phiếu nhập kho |
| ngay\_nhap | \[DATE/DATETIME\] | NOT NULL | Ngày lập/thực hiện phiếu nhập (phục vụ thống kê theo tháng/năm) |
| ma\_ncc | \[VARCHAR/INT\] | FOREIGN KEY $\rightarrow$ NHA\_CUNG\_CAP | Nhà cung cấp giao hàng cho phiếu nhập |
| ma\_nguoi\_dung | \[VARCHAR/INT\] | FOREIGN KEY $\rightarrow$ NGUOI\_DUNG \[nếu có\] | Người lập/ghi nhận phiếu nhập |

##### **Bảng 5: CHI\_TIET\_PHIEU\_NHAP (Chi tiết phiếu nhập)**

| Tên thuộc tính (khung đối chiếu) | Kiểu dữ liệu (dự kiến) | Khóa / Ràng buộc | Diễn giải |
| :---- | :---- | :---- | :---- |
| ma\_chi\_tiet\_nhap / khóa kép | \[Tùy thiết kế CSDL\] | PRIMARY KEY, NOT NULL | Định danh dòng chi tiết phiếu nhập |
| ma\_phieu\_nhap | \[VARCHAR/INT\] | FOREIGN KEY $\rightarrow$ PHIEU\_NHAP, NOT NULL | Liên kết tới phiếu nhập tương ứng |
| ma\_sach | \[VARCHAR\] | FOREIGN KEY $\rightarrow$ SACH, NOT NULL | Đầu sách được nhập trong dòng này |
| so\_luong\_nhap | \[INT\] | NOT NULL, $>0$ (số nguyên dương) | Số lượng sách nhập vào kho |
| don\_gia\_nhap | \[DECIMAL/INT\] | NOT NULL, hợp lệ | Đơn giá nhập của đầu sách tại thời điểm nhập |

##### **Bảng 6: PHIEU\_XUAT (Phiếu xuất)**

| Tên thuộc tính (khung đối chiếu) | Kiểu dữ liệu (dự kiến) | Khóa / Ràng buộc | Diễn giải |
| :---- | :---- | :---- | :---- |
| ma\_phieu\_xuat | \[VARCHAR/INT\] | PRIMARY KEY, NOT NULL | Mã định danh phiếu xuất kho |
| ngay\_xuat | \[DATE/DATETIME\] | NOT NULL | Ngày lập/thực hiện phiếu xuất |
| ma\_nguoi\_dung | \[VARCHAR/INT\] | FOREIGN KEY $\rightarrow$ NGUOI\_DUNG \[nếu có\] | Người lập/ghi nhận phiếu xuất |

##### **Bảng 7: CHI\_TIET\_PHIEU\_XUAT (Chi tiết phiếu xuất)**

| Tên thuộc tính (khung đối chiếu) | Kiểu dữ liệu (dự kiến) | Khóa / Ràng buộc | Diễn giải |
| :---- | :---- | :---- | :---- |
| ma\_chi\_tiet\_xuat / khóa kép | \[Tùy thiết kế CSDL\] | PRIMARY KEY, NOT NULL | Định danh dòng chi tiết phiếu xuất |
| ma\_phieu\_xuat | \[VARCHAR/INT\] | FOREIGN KEY $\rightarrow$ PHIEU\_XUAT, NOT NULL | Liên kết tới phiếu xuất tương ứng |
| ma\_sach | \[VARCHAR\] | FOREIGN KEY $\rightarrow$ SACH, NOT NULL | Đầu sách được xuất trong dòng này |
| so\_luong\_xuat | \[INT\] | NOT NULL, $>0$, tổng xuất $\leq$ tồn kho | Số lượng sách xuất khỏi kho (cần kiểm tra tổng khi trùng mã sách) |

#### **3.3. Lược đồ thực thể \- liên kết (ERD)**

\[Chèn sơ đồ ERD 7 bảng tại đây sau khi đối chiếu tên bảng, tên cột và khóa ngoại với bản CSDL cuối cùng và sơ đồ của Kiệt\].

