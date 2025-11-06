# CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI

## 1.1. Đặt vấn đề (Tính cấp thiết của đề tài)

### 1.1.1. Bối cảnh thực tế

Ngân hàng Nông nghiệp và Phát triển Nông thôn Việt Nam (Agribank) là một trong những ngân hàng thương mại lớn nhất Việt Nam với hệ thống chi nhánh trải rộng khắp cả nước. Tại Chi nhánh Giá Rai - Bạc Liêu, hàng ngày có hàng trăm giao dịch với khách hàng, đòi hỏi phải tạo ra nhiều loại biểu mẫu, giấy tờ khác nhau như:

- Giấy đề nghị phát hành thẻ ATM/Visa/MasterCard
- Hợp đồng mở tài khoản tiết kiệm
- Đăng ký dịch vụ ngân hàng điện tử (E-Banking, Mobile Banking)
- Giấy đề nghị vay vốn
- Các mẫu biểu tra soát, khiếu nại
- Biên bản, hợp đồng dịch vụ khác

### 1.1.2. Thực trạng hiện tại

**Trước khi có hệ thống:**

Quy trình tạo biểu mẫu được thực hiện theo cách truyền thống:

1. **Lưu trữ phân tán:** Mỗi nhân viên tự lưu file mẫu biểu trên máy tính cá nhân, dẫn đến:
   - Khó kiểm soát phiên bản mẫu biểu mới nhất
   - Mất thời gian tìm kiếm file mẫu phù hợp
   - Dễ dẫn đến sử dụng mẫu biểu lỗi thời

2. **Nhập liệu thủ công:** Nhân viên phải:
   - Mở file Word template
   - Tìm và thay thế thủ công từng trường thông tin (họ tên, CMND, địa chỉ, v.v.)
   - Kiểm tra lại nhiều lần để tránh sai sót

3. **Rủi ro cao:**
   - Dễ nhầm lẫn thông tin khách hàng (copy-paste sai)
   - Format văn bản bị lỗi khi chỉnh sửa
   - Mất nhiều thời gian (trung bình 5-10 phút cho mỗi biểu mẫu)

4. **Khó quản lý:**
   - Không có cơ sở dữ liệu khách hàng tập trung
   - Mỗi lần khách hàng quay lại phải nhập lại toàn bộ thông tin
   - Không thể tra cứu lịch sử giao dịch, biểu mẫu đã tạo

### 1.1.3. Nhu cầu cấp thiết

Từ những bất cập trên, Chi nhánh Giá Rai - Bạc Liêu cần một giải pháp công nghệ để:

1. **Tự động hóa quy trình:**
   - Giảm thời gian tạo biểu mẫu từ 5-10 phút xuống còn dưới 1 phút
   - Loại bỏ thao tác nhập liệu thủ công, dễ sai sót

2. **Quản lý tập trung:**
   - Lưu trữ thống nhất tất cả mẫu biểu tại một nơi
   - Quản lý phiên bản, cập nhật mẫu biểu dễ dàng
   - Kiểm soát quyền truy cập theo từng nhóm người dùng

3. **Tích hợp dữ liệu:**
   - Xây dựng cơ sở dữ liệu khách hàng
   - Hỗ trợ import dữ liệu từ hệ thống Core Banking của Agribank
   - Tái sử dụng thông tin khách hàng cho các giao dịch sau

4. **Đảm bảo chất lượng:**
   - Validation dữ liệu đầu vào (số CMND, số điện thoại, ngày tháng)
   - Đảm bảo format văn bản đồng nhất
   - Giảm thiểu lỗi do con người

---

## 1.2. Mục tiêu của đề tài

### 1.2.1. Mục tiêu chung

Xây dựng **Hệ thống quản lý và tạo mẫu biểu tự động** (Word Template Management System) cho Agribank Chi nhánh Giá Rai - Bạc Liêu, nhằm:

- Tự động hóa quy trình tạo biểu mẫu Word
- Quản lý tập trung kho mẫu biểu và dữ liệu khách hàng
- Nâng cao hiệu quả công việc và giảm thiểu sai sót

### 1.2.2. Mục tiêu cụ thể

Hệ thống cần đạt được các mục tiêu sau:

**1. Về quản lý mẫu biểu:**
- Cho phép upload, lưu trữ các file Word template có chứa biến động (Jinja2 syntax)
- Phân loại mẫu biểu theo danh mục (Category) để dễ tìm kiếm
- Quản lý phiên bản mẫu biểu (version control)
- Hỗ trợ import hàng loạt mẫu biểu (bulk upload)

**2. Về quản lý dữ liệu:**
- Xây dựng CSDL khách hàng với đầy đủ thông tin (họ tên, CMND, địa chỉ, SĐT, v.v.)
- Hỗ trợ CRUD (Create, Read, Update, Delete) cho dữ liệu khách hàng
- Import dữ liệu từ file Excel/CSV/TSV (đặc biệt là dữ liệu từ hệ thống AGRIBANK)
- Tích hợp mapping biến từ hệ thống cũ sang hệ thống mới

**3. Về tạo tài liệu:**
- Chọn mẫu biểu và điền thông tin khách hàng qua giao diện web
- Tự động thay thế các biến trong template bằng dữ liệu thực tế
- Xuất file Word (.docx) với format đúng chuẩn
- Hỗ trợ các biến tự động (ngày hiện tại, tính tuổi, v.v.)

**4. Về phân quyền và bảo mật:**
- Hệ thống đăng nhập, phân quyền người dùng
- Sử dụng Django Groups để quản lý quyền truy cập
- Gán quyền xem/sử dụng mẫu biểu theo từng nhóm nhân viên
- Audit log: ghi lại hành động của người dùng

**5. Về trải nghiệm người dùng:**
- Giao diện thân thiện, dễ sử dụng (theo chuẩn Agribank)
- Responsive: hoạt động tốt trên desktop, tablet
- Hỗ trợ tìm kiếm, lọc dữ liệu nhanh chóng
- Validation dữ liệu đầu vào (số CMND, SĐT, ngày tháng)

### 1.2.3. Kết quả mong đợi

Sau khi triển khai hệ thống, kỳ vọng đạt được:

| Tiêu chí | Trước | Sau | Cải thiện |
|----------|-------|-----|-----------|
| Thời gian tạo 1 biểu mẫu | 5-10 phút | < 1 phút | **Giảm 80-90%** |
| Tỷ lệ lỗi sai sót | ~5% | < 0.5% | **Giảm 90%** |
| Thời gian tìm mẫu biểu | 2-3 phút | < 10 giây | **Giảm 95%** |
| Số lần nhập thông tin KH | Mỗi lần | 1 lần | **Tái sử dụng 100%** |

---

## 1.3. Đối tượng và phạm vi nghiên cứu

### 1.3.1. Đối tượng nghiên cứu

Đề tài tập trung vào các đối tượng sau:

**1. Quy trình nghiệp vụ:**
- Quy trình tạo biểu mẫu tại quầy giao dịch
- Quy trình quản lý mẫu biểu của ngân hàng
- Quy trình lưu trữ và tra cứu thông tin khách hàng

**2. Công nghệ áp dụng:**
- Framework Django (Python) cho backend
- Template engine Jinja2 để xử lý biến
- Thư viện python-docx để thao tác với file Word
- Bootstrap 5 cho giao diện người dùng
- SQLite/PostgreSQL cho cơ sở dữ liệu

**3. Dữ liệu xử lý:**
- Dữ liệu khách hàng (thông tin cá nhân, CMND/CCCD, địa chỉ, v.v.)
- Mẫu biểu Word có chứa biến (template)
- Metadata về mẫu biểu (tên, danh mục, biến sử dụng)
- Dữ liệu cấu hình chi nhánh (tên, địa chỉ, MST, v.v.)

### 1.3.2. Phạm vi nghiên cứu

**Phạm vi TRONG đề tài (In-scope):**

1. **Quản lý mẫu biểu:**
   - Upload/Download template Word (.docx)
   - Phân loại theo danh mục
   - Quản lý biến (Variable) sử dụng trong template
   - Hỗ trợ cú pháp Jinja2 trong Word

2. **Quản lý khách hàng:**
   - CRUD thông tin khách hàng
   - Import từ Excel/CSV/TSV
   - Import trực tiếp từ clipboard (copy-paste)
   - Hỗ trợ mapping biến từ hệ thống AGRIBANK cũ

3. **Tạo tài liệu:**
   - Chọn template và điền form
   - Auto-fill từ database khách hàng
   - Xuất file Word có thể download
   - Hỗ trợ biến tự động (ngày, tháng, năm, tính tuổi)

4. **Phân quyền:**
   - Đăng nhập/Đăng xuất
   - Phân quyền theo Django Groups
   - Gán quyền cho từng mẫu biểu

**Phạm vi NGOÀI đề tài (Out-of-scope):**

1. **KHÔNG hỗ trợ:**
   - Tích hợp trực tiếp với Core Banking System (cần API riêng)
   - Chữ ký điện tử (e-Signature)
   - Mobile app (chỉ có web responsive)
   - Tạo file PDF trực tiếp (hiện tại chỉ Word)
   - Workflow phê duyệt phức tạp

2. **Giới hạn:**
   - Chỉ hỗ trợ file Word (.docx), không hỗ trợ Excel template
   - Chỉ triển khai tại 1 chi nhánh (Giá Rai)
   - Dữ liệu lưu local, chưa đồng bộ đa chi nhánh

### 1.3.3. Người dùng mục tiêu

| Nhóm người dùng | Vai trò | Quyền hạn |
|-----------------|---------|-----------|
| **Admin** | Quản trị hệ thống | Toàn quyền: quản lý user, template, dữ liệu |
| **Giao dịch viên** | Nhân viên quầy | Tạo biểu mẫu, quản lý khách hàng |
| **Kiểm soát viên** | Nhân viên kiểm soát | Xem, kiểm tra biểu mẫu |
| **Giám đốc** | Quản lý chi nhánh | Xem báo cáo, thống kê |

---

## 1.4. Phương pháp nghiên cứu

Để thực hiện đề tài, đã áp dụng các phương pháp nghiên cứu sau:

### 1.4.1. Phương pháp khảo sát, thu thập thông tin

**Khảo sát thực tế:**
- Quan sát trực tiếp quy trình làm việc tại Chi nhánh Giá Rai
- Phỏng vấn nhân viên giao dịch về các vấn đề gặp phải
- Thu thập các mẫu biểu đang sử dụng (hơn 50 mẫu)

**Nghiên cứu tài liệu:**
- Tài liệu về Django framework và Python
- Tài liệu về python-docx library
- Tài liệu về Jinja2 template engine
- Các giải pháp tương tự trên thế giới

### 1.4.2. Phương pháp phân tích hệ thống

**Phân tích yêu cầu (Requirements Analysis):**
- Phân tích yêu cầu chức năng (Functional Requirements)
- Phân tích yêu cầu phi chức năng (Non-functional Requirements)
- Phân tích các ràng buộc (Constraints)

**Phân tích quy trình (Process Analysis):**
- Vẽ sơ đồ quy trình hiện tại (As-Is)
- Thiết kế quy trình mới (To-Be)
- Xác định điểm cải tiến

### 1.4.3. Phương pháp thiết kế hướng đối tượng

**Sử dụng UML (Unified Modeling Language):**
- Use Case Diagram: mô tả chức năng
- Class Diagram: thiết kế các lớp đối tượng
- Sequence Diagram: luồng tương tác giữa các đối tượng
- Activity Diagram: quy trình xử lý
- ERD (Entity-Relationship Diagram): thiết kế CSDL

**Áp dụng Design Patterns:**
- MVC/MVT Pattern (Django)
- Repository Pattern (Data Access)
- Singleton Pattern (GlobalConfig)
- Factory Pattern (Template Generation)

### 1.4.4. Phương pháp lập trình

**Agile Development:**
- Phát triển theo sprint (1-2 tuần/sprint)
- Iterative: cải tiến liên tục dựa trên feedback
- Testing từng module ngay khi hoàn thành

**Best Practices:**
- Code convention: PEP 8 (Python)
- Version control: Git
- Code review
- Documentation

### 1.4.5. Phương pháp kiểm thử

**Các loại kiểm thử:**
- Unit Testing: kiểm thử từng function
- Integration Testing: kiểm thử tích hợp các module
- System Testing: kiểm thử toàn hệ thống
- User Acceptance Testing (UAT): người dùng thử nghiệm

**Kỹ thuật kiểm thử:**
- Black-box testing: kiểm thử không biết cấu trúc bên trong
- White-box testing: kiểm thử dựa trên source code
- Regression testing: kiểm thử lại sau khi sửa lỗi

---

## 1.5. Bố cục của báo cáo

Báo cáo được chia thành 5 chương với nội dung như sau:

**CHƯƠNG 1: TỔNG QUAN VỀ ĐỀ TÀI**
- Giới thiệu bối cảnh, lý do chọn đề tài
- Nêu mục tiêu, đối tượng, phạm vi nghiên cứu
- Trình bày phương pháp nghiên cứu được sử dụng

**CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ PHÂN TÍCH HIỆN TRẠNG**
- Trình bày các kiến thức nền tảng về công nghệ sử dụng
- Phân tích quy trình hiện tại và các vấn đề tồn tại
- Phân tích yêu cầu hệ thống chi tiết

**CHƯƠNG 3: THIẾT KẾ HỆ THỐNG**
- Lựa chọn công nghệ và giải thích lý do
- Thiết kế kiến trúc tổng thể
- Thiết kế chi tiết: Use Case, Database, UI/UX

**CHƯƠNG 4: CÀI ĐẶT VÀ THỬ NGHIỆM**
- Môi trường cài đặt (phần cứng, phần mềm)
- Trình bày cài đặt các module chính
- Kết quả kiểm thử và đánh giá

**CHƯƠNG 5: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**
- Tổng kết kết quả đạt được
- Phân tích ưu điểm, nhược điểm
- Đề xuất hướng phát triển tương lai

---

