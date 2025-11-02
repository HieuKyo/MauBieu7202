# 🚨 KHẮC PHỤC NGAY: Lỗi CSS không hiển thị

## ⚠️ Vấn đề

Bạn đã chạy `setup_first_time.bat` nhưng vẫn thấy lỗi:

```
WARNING:django.request:Not Found: /static/vendor/bootstrap/css/bootstrap.min.css
Not Found: /static/vendor/bootstrap-icons/css/bootstrap-icons.min.css
Not Found: /static/vendor/bootstrap/js/bootstrap.bundle.min.js
```

## ✅ Nguyên nhân đã tìm ra!

**Waitress (production server) KHÔNG tự động serve static files!**

Django cần **WhiteNoise** để serve CSS/JS trong production mode.

---

## 🚀 Giải pháp NHANH (3 bước)

### Bước 1: Pull code mới nhất

Tôi vừa fix và commit code. Pull về máy bạn:

```cmd
git pull
```

### Bước 2: Chạy script fix tự động

```cmd
fix_static_files.bat
```

Script này sẽ:
- ✅ Cài WhiteNoise (middleware serve static files)
- ✅ Tải Bootstrap CSS/JS (nếu chưa có)
- ✅ Chạy collectstatic (copy files vào staticfiles/)
- ✅ Xác nhận tất cả OK

### Bước 3: Khởi động lại server

```cmd
start_server.bat
```

**Xong! CSS sẽ hiển thị bình thường!** 🎉

---

## 🔧 Nếu không pull được code

Nếu bạn chưa pull được code mới, làm thủ công:

### 1. Cài WhiteNoise

```cmd
pip install whitenoise==6.8.2
```

### 2. Sửa file `wordgen/settings.py`

Tìm dòng `MIDDLEWARE = [`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # ← THÊM dòng này
    "django.contrib.sessions.middleware.SessionMiddleware",
    # ... các dòng khác giữ nguyên
]
```

Cuối file, thêm:

```python
# WhiteNoise configuration
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
```

### 3. Chạy collectstatic

```cmd
python manage.py collectstatic --noinput
```

### 4. Khởi động lại server

```cmd
start_server.bat
```

---

## ❓ Tại sao phải làm vậy?

### Development vs Production

| Mode | Server | Static Files | Cần WhiteNoise? |
|------|--------|--------------|-----------------|
| Dev  | runserver | ✅ Tự động serve | ❌ Không |
| Prod | Waitress | ❌ Không serve | ✅ **CẦN** |

Bạn đang dùng **Waitress** (production server) nên cần WhiteNoise!

---

## ✅ Kiểm tra sau khi fix

### 1. Không còn lỗi 404

Terminal **KHÔNG** còn dòng:
```
Not Found: /static/vendor/...
```

### 2. CSS hiển thị đúng

- Trang web có màu xanh Agribank
- Logo hiển thị
- Buttons có style đẹp

### 3. Developer Tools

1. Nhấn F12 trong browser
2. Tab **Network**
3. Refresh trang (F5)
4. Tìm request `/static/vendor/bootstrap/css/bootstrap.min.css`
5. Status phải là **200 OK** (màu xanh)

### 4. Folder staticfiles tồn tại

```cmd
dir staticfiles\vendor\bootstrap\css\
```

Phải thấy file `bootstrap.min.css`

---

## 🆘 Vẫn lỗi?

### Lỗi: "No module named 'whitenoise'"

```cmd
pip install whitenoise==6.8.2
```

### CSS vẫn không hiển thị

1. Dừng server (Ctrl+C)
2. Xóa staticfiles cũ:
   ```cmd
   rmdir /s /q staticfiles
   ```
3. Collect lại:
   ```cmd
   python manage.py collectstatic --noinput
   ```
4. Khởi động lại:
   ```cmd
   start_server.bat
   ```
5. Hard refresh browser: **Ctrl+F5**

### Xem thêm

Chi tiết đầy đủ trong file: **FIX_CSS_ISSUE.md**

---

## 📝 Tóm tắt

### Vấn đề:
- ❌ Waitress không serve static files
- ❌ CSS không load
- ❌ Lỗi 404 Not Found

### Giải pháp:
1. ✅ Pull code mới: `git pull`
2. ✅ Chạy fix: `fix_static_files.bat`
3. ✅ Restart: `start_server.bat`

### Kết quả:
- ✅ WhiteNoise installed
- ✅ Static files collected
- ✅ CSS hiển thị đúng
- ✅ Không còn lỗi 404

**GIỜ HÃY THỬ NGAY!** 🚀
