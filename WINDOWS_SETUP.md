# Hướng dẫn chạy ứng dụng trên Windows

## Lỗi gặp phải với Gunicorn

Gunicorn không hỗ trợ Windows vì nó sử dụng module `fcntl` chỉ có trên Unix/Linux. Lỗi:
```
ModuleNotFoundError: No module named 'fcntl'
```

## Giải pháp: Sử dụng Waitress

Waitress là một WSGI server thuần Python, hỗ trợ cross-platform (Windows, Linux, macOS) và phù hợp cho production.

## Cài đặt

### 1. Cài đặt Python

- Tải Python 3.7 trở lên từ: https://www.python.org/downloads/
- Trong quá trình cài đặt, **NHỚ CHỌN** "Add Python to PATH"

### 2. Tạo Virtual Environment (Khuyến nghị)

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Cài đặt dependencies

```cmd
pip install -r requirements.txt
```

### 4. Tải Bootstrap CSS/JS files

**QUAN TRỌNG**: Trước khi chạy ứng dụng lần đầu, cần tải các file Bootstrap:

```cmd
download_bootstrap_files.bat
```

Sau đó chạy collectstatic:

```cmd
python manage.py collectstatic --noinput
```

> **Lưu ý**: Nếu không có internet hoặc gặp lỗi, xem hướng dẫn chi tiết trong file `STATIC_FILES_SETUP.md`

## Chạy ứng dụng

### Cách 1: Sử dụng file .bat (Đơn giản nhất)

Chỉ cần **double-click** vào file `start_server.bat` hoặc chạy trong Command Prompt:

```cmd
start_server.bat
```

File .bat sẽ tự động:
- Kiểm tra Python đã cài đặt chưa
- Kích hoạt virtual environment (nếu có)
- Cài đặt dependencies nếu thiếu
- Khởi động server

### Cách 2: Chạy trực tiếp bằng Python

```cmd
python run_waitress.py
```

### Cách 3: Chạy bằng waitress-serve CLI

```cmd
waitress-serve --host=0.0.0.0 --port=8000 --threads=4 wordgen.wsgi:application
```

## Truy cập ứng dụng

Sau khi server khởi động thành công, mở trình duyệt và truy cập:

- **Trên máy chủ**: http://localhost:8000
- **Từ máy khác trong mạng LAN**: http://[IP-máy-chủ]:8000

Ví dụ: `http://192.168.1.100:8000`

## Tìm địa chỉ IP của máy chủ

Chạy lệnh sau trong Command Prompt:

```cmd
ipconfig
```

Tìm dòng "IPv4 Address" trong phần mạng đang kết nối (WiFi hoặc Ethernet).

## Cấu hình nâng cao

### Thay đổi port

Mở file `run_waitress.py` và sửa dòng:

```python
port = 8000  # Đổi thành port khác, ví dụ: 8080
```

### Thay đổi số threads

Để tăng hiệu năng với nhiều người dùng đồng thời, sửa:

```python
threads = 4  # Tăng lên 8, 16, hoặc cao hơn
```

### Chỉ cho phép truy cập từ localhost

Nếu muốn chỉ chạy local (không cho máy khác kết nối):

```python
host = '127.0.0.1'  # Thay vì '0.0.0.0'
```

## Dừng server

Nhấn `Ctrl+C` trong cửa sổ Command Prompt đang chạy server.

## Chạy khi khởi động Windows (Tùy chọn)

### Cách 1: Thêm vào Startup folder

1. Nhấn `Win+R`, gõ: `shell:startup`
2. Tạo shortcut của `start_server.bat` vào folder này

### Cách 2: Tạo Windows Service

Sử dụng NSSM (Non-Sucking Service Manager):

1. Tải NSSM: https://nssm.cc/download
2. Giải nén và chạy:

```cmd
nssm install WordGenServer "C:\đường\dẫn\đến\python.exe" "C:\đường\dẫn\đến\run_waitress.py"
```

## So sánh Gunicorn vs Waitress

| Tính năng | Gunicorn | Waitress |
|-----------|----------|----------|
| Hỗ trợ Windows | ❌ Không | ✅ Có |
| Hỗ trợ Linux | ✅ Có | ✅ Có |
| Phù hợp Production | ✅ Có | ✅ Có |
| Worker Types | Nhiều loại | Thread-based |
| Cấu hình | Phức tạp hơn | Đơn giản hơn |

## Troubleshooting

### Lỗi: "Port 8000 is already in use"

Port đang được sử dụng bởi ứng dụng khác. Giải pháp:

1. Đổi port trong `run_waitress.py`
2. Hoặc tìm và tắt ứng dụng đang dùng port 8000:

```cmd
netstat -ano | findstr :8000
taskkill /PID [PID-number] /F
```

### Lỗi: "python is not recognized"

Python chưa được thêm vào PATH. Giải pháp:

1. Cài lại Python và chọn "Add Python to PATH"
2. Hoặc thêm thủ công:
   - Mở System Properties → Environment Variables
   - Thêm đường dẫn Python vào PATH (ví dụ: `C:\Python313\`)

### Lỗi: "No module named 'waitress'"

Dependencies chưa được cài. Chạy:

```cmd
pip install -r requirements.txt
```

### Không truy cập được từ máy khác

1. Kiểm tra firewall: Cho phép port 8000
2. Kiểm tra `host` trong `run_waitress.py` phải là `0.0.0.0`
3. Kiểm tra máy khác và máy chủ trong cùng mạng LAN

### Lỗi: CSS/JS không load (trang web không có styling)

Các file Bootstrap chưa được tải về. Thấy lỗi:
```
Not Found: /static/vendor/bootstrap/css/bootstrap.min.css
```

**Giải pháp:**

1. Chạy script tải Bootstrap:
   ```cmd
   download_bootstrap_files.bat
   ```

2. Chạy collectstatic:
   ```cmd
   python manage.py collectstatic --noinput
   ```

3. Khởi động lại server

**Xem hướng dẫn chi tiết**: `STATIC_FILES_SETUP.md`

## Liên hệ hỗ trợ

Nếu gặp vấn đề, vui lòng kiểm tra:

1. Version Python: `python --version` (cần >= 3.7)
2. Waitress đã cài: `python -c "import waitress; print(waitress.__version__)"`
3. Django đã cài: `python -c "import django; print(django.__version__)"`

Hoặc xem log lỗi chi tiết khi chạy server.
