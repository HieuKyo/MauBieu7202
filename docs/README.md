# Hệ thống Quản lý Mẫu biểu Word - AGRIBANK

Ứng dụng web Django cho phép nhân viên Agribank tạo file Microsoft Word (.docx) từ các mẫu có sẵn với cú pháp Jinja2.

**Thiết kế giao diện theo chuẩn nhận diện thương hiệu Agribank** với màu xanh lá đặc trưng (#00923F).

---

## 🚀 Bắt đầu nhanh (Quick Start)

### Windows

```cmd
# Lần đầu tiên: Chạy setup
setup.bat

# Các lần sau: Chạy server
start.bat
```

### Linux/macOS

```bash
# Setup
bash scripts/setup_first_time.sh

# Chạy server
python run_waitress.py
```

**Truy cập:** http://localhost:8000

📖 **Hướng dẫn chi tiết:** [docs/QUICK_START.md](docs/QUICK_START.md)

---

## 📚 Tài liệu (Documentation)

| Tài liệu | Mô tả |
|----------|-------|
| [QUICK_START.md](docs/QUICK_START.md) | Bắt đầu nhanh trong 3 bước |
| [WINDOWS_SETUP.md](docs/WINDOWS_SETUP.md) | Hướng dẫn chi tiết cho Windows |
| [URGENT_FIX_CSS.md](docs/URGENT_FIX_CSS.md) | Khắc phục lỗi CSS không hiển thị |
| [STATIC_FILES_SETUP.md](docs/STATIC_FILES_SETUP.md) | Cài đặt Bootstrap CSS/JS |
| [OFFLINE_SETUP.md](docs/OFFLINE_SETUP.md) | Triển khai offline/mạng nội bộ |

---

## ⚡ Các lệnh chính (Main Commands)

```cmd
# Setup lần đầu
setup.bat

# Chạy server
start.bat

# Tạo admin user
python manage.py createsuperuser

# Collect static files (sau khi sửa CSS)
python manage.py collectstatic --noinput

# Khắc phục lỗi CSS
scripts\fix_static_files.bat
```

---

## 🎯 Tính năng chính (Key Features)

### 1. Phân cấp Mẫu biểu
- **Danh mục (Cha)**: Tổ chức mẫu biểu theo nhóm (VD: "Phát hành thẻ", "Tra soát")
- **Mẫu biểu (Con)**: Các file .docx cụ thể thuộc một danh mục

### 2. Quản lý qua Django Admin
- Quản lý Danh mục, Mẫu biểu, Biến
- Import/Export Biến từ CSV/Excel
- Import hàng loạt Mẫu biểu (bulk upload)

### 3. Biến thông minh (Dynamic Forms)
- Hỗ trợ: text, textarea, date, number
- Form tự động tạo dựa trên biến của mẫu biểu

### 4. Phân quyền
- Sử dụng Django Groups
- Quyền gán ở cấp độ Mẫu biểu

---

## 🛠️ Công nghệ (Technology Stack)

- **Backend**: Django 5.2.7
- **WSGI Server**: Waitress 3.0.1 (cross-platform)
- **Static Files**: WhiteNoise 6.8.2
- **Word Processing**: python-docx
- **Database**: SQLite (có thể đổi PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5.3.0, Bootstrap Icons

---

## 📁 Cấu trúc thư mục (Project Structure)

```
MauBieu7202/
├── setup.bat              # Launcher cho setup (gọi scripts/setup_first_time.bat)
├── start.bat              # Launcher cho server (gọi scripts/start_server.bat)
├── manage.py              # Django management
├── requirements.txt       # Python dependencies
├── run_waitress.py        # Waitress server script
├── docs/                  # 📚 Tài liệu
│   ├── QUICK_START.md
│   ├── WINDOWS_SETUP.md
│   ├── URGENT_FIX_CSS.md
│   └── ...
├── scripts/               # 🔧 Scripts
│   ├── setup_first_time.bat
│   ├── start_server.bat
│   ├── fix_static_files.bat
│   └── ...
├── templates_app/         # Django app chính
│   ├── models.py
│   ├── views.py
│   ├── templates/         # HTML templates
│   └── static/            # CSS, JS, images
├── wordgen/               # Django project settings
└── staticfiles/           # Collected static files (tự động tạo)
```

---

## 🐛 Troubleshooting

### CSS không hiển thị?

```cmd
scripts\fix_static_files.bat
```

Xem chi tiết: [docs/URGENT_FIX_CSS.md](docs/URGENT_FIX_CSS.md)

### Các lỗi thường gặp

| Lỗi | Giải pháp |
|-----|-----------|
| `No module named 'django'` | `pip install -r requirements.txt` |
| `Port already in use` | Đổi port trong `run_waitress.py` |
| `python is not recognized` | Thêm Python vào PATH |

Xem thêm: [docs/QUICK_START.md](docs/QUICK_START.md)

---

## 📝 License

Internal use only - Nội bộ Agribank

## 👥 Liên hệ

Agribank Chi nhánh Giá Rai Bạc Liêu

---

**Phiên bản:** 1.0
**Cập nhật:** 2025
