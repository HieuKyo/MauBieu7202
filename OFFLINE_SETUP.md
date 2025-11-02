# HƯỚNG DẪN CÀI ĐẶT OFFLINE - HỆ THỐNG MẪU BIỂU AGRIBANK

## Tổng quan
Hệ thống này được thiết kế để hoạt động hoàn toàn trên mạng nội bộ không có kết nối Internet. Tài liệu này hướng dẫn cách chuẩn bị và triển khai hệ thống.

## PHẦN 1: CHUẨN BỊ TRÊN MÁY CÓ INTERNET

### Bước 1: Tải các thư viện Static (Bootstrap & Icons)

Chạy script tự động để tải các file CSS/JS cần thiết:

```bash
chmod +x download_static_files.sh
./download_static_files.sh
```

Script này sẽ tải về:
- Bootstrap 5.3.0 CSS & JS
- Bootstrap Icons 1.11.0 fonts & CSS

Các file sẽ được lưu trong thư mục `static/vendor/`

### Bước 2: Chuẩn bị các thư viện Python

Tạo file requirements.txt (đã được tạo sẵn) và tải các package về:

```bash
# Tải tất cả các package Python về thư mục local
pip download -r requirements.txt -d python_packages/
```

### Bước 3: Đóng gói toàn bộ project

```bash
# Tạo file nén chứa toàn bộ project
tar -czf maubieu_offline.tar.gz \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  --exclude='*.sqlite3' \
  --exclude='.git' \
  .
```

## PHẦN 2: CÀI ĐẶT TRÊN MÁY CHỦ NỘI BỘ (KHÔNG CÓ INTERNET)

### Bước 1: Giải nén project

```bash
tar -xzf maubieu_offline.tar.gz -C /path/to/installation/
cd /path/to/installation/
```

### Bước 2: Cài đặt Python packages từ file local

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

# Cài đặt packages từ thư mục đã tải
pip install --no-index --find-links=python_packages/ -r requirements.txt
```

### Bước 3: Cấu hình Django settings

Chỉnh sửa file `maubieu/settings.py`:

```python
# Cho phép truy cập từ IP nội bộ
ALLOWED_HOSTS = ['*']  # Hoặc chỉ định các IP cụ thể: ['192.168.1.100', 'localhost']

# Cấu hình static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

### Bước 4: Thu thập static files

```bash
python manage.py collectstatic --noinput
```

Lệnh này sẽ sao chép tất cả các file static (bao gồm Bootstrap & Icons đã tải) vào thư mục `staticfiles/`.

### Bước 5: Thiết lập database

```bash
# Chạy migrations
python manage.py migrate

# Tạo superuser
python manage.py createsuperuser
```

### Bước 6: Khởi động server

#### Môi trường Development (test):
```bash
python manage.py runserver 0.0.0.0:8000
```

#### Môi trường Production (khuyến nghị):

**Option 1: Sử dụng Gunicorn**
```bash
# Cài đặt gunicorn (đã có trong requirements.txt)
gunicorn --bind 0.0.0.0:8000 --workers 3 maubieu.wsgi:application
```

**Option 2: Sử dụng Apache + mod_wsgi**
Tham khảo tài liệu Django deployment với Apache.

**Option 3: Sử dụng Nginx + Gunicorn**
Tham khảo tài liệu Django deployment với Nginx.

## PHẦN 3: TRUY CẬP HỆ THỐNG

Sau khi khởi động server, truy cập hệ thống qua:

- Từ chính máy chủ: `http://localhost:8000`
- Từ máy khác trong mạng: `http://[IP_CỦA_MÁY_CHỦ]:8000`

Ví dụ: `http://192.168.1.100:8000`

## KIỂM TRA

### 1. Kiểm tra Static Files
- Truy cập trang chủ và kiểm tra CSS hiển thị đúng (màu xanh Agribank, logo)
- Kiểm tra các icon hiển thị (Bootstrap Icons)
- Kiểm tra các chức năng dropdown, modal hoạt động (Bootstrap JS)

### 2. Kiểm tra Chức năng
- Đăng nhập vào admin: `http://[IP]:8000/admin/`
- Tạo template mẫu
- Tạo khách hàng
- Xuất mẫu biểu Word

## CẤU TRÚC THỨ MỤC

```
MauBieu7202/
├── static/
│   ├── vendor/
│   │   ├── bootstrap/
│   │   │   ├── css/
│   │   │   │   └── bootstrap.min.css
│   │   │   └── js/
│   │   │       └── bootstrap.bundle.min.js
│   │   └── bootstrap-icons/
│   │       ├── css/
│   │       │   └── bootstrap-icons.min.css
│   │       └── fonts/
│   │           ├── bootstrap-icons.woff
│   │           └── bootstrap-icons.woff2
│   ├── css/
│   │   └── agribank-theme.css
│   └── images/
│       └── agribank_logo.png
├── templates_app/
├── maubieu/
├── manage.py
├── requirements.txt
├── download_static_files.sh
└── OFFLINE_SETUP.md
```

## XỬ LÝ SỰ CỐ

### Static files không load
1. Kiểm tra `STATIC_URL` và `STATIC_ROOT` trong settings.py
2. Chạy lại `python manage.py collectstatic`
3. Kiểm tra quyền truy cập thư mục staticfiles

### Bootstrap/Icons không hiển thị
1. Kiểm tra các file đã được tải trong `static/vendor/`
2. Kiểm tra trong trình duyệt (F12) tab Network xem file nào bị lỗi 404
3. Xác nhận đường dẫn trong base.html đúng

### Không thể truy cập từ máy khác
1. Kiểm tra firewall trên máy chủ cho phép port 8000
2. Kiểm tra `ALLOWED_HOSTS` trong settings.py
3. Kiểm tra server đã bind đúng IP: `0.0.0.0:8000` chứ không phải `127.0.0.1:8000`

## HỖ TRỢ

Nếu gặp vấn đề, kiểm tra:
1. Log của Django: trong terminal khi chạy server
2. Log của trình duyệt: F12 > Console
3. File `db.sqlite3` có tồn tại và có quyền ghi

## GHI CHÚ BẢO MẬT

Khi triển khai production:
1. Đổi `SECRET_KEY` trong settings.py
2. Đặt `DEBUG = False`
3. Cấu hình HTTPS nếu có thể
4. Sử dụng database như PostgreSQL thay vì SQLite cho hiệu năng tốt hơn
5. Thiết lập backup định kỳ cho database

---

**Phiên bản:** 1.0
**Cập nhật:** 2025-11-02
**Ngân hàng:** Agribank Chi nhánh Giá Rai Bạc Liêu
