"""
Models cho app Salary - Quản lý chi lương và thu hộ
"""
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Bank(models.Model):
    """Ngân hàng - Lưu mã ngân hàng và tên đầy đủ"""
    code = models.CharField(
        max_length=20,
        unique=True,
        primary_key=True,
        verbose_name="Mã ngân hàng"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Tên ngân hàng"
    )

    class Meta:
        verbose_name = "Ngân hàng"
        verbose_name_plural = "Ngân hàng"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class CompanyAccount(models.Model):
    """Tài khoản công ty/đơn vị chi trả"""
    account_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Số tài khoản"
    )
    account_name = models.CharField(
        max_length=200,
        verbose_name="Tên tài khoản"
    )
    bank = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        related_name='company_accounts',
        verbose_name="Ngân hàng"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Tài khoản công ty"
        verbose_name_plural = "Tài khoản công ty"
        ordering = ['account_number']

    def __str__(self):
        return f"{self.account_number} - {self.account_name}"


class Beneficiary(models.Model):
    """Người thụ hưởng - Nhân viên nhận lương/thu hộ"""
    full_name = models.CharField(
        max_length=200,
        verbose_name="Họ và tên"
    )
    account_number = models.CharField(
        max_length=50,
        verbose_name="Số tài khoản"
    )
    bank = models.ForeignKey(
        Bank,
        on_delete=models.PROTECT,
        related_name='beneficiaries',
        verbose_name="Ngân hàng",
        null=True,
        blank=True
    )
    bank_code = models.CharField(
        max_length=20,
        verbose_name="Mã ngân hàng",
        blank=True,
        help_text="Mã ngân hàng từ file import"
    )
    company = models.ForeignKey(
        CompanyAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='beneficiaries',
        verbose_name="Công ty"
    )
    note = models.TextField(
        blank=True,
        verbose_name="Ghi chú"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Người thụ hưởng"
        verbose_name_plural = "Người thụ hưởng"
        ordering = ['full_name']
        unique_together = [['account_number', 'bank_code']]

    def __str__(self):
        return f"{self.full_name} - {self.account_number}"


class ProcessingHistory(models.Model):
    """Lịch sử xử lý file"""
    TRANSACTION_TYPE_CHOICES = [
        ('PAYROLL', 'Chi trả lương'),
        ('COLLECTION', 'Thu hộ'),
    ]

    STATUS_CHOICES = [
        ('SUCCESS', 'Thành công'),
        ('ERROR', 'Lỗi'),
        ('PARTIAL', 'Một phần'),
    ]

    filename = models.CharField(
        max_length=255,
        verbose_name="Tên file"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name="Loại giao dịch"
    )
    company_account = models.ForeignKey(
        CompanyAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processing_histories',
        verbose_name="Tài khoản công ty"
    )
    total_records = models.IntegerField(
        default=0,
        verbose_name="Tổng số bản ghi"
    )
    successful_records = models.IntegerField(
        default=0,
        verbose_name="Số bản ghi thành công"
    )
    failed_records = models.IntegerField(
        default=0,
        verbose_name="Số bản ghi lỗi"
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Tổng số tiền"
    )
    duplicate_accounts = models.TextField(
        blank=True,
        verbose_name="Tài khoản trùng lặp",
        help_text="Danh sách STK trùng lặp, ngăn cách bởi dấu phẩy"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SUCCESS',
        verbose_name="Trạng thái"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Thông báo lỗi"
    )
    output_file = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="File đầu ra"
    )
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salary_processings',
        verbose_name="Người xử lý"
    )
    processed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Thời gian xử lý"
    )

    class Meta:
        verbose_name = "Lịch sử xử lý"
        verbose_name_plural = "Lịch sử xử lý"
        ordering = ['-processed_at']

    def __str__(self):
        return f"{self.filename} - {self.get_transaction_type_display()} - {self.processed_at.strftime('%d/%m/%Y %H:%M')}"
