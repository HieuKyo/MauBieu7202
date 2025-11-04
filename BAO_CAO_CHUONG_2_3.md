# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ PHÂN TÍCH HIỆN TRẠNG

## 2.1. Cơ sở lý thuyết

### 2.1.1. Giới thiệu về Django Framework

**Django** là một high-level Python web framework khuyến khích phát triển nhanh và thiết kế sạch, thực dụng. Được phát triển bởi Django Software Foundation.

**Đặc điểm nổi bật:**
- **Batteries included**: Tích hợp sẵn nhiều tính năng (ORM, Admin, Authentication, Forms)
- **DRY Principle** (Don't Repeat Yourself): Tối ưu code, tránh lặp lại
- **Security**: Bảo vệ tự động khỏi SQL injection, XSS, CSRF
- **Scalable**: Dễ dàng mở rộng (Instagram, Pinterest sử dụng Django)

**Kiến trúc MVT (Model-View-Template):**

```
┌─────────────────────────────────────────────────┐
│              DJANGO MVT PATTERN                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  HTTP Request                                    │
│       ↓                                          │
│  [URL Dispatcher] urls.py                        │
│       ↓                                          │
│  [View] views.py ←→ [Model] models.py            │
│       ↓                        ↓                 │
│  [Template] .html ←→    [Database]               │
│       ↓                                          │
│  HTTP Response                                   │
│                                                  │
└─────────────────────────────────────────────────┘
```

**So sánh với các framework khác:**

| Framework | Ưu điểm | Nhược điểm | Lý do không chọn |
|-----------|---------|------------|------------------|
| **Django** | Admin sẵn có, ORM mạnh mẽ, bảo mật tốt | Hơi "nặng" cho dự án nhỏ | **CHỌN** |
| Flask | Nhẹ, linh hoạt | Phải tự cài đặt nhiều thứ | Mất thời gian setup |
| FastAPI | Rất nhanh, async native | Chưa có admin UI | Cần admin panel |
| Express.js | Phổ biến, cộng đồng lớn | Không hỗ trợ Word processing tốt | Ngôn ngữ khác (JS) |

### 2.1.2. Django ORM (Object-Relational Mapping)

**Khái niệm:**
ORM cho phép thao tác database bằng code Python thay vì viết SQL thuần.

**Ví dụ minh họa:**

```python
# models.py - Định nghĩa model
class Customer(models.Model):
    ho_ten = models.CharField(max_length=200)
    so_cmnd = models.CharField(max_length=20, unique=True)
    ngay_sinh = models.DateField()

# Thay vì SQL:
# INSERT INTO customer (ho_ten, so_cmnd, ngay_sinh) VALUES (?, ?, ?)

# Dùng ORM:
customer = Customer.objects.create(
    ho_ten="Nguyễn Văn A",
    so_cmnd="001234567890",
    ngay_sinh="1990-01-01"
)
```

**Ưu điểm:**
- Code dễ đọc, dễ maintain
- Tự động validate dữ liệu
- Hỗ trợ migrations (thay đổi cấu trúc DB dễ dàng)
- Database-agnostic (dễ chuyển từ SQLite → PostgreSQL)

### 2.1.3. Jinja2 Template Engine

**Jinja2** là template engine mạnh mẽ cho Python, cho phép embed biến và logic vào file text (HTML, Word, v.v.)

**Cú pháp cơ bản:**

```jinja2
{# Comment #}

{{ variable }}                    {# In giá trị #}
{% if condition %}...{% endif %}  {# Điều kiện #}
{% for item in list %}...{% endfor %}  {# Vòng lặp #}
{% set var = value %}             {# Gán biến #}

{# Ví dụ trong Word template #}
Khách hàng: {{ ho_ten }}
Số CMND: {{ so_cmnd }}

{% if tuoi < 18 %}
  Cần sự đồng ý của người giám hộ
{% endif %}
```

**Trong hệ thống:**
- Template Word chứa các biến `{{ ten_bien }}`
- Django render template với dữ liệu thực tế
- Output là file Word hoàn chỉnh

### 2.1.4. Thư viện python-docx

**python-docx** cho phép tạo và chỉnh sửa file Word (.docx) bằng Python.

**Chức năng chính:**
- Đọc/ghi file .docx
- Thao tác với paragraphs, tables, images
- Định dạng text (font, size, color, bold, italic)

**Ví dụ:**

```python
from docx import Document

# Tạo document mới
doc = Document()

# Thêm paragraph
doc.add_paragraph('Họ tên: Nguyễn Văn A')

# Thêm table
table = doc.add_table(rows=2, cols=2)
table.cell(0, 0).text = 'CMND'
table.cell(0, 1).text = '001234567890'

# Lưu file
doc.save('output.docx')
```

**Trong hệ thống:**
- Load template Word
- Render Jinja2 để thay thế biến
- Lưu file output với python-docx

### 2.1.5. Bootstrap 5 Framework

**Bootstrap** là CSS framework phổ biến nhất cho phát triển responsive web.

**Đặc điểm:**
- Grid system 12 cột responsive
- Components sẵn có (navbar, cards, modals, forms)
- Icons library (Bootstrap Icons)
- Tương thích mọi trình duyệt

**Trong hệ thống:**
- Dùng Bootstrap 5.3.0
- Customize màu chủ đạo thành màu xanh lá Agribank (#00923F)
- Responsive: desktop → tablet → mobile

### 2.1.6. Waitress WSGI Server

**Waitress** là production-ready WSGI server viết bằng Python.

**Ưu điểm:**
- Cross-platform (Windows, Linux, macOS)
- Không cần cài đặt phức tạp như Gunicorn
- Hiệu năng tốt cho mạng LAN nội bộ
- Thread-safe

**So sánh:**

| WSGI Server | Platform | Cài đặt | Lý do |
|-------------|----------|---------|-------|
| **Waitress** | Cross-platform | Dễ | **CHỌN** cho Windows |
| Gunicorn | Linux only | Dễ | Không chạy trên Windows |
| uWSGI | Cross-platform | Khó | Cấu hình phức tạp |

---

## 2.2. Khảo sát và phân tích hiện trạng

### 2.2.1. Quy trình tạo biểu mẫu hiện tại (As-Is)

**Bước 1: Khách hàng đến quầy giao dịch**
- Nhân viên tiếp nhận yêu cầu (ví dụ: Làm thẻ ATM)

**Bước 2: Thu thập thông tin**
- Khách hàng điền form giấy hoặc nhân viên ghi chép
- Thông tin: Họ tên, CMND, ngày sinh, địa chỉ, SĐT...

**Bước 3: Tìm kiếm mẫu biểu**
- Nhân viên tìm file Word template trên máy tính
- Có thể mất 2-3 phút nếu không nhớ đường dẫn
- Rủi ro sử dụng mẫu cũ nếu không cập nhật

**Bước 4: Nhập liệu thủ công**
- Mở file Word
- Tìm và thay thế từng trường:
  ```
  Họ tên: [Nhập họ tên]        → Họ tên: Nguyễn Văn A
  CMND: [Nhập CMND]             → CMND: 001234567890
  Ngày sinh: [Nhập ngày sinh]   → Ngày sinh: 01/01/1990
  ... (10-20 trường tương tự)
  ```
- Mất 5-10 phút
- Dễ nhầm lẫn (copy-paste sai)

**Bước 5: Kiểm tra và in**
- Nhân viên đọc lại toàn bộ
- In ra giấy
- Khách hàng ký

**Vấn đề:**
- ⚠️ Tốn thời gian (5-10 phút/biểu mẫu)
- ⚠️ Dễ sai sót (5% lỗi do nhập tay)
- ⚠️ Không lưu trữ thông tin khách hàng
- ⚠️ Khách hàng quay lại phải nhập lại từ đầu
- ⚠️ Khó thống kê, báo cáo

### 2.2.2. Phân tích điểm yếu

| STT | Vấn đề | Tác động | Mức độ nghiêm trọng |
|-----|--------|----------|---------------------|
| 1 | Lưu trữ file phân tán | Khó kiểm soát phiên bản | Cao |
| 2 | Nhập liệu thủ công | Tốn thời gian, dễ sai | Rất cao |
| 3 | Không có CSDL khách hàng | Nhập lại mỗi lần | Cao |
| 4 | Không validation | Lỗi format (CMND, SĐT) | Trung bình |
| 5 | Không có audit log | Không truy vết được | Thấp |

### 2.2.3. Nhu cầu cải tiến

**Quy trình mới cần có (To-Be):**

```
┌────────────────────────────────────────────────┐
│  KHÁCH HÀNG ĐẾN QUẦY                           │
│         ↓                                      │
│  NHÂN VIÊN ĐĂNG NHẬP HỆ THỐNG                  │
│         ↓                                      │
│  TÌM KIẾM KHÁCH HÀNG TRONG DB                  │
│    ├─ Có → Tự động điền thông tin             │
│    └─ Không có → Nhập mới hoặc Import từ AGRIBANK
│         ↓                                      │
│  CHỌN MẪU BIỂU TỪ DANH SÁCH                    │
│         ↓                                      │
│  HỆ THỐNG TỰ ĐỘNG ĐIỀN DỮ LIỆU                │
│         ↓                                      │
│  KIỂM TRA & DOWNLOAD FILE WORD                 │
│         ↓                                      │
│  IN VÀ CHO KHÁCH HÀNG KÝ                       │
└────────────────────────────────────────────────┘

Thời gian: < 1 phút (giảm 80-90%)
```

---

## 2.3. Phân tích yêu cầu hệ thống

### 2.3.1. Yêu cầu chức năng (Functional Requirements)

#### **FR1: Quản lý người dùng**

| Mã yêu cầu | Mô tả | Ưu tiên |
|------------|-------|---------|
| FR1.1 | Đăng nhập/Đăng xuất | Cao |
| FR1.2 | Phân quyền theo Django Groups | Cao |
| FR1.3 | Quản lý profile cá nhân | Trung bình |
| FR1.4 | Đổi mật khẩu | Trung bình |

#### **FR2: Quản lý danh mục mẫu biểu**

| Mã yêu cầu | Mô tả | Ưu tiên |
|------------|-------|---------|
| FR2.1 | Tạo/Sửa/Xóa danh mục (Category) | Cao |
| FR2.2 | Sắp xếp thứ tự hiển thị danh mục | Thấp |
| FR2.3 | Cấu hình nhóm field hiển thị cho danh mục | Trung bình |

#### **FR3: Quản lý mẫu biểu (Template)**

| Mã yêu cầu | Mô tả | Ưu tiên |
|------------|-------|---------|
| FR3.1 | Upload file Word template (.docx) | Cao |
| FR3.2 | Tạo/Sửa/Xóa template | Cao |
| FR3.3 | Gán template vào danh mục | Cao |
| FR3.4 | Gán quyền truy cập theo Groups | Cao |
| FR3.5 | Quản lý biến (Variables) trong template | Cao |
| FR3.6 | Import hàng loạt template (bulk upload) | Thấp |
| FR3.7 | Preview template | Trung bình |

#### **FR4: Quản lý biến (Variables)**

| Mã yêu cầu | Mô tả | Ưu tiên |
|------------|-------|---------|
| FR4.1 | Tạo/Sửa/Xóa biến | Cao |
| FR4.2 | Định nghĩa kiểu dữ liệu (text, date, number) | Cao |
| FR4.3 | Đặt giá trị mặc định cho biến | Trung bình |
| FR4.4 | Import/Export biến từ CSV | Thấp |

#### **FR5: Quản lý khách hàng (Customer)**

| Mã yêu cầu | Mô tả | Ưu tiên |
|------------|-------|---------|
| FR5.1 | Tạo/Sửa/Xóa thông tin khách hàng | Cao |
| FR5.2 | Tìm kiếm khách hàng (theo tên, CMND, SĐT) | Cao |
| FR5.3 | Import từ Excel/CSV | Cao |
| FR5.4 | Import từ TSV (AGRIBANK format) | Cao |
| FR5.5 | Import trực tiếp từ clipboard (paste) | Cao |
| FR5.6 | Validation dữ liệu (CMND, SĐT, ngày sinh) | Cao |
| FR5.7 | Export danh sách khách hàng | Trung bình |

#### **FR6: Tạo tài liệu từ template**

| Mã yêu cầu | Mô tả | Ưu tiên |
|------------|-------|---------|
| FR6.1 | Chọn mẫu biểu từ danh sách | Cao |
| FR6.2 | Điền form thông tin | Cao |
| FR6.3 | Auto-fill từ database khách hàng | Cao |
| FR6.4 | Import từ clipboard AGRIBANK vào form | Cao |
| FR6.5 | Validation trước khi tạo | Cao |
| FR6.6 | Render template với dữ liệu | Cao |
| FR6.7 | Download file Word output | Cao |
| FR6.8 | Hỗ trợ biến tự động (ngày hiện tại, tính tuổi) | Trung bình |

#### **FR7: Cấu hình toàn cục**

| Mã yêu cầu | Mô tả | Ưu tiên |
|------------|-------|---------|
| FR7.1 | Cấu hình thông tin chi nhánh | Cao |
| FR7.2 | Quản lý biến tùy chỉnh chung | Trung bình |
| FR7.3 | Cấu hình thông tin nhân sự (GĐV, KSV, GĐ) | Cao |

### 2.3.2. Yêu cầu phi chức năng (Non-functional Requirements)

#### **NFR1: Hiệu năng (Performance)**

| Mã | Yêu cầu | Chỉ số |
|----|---------|--------|
| NFR1.1 | Thời gian load trang dashboard | < 2 giây |
| NFR1.2 | Thời gian tìm kiếm khách hàng | < 1 giây |
| NFR1.3 | Thời gian tạo 1 file Word | < 5 giây |
| NFR1.4 | Hỗ trợ đồng thời | 10-20 users |

#### **NFR2: Bảo mật (Security)**

| Mã | Yêu cầu | Giải pháp |
|----|---------|-----------|
| NFR2.1 | Xác thực người dùng | Django Authentication |
| NFR2.2 | Phân quyền truy cập | Django Permissions & Groups |
| NFR2.3 | Bảo vệ CSRF | Django CSRF Token |
| NFR2.4 | Mã hóa mật khẩu | PBKDF2 (Django default) |
| NFR2.5 | SQL Injection protection | Django ORM auto-escape |

#### **NFR3: Tính khả dụng (Usability)**

| Mã | Yêu cầu |
|----|---------|
| NFR3.1 | Giao diện trực quan, dễ sử dụng |
| NFR3.2 | Hướng dẫn sử dụng tích hợp (tooltips, help text) |
| NFR3.3 | Thông báo lỗi rõ ràng |
| NFR3.4 | Responsive trên desktop, tablet |

#### **NFR4: Tính tương thích (Compatibility)**

| Mã | Yêu cầu |
|----|---------|
| NFR4.1 | Chạy trên Windows 10/11 |
| NFR4.2 | Hỗ trợ trình duyệt: Chrome, Edge, Firefox (latest) |
| NFR4.3 | File Word output tương thích MS Word 2016+ |

#### **NFR5: Tính bảo trì (Maintainability)**

| Mã | Yêu cầu |
|----|---------|
| NFR5.1 | Code tuân thủ PEP 8 (Python style guide) |
| NFR5.2 | Documentation đầy đủ |
| NFR5.3 | Modular design, dễ mở rộng |

---

# CHƯƠNG 3: THIẾT KẾ HỆ THỐNG

## 3.1. Lựa chọn công nghệ

### 3.1.1. Technology Stack tổng quan

| Tầng | Công nghệ | Phiên bản | Lý do chọn |
|------|-----------|-----------|------------|
| **Backend Framework** | Django | 5.2.7 | Admin sẵn có, ORM mạnh, bảo mật tốt |
| **Programming Language** | Python | 3.11+ | Dễ học, thư viện phong phú |
| **WSGI Server** | Waitress | 3.0.1 | Cross-platform, dễ deploy trên Windows |
| **Database** | SQLite | 3.x | Nhẹ, không cần server riêng, phù hợp LAN |
| **Static Files** | WhiteNoise | 6.8.2 | Serve static files hiệu quả |
| **Template Engine** | Jinja2 | 3.x | Mạnh mẽ, cú pháp linh hoạt |
| **Word Processing** | python-docx | 1.1.0+ | Tạo/chỉnh sửa file .docx |
| **Frontend Framework** | Bootstrap | 5.3.0 | Responsive, components đẹp |
| **Icons** | Bootstrap Icons | 1.11.x | Icon set đầy đủ, nhất quán |
| **Font** | Roboto | - | Font hiện đại, dễ đọc |

### 3.1.2. Lý do chọn Django

**So với Flask:**
- Django có admin panel sẵn → Tiết kiệm thời gian phát triển
- ORM mạnh mẽ → Dễ quản lý database
- Authentication & Permission tích hợp → Bảo mật tốt

**So với FastAPI:**
- FastAPI tối ưu cho API, không có admin UI
- Django phù hợp cho web app monolithic

**So với ASP.NET:**
- Python dễ học hơn C#
- Thư viện python-docx xử lý Word tốt hơn

### 3.1.3. Lý do chọn SQLite

**Ưu điểm:**
- Không cần cài database server riêng
- File-based: dễ backup (copy file .db)
- Hiệu năng tốt cho mạng LAN nội bộ (< 50 users)
- Tích hợp sẵn trong Python

**Hạn chế:**
- Không phù hợp cho ứng dụng lớn, nhiều người dùng đồng thời
- Nếu mở rộng sau này, dễ dàng migrate sang PostgreSQL/MySQL

### 3.1.4. Lý do chọn Waitress

**So với Gunicorn:**
- Gunicorn không chạy trên Windows
- Waitress cross-platform, dễ triển khai

**So với uWSGI:**
- uWSGI cấu hình phức tạp
- Waitress đơn giản, phù hợp mạng nội bộ

---

## 3.2. Thiết kế kiến trúc hệ thống

### 3.2.1. Kiến trúc tổng quan (Architecture Overview)

```
┌──────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                           │
│         Chrome / Edge / Firefox                               │
└──────────────────────────────────────────────────────────────┘
                           ↕ HTTPS/HTTP
┌──────────────────────────────────────────────────────────────┐
│                  WAITRESS WSGI SERVER                         │
│                   (Port 8000)                                 │
└──────────────────────────────────────────────────────────────┘
                           ↕
┌──────────────────────────────────────────────────────────────┐
│                   DJANGO APPLICATION                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PRESENTATION LAYER (Views + Templates)              │   │
│  │  ├─ Dashboard                                        │   │
│  │  ├─ Customer Management                              │   │
│  │  ├─ Template Management                              │   │
│  │  └─ Document Generation                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↕                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  BUSINESS LOGIC LAYER (Views + Services)             │   │
│  │  ├─ Authentication & Authorization                   │   │
│  │  ├─ Validation & Processing                          │   │
│  │  ├─ Template Rendering (Jinja2)                      │   │
│  │  └─ Word Document Generation (python-docx)           │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↕                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  DATA ACCESS LAYER (Django ORM)                      │   │
│  │  ├─ Models (Customer, Template, Variable, etc.)      │   │
│  │  └─ Database Operations (CRUD)                       │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                           ↕
┌──────────────────────────────────────────────────────────────┐
│              DATABASE (SQLite)                                │
│  ├─ auth_user, auth_group                                    │
│  ├─ templates_app_customer                                   │
│  ├─ templates_app_template                                   │
│  ├─ templates_app_variable                                   │
│  └─ templates_app_globalconfig                               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│              FILE STORAGE                                     │
│  ├─ media/templates/docx/  (Template files)                  │
│  ├─ staticfiles/           (CSS, JS, Bootstrap)              │
│  └─ media/generated/       (Generated Word files)            │
└──────────────────────────────────────────────────────────────┘
```

### 3.2.2. Mô hình MVT (Model-View-Template)

```
[HTTP Request]
      ↓
[urls.py] → Routing
      ↓
[views.py] → Business Logic
      ↓         ↓
[models.py]  [templates/]
  (Database)  (HTML + Jinja2)
      ↓         ↓
[HTTP Response] ← Rendered HTML
```

**Luồng xử lý tạo tài liệu:**

1. User chọn template và điền form
2. Form data gửi đến View (views.py)
3. View lấy dữ liệu từ Model (models.py)
4. View render template Word với Jinja2
5. python-docx tạo file .docx
6. File trả về cho user download

---

## 3.3. Thiết kế chức năng (Sử dụng UML)

### 3.3.1. Use Case Diagram - Tổng quan

```
                  ┌─────────────────────────────┐
                  │   HỆ THỐNG MẪU BIỂU         │
                  │                             │
 ┌────────┐       │  ┌──────────────────────┐  │
 │  Admin │───────┼─→│ Quản lý User/Group   │  │
 └────────┘       │  └──────────────────────┘  │
                  │  ┌──────────────────────┐  │
                  │  │ Quản lý Template     │  │
                  │  └──────────────────────┘  │
                  │  ┌──────────────────────┐  │
                  │  │ Quản lý Variable     │  │
                  │  └──────────────────────┘  │
                  │  ┌──────────────────────┐  │
 ┌────────────┐   │  │ Quản lý Khách hàng   │◄─┼───┐
 │ Giao dịch  │───┼─→│                      │  │   │
 │    viên    │   │  └──────────────────────┘  │   │
 └────────────┘   │  ┌──────────────────────┐  │   │
       │          │  │ Tạo mẫu biểu         │  │   │
       └──────────┼─→│                      │  │   │
                  │  └──────────────────────┘  │   │
                  │  ┌──────────────────────┐  │   │
                  │  │ Tìm kiếm KH          │  │   │
                  │  └──────────────────────┘  │   │
                  │                             │   │
 ┌────────────┐   │  ┌──────────────────────┐  │   │
 │ Kiểm soát  │───┼─→│ Xem báo cáo          │  │   │
 │    viên    │   │  └──────────────────────┘  │   │
 └────────────┘   │                             │   │
                  └─────────────────────────────┘   │
                                                    │
                  ┌─────────────────────────────┐   │
                  │  HỆ THỐNG AGRIBANK          │   │
                  │  (External System)          │   │
                  │  ┌──────────────────────┐   │   │
                  │  │ Export dữ liệu TSV   │───┼───┘
                  │  └──────────────────────┘   │
                  └─────────────────────────────┘
```

### 3.3.2. Use Case chi tiết - Tạo mẫu biểu

**Use Case: Tạo mẫu biểu từ template**

| Thuộc tính | Mô tả |
|------------|-------|
| **Use Case ID** | UC-06 |
| **Tên** | Tạo mẫu biểu từ template |
| **Actor** | Giao dịch viên |
| **Tiền điều kiện** | User đã đăng nhập, có quyền truy cập template |
| **Luồng chính** | 1. GDV chọn danh mục mẫu biểu<br>2. Hệ thống hiển thị danh sách template trong danh mục<br>3. GDV chọn template<br>4. Hệ thống hiển thị form với các trường cần điền<br>5. GDV điền thông tin hoặc chọn khách hàng có sẵn<br>6. Hệ thống auto-fill form từ DB<br>7. GDV kiểm tra và click "Tạo file"<br>8. Hệ thống validate dữ liệu<br>9. Hệ thống render template với Jinja2<br>10. Hệ thống tạo file Word bằng python-docx<br>11. Hệ thống trả về file để download<br>12. GDV download và in file |
| **Luồng thay thế** | **3a.** Template yêu cầu quyền cao hơn:<br>&nbsp;&nbsp;- Hệ thống hiển thị "Access Denied"<br>**8a.** Dữ liệu không hợp lệ:<br>&nbsp;&nbsp;- Hệ thống hiển thị lỗi, yêu cầu sửa |
| **Hậu điều kiện** | File Word được tạo thành công |

### 3.3.3. Sequence Diagram - Tạo mẫu biểu

```
User      Dashboard    View         Model        Jinja2    python-docx   File
 │            │          │            │            │            │         │
 │ Select     │          │            │            │            │         │
 │ template   │          │            │            │            │         │
 ├───────────>│          │            │            │            │         │
 │            │          │            │            │            │         │
 │            │ Show form│            │            │            │         │
 │            │<─────────┤            │            │            │         │
 │            │          │            │            │            │         │
 │ Fill &     │          │            │            │            │         │
 │ Submit     │          │            │            │            │         │
 ├───────────>│          │            │            │            │         │
 │            │          │            │            │            │         │
 │            │ POST data│            │            │            │         │
 │            ├─────────>│            │            │            │         │
 │            │          │            │            │            │         │
 │            │          │ Get        │            │            │         │
 │            │          │ customer   │            │            │         │
 │            │          ├───────────>│            │            │         │
 │            │          │            │            │            │         │
 │            │          │ Customer   │            │            │         │
 │            │          │ data       │            │            │         │
 │            │          │<───────────┤            │            │         │
 │            │          │            │            │            │         │
 │            │          │ Validate   │            │            │         │
 │            │          ├────────┐   │            │            │         │
 │            │          │        │   │            │            │         │
 │            │          │<───────┘   │            │            │         │
 │            │          │            │            │            │         │
 │            │          │ Load       │            │            │         │
 │            │          │ template   │            │            │         │
 │            │          ├───────────────────────>│            │         │
 │            │          │            │            │            │         │
 │            │          │ Render     │            │            │         │
 │            │          │ with data  │            │            │         │
 │            │          ├───────────────────────>│            │         │
 │            │          │            │       Rendered text     │         │
 │            │          │            │            │            │         │
 │            │          │ Create .docx           │            │         │
 │            │          ├────────────────────────────────────>│         │
 │            │          │            │            │            │         │
 │            │          │ Save file  │            │            │         │
 │            │          ├────────────────────────────────────────────>  │
 │            │          │            │            │            │         │
 │            │ Download │            │            │            │         │
 │            │ link     │            │            │            │         │
 │<───────────┤          │            │            │            │         │
 │            │          │            │            │            │         │
 │ Download   │          │            │            │            │         │
 │ file       │          │            │            │            │         │
 ├──────────────────────────────────────────────────────────────────────>│
```

### 3.3.4. Activity Diagram - Import khách hàng từ AGRIBANK

```
             [Start]
                │
                ↓
      ┌──────────────────┐
      │ User click        │
      │ "Import AGRIBANK" │
      └──────────────────┘
                │
                ↓
      ┌──────────────────┐
      │ Show modal with   │
      │ 2 tabs:           │
      │ 1. Paste clipboard│
      │ 2. Upload file    │
      └──────────────────┘
                │
          ┌─────┴─────┐
          ↓           ↓
    [Clipboard]   [File Upload]
          │           │
          └─────┬─────┘
                ↓
      ┌──────────────────┐
      │ Parse TSV data    │
      │ (tab-separated)   │
      └──────────────────┘
                │
                ↓
      ┌──────────────────┐
      │ Validate each row │
      │ - Check CMND      │
      │ - Check phone     │
      │ - Check dates     │
      └──────────────────┘
                │
          ┌─────┴─────┐
    Valid?            Invalid?
          │                │
          ↓                ↓
    ┌─────────┐      ┌─────────┐
    │ Import  │      │ Add to  │
    │ to DB   │      │ error   │
    │         │      │ list    │
    └─────────┘      └─────────┘
          │                │
          └─────┬──────────┘
                ↓
      ┌──────────────────┐
      │ Show result:      │
      │ - Success: X      │
      │ - Failed: Y       │
      │ - Error report    │
      └──────────────────┘
                │
                ↓
              [End]
```

---

## 3.4. Thiết kế cơ sở dữ liệu (CSDL)

### 3.4.1. ERD (Entity-Relationship Diagram)

```
┌──────────────────┐         ┌──────────────────┐
│   auth_user      │         │   auth_group     │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ username         │ ──────┐ │ name             │
│ password         │       │ └──────────────────┘
│ email            │       │
│ is_staff         │       │  Many-to-Many
│ is_active        │       │
└──────────────────┘       │
                           │
┌──────────────────────────┴─────────────────────────┐
│                                                     │
│                                                     │
┌──────────────────┐         ┌──────────────────┐    │
│   Category       │         │   Template       │    │
├──────────────────┤         ├──────────────────┤    │
│ id (PK)          │──────┐  │ id (PK)          │    │
│ name             │    1 │  │ name             │    │
│ description      │      │  │ description      │    │
│ order            │      │  │ file             │    │
│ visible_fields   │      └─→│ category_id (FK) │    │
└──────────────────┘     N   │ order            │    │
                              │ is_active        │    │
                              └──────────────────┘    │
                                     │                 │
                                     │ Many-to-Many    │
                                     ↓                 │
                              ┌──────────────────┐    │
                              │   Variable       │    │
                              ├──────────────────┤    │
                              │ id (PK)          │    │
                              │ name             │    │
                              │ label            │    │
                              │ field_type       │    │
                              │ help_text        │    │
                              │ required         │    │
                              │ default_value    │    │
                              └──────────────────┘    │
                                                      │
┌──────────────────────────────────────────────────┐ │
│            Customer                               │ │
├──────────────────────────────────────────────────┤ │
│ id (PK)                                           │ │
│ ma_khach_hang                                     │ │
│ cif                                               │ │
│ ho_ten                                            │ │
│ ho_ten_tieng_anh                                  │ │
│ ngay_sinh                                         │ │
│ gioi_tinh                                         │ │
│ dan_toc                                           │ │
│ so_cmnd                                           │ │
│ ngay_cap_cmnd                                     │ │
│ ngay_het_han_cmnd                                 │ │
│ noi_cap_cmnd                                      │ │
│ dia_chi                                           │ │
│ ho_khau                                           │ │
│ so_dien_thoai                                     │ │
│ email                                             │ │
│ nghe_nghiep                                       │ │
│ so_tai_khoan                                      │ │
│ loai_the                                          │ │
│ so_the_atm                                        │ │
│ ... (30+ fields)                                  │ │
│ created_by (FK) ──────────────────────────────────┘─┘
└──────────────────────────────────────────────────┘

┌──────────────────┐
│  GlobalConfig    │  (Singleton - chỉ 1 record)
├──────────────────┤
│ id (PK) = 1      │
│ ten_chi_nhanh    │
│ ten_cn_hoa       │
│ ma_chi_nhanh     │
│ mst              │
│ dia_chi          │
│ dien_thoai       │
│ so_fax           │
│ dia_danh         │
│ giao_dich_vien   │
│ kiem_soat_vien   │
│ giam_doc         │
│ custom_variables │  (JSON field)
└──────────────────┘
```

### 3.4.2. Database Schema chi tiết

#### Bảng: **auth_user** (Django built-in)

| Tên trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|------------|--------------|-----------|-------|
| id | INTEGER | PK, AUTO_INCREMENT | ID người dùng |
| username | VARCHAR(150) | UNIQUE, NOT NULL | Tên đăng nhập |
| password | VARCHAR(128) | NOT NULL | Mật khẩu (đã hash) |
| email | VARCHAR(254) | | Email |
| first_name | VARCHAR(150) | | Tên |
| last_name | VARCHAR(150) | | Họ |
| is_staff | BOOLEAN | DEFAULT FALSE | Quyền truy cập admin |
| is_active | BOOLEAN | DEFAULT TRUE | Tài khoản active |
| is_superuser | BOOLEAN | DEFAULT FALSE | Superuser |
| date_joined | DATETIME | NOT NULL | Ngày tạo |

#### Bảng: **templates_app_customer**

| Tên trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|------------|--------------|-----------|-------|
| id | INTEGER | PK, AUTO_INCREMENT | ID khách hàng |
| ma_khach_hang | VARCHAR(50) | INDEX | Mã khách hàng (CIF) |
| cif | VARCHAR(20) | UNIQUE, NULL | Mã CIF |
| ho_ten | VARCHAR(200) | NOT NULL, INDEX | Họ tên |
| ho_ten_tieng_anh | VARCHAR(200) | | Họ tên tiếng Anh |
| ngay_sinh | DATE | NULL | Ngày sinh |
| gioi_tinh | VARCHAR(10) | DEFAULT 'Nam' | Giới tính |
| dan_toc | VARCHAR(50) | DEFAULT 'Kinh' | Dân tộc |
| so_cmnd | VARCHAR(20) | UNIQUE, NOT NULL | CMND/CCCD |
| ngay_cap_cmnd | DATE | NULL | Ngày cấp |
| ngay_het_han_cmnd | DATE | NULL | Ngày hết hạn |
| noi_cap_cmnd | VARCHAR(50) | | Nơi cấp |
| ma_noi_cap_cmnd | VARCHAR(10) | | Mã nơi cấp |
| so_ho_chieu | VARCHAR(20) | | Số hộ chiếu |
| dia_chi | TEXT | | Địa chỉ thường trú |
| ho_khau | TEXT | | Hộ khẩu |
| so_dien_thoai | VARCHAR(20) | INDEX | Số điện thoại |
| email | VARCHAR(254) | | Email |
| ma_tinh | VARCHAR(10) | | Mã tỉnh |
| ma_quan_huyen | VARCHAR(10) | | Mã quận/huyện |
| ma_phuong_xa | VARCHAR(10) | | Mã phường/xã |
| quoc_tich | VARCHAR(10) | DEFAULT 'VN' | Quốc tịch |
| ma_so_thue | VARCHAR(20) | | Mã số thuế |
| nghe_nghiep | VARCHAR(200) | | Nghề nghiệp |
| noi_lam_viec | VARCHAR(200) | | Nơi làm việc |
| so_tai_khoan | VARCHAR(30) | | Số tài khoản |
| loai_tai_khoan | VARCHAR(100) | | Loại tài khoản |
| loai_tien_te | VARCHAR(10) | DEFAULT 'VND' | Loại tiền tệ |
| loai_the | VARCHAR(50) | | Loại thẻ |
| hang_the | VARCHAR(20) | | Hạng thẻ |
| so_the_atm | VARCHAR(20) | | Số thẻ ATM |
| thoi_han_the | VARCHAR(50) | | Thời hạn thẻ |
| ngay_tra_the | DATE | NULL | Ngày trả thẻ |
| loai_phi | VARCHAR(100) | | Loại phí |
| ... | ... | ... | (Các trường dịch vụ) |
| created_at | DATETIME | AUTO_NOW_ADD | Ngày tạo |
| updated_at | DATETIME | AUTO_NOW | Ngày cập nhật |
| created_by_id | INTEGER | FK → auth_user | Người tạo |

#### Bảng: **templates_app_template**

| Tên trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|------------|--------------|-----------|-------|
| id | INTEGER | PK, AUTO_INCREMENT | ID template |
| name | VARCHAR(200) | NOT NULL | Tên mẫu biểu |
| description | TEXT | | Mô tả |
| file | FileField | NOT NULL | File .docx |
| category_id | INTEGER | FK → Category | Danh mục |
| order | INTEGER | DEFAULT 0 | Thứ tự hiển thị |
| is_active | BOOLEAN | DEFAULT TRUE | Kích hoạt |
| created_at | DATETIME | AUTO_NOW_ADD | Ngày tạo |
| updated_at | DATETIME | AUTO_NOW | Ngày cập nhật |

#### Bảng: **templates_app_globalconfig** (Singleton)

| Tên trường | Kiểu dữ liệu | Ràng buộc | Mô tả |
|------------|--------------|-----------|-------|
| id | INTEGER | PK = 1 | ID cố định = 1 |
| ten_chi_nhanh | VARCHAR(200) | | Tên chi nhánh |
| ten_chi_nhanh_hoa | VARCHAR(200) | | Tên IN HOA |
| ma_chi_nhanh | VARCHAR(20) | | Mã chi nhánh |
| mst | VARCHAR(50) | | Mã số thuế |
| dia_chi_chi_nhanh | TEXT | | Địa chỉ |
| dien_thoai_chi_nhanh | VARCHAR(50) | | Điện thoại |
| so_fax | VARCHAR(50) | | Số Fax |
| dia_danh | VARCHAR(200) | | Địa danh |
| giao_dich_vien | VARCHAR(200) | | Giao dịch viên |
| kiem_soat_vien | VARCHAR(200) | | Kiểm soát viên |
| giam_doc | VARCHAR(200) | | Giám đốc |
| custom_variables | JSON | | Biến tùy chỉnh |
| updated_at | DATETIME | AUTO_NOW | Ngày cập nhật |

### 3.4.3. Indexes và Optimization

**Indexes đã tạo:**
```sql
-- Customer table
CREATE INDEX idx_customer_ho_ten ON templates_app_customer(ho_ten);
CREATE INDEX idx_customer_so_cmnd ON templates_app_customer(so_cmnd);
CREATE INDEX idx_customer_so_dien_thoai ON templates_app_customer(so_dien_thoai);
CREATE INDEX idx_customer_ma_khach_hang ON templates_app_customer(ma_khach_hang);

-- Composite index
CREATE INDEX idx_customer_search ON templates_app_customer(ho_ten, so_cmnd);
```

**Query optimization:**
- Sử dụng `select_related()` và `prefetch_related()` cho foreign key
- Pagination cho danh sách lớn
- Caching cho GlobalConfig (singleton)

---

## 3.5. Thiết kế giao diện (UI/UX)

### 3.5.1. Nguyên tắc thiết kế

**Brand Identity:**
- Màu chủ đạo: **Xanh lá Agribank (#00923F)**
- Font chữ: **Roboto** (dễ đọc, hiện đại)
- Logo: Agribank logo ở header

**UX Principles:**
- **Simplicity**: Giao diện đơn giản, dễ sử dụng
- **Consistency**: Đồng nhất về layout, button style
- **Feedback**: Hiển thị thông báo rõ ràng (success, error)
- **Efficiency**: Giảm số lần click, tối ưu workflow

### 3.5.2. Layout chung

```
┌────────────────────────────────────────────────────┐
│  [LOGO]  HỆ THỐNG MẪU BIỂU        [User] [Logout]  │  ← Header
├────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Dashboard │  │Khách hàng│  │Mẫu biểu  │  ...    │  ← Navigation
│  └──────────┘  └──────────┘  └──────────┘         │
├────────────────────────────────────────────────────┤
│                                                     │
│                 [CONTENT AREA]                      │  ← Main Content
│                                                     │
│                                                     │
├────────────────────────────────────────────────────┤
│  © 2025 Agribank - Chi nhánh Giá Rai Bạc Liêu      │  ← Footer
└────────────────────────────────────────────────────┘
```

### 3.5.3. Wireframe - Dashboard

```
┌────────────────────────────────────────────────────┐
│  DASHBOARD - CHỌN MẪU BIỂU                         │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌─ Chọn khách hàng ───────────────────────────┐   │
│  │ [Tìm kiếm...              ] [Tìm] [Thêm mới]│   │
│  │                                              │   │
│  │ Kết quả:                                     │   │
│  │ ☑ Nguyễn Văn A - 001***890 - 090123****     │   │
│  │ ☐ Trần Thị B   - 002***891 - 091234****     │   │
│  │                                              │   │
│  │ [Hoặc] [Paste từ AGRIBANK]                  │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  ┌─ Chọn mẫu biểu ──────────────────────────────┐   │
│  │                                              │   │
│  │ ┌──────────────┐  ┌──────────────┐          │   │
│  │ │ PHÁT HÀNH THẺ│  │  TRA SOÁT    │          │   │
│  │ ├──────────────┤  ├──────────────┤          │   │
│  │ │• Thẻ ATM     │  │• Khiếu nại GD│          │   │
│  │ │• Thẻ Visa    │  │• Tra soát    │          │   │
│  │ │• Thẻ Master  │  └──────────────┘          │   │
│  │ └──────────────┘                             │   │
│  └──────────────────────────────────────────────┘   │
│                                                     │
│  [← Quay lại]                    [Tiếp tục →]      │
└────────────────────────────────────────────────────┘
```

### 3.5.4. Wireframe - Form tạo mẫu biểu

```
┌────────────────────────────────────────────────────┐
│  TẠO MẪU BIỂU: Giấy đề nghị phát hành thẻ ATM      │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌─ Thông tin cá nhân ───────────────────────┐     │
│  │ Họ tên:         [Nguyễn Văn A            ]│     │
│  │ CMND:           [001234567890            ]│     │
│  │ Ngày sinh:      [01/01/1990              ]│     │
│  │ Giới tính:      (•) Nam  ( ) Nữ          │     │
│  │ Địa chỉ:        [123 Đường ABC, Bạc Liêu ]│     │
│  │ SĐT:            [0901234567              ]│     │
│  └─────────────────────────────────────────────┘     │
│                                                     │
│  ┌─ Thông tin thẻ ───────────────────────────┐     │
│  │ Loại thẻ:       [▼ Thẻ ATM nội địa      ]│     │
│  │ Hạng thẻ:       [▼ Hạng chuẩn           ]│     │
│  │ Loại phí:       [▼ Phí phát hành lần đầu]│     │
│  └─────────────────────────────────────────────┘     │
│                                                     │
│  ┌─ Dịch vụ đăng ký ─────────────────────────┐     │
│  │ ☑ SMS Banking                            │     │
│  │ ☑ E-Mobile Banking                       │     │
│  │ ☐ Internet Banking                       │     │
│  └─────────────────────────────────────────────┘     │
│                                                     │
│  [← Quay lại]     [Preview]      [Tạo file →]     │
└────────────────────────────────────────────────────┘
```

### 3.5.5. Wireframe - Quản lý khách hàng

```
┌────────────────────────────────────────────────────┐
│  QUẢN LÝ KHÁCH HÀNG                                 │
├────────────────────────────────────────────────────┤
│  [Tìm kiếm...]  [Thêm mới] [Import AGRIBANK]       │
├────────────────────────────────────────────────────┤
│  STT │ Họ tên      │ CMND        │ SĐT        │ ⚙  │
│  ────┼─────────────┼─────────────┼────────────┼──  │
│   1  │ Nguyễn Văn A│ 001***890   │ 090***567  │ ✏🗑│
│   2  │ Trần Thị B  │ 002***891   │ 091***678  │ ✏🗑│
│   3  │ Lê Văn C    │ 003***892   │ 092***789  │ ✏🗑│
│   ...│             │             │            │    │
├────────────────────────────────────────────────────┤
│  [←] 1 2 3 ... 10 [→]           Hiển thị 50/trang  │
└────────────────────────────────────────────────────┘
```

### 3.5.6. Color Palette

| Màu | Hex Code | Sử dụng |
|-----|----------|---------|
| Agribank Green | #00923F | Primary color, buttons, headers |
| Dark Green | #006B2E | Hover states |
| Light Green | #E8F5E9 | Backgrounds, highlights |
| White | #FFFFFF | Main background |
| Gray | #F5F5F5 | Borders, disabled |
| Dark Gray | #333333 | Text |
| Red | #D32F2F | Error messages |
| Blue | #1976D2 | Info messages |
| Yellow | #FFA000 | Warning messages |

### 3.5.7. Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| H1 | Roboto | 32px | Bold |
| H2 | Roboto | 24px | Bold |
| H3 | Roboto | 20px | Medium |
| Body | Roboto | 16px | Regular |
| Button | Roboto | 16px | Medium |
| Small | Roboto | 14px | Regular |

---

**Kết thúc Chương 3**

