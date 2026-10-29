from django.db import models
from django.contrib.auth.models import Group, User
from django.core.validators import FileExtensionValidator
import unicodedata
from ..storage import HybridTemplateStorage
from .text_utils import remove_vietnamese_diacritics, num_to_vietnamese_words
from .spdv_kpi import SPDVKpiRecord, SPDVKpiTarget, SPDVKpiDetail
from .cash import CanDoiUpload, BiaChungTu, BiaThuTuIn, CASH_DENOMINATIONS, CashDrawerBalance, CashDrawerStatement, CashPrintConfigBase, CashPrintConfig, CashPrintConfigNopTien, CashPrintConfigChungTuBase, CashPrintConfigBangKeThu, CashPrintConfigBangKeChi, CashPrintConfigDeNghi
from .registration import HDVRegistration, HDVImportRecord, QRRegistration
from .credit import FTPConfig, TDSnapshot
from .report import MailEnvelopeTracking, ReportConfiguration, DongMoTaiKhoanHistory, ATMReportUpload, ATMTransactionReport
from .atm import ATM, ATMManagementBoard, Vehicle, Person, ATMReplenishment, VehicleDutySchedule, ATMDiscrepancy
from .bank_statement import BankStatement, AccountName, Transaction
from .elearning import Course, CourseEnrollment
from .beautiful_number import DetailedFeeTier, OnRequestFeeTier, BeautifulNumber
from .system import GlobalConfig, BranchConfig, AppProgram, UserProfile, Promotion
from .customer import Customer, Business


class Category(models.Model):
    """Danh mục mẫu biểu (cấp cha)"""
    name = models.CharField(max_length=200, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")

    # Cấu hình các nhóm field hiển thị trong form
    # Possible values: customer_basic_info, customer_classification, banking, card, services, print_info
    visible_field_groups = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Nhóm trường hiển thị",
        help_text="Danh sách các nhóm trường cần hiển thị trong form. VD: ['customer_basic_info', 'banking', 'card']"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_visible_field_groups(self):
        """Trả về danh sách field groups, mặc định hiển thị tất cả nếu không cấu hình"""
        if not self.visible_field_groups:
            # Mặc định: hiển thị tất cả field groups
            return [
                'customer_basic_info',  # Gộp: personal_info, id_documents, contact, employment
                'customer_classification',
                'banking',
                'card',
                'services',
                'joint_savings',
                'foreign_currency',
                'print_info'
            ]
        # Handle legacy field groups - convert old groups to new merged group
        converted_groups = []
        old_groups = ['personal_info', 'id_documents', 'contact', 'employment']
        has_old_groups = any(g in self.visible_field_groups for g in old_groups)

        for group in self.visible_field_groups:
            if group in old_groups:
                if 'customer_basic_info' not in converted_groups:
                    converted_groups.append('customer_basic_info')
            else:
                if group not in converted_groups:
                    converted_groups.append(group)

        return converted_groups if has_old_groups else self.visible_field_groups


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
        storage=HybridTemplateStorage(),
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name="File Word (.docx)"
    )
    variables = models.ManyToManyField(Variable, through='TemplateVariable', related_name='templates', verbose_name="Biến")
    allowed_groups = models.ManyToManyField(Group, blank=True, related_name='templates', verbose_name="Nhóm được phép truy cập")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    # Mẫu "nhập nhanh" trên trang In mẫu biểu (vd. Phát hành thẻ Học sinh): chọn sẵn một số mục + trường bắt buộc
    preset_values = models.JSONField(
        default=dict, blank=True, verbose_name="Giá trị chọn sẵn",
        help_text='Tên trường trên form In mẫu biểu → giá trị chọn sẵn khi mở mẫu. '
                  'VD: {"nghe_nghiep": "Học sinh/Sinh viên", "phat_hanh_lan_dau": true}'
    )
    required_fields = models.JSONField(
        default=list, blank=True, verbose_name="Trường bắt buộc",
        help_text='Tên các trường bắt buộc nhập với mẫu này. VD: ["so_dien_thoai"]'
    )
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


# Alias để backward compatibility
#BranchConfig = GlobalConfig
