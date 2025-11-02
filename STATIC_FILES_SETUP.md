# Hướng dẫn cài đặt Static Files (CSS/JS)

## Vấn đề

Khi chạy ứng dụng, bạn thấy lỗi:
```
Not Found: /static/vendor/bootstrap-icons/css/bootstrap-icons.min.css
Not Found: /static/vendor/bootstrap/css/bootstrap.min.css
Not Found: /static/vendor/bootstrap/js/bootstrap.bundle.min.js
```

Các file CSS/JS Bootstrap chưa được tải về.

## Giải pháp

### Cách 1: Tải tự động bằng script (Khuyến nghị)

**Trên Windows:**

1. Double-click file `download_bootstrap_files.bat`
2. Hoặc chạy trong Command Prompt:
   ```cmd
   download_bootstrap_files.bat
   ```

3. Sau khi tải xong, chạy collectstatic:
   ```cmd
   python manage.py collectstatic --noinput
   ```

4. Khởi động lại server:
   ```cmd
   start_server.bat
   ```

**Trên Linux/macOS:**

1. Chạy script bash:
   ```bash
   bash download_static_files.sh
   ```

2. Hoặc dùng Python:
   ```bash
   python download_bootstrap.py
   ```

3. Chạy collectstatic:
   ```bash
   python manage.py collectstatic --noinput
   ```

4. Khởi động lại server:
   ```bash
   python run_waitress.py
   ```

### Cách 2: Tải thủ công

Nếu script không hoạt động (không có internet hoặc bị chặn):

#### Bước 1: Tải Bootstrap

1. Truy cập: https://getbootstrap.com/docs/5.3/getting-started/download/
2. Tải **Bootstrap v5.3.0** (Compiled CSS and JS)
3. Giải nén file tải về
4. Copy các file sau:

   ```
   bootstrap/css/bootstrap.min.css
     → templates_app/static/vendor/bootstrap/css/bootstrap.min.css

   bootstrap/js/bootstrap.bundle.min.js
     → templates_app/static/vendor/bootstrap/js/bootstrap.bundle.min.js
   ```

#### Bước 2: Tải Bootstrap Icons

1. Truy cập: https://icons.getbootstrap.com/
2. Click "Download" → Tải **Bootstrap Icons v1.11.0**
3. Giải nén file tải về
4. Copy các file sau:

   ```
   bootstrap-icons-1.11.0/font/bootstrap-icons.min.css
     → templates_app/static/vendor/bootstrap-icons/css/bootstrap-icons.min.css

   bootstrap-icons-1.11.0/font/fonts/bootstrap-icons.woff
     → templates_app/static/vendor/bootstrap-icons/fonts/bootstrap-icons.woff

   bootstrap-icons-1.11.0/font/fonts/bootstrap-icons.woff2
     → templates_app/static/vendor/bootstrap-icons/fonts/bootstrap-icons.woff2
   ```

#### Bước 3: Cấu trúc thư mục cuối cùng

Sau khi copy xong, cấu trúc thư mục sẽ như sau:

```
MauBieu7202/
└── templates_app/
    └── static/
        └── vendor/
            ├── bootstrap/
            │   ├── css/
            │   │   └── bootstrap.min.css
            │   └── js/
            │       └── bootstrap.bundle.min.js
            └── bootstrap-icons/
                ├── css/
                │   └── bootstrap-icons.min.css
                └── fonts/
                    ├── bootstrap-icons.woff
                    └── bootstrap-icons.woff2
```

#### Bước 4: Chạy collectstatic

```cmd
python manage.py collectstatic --noinput
```

#### Bước 5: Khởi động lại server

```cmd
start_server.bat
```

### Cách 3: Sử dụng CDN (Chỉ khi có Internet)

Nếu server có kết nối internet ổn định, bạn có thể sử dụng CDN thay vì file local.

**Lưu ý:** Cách này chỉ phù hợp khi triển khai trên server có internet.

Chỉnh sửa file template `templates_app/templates/base.html` hoặc tương tự, thay:

```html
<!-- File local -->
<link rel="stylesheet" href="{% static 'vendor/bootstrap/css/bootstrap.min.css' %}">
```

Bằng:

```html
<!-- CDN -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
```

## Kiểm tra Static Files

### Kiểm tra file đã tải chưa

**Windows:**
```cmd
dir /s templates_app\static\vendor\*.css
dir /s templates_app\static\vendor\*.js
```

**Linux/macOS:**
```bash
find templates_app/static/vendor -name "*.css"
find templates_app/static/vendor -name "*.js"
```

### Kiểm tra collectstatic đã chạy chưa

Kiểm tra thư mục `staticfiles/`:

**Windows:**
```cmd
dir staticfiles\vendor\
```

**Linux/macOS:**
```bash
ls -la staticfiles/vendor/
```

### Kiểm tra server đang phục vụ static files

1. Khởi động server:
   ```cmd
   start_server.bat
   ```

2. Mở trình duyệt và truy cập:
   ```
   http://localhost:8000/static/vendor/bootstrap/css/bootstrap.min.css
   ```

3. Nếu hiển thị nội dung CSS → Thành công!
4. Nếu lỗi 404 → Chạy lại collectstatic

## Troubleshooting

### Lỗi: "curl is not recognized"

**Windows:**
- Cài đặt curl (Windows 10+ đã có sẵn)
- Hoặc tải thủ công theo Cách 2

### Lỗi: "Access denied" hoặc "403 Forbidden"

CDN bị chặn bởi firewall/proxy.

**Giải pháp:** Tải thủ công theo Cách 2

### Static files vẫn không load sau khi collectstatic

1. Kiểm tra settings.py:
   ```python
   STATIC_URL = "static/"
   STATIC_ROOT = BASE_DIR / "staticfiles"
   ```

2. Xóa thư mục staticfiles và chạy lại:
   ```cmd
   rmdir /s /q staticfiles
   python manage.py collectstatic --noinput
   ```

3. Khởi động lại server

### Lỗi khi chạy collectstatic

**Lỗi:** "You're using the staticfiles app without having set the STATIC_ROOT setting"

**Giải pháp:** Đã được cấu hình trong `wordgen/settings.py`:
```python
STATIC_ROOT = BASE_DIR / "staticfiles"
```

### CSS hiển thị nhưng không có styling

1. Kiểm tra file CSS không bị rỗng:
   ```cmd
   type templates_app\static\vendor\bootstrap\css\bootstrap.min.css | more
   ```

2. Nếu file rỗng hoặc chỉ có vài bytes → Tải lại file

3. File Bootstrap CSS chuẩn phải có kích thước ~200KB

## Triển khai Offline

Nếu bạn triển khai trên mạng nội bộ không có internet:

1. **Trên máy có internet:**
   - Chạy `download_bootstrap_files.bat`
   - Copy toàn bộ thư mục `templates_app/static/vendor/` ra USB

2. **Trên máy server offline:**
   - Paste thư mục `vendor/` vào `templates_app/static/`
   - Chạy `python manage.py collectstatic --noinput`
   - Khởi động server

## Tài liệu tham khảo

- Django Static Files: https://docs.djangoproject.com/en/5.2/howto/static-files/
- Bootstrap Download: https://getbootstrap.com/docs/5.3/getting-started/download/
- Bootstrap Icons: https://icons.getbootstrap.com/

## Liên hệ hỗ trợ

Nếu vẫn gặp vấn đề, kiểm tra:

1. Python version: `python --version`
2. Django version: `python -c "import django; print(django.__version__)"`
3. Static files cấu hình: `python manage.py findstatic vendor/bootstrap/css/bootstrap.min.css`
