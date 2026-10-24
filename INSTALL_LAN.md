# Hướng dẫn cài đặt MauBieu7202 trên mạng LAN (Offline)

## 📋 Yêu cầu hệ thống

- Windows 10/11 hoặc Windows Server
- Python 3.8 trở lên
- 2GB RAM tối thiểu
- 1GB dung lượng ổ cứng

## 🚀 Quy trình cài đặt

### Bước 1: Chuẩn bị trên máy có Internet

1. **Clone repository hoặc download source code**
   ```bash
   git clone <repository-url>
   cd MauBieu7202
   ```

2. **Download tất cả packages offline**
   ```bash
   download_offline_packages.bat
   ```

   Script này sẽ:
   - Tạo thư mục `offline_packages`
   - Download tất cả dependencies từ `requirements.txt`
   - Lưu các file `.whl` vào `offline_packages`

3. **Copy sang máy LAN**
   - Copy toàn bộ thư mục `MauBieu7202` (bao gồm `offline_packages`)
   - Có thể dùng USB, ổ mạng, hoặc phương thức khác

### Bước 2: Cài đặt Python trên máy LAN

1. **Download Python installer** (trên máy có internet):
   - Truy cập: https://www.python.org/downloads/
   - Download Python 3.10 hoặc 3.11 (Windows installer 64-bit)
   - Copy file installer sang máy LAN

2. **Cài đặt Python**:
   - Chạy file installer
   - ✅ **QUAN TRỌNG**: Chọn "Add Python to PATH"
   - Chọn "Install Now"
   - Đợi cài đặt hoàn tất

3. **Verify Python đã cài đặt**:
   ```bash
   python --version
   ```

### Bước 3: Cài đặt MauBieu7202 trên máy LAN

1. **Mở Command Prompt** (với quyền Administrator):
   - Nhấn `Win + X`
   - Chọn "Command Prompt (Admin)" hoặc "Windows PowerShell (Admin)"

2. **Di chuyển đến thư mục MauBieu7202**:
   ```bash
   cd D:\MauBieu7202
   ```

3. **Chạy script cài đặt offline**:
   ```bash
   install_offline.bat
   ```

   Script này sẽ:
   - Tạo virtual environment
   - Cài đặt tất cả packages từ `offline_packages`
   - Không cần kết nối internet

### Bước 4: Cấu hình Database

1. **Copy file .env.example thành .env**:
   ```bash
   copy .env.example .env
   ```

2. **Chỉnh sửa file .env** (dùng Notepad hoặc editor khác):
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,192.168.x.x

   # Database (SQLite mặc định - không cần cấu hình)
   # DATABASE_URL=sqlite:///db.sqlite3
   ```

### Bước 5: Khởi tạo Database

1. **Chạy migrations**:
   ```bash
   venv\Scripts\activate
   python manage.py migrate
   ```

2. **Tạo superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   - Nhập username (VD: admin)
   - Nhập email (có thể để trống)
   - Nhập password (2 lần)

### Bước 6: Khởi động Server

1. **Development mode** (cho testing):
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

2. **Production mode** (khuyến nghị cho LAN):
   ```bash
   python manage.py collectstatic --noinput
   waitress-serve --host=0.0.0.0 --port=8000 wordgen.wsgi:application
   ```

3. **Truy cập ứng dụng**:
   - Trên máy chủ: http://localhost:8000
   - Từ máy khác trong LAN: http://192.168.x.x:8000
   - Login với tài khoản superuser vừa tạo

## 🔧 Sửa lỗi thường gặp

### Lỗi: "No module named 'dbfread'"

**Nguyên nhân**: Thiếu package `dbfread` trong offline_packages

**Giải pháp**:
1. Trên máy có internet, chạy lại:
   ```bash
   download_offline_packages.bat
   ```
2. Copy lại thư mục `offline_packages` sang máy LAN
3. Chạy lại:
   ```bash
   install_offline.bat
   ```

### Lỗi: "Python was not found"

**Nguyên nhân**: Python chưa được cài đặt hoặc chưa có trong PATH

**Giải pháp**:
1. Cài đặt lại Python
2. Chọn "Add Python to PATH" trong quá trình cài đặt
3. Restart Command Prompt

### Lỗi: Port 8000 đã được sử dụng

**Giải pháp**: Đổi port khác:
```bash
python manage.py runserver 0.0.0.0:8001
```

## 📦 Cập nhật ứng dụng

1. **Tải phiên bản mới** (trên máy có internet):
   ```bash
   git pull
   download_offline_packages.bat
   ```

2. **Copy sang máy LAN**

3. **Cài đặt packages mới**:
   ```bash
   install_offline.bat
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

4. **Restart server**

## 🔒 Bảo mật cho môi trường Production

1. **Tắt DEBUG mode** trong `.env`:
   ```
   DEBUG=False
   ```

2. **Đổi SECRET_KEY** thành giá trị ngẫu nhiên:
   ```
   SECRET_KEY=<random-string-here>
   ```

3. **Cấu hình ALLOWED_HOSTS** chính xác:
   ```
   ALLOWED_HOSTS=192.168.1.100,agribank.local
   ```

4. **Sử dụng HTTPS** nếu có thể

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log trong Command Prompt
2. Kiểm tra file `debug.log` (nếu có)
3. Liên hệ IT support với thông tin lỗi chi tiết
