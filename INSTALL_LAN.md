# Hướng dẫn cài đặt, chạy và cập nhật MauBieu7202 (mạng LAN, offline)

Máy chủ LAN **không có Internet**. Mọi thư viện Python được cài từ thư mục `packages/` (file `.whl`) đi kèm mã nguồn.

| Việc cần làm | Chạy trên | Lệnh |
|---|---|---|
| Tải thư viện về `packages/` | Máy có Internet | `download_offline_packages.bat` |
| Kiểm tra `packages/` đủ thư viện | Máy có Internet | `verify_packages.bat` |
| Cài đặt lần đầu | Máy LAN | `setup.bat` |
| Chạy chương trình | Máy LAN | `run.bat` |
| Tạo gói cập nhật | Máy phát triển | `tao_ban_cap_nhat.bat` |
| Cập nhật / quay về bản trước | Máy LAN | `cap_nhat.bat` / `khoi_phuc.bat` (trong gói cập nhật) |

---

## 1. Cài đặt lần đầu

### Bước 1 – Chuẩn bị (máy có Internet)

1. Lấy mã nguồn MauBieu7202 (git clone hoặc copy thư mục).
2. Chạy `download_offline_packages.bat` để tải toàn bộ thư viện trong `requirements.txt` vào `packages/`.
3. Chạy `verify_packages.bat` để chắc chắn không thiếu file `.whl` nào.
4. Tải bộ cài Python 3.11+ (Windows 64-bit) từ https://www.python.org/downloads/.
5. Copy cả thư mục `MauBieu7202` (có `packages/`) và bộ cài Python sang máy LAN.

> Thêm thư viện mới vào `requirements.txt` thì **phải** có file `.whl` tương ứng trong `packages/`, nếu không máy LAN sẽ không cài được.

### Bước 2 – Cài Python (máy LAN)

Chạy bộ cài Python, **tick "Add Python to PATH"**, chọn *Install Now*. Mở Command Prompt mới và kiểm tra: `python --version`.

### Bước 3 – Cấu hình `.env` (máy LAN)

Copy `.env.example` thành `.env` trong thư mục MauBieu7202 và sửa:

```env
SECRET_KEY=<chuỗi ngẫu nhiên>
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,10.135.7.108
```

- Tạo `SECRET_KEY` mới:
  `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `ALLOWED_HOSTS`: ghi đúng IP máy chủ LAN.
- **Không** để `DEBUG=True` khi chạy thật: trang lỗi sẽ lộ cấu hình và dữ liệu cho mọi máy trong mạng.

### Bước 4 – Chạy `setup.bat` (máy LAN)

`setup.bat` tự làm 4 việc:

1. Kiểm tra Python
2. Cài thư viện từ `packages/` (`pip install --no-index --find-links=packages`)
3. Tạo/cập nhật database (`migrate`)
4. Thu thập file tĩnh CSS/JS (`collectstatic`)

Sau đó hỏi tạo tài khoản admin và có khởi động server luôn không.

---

## 2. Chạy chương trình

Chạy `run.bat` (kiểm tra thư viện rồi khởi động Waitress qua `run_waitress.py`).

- Truy cập: `http://10.135.7.108:8888` (máy chủ: `http://localhost:8888`)
- Trang quản trị: `http://10.135.7.108:8888/admin`
- Dừng server: nhấn `Ctrl+C` trong cửa sổ `run.bat`.
- Đổi cổng: sửa biến `port` trong `run_waitress.py`.

### Tự chạy khi bật máy (tùy chọn)

- **Cách 1 – Startup folder:** nhấn `Win+R`, gõ `shell:startup`, tạo shortcut của `run.bat` vào thư mục vừa mở.
- **Cách 2 – Windows Service (NSSM):** tải NSSM (https://nssm.cc/download), rồi chạy:
  `nssm install MauBieu7202 "C:\đường\dẫn\python.exe" "D:\MauBieu7202\run_waitress.py"`

---

## 3. Cập nhật lên bản mới (gói USB)

**Máy phát triển:**

1. Commit code mới.
2. Chạy `tao_ban_cap_nhat.bat` (chỉ lấy file thay đổi từ bản trước) hoặc `tao_ban_cap_nhat.bat --full` (toàn bộ code).
3. Gói `CapNhat_MauBieu_<phiên bản>/` được ghi thẳng vào USB đang cắm (không có USB → lưu ở `ban_cap_nhat/`).
   Nếu có thư viện mới, gói tự kèm file `.whl` cần thiết.

**Máy LAN:**

1. Cắm USB, mở thư mục gói, chạy `cap_nhat.bat`.
2. Nếu server đang chạy, script sẽ nhắc tắt cửa sổ `run.bat` rồi bấm Enter.
3. Script tự: sao lưu `db.sqlite3` + file sắp bị thay vào `backups/`, chép file mới, cài thư viện (nếu cần), `migrate`, `collectstatic`.
   Lỗi ở bất kỳ bước nào → tự khôi phục bản cũ.
4. Chạy lại `run.bat`.

**Quay về bản trước:** chạy `khoi_phuc.bat` trong cùng gói (giữ 5 bản sao lưu gần nhất).

---

## 4. Sao lưu dữ liệu

Gói cập nhật đã tự sao lưu database trước mỗi lần cập nhật. Nên sao lưu thêm định kỳ (ra ổ khác/USB) các mục:

- `db.sqlite3` – toàn bộ dữ liệu (tắt `run.bat` trước khi copy)
- `media/` – mẫu Word, ảnh tải lên
- `private_media/` – ảnh CCCD, chữ ký khách hàng
- `.env` – cấu hình

---

## 5. Sửa lỗi thường gặp

| Lỗi | Cách xử lý |
|---|---|
| `Python was not found` / `python is not recognized` | Cài lại Python, tick *Add Python to PATH*, mở Command Prompt mới. |
| `No module named '...'` | Thiếu file `.whl` trong `packages/`: trên máy có Internet chạy `download_offline_packages.bat` + `verify_packages.bat`, copy `packages/` sang rồi chạy lại `setup.bat`. |
| Trang web không có màu sắc / CSS lỗi 404 | Chạy `python manage.py collectstatic --noinput`, khởi động lại `run.bat`, nhấn `Ctrl+F5` trên trình duyệt. Bootstrap và icon đã có sẵn trong `templates_app/static/vendor/`, không cần Internet. |
| Cổng 8888 đang bị dùng | `netstat -ano \| findstr :8888` để tìm PID, `taskkill /PID <PID> /F`; hoặc đổi cổng trong `run_waitress.py`. |
| Máy khác không truy cập được | Kiểm tra IP trong `ALLOWED_HOSTS` (`.env`) và mở cổng 8888 trên Windows Firewall. |
| Lỗi 500 / trang báo lỗi | Xem chi tiết trong `logs/errors.log` (log chung: `logs/app.log`). |
