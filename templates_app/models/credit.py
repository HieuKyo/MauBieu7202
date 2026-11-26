"""
Model Tín dụng: cấu hình FTP & NIM, ảnh chụp kết quả phân tích MSIT80.
"""
from django.db import models


# ---------------------------------------------------------------------------
# Tín dụng — Cấu hình FTP & NIM theo gói ưu đãi
# ---------------------------------------------------------------------------

class FTPConfig(models.Model):
    """Bảng cấu hình FTP và NIM theo mã gói ưu đãi AGRIBANK."""

    CACH_TINH_CHOICES = [
        ('SPRD-FTP+DIEU_CHINH',  'NIM = Lãi suất - FTP + Biên độ'),
        ('SPRD-FTP-DIEU_CHINH',  'NIM = Lãi suất - FTP - Biên độ'),
        ('SPRD-FTP',             'NIM = Lãi suất - FTP (không biên độ)'),
        ('NIM_CO_DINH',          'NIM cố định'),
    ]

    LOAI_KH_CHOICES = [
        ('Tất cả',  'Tất cả'),
        ('Cá nhân', 'Cá nhân'),
        ('Tổ chức', 'Tổ chức'),
    ]

    ma_goi     = models.CharField(max_length=50, verbose_name="Mã gói ưu đãi")
    ten_goi    = models.CharField(max_length=200, verbose_name="Tên gói")
    ftp_pct    = models.FloatField(default=5.0, verbose_name="FTP % bán")
    bien_do_pct = models.FloatField(default=0.0, verbose_name="Biên độ hỗ trợ %")
    cach_tinh  = models.CharField(
        max_length=30, choices=CACH_TINH_CHOICES,
        default='SPRD-FTP+DIEU_CHINH', verbose_name="Công thức NIM",
    )
    nim_co_dinh_pct = models.FloatField(default=0.0, verbose_name="NIM cố định %")
    loai_kh    = models.CharField(
        max_length=10, choices=LOAI_KH_CHOICES,
        default='Tất cả', verbose_name="Loại khách hàng",
    )
    is_default = models.BooleanField(
        default=False, verbose_name="Dùng khi không khớp gói",
        help_text="Đặt một bản ghi làm mặc định (FTP chung khi khoản vay không có mã gói).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cấu hình FTP/NIM"
        verbose_name_plural = "Cấu hình FTP/NIM"
        ordering = ['ma_goi']

    def __str__(self):
        return f"{self.ma_goi} — {self.ten_goi} (FTP {self.ftp_pct}%)"

    def compute_nim(self, sprd: float) -> float:
        """Tính NIM từ lãi suất vay (sprd) và cấu hình gói."""
        if self.cach_tinh == 'NIM_CO_DINH':
            return self.nim_co_dinh_pct
        if self.cach_tinh == 'SPRD-FTP+DIEU_CHINH':
            return sprd - self.ftp_pct + self.bien_do_pct
        if self.cach_tinh == 'SPRD-FTP-DIEU_CHINH':
            return sprd - self.ftp_pct - self.bien_do_pct
        return sprd - self.ftp_pct


# ---------------------------------------------------------------------------
# Tín dụng — Lưu trữ snapshot phân tích (cho so sánh kỳ)
# ---------------------------------------------------------------------------

class TDSnapshot(models.Model):
    """Lưu kết quả phân tích MSIT80 theo ngày để so sánh kỳ trước."""

    file_date   = models.DateField(verbose_name="Ngày dữ liệu file MSIT80", db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời điểm upload")
    uploaded_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='td_snapshots', verbose_name="Người upload",
    )
    file_name   = models.CharField(max_length=200, blank=True, verbose_name="Tên file gốc")
    so_lds      = models.IntegerField(default=0, verbose_name="Số LDS")
    so_kh       = models.IntegerField(default=0, verbose_name="Số KH")
    so_hd       = models.IntegerField(default=0, verbose_name="Số HĐ tín dụng")
    tong_du_no  = models.BigIntegerField(default=0, verbose_name="Tổng dư nợ (đồng)")
    qua_han     = models.IntegerField(default=0, verbose_name="Số khoản quá hạn")
    nhom2       = models.IntegerField(default=0, verbose_name="Nhóm 2")
    nhom35      = models.IntegerField(default=0, verbose_name="Nhóm 3-5")
    kh_dac_biet = models.IntegerField(default=0, verbose_name="KH đặc biệt")
    summary_json = models.JSONField(default=dict, verbose_name="JSON tóm tắt phân tích")

    class Meta:
        verbose_name = "Snapshot phân tích tín dụng"
        verbose_name_plural = "Snapshot phân tích tín dụng"
        ordering = ['-file_date', '-uploaded_at']

    def __str__(self):
        return f"Snapshot {self.file_date} — {self.so_lds} LDS"
