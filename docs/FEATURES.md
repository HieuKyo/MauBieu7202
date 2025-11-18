# DANH SÁCH CHỨC NĂNG MAUBIEU7202

## Mục lục
- [Tổng quan chức năng](#tổng-quan-chức-năng)
- [Bảng chi tiết chức năng](#bảng-chi-tiết-chức-năng)

---

## Tổng quan chức năng

### Bảng tóm tắt các chức năng chính

| STT | Chức năng | Mô tả ngắn | Đường dẫn |
|-----|-----------|------------|-----------|
| 1 | Quản lý Mẫu biểu | Tạo tài liệu Word từ template | `/` |
| 2 | Quản lý Khách hàng | Lưu trữ và quản lý thông tin KH | `/customers/` |
| 3 | Quản lý Nhân viên | Quản lý hồ sơ nhân viên | `/employees/` |
| 4 | E-Learning | Quản lý khóa học và đào tạo | `/elearning/` |
| 5 | Tra cứu Số đẹp | Tra cứu phí số đẹp tài khoản | `/beautiful-number-lookup/` |
| 6 | Phân tích Sao kê | Upload và phân tích sao kê | `/bank-statement/upload/` |
| 7 | Cấu hình Chi nhánh | Thiết lập thông tin chi nhánh | `/branch-config/` |
| 8 | Thư viện Biến | Quản lý các biến trong template | `/variable-library/` |
| 9 | Trang Quản trị | Quản lý hệ thống | `/admin/` |

---

## Bảng chi tiết chức năng

### 1. Quản lý Mẫu biểu Word

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Dashboard danh mục | Hiển thị tất cả danh mục mẫu biểu với số lượng template | `/` |
| Xem chi tiết danh mục | Danh sách các mẫu biểu trong danh mục | `/category/<id>/` |
| Form nhập liệu | Form động để điền thông tin vào template | `/template/<id>/` |
| Tạo file Word | Tạo file .docx từ template với dữ liệu đã nhập | `/template/<id>/generate/` |
| Xem trước in | Preview mẫu biểu trước khi in | `/template/<id>/preview/` |
| Hỗ trợ Jinja2 | Cú pháp Jinja2 cho các biến trong template | - |
| Hỗ trợ bảng | Tự động điền dữ liệu vào bảng trong Word | - |
| Hỗ trợ checkbox | Đánh dấu checkbox trong template | - |
| Định dạng ngày | Tự động định dạng ngày tháng tiếng Việt | - |
| API lấy templates | API lấy danh sách template theo danh mục | `/api/categories/<id>/templates/` |

### 2. Quản lý Khách hàng

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Danh sách khách hàng | Hiển thị tất cả KH với tìm kiếm, phân trang | `/customers/` |
| Tìm kiếm nhanh | Tìm kiếm theo tên, CMND, số tài khoản | `/api/customers/search/` |
| Xem chi tiết KH | Lấy thông tin chi tiết của khách hàng | `/api/customers/<id>/` |
| Thêm mới KH | Tạo khách hàng mới | `/api/customers/create/` |
| Cập nhật KH | Sửa thông tin khách hàng | `/api/customers/<id>/update/` |
| Xóa KH | Xóa khách hàng khỏi hệ thống | `/api/customers/<id>/delete/` |
| Import từ Excel | Nhập hàng loạt KH từ file Excel | `/api/customers/import-excel/` |
| Import từ TSV | Nhập từ định dạng TSV (Agribank) | `/api/customers/import/tsv/` |
| Auto-fill template | Tự động điền thông tin KH vào mẫu biểu | - |
| Lưu trữ dịch vụ | Lưu thông tin các dịch vụ KH đang sử dụng | - |

**Các trường thông tin KH:**
- Họ tên, Ngày sinh, Giới tính
- CMND/CCCD, Ngày cấp, Nơi cấp
- Địa chỉ (Tỉnh/Huyện/Xã/Ấp)
- Số điện thoại, Email
- Số tài khoản, Ngày mở TK
- Các dịch vụ: SMS Banking, E-Banking, Agri-Card...

### 3. Quản lý Nhân viên

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Danh sách nhân viên | Hiển thị tất cả NV với tìm kiếm, lọc | `/employees/` |
| Import từ Excel | Nhập hàng loạt NV từ file Excel | `/employees/import/` |
| Tải template Excel | Tải file mẫu để import | `/employees/import/template/` |
| Thêm mới NV | Tạo nhân viên mới | `/employees/create/` |
| Cập nhật NV | Sửa thông tin nhân viên | `/employees/<id>/update/` |
| Xóa NV | Xóa nhân viên | `/employees/<id>/delete/` |
| Liên kết User | Liên kết NV với tài khoản đăng nhập | - |

**Các trường thông tin NV:**
- Mã nhân viên
- Họ tên đầy đủ
- Chi nhánh/Phòng giao dịch
- Phòng ban
- Chức vụ
- Email, Số điện thoại

### 4. Hệ thống E-Learning

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Dashboard khóa học | Hiển thị tất cả khóa học | `/elearning/` |
| Tạo khóa học | Tạo khóa học mới với thông tin | `/elearning/courses/create/` |
| Thêm học viên | Ghi danh nhân viên vào khóa học | `/elearning/courses/<id>/add-students/` |
| Toggle hoàn thành | Đánh dấu hoàn thành/chưa hoàn thành | `/elearning/enrollment/<id>/toggle/` |
| Theo dõi tiến độ | Xem tỷ lệ hoàn thành của khóa học | - |
| Thống kê | Số người đăng ký, đã hoàn thành | - |

**Thông tin khóa học:**
- Tên khóa học
- Ngày bắt đầu, Ngày kết thúc
- Danh sách học viên
- Trạng thái hoàn thành

### 5. Tra cứu Số đẹp Tài khoản

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Tra cứu phí | Tra cứu phí số đẹp theo quy tắc | `/beautiful-number-lookup/` |
| Danh sách số đẹp | Xem danh sách số đẹp có sẵn | `/beautiful-number-list/` |
| Sinh số đẹp | Tạo số đẹp mới theo tiêu chí | `/api/beautiful-numbers/generate/` |

**Các loại số đẹp:**
- Lộc Phát (68, 86, 168, 268...)
- Tài Lộc (79, 39, 69...)
- Tam Hoa (111, 222, 333...)
- Tứ Quý (1111, 2222...)
- Hợp Tuổi
- Phong Thủy
- VIP

**Bảng phí theo số lượng:**
- Mở mới: theo bậc số lượng
- Chọn số theo yêu cầu: phí riêng

### 6. Phân tích Sao kê Ngân hàng

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Upload sao kê | Tải lên file sao kê Excel | `/bank-statement/upload/` |
| Phân tích tự động | Tự động đọc và phân tích giao dịch | - |
| Xem kết quả | Hiển thị chi tiết các giao dịch | `/bank-statement/result/<id>/` |
| Export Excel | Xuất kết quả ra file Excel | `/bank-statement/export/<id>/` |

**Thông tin phân tích:**
- Tổng số giao dịch
- Tổng ghi nợ
- Tổng ghi có
- Chi tiết từng giao dịch

### 7. Cấu hình Hệ thống

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Cấu hình chi nhánh | Thiết lập thông tin chi nhánh | `/branch-config/` |
| Thêm biến tùy chỉnh | Tạo biến mới cho template | `/api/custom-variables/add/` |
| Cập nhật biến | Sửa giá trị biến | `/api/custom-variables/update/` |
| Xóa biến | Xóa biến khỏi hệ thống | `/api/custom-variables/delete/` |

**Cấu hình chi nhánh:**
- Tên chi nhánh
- Mã chi nhánh
- Tên giao dịch viên mặc định
- Các biến tùy chỉnh (key-value)

**Biến tự động:**
- `ngay_hien_tai`: Ngày hiện tại
- `nam_hien_tai`: Năm hiện tại
- `thang_hien_tai`: Tháng hiện tại

### 8. Thư viện Biến

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Danh sách biến | Xem tất cả biến có trong hệ thống | `/variable-library/` |
| Biến khách hàng | Các biến từ thông tin KH | - |
| Biến cấu hình | Các biến từ cấu hình chi nhánh | - |
| Biến tự động | Các biến hệ thống tự tạo | - |

### 9. Xác thực & Phân quyền

| Tính năng | Mô tả chi tiết | Đường dẫn/API |
|-----------|----------------|---------------|
| Đăng nhập | Xác thực người dùng | `/login/` |
| Đăng xuất | Kết thúc phiên làm việc | `/logout/` |
| Phân quyền nhóm | Giới hạn truy cập template theo nhóm | - |
| Quản lý User | Quản lý tài khoản trong Admin | `/admin/` |

**Mô hình phân quyền:**
- Mỗi Template có thể giới hạn cho một số nhóm (Groups)
- User thuộc nhóm nào sẽ thấy template của nhóm đó
- Admin có toàn quyền truy cập

---

## Tích hợp & API

### RESTful API Endpoints

| Endpoint | Method | Mô tả |
|----------|--------|-------|
| `/api/categories/<id>/templates/` | GET | Lấy templates theo danh mục |
| `/api/customers/search/` | GET | Tìm kiếm khách hàng |
| `/api/customers/<id>/` | GET | Chi tiết khách hàng |
| `/api/customers/create/` | POST | Tạo khách hàng mới |
| `/api/customers/<id>/update/` | PUT | Cập nhật khách hàng |
| `/api/customers/<id>/delete/` | DELETE | Xóa khách hàng |
| `/api/customers/import-excel/` | POST | Import từ Excel |
| `/api/customers/import/tsv/` | POST | Import từ TSV |
| `/api/custom-variables/add/` | POST | Thêm biến tùy chỉnh |
| `/api/custom-variables/update/` | PUT | Cập nhật biến |
| `/api/custom-variables/delete/` | DELETE | Xóa biến |
| `/api/beautiful-numbers/generate/` | POST | Sinh số đẹp |

---

## Công nghệ sử dụng

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| Backend | Django | 5.2.7 |
| Database | SQLite | 3.x |
| Frontend | Bootstrap | 5.3.0 |
| Icons | Bootstrap Icons | 1.x |
| Word Processing | python-docx | 1.2.0 |
| Excel Processing | openpyxl | 3.1.5 |
| Data Analysis | pandas | 1.5+ |
| Production Server | Waitress | 3.0.1 |
| Static Files | WhiteNoise | 6.8.2 |

---

## Ghi chú

- Tất cả đường dẫn đều yêu cầu đăng nhập (trừ `/login/`)
- Admin panel (`/admin/`) chỉ dành cho superuser
- File Word template sử dụng cú pháp Jinja2
- Database mặc định là SQLite, có thể chuyển sang PostgreSQL/MySQL
