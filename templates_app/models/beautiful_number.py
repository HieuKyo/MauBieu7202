"""
Model số đẹp: biểu phí chi tiết, biểu phí theo yêu cầu, danh sách số đẹp.
"""
from django.db import models


# ====================
# Beautiful Number Fee Management Models
# ====================

class DetailedFeeTier(models.Model):
    """
    Biểu phí chi tiết dựa trên số lượng và loại số đẹp (Bảng 1).
    Phí phụ thuộc vào số lượng số đẹp (2-10+) và loại (Thường/Đặc biệt).
    """
    # Định nghĩa các loại số đẹp
    IS_SPECIAL_TYPE = "SPECIAL"
    IS_NORMAL_TYPE = "NORMAL"
    TYPE_CHOICES = [
        (IS_NORMAL_TYPE, "Loại thường"),
        (IS_SPECIAL_TYPE, "Loại đặc biệt (Lặp, Lộc Phát, Tiến)"),
    ]

    quantity = models.PositiveSmallIntegerField(
        verbose_name="Số lượng số đẹp",
        help_text="Số lượng số đẹp trong tài khoản (2-10+)"
    )
    fee_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=IS_NORMAL_TYPE,
        verbose_name="Loại số đẹp"
    )
    min_fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Phí tối thiểu (VNĐ)",
        help_text="Mức phí tối thiểu cho loại số đẹp này"
    )
    max_fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Phí tối đa (VNĐ)",
        null=True,
        blank=True,
        help_text="Mức phí tối đa. Để trống = 'Thỏa thuận'"
    )

    class Meta:
        verbose_name = "Bậc phí chi tiết"
        verbose_name_plural = "Biểu phí chi tiết (Bảng 1)"
        unique_together = [['quantity', 'fee_type']]  # Đảm bảo không trùng lặp
        ordering = ['quantity', 'fee_type']

    def __str__(self):
        return f"{self.quantity} số đẹp ({self.get_fee_type_display()}): {self.min_fee:,} - {self.max_fee:,} VNĐ" if self.max_fee else f"{self.quantity} số đẹp ({self.get_fee_type_display()}): Từ {self.min_fee:,} VNĐ (Thỏa thuận)"


class OnRequestFeeTier(models.Model):
    """
    Biểu phí chọn số theo yêu cầu (Bảng 2).
    Áp dụng khi khách hàng tự chọn số tài khoản.
    """
    min_quantity = models.PositiveSmallIntegerField(
        verbose_name="Từ (số lượng)",
        help_text="Số lượng số đẹp tối thiểu trong khoảng này"
    )
    max_quantity = models.PositiveSmallIntegerField(
        verbose_name="Đến (số lượng)",
        help_text="Số lượng số đẹp tối đa trong khoảng này"
    )
    min_fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Phí tối thiểu (VNĐ)"
    )
    max_fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Phí tối đa (VNĐ)"
    )

    class Meta:
        verbose_name = "Bậc phí theo yêu cầu"
        verbose_name_plural = "Biểu phí theo yêu cầu (Bảng 2)"
        ordering = ['min_quantity']

    def __str__(self):
        return f"Chọn {self.min_quantity}-{self.max_quantity} số: {self.min_fee:,} - {self.max_fee:,} VNĐ"


class BeautifulNumber(models.Model):
    """
    Danh sách số đẹp có sẵn để khách hàng chọn.
    Phân loại theo mức giá và loại số đẹp (Tài lộc, Hợp tuổi, Phong thủy...).
    """
    # Định nghĩa các mức giá
    PRICE_500K_1M = "500K-1M"
    PRICE_1M_3M = "1M-3M"
    PRICE_3M_5M = "3M-5M"
    PRICE_5M_10M = "5M-10M"
    PRICE_10M_20M = "10M-20M"
    PRICE_20M_PLUS = "20M+"

    PRICE_TIER_CHOICES = [
        (PRICE_500K_1M, "550,000 - 1,100,000 VNĐ"),
        (PRICE_1M_3M, "1,100,000 - 3,300,000 VNĐ"),
        (PRICE_3M_5M, "3,300,000 - 5,500,000 VNĐ"),
        (PRICE_5M_10M, "5,500,000 - 11,000,000 VNĐ"),
        (PRICE_10M_20M, "11,000,000 - 22,000,000 VNĐ"),
        (PRICE_20M_PLUS, "Trên 22,000,000 VNĐ"),
    ]

    # Định nghĩa các loại số đẹp
    CATEGORY_LOC_PHAT = "LOC_PHAT"
    CATEGORY_TAI_LOC = "TAI_LOC"
    CATEGORY_HOP_TUOI = "HOP_TUOI"
    CATEGORY_PHONG_THUY = "PHONG_THUY"
    CATEGORY_SO_LAP = "SO_LAP"
    CATEGORY_SO_TIEN = "SO_TIEN"
    CATEGORY_SO_DOI_XUNG = "SO_DOI_XUNG"
    CATEGORY_DAC_BIET = "DAC_BIET"

    CATEGORY_CHOICES = [
        (CATEGORY_LOC_PHAT, "Lộc Phát (Số 6, 8)"),
        (CATEGORY_TAI_LOC, "Tài Lộc"),
        (CATEGORY_HOP_TUOI, "Hợp Tuổi"),
        (CATEGORY_PHONG_THUY, "Phong Thủy"),
        (CATEGORY_SO_LAP, "Số Lặp"),
        (CATEGORY_SO_TIEN, "Số Tiến"),
        (CATEGORY_SO_DOI_XUNG, "Số Đối Xứng"),
        (CATEGORY_DAC_BIET, "Đặc Biệt"),
    ]

    account_number = models.CharField(
        max_length=13,
        unique=True,
        verbose_name="Số tài khoản",
        help_text="Số tài khoản 13 số (7202XXXXXXXXX)"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Loại số đẹp",
        db_index=True
    )
    price_tier = models.CharField(
        max_length=20,
        choices=PRICE_TIER_CHOICES,
        verbose_name="Mức giá",
        db_index=True
    )
    fee = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="Phí (VNĐ)",
        help_text="Phí cụ thể cho số này"
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Còn số",
        db_index=True
    )
    description = models.TextField(
        blank=True,
        verbose_name="Mô tả",
        help_text="Mô tả đặc điểm của số đẹp này"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày thêm"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Ngày cập nhật"
    )

    class Meta:
        verbose_name = "Số đẹp có sẵn"
        verbose_name_plural = "Danh sách số đẹp có sẵn"
        ordering = ['price_tier', 'category', 'account_number']
        indexes = [
            models.Index(fields=['category', 'price_tier', 'is_available']),
        ]

    def __str__(self):
        status = "✓" if self.is_available else "✗"
        return f"{status} {self.account_number} - {self.get_category_display()} - {self.fee:,} VNĐ"
