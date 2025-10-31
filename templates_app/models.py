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
