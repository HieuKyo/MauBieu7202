# Quick Start Guide - WordGen Application

## Khởi động nhanh (3 bước)

### Bước 1: Cài đặt lần đầu

Chạy **MỘT** trong các script sau:

#### Option A: Setup đầy đủ (Khuyến nghị)
```cmd
setup_first_time.bat
```
Script này sẽ:
- Cài đặt dependencies
- Tải Bootstrap CSS/JS
- Setup database
- Tạo admin user
- Collect static files

#### Option B: Setup nhanh (Tối thiểu)
```cmd
quick_setup.bat
```
Script này chỉ làm những việc cần thiết nhất:
- Cài đặt dependencies
- Setup database
- Collect static files

### Bước 2: Tải Bootstrap (Nếu chưa có)

**Chỉ cần nếu bạn chọn Option B ở trên hoặc setup_first_time.bat thất bại**

```cmd
download_bootstrap_files.bat
python manage.py collectstatic --noinput
```

Hoặc tải thủ công theo hướng dẫn trong `STATIC_FILES_SETUP.md`

### Bước 3: Chạy server

```cmd
start_server.bat
```

Mở trình duyệt: **http://localhost:8000**

---

## Giải quyết lỗi thường gặp

### ❌ Lỗi: "CSS không load" (trang web không có màu sắc)

**Triệu chứng:**
```
Not Found: /static/vendor/bootstrap/css/bootstrap.min.css
```

**Giải pháp:**
```cmd
# Cách 1: Tự động
download_bootstrap_files.bat
python manage.py collectstatic --noinput

# Cách 2: Thủ công (nếu không có internet)
# Xem hướng dẫn trong STATIC_FILES_SETUP.md
```

### ❌ Lỗi: "No module named 'django'"

**Giải pháp:**
```cmd
pip install -r requirements.txt
```

### ❌ Lỗi: "Port 8000 is already in use"

**Giải pháp 1:** Tắt ứng dụng đang dùng port 8000
```cmd
netstat -ano | findstr :8000
taskkill /PID [số-PID] /F
```

**Giải pháp 2:** Đổi port trong `run_waitress.py`

### ❌ Lỗi: "python is not recognized"

**Giải pháp:**
- Cài đặt Python: https://www.python.org/downloads/
- **NHỚ CHỌN** "Add Python to PATH" khi cài đặt

---

## Các lệnh hữu ích

### Tạo admin user
```cmd
python manage.py createsuperuser
```

### Chạy migrations
```cmd
python manage.py migrate
```

### Collect static files (sau khi thêm/sửa CSS/JS)
```cmd
python manage.py collectstatic --noinput
```

### Xem tất cả static files
```cmd
python manage.py findstatic --verbosity 2 vendor/bootstrap/css/bootstrap.min.css
```

### Khởi động server development mode
```cmd
python manage.py runserver 0.0.0.0:8000
```

### Khởi động server production mode (waitress)
```cmd
python run_waitress.py
```

---

## Cấu trúc thư mục quan trọng

```
MauBieu7202/
├── start_server.bat           # Chạy server (cách đơn giản nhất)
├── setup_first_time.bat       # Setup đầy đủ lần đầu
├── quick_setup.bat            # Setup nhanh tối thiểu
├── download_bootstrap_files.bat  # Tải Bootstrap
├── run_waitress.py            # Python script chạy server
├── manage.py                  # Django management
├── requirements.txt           # Dependencies
├── templates_app/
│   └── static/               # Static files (CSS, JS, images)
│       ├── css/
│       │   └── agribank-theme.css
│       ├── images/
│       │   └── agribank_logo.png
│       └── vendor/           # Bootstrap files
│           ├── bootstrap/
│           │   ├── css/bootstrap.min.css
│           │   └── js/bootstrap.bundle.min.js
│           └── bootstrap-icons/
│               ├── css/bootstrap-icons.min.css
│               └── fonts/
├── staticfiles/              # Collected static (tự động tạo)
└── db.sqlite3               # Database (tự động tạo)
```

---

## URLs quan trọng

Sau khi chạy server thành công:

- **Trang chủ**: http://localhost:8000
- **Admin panel**: http://localhost:8000/admin
- **Dashboard**: http://localhost:8000/dashboard
- **Từ máy khác**: http://[IP-máy-chủ]:8000

Tìm IP máy chủ:
```cmd
ipconfig
```
Tìm "IPv4 Address"

---

## Tài liệu chi tiết

- **WINDOWS_SETUP.md** - Hướng dẫn chi tiết cho Windows
- **STATIC_FILES_SETUP.md** - Hướng dẫn xử lý static files
- **OFFLINE_SETUP.md** - Triển khai offline
- **README.md** - Tổng quan ứng dụng

---

## Luồng làm việc đề xuất

### Lần đầu tiên setup:
1. `setup_first_time.bat` (hoặc `quick_setup.bat`)
2. `start_server.bat`
3. Truy cập http://localhost:8000

### Mỗi khi chạy:
1. `start_server.bat`
2. Truy cập http://localhost:8000

### Khi cập nhật code:
1. `git pull`
2. `pip install -r requirements.txt` (nếu có thay đổi)
3. `python manage.py migrate` (nếu có thay đổi database)
4. `python manage.py collectstatic --noinput` (nếu có thay đổi static files)
5. `start_server.bat`

---

## Hỗ trợ

Nếu gặp vấn đề:

1. Kiểm tra Python version: `python --version` (cần >= 3.7)
2. Kiểm tra Django: `python -c "import django; print(django.__version__)"`
3. Kiểm tra Waitress: `python -c "import waitress; print(waitress.__version__)"`
4. Xem log lỗi trong terminal khi chạy server

Tham khảo tài liệu chi tiết trong các file .md
