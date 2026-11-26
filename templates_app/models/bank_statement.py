"""
Model phân tích sao kê ngân hàng: file sao kê, tên tài khoản, giao dịch.
"""
from django.db import models


# ====================
# Bank Statement Analyzer Models
# ====================

class BankStatement(models.Model):
    """Sao kê ngân hàng được upload"""
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày upload")
    file_name = models.CharField(max_length=255, verbose_name="Tên file")
    total_transactions = models.IntegerField(verbose_name="Tổng số giao dịch")
    total_debit = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        default=0,
        verbose_name="Tổng tiền ghi nợ"
    )
    total_credit = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        default=0,
        verbose_name="Tổng tiền ghi có"
    )
    final_balance = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        default=0,
        verbose_name="Số dư cuối kỳ"
    )
    processed = models.BooleanField(default=False, verbose_name="Đã xử lý")
    unmatched_rows = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Dòng file CSP/MSPH02 không khớp DPTB18"
    )
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bank_statements',
        verbose_name="Người upload"
    )

    class Meta:
        verbose_name = "Sao kê ngân hàng"
        verbose_name_plural = "Sao kê ngân hàng"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} - {self.uploaded_at.strftime('%d/%m/%Y %H:%M')}"


class AccountName(models.Model):
    """
    Danh bạ dùng chung "Số TK + Ngân hàng → Tên", do người dùng điền ở sheet
    'TK giao dịch nhiều lần' của file Excel xuất ra rồi upload lại.
    Dùng để điền tên cho các lần phân tích sao kê sau.
    """
    account_key = models.CharField(max_length=50, verbose_name="Số TK (chuẩn hoá)")
    bank_key = models.CharField(max_length=100, blank=True, verbose_name="Ngân hàng (chuẩn hoá)")
    account_number = models.CharField(max_length=50, verbose_name="Số tài khoản")
    bank_name = models.CharField(max_length=100, blank=True, verbose_name="Ngân hàng")
    name = models.CharField(max_length=200, verbose_name="Tên chủ tài khoản")
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='account_names',
        verbose_name="Người cập nhật"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lúc")

    class Meta:
        verbose_name = "Danh bạ tài khoản"
        verbose_name_plural = "Danh bạ tài khoản"
        unique_together = [('account_key', 'bank_key')]

    def __str__(self):
        return f"{self.bank_name} {self.account_number} - {self.name}"


class Transaction(models.Model):
    """Giao dịch trong sao kê ngân hàng"""
    statement = models.ForeignKey(
        BankStatement,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Sao kê"
    )
    stt = models.IntegerField(verbose_name="STT")
    transaction_date = models.DateField(verbose_name="Ngày giao dịch")
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name="Số tiền ghi nợ"
    )
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name="Số tiền ghi có"
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="Số dư sau GD"
    )
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ngân hàng"
    )
    account_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Số tài khoản"
    )
    beneficiary_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tên người thụ hưởng"
    )
    description = models.TextField(verbose_name="Nội dung gốc")
    transaction_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Loại giao dịch"
    )
    source = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nguồn thông tin đối tác"
    )

    # Raw data fields từ file Excel
    raw_trcdnm = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tên mã giao dịch (raw)"
    )
    raw_tomgntno = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tài khoản đối ứng (raw)"
    )

    class Meta:
        verbose_name = "Giao dịch"
        verbose_name_plural = "Giao dịch"
        ordering = ['statement', 'stt']
        indexes = [
            models.Index(fields=['statement', 'transaction_date']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.stt}. {self.transaction_date.strftime('%d/%m/%Y')} - {self.transaction_type}"
