# Hướng Dẫn Setup Template Storage - Giải Quyết Vấn Đề Template Hết Hạn

## 📋 Tổng Quan Vấn Đề

**Hiện trạng:**
- Template bị lỗi "We're sorry, we can't open... because we found a problem with its contents" sau ~1 tuần không sử dụng
- Nguyên nhân: Template được upload vào folder tạm thời → Bị xóa sau 1 tuần → File corrupt khi generate

**Giải pháp:** 3 phương án tùy theo nhu cầu

---

## 🎯 GIẢI PHÁP 1: Setup Hệ Thống Chuẩn (KHUYÊN DÙNG)

### Ưu điểm:
- ✅ Template **không bao giờ hết hạn**
- ✅ Quản lý qua Django Admin
- ✅ Không phụ thuộc folder bên ngoài
- ✅ Backup dễ dàng

### Nhược điểm:
- ❌ Chiếm dung lượng server
- ❌ Phải upload lại templates

### Các bước thực hiện:

```bash
# Bước 1: Migrate database (tạo bảng templates)
cd /home/user/MauBieu7202
python manage.py migrate

# Bước 2: Tạo media folder
mkdir -p media/templates/docx
chmod -R 755 media

# Bước 3: Tạo superuser (nếu chưa có)
python manage.py createsuperuser

# Bước 4: Chạy server
python manage.py runserver 0.0.0.0:8000

# Bước 5: Truy cập Admin và upload templates
# URL: http://your-server-ip:8000/admin
# Login → Templates → Add Template → Upload file .docx
```

### Verify:
```bash
# Kiểm tra templates đã upload
ls -lah media/templates/docx/

# Kiểm tra database
python manage.py shell
>>> from templates_app.models import Template
>>> Template.objects.all()
```

---

## 🎯 GIẢI PHÁP 2: Link Trực Tiếp Folder `maubieumoi`

### Ưu điểm:
- ✅ Không chiếm dung lượng server
- ✅ Cập nhật template dễ (chỉ cần thay file)
- ✅ Dùng chung với hệ thống khác

### Nhược điểm:
- ❌ **CRITICAL**: Nếu mất kết nối folder → Hệ thống ngừng hoạt động
- ❌ Performance chậm hơn (nếu qua network)

### Trường hợp A: Folder trên cùng máy server

```bash
# Bước 1: Tạo folder maubieumoi
mkdir -p /home/user/maubieumoi
chmod -R 755 /home/user/maubieumoi

# Bước 2: Copy templates vào đây
cp /path/to/your/templates/*.docx /home/user/maubieumoi/

# Bước 3: Tạo symbolic link
mkdir -p /home/user/MauBieu7202/media/templates
ln -sf /home/user/maubieumoi /home/user/MauBieu7202/media/templates/docx

# Bước 4: Verify
ls -la /home/user/MauBieu7202/media/templates/docx/
```

### Trường hợp B: Folder trên máy khác (Network Share)

```bash
# Bước 1: Mount network folder (ví dụ: SMB/CIFS)
sudo mkdir -p /mnt/maubieumoi
sudo mount -t cifs //192.168.1.100/maubieumoi /mnt/maubieumoi \
  -o username=your_user,password=your_pass,uid=1000,gid=1000

# Bước 2: Tạo symbolic link
mkdir -p /home/user/MauBieu7202/media/templates
ln -sf /mnt/maubieumoi /home/user/MauBieu7202/media/templates/docx

# Bước 3: Auto-mount khi khởi động (thêm vào /etc/fstab)
sudo nano /etc/fstab
# Thêm dòng:
# //192.168.1.100/maubieumoi /mnt/maubieumoi cifs username=user,password=pass,uid=1000,gid=1000 0 0

# Bước 4: Test mount
sudo mount -a
```

### ⚠️ Lưu ý:
- Nếu network share disconnect → Toàn bộ hệ thống lỗi
- Cần kiểm tra kết nối thường xuyên
- Setup monitoring để cảnh báo khi mất kết nối

---

## 🎯 GIẢI PHÁP 3: Hybrid - Fallback Mechanism (TỐT NHẤT)

### Ưu điểm:
- ✅ **Kết hợp ưu điểm của cả 2 giải pháp trên**
- ✅ Ưu tiên đọc từ `maubieumoi`
- ✅ Fallback sang `media/` nếu mất kết nối
- ✅ Auto-cache để tăng performance

### Nhược điểm:
- ❌ Phức tạp hơn trong implementation

### Các bước thực hiện:

#### Bước 1: Tạo folder maubieumoi
```bash
mkdir -p /home/user/maubieumoi
chmod -R 755 /home/user/maubieumoi

# Copy templates hiện có vào đây
cp /path/to/templates/*.docx /home/user/maubieumoi/
```

#### Bước 2: Cập nhật settings.py

Thêm vào file `wordgen/settings.py`:

```python
# Template Storage Configuration
OFFLINE_TEMPLATE_PATH = '/home/user/maubieumoi'  # Hoặc '/mnt/maubieumoi' cho network share
TEMPLATE_AUTO_CACHE = True  # Auto-copy từ offline sang media để cache
```

#### Bước 3: Update Template model

Sửa file `templates_app/models.py` (dòng 142-146):

```python
# BEFORE:
file = models.FileField(
    upload_to='templates/docx/',
    validators=[FileExtensionValidator(allowed_extensions=['docx'])],
    verbose_name="File Word (.docx)"
)

# AFTER:
from .storage import HybridTemplateStorage

file = models.FileField(
    upload_to='templates/docx/',
    storage=HybridTemplateStorage(),
    validators=[FileExtensionValidator(allowed_extensions=['docx'])],
    verbose_name="File Word (.docx)"
)
```

#### Bước 4: Migrate và restart

```bash
# Migrate database
python manage.py makemigrations
python manage.py migrate

# Restart server
python manage.py runserver 0.0.0.0:8000
```

#### Bước 5: Test

```python
# Test trong Python shell
python manage.py shell

from templates_app.models import Template
from pathlib import Path

# Kiểm tra storage hoạt động
template = Template.objects.first()
if template:
    print(f"Template path: {template.file.path}")
    print(f"File exists: {template.file.storage.exists(template.file.name)}")
```

### Cách hoạt động:

```
User request template
    ↓
1. Check offline folder (/home/user/maubieumoi)
    ↓
   [Có] → Load template → Auto-cache vào media/ → Return
    ↓
   [Không] → Check media folder
    ↓
   [Có] → Load từ cache → Return
    ↓
   [Không] → Error: File not found
```

---

## 📊 So Sánh Các Giải Pháp

| Tiêu chí | Giải pháp 1 | Giải pháp 2 | Giải pháp 3 |
|----------|-------------|-------------|-------------|
| **Độ tin cậy** | ⭐⭐⭐⭐⭐ | ⭐⭐ (phụ thuộc network) | ⭐⭐⭐⭐⭐ |
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Dễ setup** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Flexibility** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Dung lượng** | ❌ Chiếm | ✅ Không chiếm | ⚠️ Chiếm (cache) |
| **Backup** | ✅ Dễ | ⚠️ Phụ thuộc | ✅ Dễ |

---

## 🔧 Troubleshooting

### Vấn đề 1: File vẫn bị corrupt sau khi setup

**Nguyên nhân:** Template gốc trong `maubieumoi` đã bị corrupt

**Giải pháp:**
```bash
# Test template file
python3 << EOF
from docx import Document
import sys

try:
    doc = Document('/home/user/maubieumoi/your_template.docx')
    print(f"✓ Template OK - {len(doc.paragraphs)} paragraphs")
except Exception as e:
    print(f"✗ Template corrupt: {e}")
    sys.exit(1)
EOF
```

### Vấn đề 2: Permission denied

**Giải pháp:**
```bash
# Fix permissions
sudo chown -R www-data:www-data /home/user/MauBieu7202/media
sudo chmod -R 755 /home/user/MauBieu7202/media
sudo chmod -R 755 /home/user/maubieumoi
```

### Vấn đề 3: Network share disconnect

**Giải pháp:** Tạo script monitoring

```bash
# /usr/local/bin/check_maubieu.sh
#!/bin/bash

MOUNT_POINT="/mnt/maubieumoi"

if ! mountpoint -q "$MOUNT_POINT"; then
    echo "$(date): maubieumoi disconnected! Attempting remount..." >> /var/log/maubieu.log
    mount -a

    if mountpoint -q "$MOUNT_POINT"; then
        echo "$(date): Remount successful" >> /var/log/maubieu.log
    else
        echo "$(date): Remount FAILED! Alert admin!" >> /var/log/maubieu.log
        # Gửi email hoặc SMS cảnh báo
    fi
fi
```

```bash
# Thêm vào crontab để chạy mỗi 5 phút
crontab -e
# Thêm dòng:
# */5 * * * * /usr/local/bin/check_maubieu.sh
```

---

## 🎬 Khuyến Nghị Cuối Cùng

**Nếu hệ thống chỉ chạy trên 1 server:**
→ Dùng **Giải pháp 1** (đơn giản, ổn định nhất)

**Nếu cần dùng chung templates với nhiều hệ thống:**
→ Dùng **Giải pháp 3** (Hybrid) với network share

**Nếu folder maubieumoi trên cùng máy server:**
→ Dùng **Giải pháp 2** (Symbolic link) - đơn giản và nhanh

---

## 📞 Hỗ Trợ

Nếu gặp vấn đề, kiểm tra:
1. Log file: `tail -f /var/log/django.log`
2. Template paths: `python manage.py shell` → kiểm tra `Template.objects.first().file.path`
3. Permissions: `ls -la media/templates/docx/`
4. Network (nếu dùng share): `mountpoint /mnt/maubieumoi`
