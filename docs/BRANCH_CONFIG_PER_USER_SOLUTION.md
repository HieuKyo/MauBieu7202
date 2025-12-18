# Giải pháp: Branch Config theo User/Đơn vị

## Vấn đề hiện tại

Hiện tại hệ thống sử dụng **GlobalConfig** với **Singleton pattern** (chỉ có 1 instance duy nhất).
Điều này có nghĩa là:
- Tất cả user đều sử dụng chung một bộ thông tin chi nhánh
- User ở **CN Giá Rai** và user ở **PGD Láng Tròn** đều hiển thị cùng thông tin branch-config

## Giải pháp đề xuất

### Option 1: Tạo Model BranchConfig mới (Khuyến nghị ⭐)

Tạo model `BranchConfig` mới, giữ nguyên `GlobalConfig` làm fallback default.

#### Ưu điểm:
- ✅ Không phá vỡ code hiện tại
- ✅ Mỗi chi nhánh/PGD có config riêng
- ✅ Dễ quản lý và mở rộng
- ✅ Có thể gán config cho từng user hoặc nhóm

#### Cách triển khai:

```python
# templates_app/models.py

class BranchConfig(models.Model):
    """
    Cấu hình chi nhánh/phòng giao dịch riêng cho từng đơn vị
    Mỗi đơn vị có thể có cấu hình riêng
    """

    BRANCH_TYPE_CHOICES = [
        ('CHI_NHANH', 'Chi nhánh'),
        ('PGD', 'Phòng giao dịch'),
    ]

    # Thông tin đơn vị
    branch_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã đơn vị",
        help_text="Ví dụ: HOI_SO, PGD_LANG_TRON"
    )
    branch_type = models.CharField(
        max_length=20,
        choices=BRANCH_TYPE_CHOICES,
        default='CHI_NHANH',
        verbose_name="Loại đơn vị"
    )
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    # Thông tin chi nhánh (giống GlobalConfig)
    ten_chi_nhanh = models.CharField(max_length=200, verbose_name="Tên chi nhánh")
    ten_chi_nhanh_hoa = models.CharField(max_length=200, verbose_name="Tên chi nhánh (IN HOA)")
    ma_chi_nhanh = models.CharField(max_length=20, verbose_name="Mã chi nhánh", blank=True)
    mst = models.CharField(max_length=50, verbose_name="Mã số thuế", blank=True)
    gcndkdn = models.CharField(max_length=50, verbose_name="GCNĐKDN", blank=True)
    mst_chi_nhanh = models.CharField(max_length=50, verbose_name="MST chi nhánh", blank=True)
    dia_chi_chi_nhanh = models.TextField(verbose_name="Địa chỉ", blank=True)
    dien_thoai_chi_nhanh = models.CharField(max_length=50, verbose_name="Điện thoại", blank=True)
    so_fax = models.CharField(max_length=50, verbose_name="Số Fax", blank=True)
    dia_danh = models.CharField(max_length=200, verbose_name="Địa danh", blank=True)

    # Nhân sự
    nguoi_dai_dien = models.CharField(max_length=200, verbose_name="Người đại diện", blank=True)
    chuc_vu = models.CharField(max_length=200, verbose_name="Chức vụ", blank=True)
    so_uy_quyen = models.CharField(max_length=100, verbose_name="Số uỷ quyền", blank=True)
    ngay_uy_quyen = models.DateField(verbose_name="Ngày uỷ quyền", null=True, blank=True)
    giao_dich_vien = models.CharField(max_length=200, verbose_name="Giao dịch viên", blank=True)
    kiem_soat_vien = models.CharField(max_length=200, verbose_name="Kiểm soát viên", blank=True)
    giam_doc = models.CharField(max_length=200, verbose_name="Giám đốc", blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Cấu hình Chi nhánh"
        verbose_name_plural = "Cấu hình Chi nhánh"
        ordering = ['branch_code']

    def __str__(self):
        return f"{self.get_branch_type_display()}: {self.ten_chi_nhanh}"

    def get_all_variables(self):
        """Trả về tất cả biến dưới dạng dict"""
        from datetime import datetime

        data = {
            'ten_chi_nhanh': self.ten_chi_nhanh or '',
            'ten_chi_nhanh_hoa': self.ten_chi_nhanh_hoa or '',
            'ma_chi_nhanh': self.ma_chi_nhanh or '',
            'mst': self.mst or '',
            'gcndkdn': self.gcndkdn or '',
            'mst_chi_nhanh': self.mst_chi_nhanh or '',
            'dia_chi_chi_nhanh': self.dia_chi_chi_nhanh or '',
            'dien_thoai_chi_nhanh': self.dien_thoai_chi_nhanh or '',
            'so_fax': self.so_fax or '',
            'dia_danh': self.dia_danh or '',
            'nguoi_dai_dien': self.nguoi_dai_dien or '',
            'chuc_vu': self.chuc_vu or '',
            'so_uy_quyen': self.so_uy_quyen or '',
            'ngay_uy_quyen': self.ngay_uy_quyen.strftime('%d/%m/%Y') if self.ngay_uy_quyen else '',
            'giao_dich_vien': self.giao_dich_vien or '',
            'kiem_soat_vien': self.kiem_soat_vien or '',
            'giam_doc': self.giam_doc or '',
        }
        return data

    @classmethod
    def get_for_user(cls, user):
        """
        Lấy BranchConfig cho user dựa vào UserProfile.branch
        Nếu không tìm thấy, fallback về GlobalConfig
        """
        try:
            # Lấy branch code từ UserProfile
            user_branch = user.profile.branch

            if user_branch:
                # Tìm BranchConfig tương ứng
                branch_config = cls.objects.filter(
                    branch_code=user_branch,
                    is_active=True
                ).first()

                if branch_config:
                    return branch_config
        except:
            pass

        # Fallback: trả về GlobalConfig
        from .models import GlobalConfig
        return GlobalConfig.get_instance()
```

#### Cập nhật UserProfile mapping:

```python
# templates_app/models.py - trong class UserProfile

BRANCH_CHOICES = [
    ('HOI_SO', 'Hội sở Giá Rai Bạc Liêu'),
    ('PGD_P1', 'Phòng Giao dịch Phường 1'),
    ('PGD_LANG_TRON', 'Phòng Giao dịch Láng Tròn'),
]
```

#### Cập nhật views.py để sử dụng BranchConfig:

```python
# templates_app/views.py

# Thay đổi từ:
global_config = GlobalConfig.get_instance()
data.update(global_config.get_all_variables())

# Thành:
branch_config = BranchConfig.get_for_user(request.user)
data.update(branch_config.get_all_variables())
```

---

### Option 2: Bỏ Singleton Pattern trong GlobalConfig

Cho phép nhiều instances của GlobalConfig, mỗi instance cho một chi nhánh.

#### Ưu điểm:
- ✅ Đơn giản hóa model
- ✅ Sử dụng lại code hiện tại

#### Nhược điểm:
- ❌ Phải refactor nhiều code hiện tại
- ❌ Breaking changes cho các views đã sử dụng `get_instance()`

---

## Cách triển khai được khuyến nghị

### Bước 1: Tạo model BranchConfig

Thêm model mới vào `templates_app/models.py` như đã mô tả ở Option 1.

### Bước 2: Tạo migration

```bash
python manage.py makemigrations templates_app --name add_branch_config_model
python manage.py migrate
```

### Bước 3: Tạo dữ liệu mẫu

```python
# Tạo cấu hình cho CN Giá Rai
BranchConfig.objects.create(
    branch_code='HOI_SO',
    branch_type='CHI_NHANH',
    ten_chi_nhanh='Chi nhánh Giá Rai Bạc Liêu',
    ten_chi_nhanh_hoa='CHI NHÁNH GIÁ RAI BẠC LIÊU',
    mst='0123456789',
    dia_chi_chi_nhanh='123 Đường ABC, Phường XYZ',
    dien_thoai_chi_nhanh='0291.3822468',
    giam_doc='Lê Văn C',
)

# Tạo cấu hình cho PGD Láng Tròn
BranchConfig.objects.create(
    branch_code='PGD_LANG_TRON',
    branch_type='PGD',
    ten_chi_nhanh='Phòng Giao dịch Láng Tròn',
    ten_chi_nhanh_hoa='PHÒNG GIAO DỊCH LÁNG TRÒN',
    mst='0123456789-001',
    dia_chi_chi_nhanh='456 Đường DEF, Xã Láng Tròn',
    dien_thoai_chi_nhanh='0291.3822469',
    giam_doc='Nguyễn Văn D',
)
```

### Bước 4: Cập nhật views.py

Thay thế tất cả các dòng:
```python
global_config = GlobalConfig.get_instance()
```

Thành:
```python
branch_config = BranchConfig.get_for_user(request.user)
```

### Bước 5: Tạo admin interface

```python
# templates_app/admin.py

@admin.register(BranchConfig)
class BranchConfigAdmin(admin.ModelAdmin):
    list_display = ['branch_code', 'ten_chi_nhanh', 'branch_type', 'is_active', 'updated_at']
    list_filter = ['branch_type', 'is_active']
    search_fields = ['branch_code', 'ten_chi_nhanh', 'dia_chi_chi_nhanh']
    fieldsets = (
        ('Thông tin đơn vị', {
            'fields': ('branch_code', 'branch_type', 'is_active')
        }),
        ('Thông tin chi nhánh', {
            'fields': ('ten_chi_nhanh', 'ten_chi_nhanh_hoa', 'ma_chi_nhanh',
                      'mst', 'gcndkdn', 'mst_chi_nhanh', 'dia_chi_chi_nhanh',
                      'dien_thoai_chi_nhanh', 'so_fax', 'dia_danh')
        }),
        ('Nhân sự', {
            'fields': ('nguoi_dai_dien', 'chuc_vu', 'so_uy_quyen', 'ngay_uy_quyen',
                      'giao_dich_vien', 'kiem_soat_vien', 'giam_doc')
        }),
    )
```

---

## Kết quả

Sau khi triển khai:

1. **User GRATHIEU** (branch='HOI_SO') → Sử dụng config của **Chi nhánh Giá Rai**
2. **User GRANTHAO** (branch='PGD_LANG_TRON') → Sử dụng config của **PGD Láng Tròn**
3. User chưa có branch → Sử dụng **GlobalConfig** (fallback mặc định)

---

## Timeline triển khai

- **Giai đoạn 1** (1-2 ngày): Tạo model BranchConfig + migration
- **Giai đoạn 2** (1 ngày): Nhập dữ liệu config cho các chi nhánh/PGD
- **Giai đoạn 3** (2-3 ngày): Refactor views.py để sử dụng BranchConfig.get_for_user()
- **Giai đoạn 4** (1 ngày): Testing và điều chỉnh

**Tổng cộng: ~5-7 ngày**

---

## Lưu ý

- Giữ nguyên `GlobalConfig` để backward compatibility
- Có thể áp dụng từng bước, không cần deploy một lúc
- Test kỹ với các user khác nhau trước khi deploy production
