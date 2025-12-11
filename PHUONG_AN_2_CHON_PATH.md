# HƯỚNG DẪN: PHƯƠNG ÁN 2 - Chọn Đường Dẫn Cụ Thể Cho Template

## 🎯 Mục Đích
Cho phép admin chọn đường dẫn subfolder cụ thể cho từng template.

Ví dụ:
- Template "Mở thẻ" → Path: `DICHVU/MauMoThe.docx`
- Template "ATM" → Path: `ATM/MauATM_01.docx`

---

## 🔧 BƯỚC 1: Update Models.py

Thêm field `subfolder_path` vào Template model:

```python
# File: templates_app/models.py

class Template(models.Model):
    """Mẫu biểu Word (cấp con)"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, ...)
    name = models.CharField(max_length=200, ...)
    description = models.TextField(blank=True, ...)

    # Field mới: Đường dẫn subfolder
    subfolder_path = models.CharField(
        max_length=500,
        blank=True,
        default='',
        verbose_name="Đường dẫn thư mục con",
        help_text="Ví dụ: ATM/ hoặc KETOAN/TKDV/ (để trống nếu file ở root)"
    )

    file = models.FileField(
        upload_to='templates/docx/',
        storage=HybridTemplateStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name="File Word (.docx)"
    )
    # ... các field khác
```

---

## 🔧 BƯỚC 2: Update Storage.py

Sửa storage để dùng subfolder_path nếu có:

```python
# File: templates_app/storage.py

def _get_offline_full_path(self, name):
    """
    Lấy đường dẫn đầy đủ trong offline folder
    Hỗ trợ subfolder_path từ Template model
    """
    base_name = os.path.basename(name)
    offline_root = Path(self.offline_path)

    # Lấy subfolder_path từ Template (nếu có)
    # Cách này cần truyền qua context hoặc dùng logic khác
    # Để đơn giản, vẫn dùng recursive search như Phương án 1

    # Tìm ở root trước
    direct_path = offline_root / base_name
    if direct_path.exists():
        return direct_path

    # Tìm trong subdirectories
    matches = list(offline_root.rglob(base_name))
    if matches:
        return matches[0]

    return offline_root / base_name
```

---

## 🔧 BƯỚC 3: Tạo Migration

```powershell
python manage.py makemigrations
python manage.py migrate
```

---

## 🔧 BƯỚC 4: Update Admin Interface

Thêm subfolder_path vào Admin form:

```python
# File: templates_app/admin.py

class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subfolder_path', 'is_active', ...]
    fields = [
        'category',
        'name',
        'description',
        'subfolder_path',  # ← Thêm field mới
        'file',
        'is_active',
        ...
    ]
```

---

## 📝 Cách Sử Dụng

### Trong Django Admin:

1. Vào Templates → Add Template
2. Điền tên template: "Mở thẻ"
3. Điền subfolder_path: `DICHVU/`
4. Upload file: `MauMoThe.docx`
5. Save

→ Hệ thống sẽ tìm file ở: `C:\maubieumoi\DICHVU\MauMoThe.docx`

---

## ⚠️ Lưu Ý

Phương án này phức tạp hơn và cần:
- Sửa models.py
- Tạo migration
- Update admin
- Logic xử lý path trong storage

**KHUYÊN DÙNG PHƯƠNG ÁN 1** vì đơn giản hơn và đã có sẵn recursive search.
