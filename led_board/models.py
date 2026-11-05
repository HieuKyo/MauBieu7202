from datetime import time
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import (
    FileExtensionValidator, MaxValueValidator, MinValueValidator,
)
from django.db import models

RATE_FIELDS = ('buy_cash', 'sell_cash', 'buy_transfer', 'sell_transfer')
SECONDS_VALIDATORS = [MinValueValidator(3), MaxValueValidator(3600)]


def _rate_field(label):
    # Cho phép rỗng trong DB để ngoại tệ mới tạo không hiện số giả; form bắt buộc nhập.
    return models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal('0.01'))], verbose_name=label,
    )


class ExchangeRate(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name='Ngoại tệ')
    order = models.PositiveIntegerField(default=0, verbose_name='Thứ tự')
    buy_cash = _rate_field('Mua tiền mặt')
    sell_cash = _rate_field('Bán tiền mặt')
    buy_transfer = _rate_field('Mua chuyển khoản')
    sell_transfer = _rate_field('Bán chuyển khoản')
    updated_at = models.DateTimeField(null=True, blank=True, editable=False)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, editable=False,
    )

    class Meta:
        ordering = ['order', 'code']
        verbose_name = 'Tỷ giá'
        verbose_name_plural = 'Tỷ giá'

    def __str__(self):
        return self.code


class RateHistory(models.Model):
    """Mỗi lần thêm, sửa, xóa một ngoại tệ. Giá trị lưu đúng dạng đã hiện trên bảng."""
    code = models.CharField(max_length=10, verbose_name='Ngoại tệ')
    action = models.CharField(max_length=10, verbose_name='Thao tác')
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name='Thời gian')
    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người sửa',
    )

    class Meta:
        ordering = ['-changed_at', '-id']
        verbose_name = 'Lịch sử tỷ giá'
        verbose_name_plural = 'Lịch sử tỷ giá'


class LedSlide(models.Model):
    image = models.ImageField(
        upload_to='led_board/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name='Ảnh',
    )
    order = models.PositiveIntegerField(default=0, verbose_name='Thứ tự')
    is_active = models.BooleanField(default=True, verbose_name='Hiển thị')
    seconds = models.PositiveIntegerField(
        null=True, blank=True, validators=SECONDS_VALIDATORS, verbose_name='Số giây riêng',
    )
    start_date = models.DateField(null=True, blank=True, verbose_name='Từ ngày')
    end_date = models.DateField(null=True, blank=True, verbose_name='Đến ngày')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Ảnh trình chiếu'
        verbose_name_plural = 'Ảnh trình chiếu'

    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        return super().delete(*args, **kwargs)


class BoardSetting(models.Model):
    """Một dòng duy nhất (pk=1), tạo sẵn trong migration."""
    rate_seconds = models.PositiveIntegerField(
        default=20, validators=SECONDS_VALIDATORS,
        verbose_name='Thời gian hiện bảng tỷ giá (giây)',
    )
    savings_seconds = models.PositiveIntegerField(
        default=15, validators=SECONDS_VALIDATORS,
        verbose_name='Thời gian hiện bảng lãi suất (giây)',
    )
    slide_seconds = models.PositiveIntegerField(
        default=8, validators=SECONDS_VALIDATORS,
        verbose_name='Thời gian mặc định mỗi ảnh (giây)',
    )
    savings_product = models.ForeignKey(
        'savings_calculator.SavingsProduct', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Sản phẩm tiết kiệm hiện trên bảng',
    )
    ticker_text = models.CharField(
        max_length=300, blank=True, verbose_name='Dòng chữ chạy (để trống nếu không dùng)',
    )
    board_width = models.PositiveIntegerField(
        default=640, validators=[MinValueValidator(16)],
        verbose_name='Chiều rộng bảng LED (điểm ảnh)',
    )
    board_height = models.PositiveIntegerField(
        default=192, validators=[MinValueValidator(16)],
        verbose_name='Chiều cao bảng LED (điểm ảnh)',
    )
    remind_time = models.TimeField(
        default=time(8, 30), verbose_name='Nhắc nhập tỷ giá sau giờ',
    )
    shutdown_time = models.TimeField(
        null=True, blank=True, verbose_name='Giờ tắt PC LED (để trống nếu không tắt)',
    )

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]
