from django.db import models
from django.contrib.auth.models import User


class OutgoingDocument(models.Model):
    NGUOI_KY_CHOICES = [
        ('TCCong', 'Trần Chí Công'),
        ('NXMo', 'Nguyễn Xuân Mơ'),
        ('LHNgan', 'La Hoàng Ngân'),
        ('other', 'Người khác'),
    ]

    LOAI_CHUYEN_PHAT_CHOICES = [
        ('', 'Không chọn'),
        ('noi_bo', 'Văn bản chuyển phát nội bộ'),
        ('buu_dien', 'Văn bản chuyển phát bưu điện'),
    ]

    so_ky_hieu = models.CharField(max_length=200, verbose_name='Số, ký hiệu văn bản')
    ngay_van_ban = models.DateField(verbose_name='Ngày tháng văn bản')
    ten_loai_trich_yeu = models.TextField(verbose_name='Tên loại và trích yếu nội dung văn bản')
    nguoi_ky = models.CharField(max_length=20, choices=NGUOI_KY_CHOICES, verbose_name='Người ký')
    nguoi_ky_khac = models.CharField(max_length=200, blank=True, default='', verbose_name='Tên người ký (khác)')
    noi_nhan_truong_phong = models.BooleanField(default=False, verbose_name='Trưởng các phòng')
    noi_nhan_giam_doc_pgd = models.BooleanField(default=False, verbose_name='Giám đốc phòng Giao dịch')
    noi_nhan_khac = models.TextField(blank=True, default='', verbose_name='Nơi nhận khác')
    don_vi_nhan_ban_luu = models.CharField(max_length=500, blank=True, default='', verbose_name='Đơn vị, người nhận bản lưu')
    so_luong_ban = models.PositiveIntegerField(default=1, verbose_name='Số lượng bản')
    ngay_chuyen = models.DateField(verbose_name='Ngày chuyển')
    ky_nhan = models.CharField(max_length=500, blank=True, default='', verbose_name='Ký nhận')
    ghi_chu = models.TextField(blank=True, default='', verbose_name='Ghi chú')
    loai_chuyen_phat = models.CharField(
        max_length=10, choices=LOAI_CHUYEN_PHAT_CHOICES,
        blank=True, default='', verbose_name='Loại chuyển phát'
    )
    so_luong_bi = models.PositiveIntegerField(null=True, blank=True, verbose_name='Số lượng bì')
    ky_nhan_buu_dien = models.CharField(max_length=500, blank=True, default='', verbose_name='Ký nhận và dấu bưu điện')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='outgoing_documents_created'
    )

    class Meta:
        ordering = ['-ngay_van_ban', '-id']
        verbose_name = 'Văn bản đi'
        verbose_name_plural = 'Đăng ký văn bản đi'

    def get_nguoi_ky_display_name(self):
        if self.nguoi_ky == 'other':
            return self.nguoi_ky_khac or 'Người khác'
        return dict(self.NGUOI_KY_CHOICES).get(self.nguoi_ky, self.nguoi_ky)

    def get_noi_nhan_display(self):
        parts = []
        if self.noi_nhan_truong_phong:
            parts.append('Trưởng các phòng')
        if self.noi_nhan_giam_doc_pgd:
            parts.append('Giám đốc phòng Giao dịch')
        if self.noi_nhan_khac:
            parts.append(self.noi_nhan_khac)
        return '; '.join(parts)

    def get_loai_chuyen_phat_display_name(self):
        return dict(self.LOAI_CHUYEN_PHAT_CHOICES).get(self.loai_chuyen_phat, '')

    def __str__(self):
        return f"{self.so_ky_hieu} ({self.ngay_van_ban})"


class IncomingDocument(models.Model):
    ngay_den = models.DateField(verbose_name='Ngày đến')
    so_den = models.CharField(max_length=100, verbose_name='Số đến')
    tac_gia = models.CharField(max_length=500, verbose_name='Tác giả')
    so_ky_hieu = models.CharField(max_length=200, verbose_name='Số, ký hiệu văn bản')
    ngay_van_ban = models.DateField(verbose_name='Ngày tháng văn bản')
    ten_loai_trich_yeu = models.TextField(verbose_name='Tên loại và trích yếu nội dung văn bản')
    don_vi_nguoi_nhan = models.CharField(max_length=500, verbose_name='Đơn vị hoặc người nhận')
    ngay_chuyen = models.DateField(verbose_name='Ngày chuyển')
    ky_nhan = models.CharField(max_length=500, blank=True, default='', verbose_name='Ký nhận')
    ghi_chu = models.TextField(blank=True, default='', verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='incoming_documents_created'
    )

    class Meta:
        ordering = ['-ngay_den', '-id']
        verbose_name = 'Văn bản đến'
        verbose_name_plural = 'Đăng ký văn bản đến'

    def __str__(self):
        return f"{self.so_den} - {self.so_ky_hieu} ({self.ngay_den})"
