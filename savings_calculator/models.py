from django.db import models


class SavingsProduct(models.Model):
    """Sản phẩm tiết kiệm (VD: Tiết kiệm thường trả lãi sau, Online...)"""

    name = models.CharField("Tên sản phẩm", max_length=200)
    code = models.CharField("Mã sản phẩm", max_length=50, unique=True)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Đang áp dụng", default=True)
    order = models.PositiveIntegerField("Thứ tự hiển thị", default=0)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Sản phẩm tiết kiệm"
        verbose_name_plural = "Sản phẩm tiết kiệm"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class InterestRate(models.Model):
    """Lãi suất theo kỳ hạn, liên kết với SavingsProduct"""

    product = models.ForeignKey(
        SavingsProduct,
        on_delete=models.CASCADE,
        related_name="rates",
        verbose_name="Sản phẩm",
    )
    term_month_min = models.PositiveIntegerField("Kỳ hạn tối thiểu (tháng)")
    term_month_max = models.PositiveIntegerField("Kỳ hạn tối đa (tháng)")
    interest_rate_yearly = models.FloatField("Lãi suất %/năm")
    description = models.CharField(
        "Mô tả kỳ hạn", max_length=100, blank=True,
        help_text='VD: "6 đến 11 tháng"',
    )
    effective_date = models.DateField(
        "Ngày hiệu lực", null=True, blank=True,
        help_text="Ngày bắt đầu áp dụng mức lãi suất này",
    )
    is_active = models.BooleanField("Đang áp dụng", default=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Ngày cập nhật", auto_now=True)

    class Meta:
        verbose_name = "Lãi suất"
        verbose_name_plural = "Bảng lãi suất"
        ordering = ["product", "term_month_min"]

    def __str__(self):
        return f"{self.product.name} | {self.description} | {self.interest_rate_yearly}%/năm"
