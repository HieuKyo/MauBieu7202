"""
Models cho module quy đổi bút toán tự động
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ConversionRule(models.Model):
    """
    Bảng quy tắc quy đổi - Import từ file hesoquydoi.BAK
    """
    code = models.CharField(
        max_length=50,
        verbose_name="Mã nghiệp vụ",
        help_text="Mã định danh nghiệp vụ"
    )
    debit_account_pattern = models.CharField(
        max_length=100,
        verbose_name="Mẫu tài khoản Nợ",
        help_text="Tài khoản Nợ hoặc đầu mã (ví dụ: 1011, 101)"
    )
    credit_account_pattern = models.CharField(
        max_length=100,
        verbose_name="Mẫu tài khoản Có",
        help_text="Tài khoản Có hoặc đầu mã (ví dụ: 3591, 359)"
    )
    score_1 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Hệ số quy đổi 1",
        help_text="HESOQUAY1 - Điểm số cho loại giao dịch này"
    )
    score_2 = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Hệ số quy đổi 2",
        help_text="HESOQUAY2 - Điểm số phụ (nếu có)"
    )
    formula = models.TextField(
        blank=True,
        null=True,
        verbose_name="Công thức bổ sung",
        help_text="CONGTHUC - Logic bổ sung (ví dụ: LEFT(TKCO,3)=[359])"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả nghiệp vụ",
        help_text="Ghi chú về loại nghiệp vụ này"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang kích hoạt",
        help_text="Quy tắc này có được áp dụng không"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Quy tắc quy đổi"
        verbose_name_plural = "Quy tắc quy đổi"
        ordering = ['code']
        indexes = [
            models.Index(fields=['debit_account_pattern', 'credit_account_pattern']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.debit_account_pattern}/{self.credit_account_pattern}"

    def matches_transaction(self, debit_account, credit_account):
        """
        Kiểm tra xem giao dịch có khớp với quy tắc này không
        Hỗ trợ cả exact match và starts with
        """
        if not self.is_active:
            return False

        # Kiểm tra tài khoản Nợ
        debit_match = (
            debit_account == self.debit_account_pattern or
            debit_account.startswith(self.debit_account_pattern)
        )

        # Kiểm tra tài khoản Có
        credit_match = (
            credit_account == self.credit_account_pattern or
            credit_account.startswith(self.credit_account_pattern)
        )

        return debit_match and credit_match


class TellerTransactionBatch(models.Model):
    """
    Lô giao dịch - Quản lý việc upload file theo tháng
    """
    teller_id = models.CharField(
        max_length=50,
        verbose_name="Mã giao dịch viên",
        help_text="User ID từ tên file (ví dụ: GRATHIEU)"
    )
    teller_name = models.CharField(
        max_length=200,
        verbose_name="Tên giao dịch viên",
        help_text="Tên đầy đủ của giao dịch viên"
    )
    month = models.IntegerField(
        verbose_name="Tháng",
        help_text="Tháng báo cáo (1-12)"
    )
    year = models.IntegerField(
        verbose_name="Năm",
        help_text="Năm báo cáo"
    )
    file_date = models.DateField(
        verbose_name="Ngày file",
        help_text="Ngày tháng từ tên file (DDMMYYYY)"
    )
    total_transactions = models.IntegerField(
        default=0,
        verbose_name="Tổng số giao dịch",
        help_text="Số lượng bút toán được xử lý"
    )
    total_score = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Tổng điểm quy đổi",
        help_text="Tổng điểm quy đổi trong kỳ"
    )
    matched_transactions = models.IntegerField(
        default=0,
        verbose_name="Số giao dịch khớp",
        help_text="Số giao dịch khớp với quy tắc"
    )
    unmatched_transactions = models.IntegerField(
        default=0,
        verbose_name="Số giao dịch không khớp",
        help_text="Số giao dịch không khớp quy tắc"
    )
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('processing', 'Đang xử lý'),
            ('completed', 'Hoàn thành'),
            ('error', 'Có lỗi'),
        ],
        default='processing',
        verbose_name="Trạng thái xử lý"
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Thông báo lỗi"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Lô giao dịch"
        verbose_name_plural = "Lô giao dịch"
        ordering = ['-year', '-month', '-file_date']
        unique_together = ['teller_id', 'file_date']
        indexes = [
            models.Index(fields=['teller_id', 'year', 'month']),
            models.Index(fields=['processing_status']),
        ]

    def __str__(self):
        return f"{self.teller_name} - {self.month}/{self.year}"


class TellerTransactionDetail(models.Model):
    """
    Chi tiết giao dịch - Lưu chi tiết từng bút toán đã xử lý
    """
    batch = models.ForeignKey(
        TellerTransactionBatch,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Lô giao dịch"
    )
    reference_no = models.CharField(
        max_length=50,
        verbose_name="Số tham chiếu",
        help_text="REFNO - Số gom nhóm bút toán Nợ/Có"
    )
    transaction_date = models.DateField(
        verbose_name="Ngày giao dịch",
        help_text="Ngày thực hiện giao dịch"
    )
    transaction_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="Giờ giao dịch",
        help_text="TRTIME - Thời gian giao dịch"
    )
    debit_account = models.CharField(
        max_length=50,
        verbose_name="Tài khoản Nợ",
        help_text="ACCTCD khi TRDRCR='D'"
    )
    credit_account = models.CharField(
        max_length=50,
        verbose_name="Tài khoản Có",
        help_text="ACCTCD khi TRDRCR='C'"
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name="Số tiền",
        help_text="TRAMT - Số tiền giao dịch"
    )
    matched_rule = models.ForeignKey(
        ConversionRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name="Quy tắc khớp"
    )
    score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Điểm quy đổi",
        help_text="Điểm số được tính cho giao dịch này"
    )
    is_matched = models.BooleanField(
        default=False,
        verbose_name="Đã khớp quy tắc",
        help_text="Giao dịch có khớp với quy tắc nào không"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Ghi chú",
        help_text="Ghi chú bổ sung về giao dịch"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Chi tiết giao dịch"
        verbose_name_plural = "Chi tiết giao dịch"
        ordering = ['batch', 'transaction_date', 'transaction_time']
        indexes = [
            models.Index(fields=['batch', 'transaction_date']),
            models.Index(fields=['reference_no']),
            models.Index(fields=['is_matched']),
        ]

    def __str__(self):
        return f"{self.reference_no} - {self.debit_account}/{self.credit_account}"
