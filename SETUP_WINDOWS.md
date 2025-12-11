# Setup Hybrid Template Storage Trên Windows

## 🔧 Fix Lỗi Pull (Chạy Trong PowerShell)

### ⚡ Quick Fix

Copy và paste vào PowerShell:

```powershell
# Xóa file conflict
Remove-Item "payroll_statistics\migrations\0003_rename_payroll_sta_transac_76d4e5_idx_payroll_sta_transac_691697_idx_and_more.py" -ErrorAction SilentlyContinue

# Pull code
git pull origin claude/django-word-template-generator-011CUfkKT1HZ7HQosuoKML8r
```

---

## 📂 Setup Folders trên Windows

### **1. Tạo folder maubieumoi**

```powershell
# Tạo folder C:\maubieumoi
New-Item -ItemType Directory -Path "C:\maubieumoi" -Force

# Verify
Test-Path "C:\maubieumoi"
```

### **2. Tạo media folder**

```powershell
# Trong thư mục project
New-Item -ItemType Directory -Path "media\templates\docx" -Force
```

---

## ⚙️ Update Settings.py Cho Windows

### **Option 1: Auto-detect OS** ⭐ Khuyên dùng

Sửa file `wordgen/settings.py`, thay thế phần config cũ:

```python
import platform

# Template Storage Configuration - Hybrid Fallback Mechanism
# Giải quyết vấn đề template hết hạn sau 1 tuần

# Auto-detect OS
if platform.system() == 'Windows':
    OFFLINE_TEMPLATE_PATH = r'C:\maubieumoi'
else:
    OFFLINE_TEMPLATE_PATH = '/home/user/maubieumoi'

TEMPLATE_AUTO_CACHE = True  # Auto-copy từ offline sang media để cache và tăng performance
```

### **Option 2: Hard-code Windows Path**

```python
# Template Storage Configuration - Hybrid Fallback Mechanism
OFFLINE_TEMPLATE_PATH = r'C:\maubieumoi'  # Raw string với r''
TEMPLATE_AUTO_CACHE = True
```

### **Option 3: Forward Slash (Cũng Work)**

```python
OFFLINE_TEMPLATE_PATH = 'C:/maubieumoi'  # Forward slash
TEMPLATE_AUTO_CACHE = True
```

---

## 🗃️ Migrate Database

```powershell
# Chạy migrations
python manage.py migrate

# Tạo superuser (nếu chưa có)
python manage.py createsuperuser
```

---

## 📋 Copy Templates vào Folder

### **Cách 1: Copy thủ công**

```powershell
# Copy tất cả file .docx vào C:\maubieumoi
Copy-Item "path\to\your\templates\*.docx" -Destination "C:\maubieumoi\"

# List templates
Get-ChildItem "C:\maubieumoi\*.docx"
```

### **Cách 2: Dùng File Explorer**

1. Mở File Explorer (`Win + E`)
2. Vào `C:\maubieumoi`
3. Copy paste file .docx vào đây

---

## ✅ Validate Templates

```powershell
# Validate templates
python validate_templates.py C:\maubieumoi

# Test hybrid storage
python test_hybrid_storage.py
```

---

## 🚀 Chạy Server

```powershell
# Development server
python manage.py runserver 0.0.0.0:8000

# Hoặc chỉ localhost
python manage.py runserver 8000
```

Truy cập:
- **Frontend:** http://localhost:8000
- **Admin:** http://localhost:8000/admin

---

## 🔍 Troubleshooting Windows

### **Lỗi: Module not found**

```powershell
# Install dependencies
pip install -r requirements.txt

# Hoặc từng package
pip install Django python-docx openpyxl pandas unidecode
pip install django-import-export whitenoise gunicorn
```

### **Lỗi: Permission denied**

Chạy PowerShell **as Administrator**:
1. Click chuột phải vào PowerShell
2. Chọn "Run as Administrator"

### **Lỗi: python không được nhận diện**

```powershell
# Kiểm tra Python đã cài chưa
python --version

# Nếu không có, dùng py
py --version

# Thay python bằng py trong các lệnh
py manage.py runserver
```

### **Lỗi: Path không tìm thấy**

Kiểm tra path trong settings.py:

```powershell
# Trong PowerShell, test path
Test-Path "C:\maubieumoi"

# Nếu False → Tạo folder
New-Item -ItemType Directory -Path "C:\maubieumoi" -Force
```

---

## 📝 PowerShell Aliases (Optional)

Tạo file `profile.ps1`:

```powershell
# Aliases cho Django
function Run-Django-Server { python manage.py runserver 8000 }
function Django-Migrate { python manage.py migrate }
function Django-Shell { python manage.py shell }

Set-Alias -Name dj-run -Value Run-Django-Server
Set-Alias -Name dj-migrate -Value Django-Migrate
Set-Alias -Name dj-shell -Value Django-Shell
```

Load profile:
```powershell
. .\profile.ps1
```

Sử dụng:
```powershell
dj-run      # Thay vì python manage.py runserver
dj-migrate  # Thay vì python manage.py migrate
```

---

## 🎯 Complete Setup Script cho Windows

Tạo file `setup-windows.ps1`:

```powershell
# setup-windows.ps1
Write-Host "=== Setup Hybrid Template Storage ===" -ForegroundColor Cyan

# 1. Tạo folders
Write-Host "`n1. Creating folders..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "C:\maubieumoi" -Force | Out-Null
New-Item -ItemType Directory -Path "media\templates\docx" -Force | Out-Null
Write-Host "   ✓ Folders created" -ForegroundColor Green

# 2. Install dependencies
Write-Host "`n2. Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "   ✓ Dependencies installed" -ForegroundColor Green

# 3. Migrate database
Write-Host "`n3. Migrating database..." -ForegroundColor Yellow
python manage.py migrate --noinput
Write-Host "   ✓ Database migrated" -ForegroundColor Green

# 4. Validate templates
Write-Host "`n4. Validating templates..." -ForegroundColor Yellow
if (Test-Path "C:\maubieumoi\*.docx") {
    python validate_templates.py C:\maubieumoi
} else {
    Write-Host "   ⚠ No templates found in C:\maubieumoi" -ForegroundColor Yellow
    Write-Host "   → Copy .docx files to C:\maubieumoi" -ForegroundColor Cyan
}

# 5. Test storage
Write-Host "`n5. Testing hybrid storage..." -ForegroundColor Yellow
python test_hybrid_storage.py

Write-Host "`n=== Setup Complete! ===" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Copy templates to C:\maubieumoi\" -ForegroundColor White
Write-Host "  2. Run: python manage.py runserver" -ForegroundColor White
Write-Host "  3. Visit: http://localhost:8000" -ForegroundColor White
```

Chạy:
```powershell
.\setup-windows.ps1
```

---

## 📊 Kiểm Tra Setup

```powershell
# Kiểm tra folders
Test-Path "C:\maubieumoi"
Test-Path "media\templates\docx"

# Kiểm tra templates
Get-ChildItem "C:\maubieumoi\*.docx" | Select-Object Name, Length

# Kiểm tra database
python manage.py showmigrations

# Kiểm tra settings
python -c "from wordgen import settings; print(settings.OFFLINE_TEMPLATE_PATH)"
```

---

## 🎨 VSCode trên Windows

### **Integrated Terminal:**

1. Mở VSCode
2. Terminal → New Terminal (Ctrl + `)
3. Chọn PowerShell làm default shell
4. Chạy các lệnh như bình thường

### **Recommended Extensions:**

- **Python** (Microsoft)
- **Django** (Baptiste Darthenay)
- **GitLens** (GitKraken)
- **PowerShell** (Microsoft)

---

## 🔐 Virtual Environment (Optional nhưng khuyên dùng)

```powershell
# Tạo venv
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Nếu lỗi execution policy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Sau đó activate lại
.\venv\Scripts\Activate.ps1

# Install dependencies trong venv
pip install -r requirements.txt
```

---

## 📁 Cấu Trúc Thư Mục Windows

```
C:\HIEU\MauBieu7202\
├── media\
│   └── templates\
│       └── docx\           ← Cache folder
├── templates_app\
│   ├── models.py
│   └── storage.py
├── wordgen\
│   └── settings.py         ← Update path cho Windows
├── manage.py
├── requirements.txt
└── db.sqlite3

C:\maubieumoi\              ← Offline templates folder
└── *.docx                  ← Copy templates vào đây
```

---

## ✅ Checklist

- [ ] Pull code thành công
- [ ] Tạo `C:\maubieumoi`
- [ ] Update `settings.py` với Windows path
- [ ] Migrate database
- [ ] Copy templates vào `C:\maubieumoi`
- [ ] Validate templates
- [ ] Test hybrid storage
- [ ] Chạy server thành công
- [ ] Truy cập http://localhost:8000 OK

---

**Nếu gặp vấn đề, check logs:**

```powershell
# Django logs
python manage.py runserver --verbosity 2

# Test storage với verbose output
python test_hybrid_storage.py
```

---

**Good luck! 🚀**
