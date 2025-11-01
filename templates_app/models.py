from django.db import models
from django.contrib.auth.models import Group
from django.core.validators import FileExtensionValidator


class Category(models.Model):
    """Danh mục mẫu biểu (cấp cha)"""
    name = models.CharField(max_length=200, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Variable(models.Model):
    """Biến dùng trong template Word"""
    FIELD_TYPES = [
        ('text', 'Văn bản'),
        ('textarea', 'Đoạn văn'),
        ('date', 'Ngày tháng'),
        ('number', 'Con số'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Tên biến (không dấu, không khoảng trắng)")
    label = models.CharField(max_length=200, verbose_name="Nhãn hiển thị")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text', verbose_name="Kiểu dữ liệu")
    help_text = models.CharField(max_length=500, blank=True, verbose_name="Gợi ý nhập liệu")
    required = models.BooleanField(default=True, verbose_name="Bắt buộc nhập")
    default_value = models.TextField(blank=True, verbose_name="Giá trị mặc định")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Biến"
        verbose_name_plural = "Biến"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.label})"


class Template(models.Model):
    """Mẫu biểu Word (cấp con)"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='templates', verbose_name="Danh mục")
    name = models.CharField(max_length=200, verbose_name="Tên mẫu biểu")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    file = models.FileField(
        upload_to='templates/docx/',
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name="File Word (.docx)"
    )
    variables = models.ManyToManyField(Variable, through='TemplateVariable', related_name='templates', verbose_name="Biến")
    allowed_groups = models.ManyToManyField(Group, blank=True, related_name='templates', verbose_name="Nhóm được phép truy cập")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Mẫu biểu"
        verbose_name_plural = "Mẫu biểu"
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def user_has_access(self, user):
        """Kiểm tra user có quyền truy cập template này không"""
        if user.is_superuser:
            return True
        if self.allowed_groups.count() == 0:
            return True  # Nếu không có group nào được gán, cho phép tất cả
        return self.allowed_groups.filter(id__in=user.groups.all()).exists()


class TemplateVariable(models.Model):
    """Liên kết giữa Template và Variable"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, verbose_name="Mẫu biểu")
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE, verbose_name="Biến")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị trong form")

    class Meta:
        verbose_name = "Biến của mẫu biểu"
        verbose_name_plural = "Biến của mẫu biểu"
        ordering = ['order', 'variable__name']
        unique_together = ['template', 'variable']

    def __str__(self):
        return f"{self.template.name} - {self.variable.name}"


class Customer(models.Model):
    """Thông tin khách hàng"""

    NGHE_NGHIEP_CHOICES = [
        ('Công chức viên chức', 'Công chức viên chức'),
        ('Kinh doanh tự do', 'Kinh doanh tự do'),
        ('Nội trợ', 'Nội trợ'),
        ('Khác', 'Khác'),
    ]

    NOI_CAP_CHOICES = [
        ('Cục CSQLHC về TTXH', 'Cục CSQLHC về TTXH'),
        ('Bộ Công An', 'Bộ Công An'),
        ('Khác', 'Khác'),
    ]

    # Mã khách hàng
    ma_khach_hang = models.CharField(max_length=50, blank=True, verbose_name="Mã khách hàng", db_index=True)

    # Thông tin cá nhân cơ bản
    ho_ten = models.CharField(max_length=200, verbose_name="Họ và tên", db_index=True)
    ngay_sinh = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gioi_tinh = models.CharField(
        max_length=10,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
        default='Nam',
        verbose_name="Giới tính"
    )

    # Giấy tờ tùy thân
    so_cmnd = models.CharField(max_length=20, unique=True, verbose_name="Số CMND/CCCD", db_index=True)
    ngay_cap_cmnd = models.DateField(null=True, blank=True, verbose_name="Ngày cấp CMND/CCCD")
    noi_cap_cmnd = models.CharField(
        max_length=50,
        choices=NOI_CAP_CHOICES,
        default='Cục CSQLHC về TTXH',
        verbose_name="Nơi cấp CMND/CCCD"
    )
    noi_cap_cmnd_custom = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nơi cấp CMND/CCCD (tùy chỉnh)"
    )

    # Liên hệ
    dia_chi = models.TextField(blank=True, verbose_name="Địa chỉ thường trú")
    so_dien_thoai = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại", db_index=True)
    email = models.EmailField(blank=True, verbose_name="Email")

    # Thông tin nghề nghiệp
    nghe_nghiep = models.CharField(
        max_length=200,
        blank=True,
        choices=NGHE_NGHIEP_CHOICES,
        verbose_name="Nghề nghiệp"
    )
    noi_lam_viec = models.CharField(max_length=200, blank=True, verbose_name="Nơi làm việc")

    # Thông tin tài khoản
    so_tai_khoan = models.CharField(max_length=30, blank=True, verbose_name="Số tài khoản")
    loai_tai_khoan = models.CharField(max_length=100, blank=True, verbose_name="Loại tài khoản")

    # Metadata
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        verbose_name="Người tạo"
    )

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ho_ten', 'so_cmnd']),
            models.Index(fields=['so_dien_thoai']),
        ]

    def __str__(self):
        return f"{self.ho_ten} - {self.so_cmnd}"

    def get_noi_cap_display_value(self):
        """Lấy giá trị nơi cấp để hiển thị (ưu tiên custom nếu chọn 'Khác')"""
        if self.noi_cap_cmnd == 'Khác' and self.noi_cap_cmnd_custom:
            return self.noi_cap_cmnd_custom
        return self.noi_cap_cmnd

    def get_data_dict(self):
        """
        Trả về dictionary chứa thông tin khách hàng
        Dùng để auto-fill form
        """
        # Date variables for ngay_sinh
        d1, d2, m1, m2, y1, y2, y3, y4 = '', '', '', '', '', '', '', ''
        if self.ngay_sinh:
            date_str = self.ngay_sinh.strftime('%d%m%Y')
            if len(date_str) == 8:
                d1, d2 = date_str[0], date_str[1]
                m1, m2 = date_str[2], date_str[3]
                y1, y2, y3, y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        data = {
            'ma_khach_hang': self.ma_khach_hang or '',
            'ho_ten': self.ho_ten or '',
            'ngay_sinh': self.ngay_sinh.strftime('%d/%m/%Y') if self.ngay_sinh else '',
            'gioi_tinh': self.gioi_tinh or '',
            'so_cmnd': self.so_cmnd or '',
            'ngay_cap_cmnd': self.ngay_cap_cmnd.strftime('%d/%m/%Y') if self.ngay_cap_cmnd else '',
            'noi_cap_cmnd': self.get_noi_cap_display_value(),
            'dia_chi': self.dia_chi or '',
            'so_dien_thoai': self.so_dien_thoai or '',
            'email': self.email or '',
            'nghe_nghiep': self.nghe_nghiep or '',
            'noi_lam_viec': self.noi_lam_viec or '',
            'so_tai_khoan': self.so_tai_khoan or '',
            'loai_tai_khoan': self.loai_tai_khoan or '',
            'ghi_chu': self.ghi_chu or '',
            # Date variables (ngày sinh)
            'd1': d1,
            'd2': d2,
            'm1': m1,
            'm2': m2,
            'y1': y1,
            'y2': y2,
            'y3': y3,
            'y4': y4,
        }
        return data


class BranchConfig(models.Model):
    """
    Cấu hình thông tin chi nhánh (Singleton - chỉ có 1 record duy nhất)
    """
    ten_chi_nhanh = models.CharField(max_length=200, verbose_name="Tên chi nhánh", default="Chi nhánh Giá Rai Bạc Liêu")
    ten_chi_nhanh_hoa = models.CharField(max_length=200, verbose_name="Tên chi nhánh (IN HOA)", default="CHI NHÁNH GIÁ RAI BẠC LIÊU")
    mst = models.CharField(max_length=50, verbose_name="Mã số thuế", blank=True)
    giao_dich_vien = models.CharField(max_length=200, verbose_name="Giao dịch viên", blank=True)
    kiem_soat_vien = models.CharField(max_length=200, verbose_name="Kiểm soát viên", blank=True)
    giam_doc = models.CharField(max_length=200, verbose_name="Giám đốc", blank=True)
    dia_chi_chi_nhanh = models.TextField(verbose_name="Địa chỉ chi nhánh", blank=True)

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Người cập nhật"
    )

    class Meta:
        verbose_name = "Cấu hình Chi nhánh"
        verbose_name_plural = "Cấu hình Chi nhánh"

    def __str__(self):
        return f"Cấu hình: {self.ten_chi_nhanh}"

    def save(self, *args, **kwargs):
        """Đảm bảo chỉ có 1 instance duy nhất (Singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Không cho phép xóa"""
        pass

    @classmethod
    def get_instance(cls):
        """Lấy instance duy nhất, tạo mới nếu chưa tồn tại"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def get_branch_dict(self):
        """Trả về dictionary chứa thông tin chi nhánh để chèn vào template"""
        return {
            'ten_chi_nhanh': self.ten_chi_nhanh or '',
            'ten_chi_nhanh_hoa': self.ten_chi_nhanh_hoa or '',
            'mst': self.mst or '',
            'giao_dich_vien': self.giao_dich_vien or '',
            'kiem_soat_vien': self.kiem_soat_vien or '',
            'giam_doc': self.giam_doc or '',
            'dia_chi_chi_nhanh': self.dia_chi_chi_nhanh or '',
        }
