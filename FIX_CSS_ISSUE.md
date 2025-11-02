# Khắc phục lỗi CSS không hiển thị

## Triệu chứng

Khi chạy server, bạn thấy các lỗi sau trong terminal:

```
WARNING:django.request:Not Found: /static/vendor/bootstrap/css/bootstrap.min.css
Not Found: /static/vendor/bootstrap-icons/css/bootstrap-icons.min.css
Not Found: /static/vendor/bootstrap/js/bootstrap.bundle.min.js
```

Trang web hiển thị không có CSS (không màu sắc, không định dạng).

---

## Nguyên nhân

**Vấn đề 1: WhiteNoise chưa được cài**
- Django production server (Waitress) KHÔNG tự động serve static files
- Cần WhiteNoise để serve static files trong production

**Vấn đề 2: Collectstatic chưa chạy**
- Static files trong `templates_app/static/` chưa được copy vào `staticfiles/`
- Server chỉ serve files từ `staticfiles/`, không phải từ app folders

---

## Giải pháp nhanh

### Chạy script tự động (Khuyến nghị)

```cmd
fix_static_files.bat
```

Script này sẽ:
1. ✅ Cài đặt WhiteNoise
2. ✅ Tải Bootstrap files (nếu chưa có)
3. ✅ Chạy collectstatic
4. ✅ Xác nhận files đã được copy

Sau đó **khởi động lại server**:
```cmd
start_server.bat
```

---

## Giải pháp thủ công

### Bước 1: Cài đặt WhiteNoise

```cmd
pip install --upgrade -r requirements.txt
```

Hoặc:
```cmd
pip install whitenoise==6.8.2
```

### Bước 2: Tải Bootstrap files (nếu chưa có)

```cmd
download_bootstrap_files.bat
```

### Bước 3: Chạy collectstatic

```cmd
# Xóa staticfiles cũ
rmdir /s /q staticfiles

# Collect lại
python manage.py collectstatic --noinput
```

### Bước 4: Khởi động lại server

```cmd
start_server.bat
```

### Bước 5: Xóa cache trình duyệt

Nhấn **Ctrl+F5** hoặc **Ctrl+Shift+R** để hard refresh

---

## Cách WhiteNoise hoạt động

### Trước khi có WhiteNoise:

```
Browser → Waitress → Django → ❌ Static files không được serve
```

### Sau khi có WhiteNoise:

```
Browser → Waitress → Django + WhiteNoise → ✅ Static files được serve
```

WhiteNoise là middleware đặc biệt:
- Tự động serve files từ `STATIC_ROOT` (staticfiles/)
- Tối ưu hiệu năng với compression và caching
- Hoạt động tốt với Waitress, Gunicorn, uWSGI
- Không cần Nginx hay Apache

---

## Kiểm tra sau khi fix

### 1. Kiểm tra staticfiles folder

```cmd
dir staticfiles\vendor\bootstrap\css\
dir staticfiles\css\
dir staticfiles\images\
```

Bạn phải thấy:
- `bootstrap.min.css`
- `agribank-theme.css`
- `agribank_logo.png`

### 2. Kiểm tra WhiteNoise đã cài

```cmd
python -c "import whitenoise; print(whitenoise.__version__)"
```

Kết quả: `6.8.2`

### 3. Kiểm tra server log

Khi start server, **KHÔNG** được thấy lỗi:
```
Not Found: /static/vendor/...
```

### 4. Kiểm tra trên trình duyệt

1. Mở http://localhost:8000
2. Nhấn **F12** (Developer Tools)
3. Tab **Network**
4. Refresh trang (F5)
5. Kiểm tra các request `/static/vendor/bootstrap/...`:
   - Status phải là **200 OK** (màu xanh)
   - KHÔNG phải **404 Not Found** (màu đỏ)

---

## Troubleshooting

### Lỗi: "No module named 'whitenoise'"

```cmd
pip install whitenoise==6.8.2
```

### Lỗi: "ImproperlyConfigured: You're using the staticfiles app..."

Settings.py đã được cập nhật đúng. Chạy:
```cmd
python manage.py check
```

### Collectstatic báo lỗi manifest

```cmd
# Dùng storage đơn giản hơn tạm thời
# Sửa settings.py, đổi:
"staticfiles": {
    "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
}
```

### CSS vẫn không hiển thị sau khi fix

1. **Dừng server** (Ctrl+C)
2. **Xóa staticfiles**:
   ```cmd
   rmdir /s /q staticfiles
   ```
3. **Collectstatic lại**:
   ```cmd
   python manage.py collectstatic --noinput
   ```
4. **Khởi động lại server**:
   ```cmd
   start_server.bat
   ```
5. **Hard refresh browser**: Ctrl+F5

### Static files bị cache

Xóa cache trình duyệt:

**Chrome/Edge:**
1. Ctrl+Shift+Delete
2. Chọn "Cached images and files"
3. Clear data

**Hoặc:** Mở Developer Tools → Tab Network → Tích "Disable cache"

---

## Cấu hình đã thay đổi

### `requirements.txt`

Đã thêm:
```
whitenoise==6.8.2
```

### `wordgen/settings.py`

Đã thêm WhiteNoise middleware:
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← MỚI
    ...
]
```

Đã thêm STORAGES config:
```python
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

---

## Tại sao cần WhiteNoise?

### Development (runserver):
- Django tự động serve static files
- KHÔNG cần WhiteNoise
- Chỉ dùng cho dev, không dùng production

### Production (Waitress):
- Django KHÔNG serve static files
- CẦN WhiteNoise để serve
- Tối ưu hiệu năng, bảo mật

### So sánh:

| | Development | Production |
|---|---|---|
| Server | runserver | Waitress |
| Static files | ✅ Tự động | ❌ Cần WhiteNoise |
| Collectstatic | Không cần | ✅ Bắt buộc |
| Performance | Chậm | ✅ Nhanh |

---

## Tóm tắt

### Lỗi CSS không hiển thị xảy ra vì:
1. ❌ WhiteNoise chưa được cài
2. ❌ Collectstatic chưa chạy
3. ❌ Server production không serve static files

### Giải pháp:
1. ✅ Chạy `fix_static_files.bat`
2. ✅ Hoặc cài WhiteNoise + collectstatic thủ công
3. ✅ Khởi động lại server

### Sau khi fix:
- ✅ CSS hiển thị đúng
- ✅ Bootstrap hoạt động
- ✅ Logo và icons hiển thị
- ✅ Không còn lỗi 404

---

## Tài liệu tham khảo

- WhiteNoise: http://whitenoise.evans.io/
- Django Static Files: https://docs.djangoproject.com/en/5.2/howto/static-files/
- Collectstatic: https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#collectstatic
