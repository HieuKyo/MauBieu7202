# Hệ thống Quản lý Mẫu biểu Word - AGRIBANK

Ứng dụng web Django cho phép nhân viên Agribank tạo file Microsoft Word (.docx) từ các mẫu có sẵn với cú pháp Jinja2.

**Thiết kế giao diện theo chuẩn nhận diện thương hiệu Agribank** với màu xanh lá đặc trưng (#00923F).

## Tính năng chính

### 1. Phân cấp Mẫu biểu
- **Danh mục (Cha)**: Tổ chức mẫu biểu theo nhóm (VD: "Phát hành thẻ", "Tra soát", "Mở tài khoản")
- **Mẫu biểu (Con)**: Các file .docx cụ thể thuộc một danh mục

### 2. Quản lý qua Django Admin
- Quản lý Danh mục (CRUD)
- Quản lý Mẫu biểu (upload file .docx, gán danh mục)
- Quản lý Biến (định nghĩa các biến như `ho_ten`, `ngay_sinh`)
- Gán biến cho từng mẫu biểu
- **Import/Export Biến** từ CSV/Excel
- **Import hàng loạt Mẫu biểu** (bulk upload nhiều file .docx)

### 3. Biến thông minh (Dynamic Forms)
- Hỗ trợ 4 kiểu dữ liệu:
  - `text`: Văn bản ngắn
  - `textarea`: Đoạn văn dài
  - `date`: Ngày tháng
  - `number`: Số
- Form nhập liệu tự động được tạo dựa trên biến của mẫu biểu

### 4. Luồng nghiệp vụ
1. Đăng nhập
2. Xem danh sách **Danh mục** trên Dashboard
3. Chọn Danh mục → Xem danh sách **Mẫu biểu con**
4. Chọn Mẫu biểu → Điền form nhập liệu
5. Tạo và tải xuống file Word

### 5. Phân quyền
- Sử dụng Django Groups (VD: "Phòng Kinh doanh", "Phòng Kế toán")
- Quyền gán ở cấp độ **Mẫu biểu**
- Danh mục chỉ hiển thị nếu user có quyền ít nhất 1 mẫu biểu con

## Cài đặt

### 1. Yêu cầu hệ thống
- Python 3.8+
- pip

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Chạy migrations

```bash
python manage.py migrate
```

### 4. Tạo superuser

```bash
python manage.py createsuperuser
```

Nhập thông tin:
- Username: `admin`
- Email: (có thể bỏ trống)
- Password: (nhập password mạnh)

### 5. Chạy server

```bash
python manage.py runserver 0.0.0.0:8000
```

Truy cập:
- Trang chủ: `http://localhost:8000/`
- Admin: `http://localhost:8000/admin/`

## Hướng dẫn sử dụng

### A. Quản trị viên (Admin)

#### 1. Tạo Danh mục
1. Đăng nhập Admin: `http://localhost:8000/admin/`
2. Vào **Danh mục** → **Thêm danh mục**
3. Nhập:
   - Tên danh mục: "Phát hành thẻ"
   - Mô tả: "Các mẫu biểu liên quan đến phát hành thẻ"
   - Thứ tự: 1
4. Lưu

#### 2. Tạo Biến
1. Vào **Biến** → **Thêm biến**
2. Nhập:
   - Tên biến: `ho_ten` (không dấu, không khoảng trắng)
   - Nhãn hiển thị: "Họ và tên"
   - Kiểu dữ liệu: "Văn bản"
   - Bắt buộc nhập: ✓
3. Lưu

Tạo thêm các biến khác:
- `ngay_sinh` - "Ngày sinh" - Kiểu: Date
- `so_cmnd` - "Số CMND/CCCD" - Kiểu: Text
- `dia_chi` - "Địa chỉ" - Kiểu: Textarea

#### 3. Tạo file Word template
Tạo file Word với các biến Jinja2:

```
Họ và tên: {{ ho_ten }}
Ngày sinh: {{ ngay_sinh }}
Số CMND: {{ so_cmnd }}
Địa chỉ: {{ dia_chi }}
```

Lưu file: `mau_phat_hanh_the.docx`

#### 4. Tạo Mẫu biểu
1. Vào **Mẫu biểu** → **Thêm mẫu biểu**
2. Nhập:
   - Danh mục: "Phát hành thẻ"
   - Tên mẫu biểu: "Mẫu phát hành thẻ tín dụng"
   - Mô tả: "Mẫu đơn xin phát hành thẻ tín dụng"
   - File Word: (upload `mau_phat_hanh_the.docx`)
   - Kích hoạt: ✓
3. Trong phần **Biến của mẫu biểu**, thêm các biến:
   - Biến: `ho_ten`, Thứ tự: 1
   - Biến: `ngay_sinh`, Thứ tự: 2
   - Biến: `so_cmnd`, Thứ tự: 3
   - Biến: `dia_chi`, Thứ tự: 4
4. Lưu

#### 5. Phân quyền (Optional)
1. Vào **Groups** → **Thêm group**
2. Tạo group: "Phòng Kinh doanh"
3. Quay lại **Mẫu biểu** → Edit mẫu biểu
4. Chọn **Nhóm được phép truy cập**: "Phòng Kinh doanh"
5. Lưu

6. Vào **Users** → Chọn user → Edit
7. Trong **Groups**, thêm user vào "Phòng Kinh doanh"
8. Lưu

### B. Người dùng (Nhân viên)

#### 1. Đăng nhập
1. Truy cập: `http://localhost:8000/`
2. Nhập username và password
3. Đăng nhập

#### 2. Chọn Danh mục
1. Dashboard hiển thị danh sách **Danh mục**
2. Nhấn vào danh mục "Phát hành thẻ"

#### 3. Chọn Mẫu biểu
1. Danh sách **Mẫu biểu con** hiển thị
2. Nhấn vào "Mẫu phát hành thẻ tín dụng"

#### 4. Điền form
1. Form nhập liệu hiển thị với các trường:
   - Họ và tên: `Nguyễn Văn A`
   - Ngày sinh: `01/01/1990`
   - Số CMND: `123456789`
   - Địa chỉ: `123 Đường ABC, Quận XYZ, TP.HCM`
2. Nhấn **Tạo mẫu biểu**

#### 5. Tải file Word
- File Word được tạo và tải xuống tự động
- Tên file: `Mẫu phát hành thẻ tín dụng_username.docx`

## Triển khai trên LAN

### 1. Cấu hình ALLOWED_HOSTS

Sửa file `wordgen/settings.py`:

```python
ALLOWED_HOSTS = ['192.168.1.100', 'localhost', '127.0.0.1']
```

Thay `192.168.1.100` bằng IP LAN của máy chủ.

### 2. Chạy server trên LAN

```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. Truy cập từ máy khác trong LAN

```
http://192.168.1.100:8000/
```

## Cấu trúc dự án

```
MauBieu7202/
├── wordgen/                 # Django project
│   ├── settings.py         # Cấu hình
│   ├── urls.py             # URL routing
│   └── wsgi.py
├── templates_app/          # Django app
│   ├── models.py           # Models (Category, Template, Variable)
│   ├── views.py            # Views (Dashboard, Form, Generate)
│   ├── forms.py            # Dynamic forms
│   ├── admin.py            # Django admin config
│   ├── utils.py            # Word template processor
│   ├── urls.py             # App URLs
│   └── templates/          # HTML templates
│       └── templates_app/
│           ├── base.html
│           ├── login.html
│           ├── dashboard.html
│           ├── category_detail.html
│           └── template_form.html
├── media/                  # Uploaded files (templates)
├── db.sqlite3              # Database
├── manage.py
└── requirements.txt
```

## Models

### Category
- `name`: Tên danh mục
- `description`: Mô tả
- `order`: Thứ tự hiển thị

### Variable
- `name`: Tên biến (VD: `ho_ten`)
- `label`: Nhãn hiển thị (VD: "Họ và tên")
- `field_type`: Kiểu dữ liệu (text/textarea/date/number)
- `required`: Bắt buộc nhập
- `default_value`: Giá trị mặc định

### Template
- `category`: Danh mục cha
- `name`: Tên mẫu biểu
- `file`: File Word .docx
- `variables`: Các biến (ManyToMany)
- `allowed_groups`: Nhóm được phép truy cập
- `is_active`: Kích hoạt

### TemplateVariable
- `template`: Mẫu biểu
- `variable`: Biến
- `order`: Thứ tự hiển thị trong form

## Tính năng Import/Export (Mới)

### Import Biến từ CSV/Excel

Quản trị viên có thể import hàng loạt biến từ file CSV hoặc Excel:

#### Cách sử dụng:

1. Vào trang Admin: `/admin/`
2. Click vào **Biến**
3. Click nút **"Import Biến"** ở góc phải trên
4. Upload file CSV hoặc Excel (.xlsx)

#### Định dạng file CSV:

```csv
name,label,field_type,required,default_value,help_text
ho_ten,Họ và tên,text,True,,Nhập họ tên đầy đủ
ngay_sinh,Ngày sinh,date,True,,Nhập ngày sinh
so_cmnd,Số CMND/CCCD,text,True,,Nhập số CMND hoặc CCCD
dia_chi,Địa chỉ,textarea,False,,Nhập địa chỉ chi tiết
```

**Các cột:**
- `name` (bắt buộc): Tên biến, không dấu, không khoảng trắng
- `label` (bắt buộc): Nhãn hiển thị
- `field_type`: text, textarea, date, hoặc number (mặc định: text)
- `required`: True/False (mặc định: True)
- `default_value`: Giá trị mặc định (tùy chọn)
- `help_text`: Gợi ý nhập liệu (tùy chọn)

**File mẫu:** `sample_variables.csv` trong thư mục gốc

#### Export Biến:

Để tạo file mẫu hoặc backup:

1. Vào trang Admin → **Biến**
2. Click nút **"Export CSV"** hoặc **"Export Excel"**
3. File sẽ được tải xuống

### Import Nhiều Mẫu biểu (Bulk Upload)

Quản trị viên có thể upload nhiều file Word (.docx) cùng lúc:

#### Cách sử dụng:

1. Vào trang Admin: `/admin/`
2. Click vào **Mẫu biểu**
3. Click nút **"Import Nhiều Mẫu biểu"** ở góc phải trên
4. Chọn **nhiều file .docx** (giữ Ctrl hoặc Cmd)
5. Chọn **Danh mục** chung cho các mẫu biểu
6. (Tùy chọn) Chọn **Biến** để gán cho tất cả mẫu biểu
7. (Tùy chọn) Chọn **Nhóm phân quyền**
8. Click **"Import"**

#### Ví dụ:

Nếu bạn chọn 3 file:
- `Mau_phat_hanh_the_tin_dung.docx` → Tạo mẫu biểu tên "Mau phat hanh the tin dung"
- `Mau_tra_soat_ATM.docx` → Tạo mẫu biểu tên "Mau tra soat ATM"
- `Mau_mo_tai_khoan.docx` → Tạo mẫu biểu tên "Mau mo tai khoan"

**Lưu ý:**
- Tên mẫu biểu tự động lấy từ tên file (bỏ `.docx`)
- Tất cả mẫu biểu sẽ được gán vào cùng 1 danh mục
- Bạn có thể chỉnh sửa từng mẫu biểu sau khi import

## Giao diện Agribank Branding

Hệ thống được thiết kế theo chuẩn nhận diện thương hiệu Agribank:

- **Màu chủ đạo:** Xanh lá Agribank (#00923F)
- **Màu phụ:** Xanh đậm (#006838)
- **Màu nhấn:** Vàng (#FFB81C)
- **Logo:** Hiển thị trên header và trang login
- **Font chữ:** Arial, sans-serif (chuẩn Agribank)

### Các file theme:

- `templates_app/static/css/agribank-theme.css`: CSS theme Agribank
- `templates_app/static/images/agribank-logo.svg`: Logo Agribank (placeholder)

**Lưu ý:** Thay file `agribank-logo.svg` bằng logo chính thức của Agribank nếu có

## Troubleshooting

### Lỗi: "Cannot import name 'OxmlElement'"
- Đã được fix trong `utils.py`
- Không cần thư viện `docxtpl`, sử dụng custom processor

### File Word không hiển thị đúng biến
- Kiểm tra cú pháp trong file Word: `{{ ten_bien }}`
- Đảm bảo tên biến trong Word khớp với tên biến trong database

### Không thấy Danh mục trên Dashboard
- Kiểm tra user có thuộc Group được phân quyền không
- Kiểm tra Mẫu biểu có `is_active = True` không
- Kiểm tra Danh mục có ít nhất 1 Mẫu biểu con không

## License

Internal use only - Nội bộ tổ chức

## Liên hệ

Vui lòng liên hệ quản trị viên nếu có vấn đề.
