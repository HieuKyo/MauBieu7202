# Hướng dẫn tạo Pull Request và Merge

## Thông tin Pull Request

### Branch nguồn
```
claude/replace-gunicorn-waitress-011CUiAXzF8XNxip1CBgAgMk
```

### Commit hash
```
9c51a17
```

### Các thay đổi
1. ✅ Thay thế `gunicorn` bằng `waitress` trong `requirements.txt`
2. ✅ Tạo file `run_waitress.py` - Script Python để chạy Waitress server
3. ✅ Tạo file `start_server.bat` - File batch để chạy dễ dàng trên Windows
4. ✅ Tạo file `WINDOWS_SETUP.md` - Hướng dẫn chi tiết bằng tiếng Việt

## Cách 1: Tạo Pull Request trên GitHub (Khuyến nghị)

### Bước 1: Truy cập GitHub
Vào link sau để tạo Pull Request:
```
https://github.com/HieuKyo/MauBieu7202/pull/new/claude/replace-gunicorn-waitress-011CUiAXzF8XNxip1CBgAgMk
```

### Bước 2: Điền thông tin PR

**Tiêu đề:**
```
Replace gunicorn with waitress for Windows compatibility
```

**Mô tả:**
```markdown
## Tóm tắt
Thay thế gunicorn bằng waitress để hỗ trợ chạy trên Windows.

## Vấn đề
- Gunicorn không hỗ trợ Windows (lỗi: `ModuleNotFoundError: No module named 'fcntl'`)
- fcntl module chỉ có trên Unix/Linux

## Giải pháp
- Sử dụng Waitress - WSGI server cross-platform (Windows/Linux/macOS)
- Tạo script và batch file để chạy dễ dàng

## Các thay đổi
- ✅ `requirements.txt`: gunicorn → waitress
- ✅ `run_waitress.py`: Script Python để cấu hình và chạy Waitress
- ✅ `start_server.bat`: Batch file để chạy trên Windows (double-click)
- ✅ `WINDOWS_SETUP.md`: Hướng dẫn đầy đủ bằng tiếng Việt

## Test plan
### Trên Windows:
1. Chạy `start_server.bat`
2. Hoặc chạy `python run_waitress.py`
3. Truy cập http://localhost:8000
4. Verify ứng dụng chạy bình thường

### Trên Linux:
1. `pip install -r requirements.txt`
2. `python run_waitress.py`
3. Verify ứng dụng chạy bình thường
```

### Bước 3: Chọn base branch
- Nếu có branch `main`: chọn `main`
- Nếu không: chọn branch bạn muốn merge vào (có thể là `claude/django-word-template-generator-011CUfkKT1HZ7HQosuoKML8r`)

### Bước 4: Create Pull Request
Click nút **"Create Pull Request"**

### Bước 5: Merge
Sau khi review, click **"Merge Pull Request"**

## Cách 2: Merge trực tiếp trên local (Nếu bạn có quyền push)

Nếu bạn có quyền push lên branch main:

```bash
# Clone repository về máy của bạn
git clone https://github.com/HieuKyo/MauBieu7202.git
cd MauBieu7202

# Tạo hoặc checkout branch main
git checkout -b main
# Hoặc nếu đã có: git checkout main

# Merge changes từ branch waitress
git merge claude/replace-gunicorn-waitress-011CUiAXzF8XNxip1CBgAgMk

# Push lên remote
git push -u origin main
```

## Cách 3: Set branch mặc định trên GitHub

Nếu muốn set branch `claude/replace-gunicorn-waitress-011CUiAXzF8XNxip1CBgAgMk` làm default:

1. Vào GitHub repository settings
2. Chọn **Branches** ở sidebar
3. Trong **Default branch**, click nút pencil
4. Chọn branch `claude/replace-gunicorn-waitress-011CUiAXzF8XNxip1CBgAgMk`
5. Click **Update**

## Xác nhận thay đổi đã được push

Branch đã được push thành công lên remote. Bạn có thể xem:

**URL branch:**
```
https://github.com/HieuKyo/MauBieu7202/tree/claude/replace-gunicorn-waitress-011CUiAXzF8XNxip1CBgAgMk
```

**URL commit:**
```
https://github.com/HieuKyo/MauBieu7202/commit/9c51a17
```

**Các file mới:**
- `/WINDOWS_SETUP.md`
- `/run_waitress.py`
- `/start_server.bat`
- `/requirements.txt` (đã sửa)

## Sau khi merge

Sau khi merge vào branch chính, để sử dụng:

### Trên Windows:
```cmd
# Clone repository
git clone https://github.com/HieuKyo/MauBieu7202.git
cd MauBieu7202

# Checkout branch chính (main hoặc master)
git checkout main

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
start_server.bat
```

### Trên Linux:
```bash
git clone https://github.com/HieuKyo/MauBieu7202.git
cd MauBieu7202
git checkout main
pip install -r requirements.txt
python run_waitress.py
```

## Lưu ý

- Waitress hoạt động tốt trên cả Windows và Linux
- Không cần cấu hình đặc biệt
- Hiệu năng tương đương gunicorn cho ứng dụng Django nhỏ-trung bình
