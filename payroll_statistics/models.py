"""
Models cho app Payroll Statistics
Quản lý thống kê lương và thu hộ
"""
from django.db import models


class PayingUnit(models.Model):
    """
    Đơn vị - Có thể là:
    - Đơn vị trả lương (trong giao dịch Chi lương)
    - Đơn vị thu hộ (trong giao dịch Thu hộ/Khoản trừ)
    """
    account_number = models.CharField(
        max_length=50,
        unique=True,
        primary_key=True,
        verbose_name="Số tài khoản đơn vị"
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Tên đơn vị"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Đơn vị"
        verbose_name_plural = "Đơn vị"
        ordering = ['account_number']

    def __str__(self):
        if self.name:
            return f"{self.account_number} - {self.name}"
        return self.account_number


class BeneficiaryAccount(models.Model):
    """
    Nhân viên/Người hưởng - Có thể là:
    - Nhân viên nhận lương (trong giao dịch Chi lương)
    - Nhân viên bị trừ tiền (trong giao dịch Thu hộ/Khoản trừ)
    """
    unit = models.ForeignKey(
        PayingUnit,
        on_delete=models.CASCADE,
        related_name='beneficiaries',
        verbose_name="Đơn vị"
    )
    account_number = models.CharField(
        max_length=50,
        verbose_name="Số tài khoản nhân viên"
    )
    remark_ref = models.TextField(
        blank=True,
        verbose_name="Nội dung giao dịch mẫu"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Nhân viên/Người hưởng"
        verbose_name_plural = "Nhân viên/Người hưởng"
        unique_together = [['unit', 'account_number']]
        ordering = ['unit', 'account_number']

    def __str__(self):
        return f"{self.unit.account_number} -> {self.account_number}"


class Transaction(models.Model):
    """
    Giao dịch lương/thu hộ
    Lưu chi tiết từng giao dịch bao gồm số tiền, ngày tháng
    """
    TRANSACTION_TYPE_CHOICES = [
        ('payroll', 'Chi lương'),
        ('collection', 'Thu hộ/Khoản trừ'),
    ]

    unit = models.ForeignKey(
        PayingUnit,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Đơn vị"
    )
    beneficiary = models.ForeignKey(
        BeneficiaryAccount,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Nhân viên/Người hưởng"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name="Loại giao dịch"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Số tiền"
    )
    transaction_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày giao dịch"
    )
    remark = models.TextField(
        blank=True,
        verbose_name="Nội dung giao dịch"
    )
    # Lưu dữ liệu gốc từ file
    facno = models.CharField(max_length=50, blank=True, verbose_name="Facno (gốc)")
    tacno = models.CharField(max_length=50, blank=True, verbose_name="Tacno (gốc)")
    rsltremark = models.CharField(max_length=50, blank=True, verbose_name="Rsltremark (gốc)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Giao dịch"
        verbose_name_plural = "Giao dịch"
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['unit', 'transaction_date']),
        ]

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.unit.account_number} - {self.amount}"
