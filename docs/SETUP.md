# HƯỚNG DẪN CÀI ĐẶT MAUBIEU7202

## Mục lục
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt ban đầu](#cài-đặt-ban-đầu)
- [Cấu hình](#cấu-hình)
- [Khởi chạy chương trình](#khởi-chạy-chương-trình)
- [Truy cập ứng dụng](#truy-cập-ứng-dụng)
- [Khắc phục sự cố](#khắc-phục-sự-cố)

---

## Yêu cầu hệ thống

### Phần mềm cần thiết
- **Python**: 3.10 trở lên (khuyến nghị 3.11+)
- **Hệ điều hành**: Windows 10/11, Linux, macOS

### Kiểm tra phiên bản Python
```bash
python --version
# hoặc
python3 --version
```

---

## Cài đặt ban đầu

### Bước 1: Tải mã nguồn
```bash
# Clone từ repository (nếu dùng Git)
git clone <repository-url>
cd MauBieu7202

# Hoặc giải nén file zip vào thư mục
```

### Bước 2: Tạo môi trường ảo (Virtual Environment)

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình biến môi trường
```bash
# Sao chép file mẫu
cp .env.example .env

# Chỉnh sửa file .env theo nhu cầu (xem phần Cấu hình bên dưới)
```

### Bước 5: Khởi tạo cơ sở dữ liệu
```bash
python manage.py migrate
```

### Bước 6: Tạo tài khoản quản trị
```bash
python manage.py createsuperuser
```
Nhập thông tin:
- Username: admin (hoặc tên bạn muốn)
- Email: (có thể bỏ trống)
- Password: Mật khẩu mạnh

### Bước 7: Thu thập file tĩnh
```bash
python manage.py collectstatic --noinput
```

---

## Cấu hình

### File `.env`

```env
# Khóa bảo mật (BẮT BUỘC phải thay đổi trong production)
SECRET_KEY=your-very-secure-secret-key-here

# Chế độ debug (True cho phát triển, False cho production)
DEBUG=False

# Các host được phép truy cập
# Thêm IP của server và tên domain nếu có
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.100

# Cơ sở dữ liệu (mặc định SQLite)
# DATABASE_URL=sqlite:///db.sqlite3
```

### Tạo SECRET_KEY mới
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Cấu hình ALLOWED_HOSTS
Thêm tất cả IP và hostname có thể truy cập:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,10.135.7.108
```

---

## Khởi chạy chương trình

### Chế độ Development (Phát triển)
```bash
python manage.py runserver 0.0.0.0:8888
```

### Chế độ Production (Triển khai thực tế)
```bash
python run_waitress.py
```

### Windows - Sử dụng script có sẵn

**Lần đầu tiên:**
```cmd
setup.bat
```

**Các lần sau:**
```cmd
start.bat
```

---

## Truy cập ứng dụng

### Từ máy chủ
- **Ứng dụng chính**: http://localhost:8888
- **Trang quản trị**: http://localhost:8888/admin

### Từ máy khác trong mạng nội bộ Agribank
- **Ứng dụng chính**: http://10.135.7.108:8888
- **Trang quản trị**: http://10.135.7.108:8888/admin

### Kiểm tra IP máy chủ

**Windows:**
```cmd
ipconfig
```

**Linux:**
```bash
ip addr
# hoặc
hostname -I
```

---

## Thiết lập ban đầu sau khi cài đặt

### 1. Cấu hình thông tin chi nhánh
1. Đăng nhập vào hệ thống
2. Vào menu **Cấu hình** > **Cấu hình chi nhánh**
3. Điền các thông tin:
   - Tên chi nhánh
   - Mã chi nhánh
   - Tên giao dịch viên mặc định
   - Các biến tùy chỉnh khác

### 2. Tạo danh mục và mẫu biểu
1. Đăng nhập trang quản trị: http://localhost:8888/admin
2. Thêm **Categories** (Danh mục)
3. Thêm **Templates** (Mẫu biểu Word)
4. Thêm **Variables** (Biến) nếu cần

### 3. Nhập danh sách nhân viên
1. Vào menu **Quản lý nhân viên**
2. Sử dụng chức năng **Import từ Excel**
3. Hoặc thêm thủ công từng nhân viên

### 4. Phân quyền người dùng
1. Trang quản trị > **Groups**
2. Tạo nhóm và gán quyền
3. Thêm người dùng vào nhóm tương ứng

---

## Khắc phục sự cố

### Lỗi "No module named..."
```bash
pip install -r requirements.txt
```

### Lỗi "Address already in use"
```bash
# Tìm và dừng tiến trình đang dùng port 8888
# Windows:
netstat -ano | findstr :8888
taskkill /PID <PID> /F

# Linux:
lsof -i :8888
kill <PID>
```

### Lỗi "DisallowedHost"
Thêm host vào file `.env`:
```env
ALLOWED_HOSTS=localhost,127.0.0.1,your-ip-address
```

### Lỗi static files không hiển thị
```bash
python manage.py collectstatic --noinput
```

### Reset mật khẩu admin
```bash
python manage.py changepassword admin
```

### Xóa và tạo lại database
```bash
# Xóa file database cũ
rm db.sqlite3

# Chạy migrations
python manage.py migrate

# Tạo lại superuser
python manage.py createsuperuser
```

---

## Cấu trúc thư mục quan trọng

```
MauBieu7202/
├── manage.py           # Django CLI
├── run_waitress.py     # Production server
├── requirements.txt    # Dependencies
├── .env               # Cấu hình (cần tạo)
├── db.sqlite3         # Database (tự động tạo)
├── wordgen/           # Django settings
├── templates_app/     # Ứng dụng chính
├── media/             # File upload
├── staticfiles/       # Static files (collectstatic)
└── docs/              # Tài liệu
```

---

## Liên hệ hỗ trợ

Nếu gặp vấn đề khi cài đặt, vui lòng liên hệ bộ phận IT hoặc tạo issue trên repository.
