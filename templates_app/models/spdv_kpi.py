"""
Model thống kê chỉ tiêu SPDV (theo giao dịch viên).
"""
from django.db import models
from django.contrib.auth.models import User


# ---------------------------------------------------------------------------
# Thống kê chỉ tiêu Sản phẩm dịch vụ (Kế toán Ngân quỹ)
# ---------------------------------------------------------------------------

class SPDVKpiRecord(models.Model):
    """
    Kết quả chỉ tiêu SPDV đã import cho 1 GDV trong 1 tháng (ghi đè khi import lại,
    không cộng dồn — tránh phải tự khử trùng lặp dòng thô).
    """
    METRIC_CHOICES = [
        ('THE', 'Số lượng thẻ'),
        ('AGRIBANK_PLUS', 'Agribank Plus'),
        ('MOBILE_BANKING', 'Mobile Banking'),
        ('TK_PLUS', 'Tài khoản Plus'),
        ('OTT', 'Đăng ký OTT'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='spdv_kpi_records',
        verbose_name="Giao dịch viên"
    )
    metric_type = models.CharField(max_length=20, choices=METRIC_CHOICES, verbose_name="Chỉ tiêu")
    year = models.IntegerField(verbose_name="Năm")
    month = models.IntegerField(verbose_name="Tháng")
    quantity = models.IntegerField(default=0, verbose_name="Số lượng đạt được")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='spdv_kpi_records_updated', verbose_name="Người import"
    )

    class Meta:
        verbose_name = "Kết quả chỉ tiêu SPDV"
        verbose_name_plural = "Kết quả chỉ tiêu SPDV"
        unique_together = ('user', 'metric_type', 'year', 'month')
        ordering = ['-year', '-month', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.get_metric_type_display()} {self.month}/{self.year}: {self.quantity}"


class SPDVKpiTarget(models.Model):
    """Chỉ tiêu SPDV do Trưởng phòng/Admin đặt cho từng GDV theo tháng."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='spdv_kpi_targets',
        verbose_name="Giao dịch viên"
    )
    metric_type = models.CharField(max_length=20, choices=SPDVKpiRecord.METRIC_CHOICES, verbose_name="Chỉ tiêu")
    year = models.IntegerField(verbose_name="Năm")
    month = models.IntegerField(verbose_name="Tháng")
    target_quantity = models.IntegerField(default=0, verbose_name="Số lượng chỉ tiêu giao")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='spdv_kpi_targets_updated', verbose_name="Người đặt chỉ tiêu"
    )

    class Meta:
        verbose_name = "Chỉ tiêu SPDV"
        verbose_name_plural = "Chỉ tiêu SPDV"
        unique_together = ('user', 'metric_type', 'year', 'month')
        ordering = ['-year', '-month', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.get_metric_type_display()} {self.month}/{self.year}: {self.target_quantity}"


class SPDVKpiDetail(models.Model):
    """
    Từng dòng giao dịch góp phần vào 1 SPDVKpiRecord (phục vụ xem/tải chi tiết khi bấm
    vào số "Thực hiện"). Bị xóa và tạo lại mỗi khi import lại đúng (user, metric_type,
    year, month) — không cộng dồn, khớp với cách SPDVKpiRecord hoạt động.
    """
    SOURCE_CHOICES = [
        ('CSP', 'Thẻ CSP'),
        ('VISA', 'Thẻ Visa'),
        ('EMOBILE', 'E-Mobile Banking'),
        ('SMS', 'SMS Banking'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='spdv_kpi_details',
        verbose_name="Giao dịch viên"
    )
    metric_type = models.CharField(max_length=20, choices=SPDVKpiRecord.METRIC_CHOICES, verbose_name="Chỉ tiêu")
    year = models.IntegerField(verbose_name="Năm")
    month = models.IntegerField(verbose_name="Tháng")
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, verbose_name="Nguồn")
    transaction_date = models.DateField(verbose_name="Ngày giao dịch")
    customer_code = models.CharField(max_length=50, blank=True, verbose_name="Mã khách hàng")
    customer_name = models.CharField(max_length=255, blank=True, verbose_name="Họ tên")
    account_number = models.CharField(max_length=50, blank=True, verbose_name="Số tài khoản")

    class Meta:
        verbose_name = "Chi tiết chỉ tiêu SPDV"
        verbose_name_plural = "Chi tiết chỉ tiêu SPDV"
        indexes = [
            models.Index(fields=['user', 'metric_type', 'year', 'month']),
        ]
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.user.username} - {self.get_source_display()} - {self.transaction_date}"
