"""
Model Kế toán Ngân quỹ: quỹ tiền mặt GDV, bảng kê, cấu hình in, đọc cân đối, bìa chứng từ.
"""
from django.db import models
from django.contrib.auth.models import User


class CanDoiUpload(models.Model):
    """Kết quả đọc file Cân đối tài khoản - số liệu cốt yếu doanh thu phí dịch vụ"""
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày upload")
    file_name = models.CharField(max_length=255, verbose_name="Tên file")
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='can_doi_uploads',
        verbose_name="Người upload"
    )

    tt_trong_nuoc = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.1 Thanh toán trong nước")
    tt_quoc_te = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.2 Thanh toán quốc tế")
    kieu_hoi = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.3 Dịch vụ kiều hối")
    dich_vu_the = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.4 Dịch vụ thẻ")
    e_banking = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.5 E-Banking")
    uy_thac_dai_ly = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.6 Ủy thác và đại lý")
    bao_lanh = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.7 Bảo lãnh")
    ngan_quy = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.8 Ngân quỹ")
    thu_khac = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.9 Thu khác")
    kd_ngoai_hoi = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="1.10 Thu ròng từ KD ngoại hối")
    dieu_tiet_noi_bo = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="III. Điều tiết nội bộ phí dịch vụ")
    tong_doanh_thu = models.DecimalField(max_digits=18, decimal_places=0, default=0, verbose_name="IV. Tổng DT Dịch vụ")

    class Meta:
        verbose_name = "Đọc Cân đối"
        verbose_name_plural = "Đọc Cân đối"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} - {self.uploaded_at.strftime('%d/%m/%Y %H:%M')}"


class BiaChungTu(models.Model):
    """Bìa lưu trữ Nhật ký chứng từ (mẫu M01/LHS) — mỗi bản ghi là 1 tập chứng từ
    trong ngày, in kèm mã QR. Số hồ sơ đánh riêng theo từng đơn vị (UserProfile.branch)."""
    branch = models.CharField(max_length=50, db_index=True, verbose_name="Đơn vị")
    so_ho_so = models.CharField(max_length=30, verbose_name="Số hồ sơ")
    ngay_chung_tu = models.DateField(db_index=True, verbose_name="Ngày chứng từ")
    tap_so = models.PositiveIntegerField(default=1, verbose_name="Tập số")
    tong_tap = models.PositiveIntegerField(default=1, verbose_name="Tổng số tập")
    gdv = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bia_chung_tu_gdv', verbose_name="Giao dịch viên"
    )
    so_to = models.PositiveIntegerField(default=1, verbose_name="Số tờ")
    so_to_tap = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Số tờ của tập chứng từ",
        help_text="In ở nhãn QR \"Chứng từ ngày ... (n tờ)\"; trống thì in \"(…. tờ)\" để hậu kiểm điền tay"
    )
    don_vi = models.CharField(max_length=30, default='Quyển', verbose_name="Đơn vị tính")
    thoi_han_bao_quan = models.CharField(max_length=30, default='20 năm', verbose_name="Thời hạn bảo quản")
    user_ipcas = models.CharField(max_length=100, verbose_name="UserIPCAS (in vào QR)")
    nguoi_lap = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='bia_chung_tu_lap', verbose_name="Người lập"
    )
    ngay_in = models.DateTimeField(null=True, blank=True, verbose_name="Ngày in gần nhất")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Bìa chứng từ"
        verbose_name_plural = "Bìa chứng từ"
        ordering = ['-ngay_chung_tu', 'so_ho_so']
        constraints = [
            models.UniqueConstraint(fields=['branch', 'so_ho_so'], name='uniq_bia_chung_tu_branch_so_ho_so'),
        ]

    def __str__(self):
        return f"{self.so_ho_so} - {self.ngay_chung_tu.strftime('%d/%m/%Y')} - Tập {self.tap_so}/{self.tong_tap}"


class BiaThuTuIn(models.Model):
    """Thứ tự in (thứ tự cấp số) đã nhớ của từng GDV ở màn hình Cấp số bìa chứng từ."""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='bia_thu_tu_in', verbose_name="Giao dịch viên")
    thu_tu = models.PositiveIntegerField(verbose_name="Thứ tự in")

    class Meta:
        verbose_name = "Thứ tự in bìa chứng từ"
        verbose_name_plural = "Thứ tự in bìa chứng từ"

    def __str__(self):
        return f"{self.user} - {self.thu_tu}"
# ---------------------------------------------------------------------------
# Bảng kê tiền mặt (Kế toán Ngân quỹ)
# ---------------------------------------------------------------------------

CASH_DENOMINATIONS = [500000, 200000, 100000, 50000, 20000, 10000, 5000, 2000, 1000, 500, 200]


class CashDrawerBalance(models.Model):
    """Tồn quỹ tiền mặt theo mệnh giá của từng cán bộ (GDV) — cộng dồn xuyên suốt,
    chỉ về 0 khi cán bộ tự bấm Reset Counter (out quỹ về quỹ chính)."""

    user       = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='cash_drawer_balances')
    menh_gia   = models.IntegerField(verbose_name="Mệnh giá")
    so_to      = models.IntegerField(default=0, verbose_name="Số tờ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        verbose_name = "Tồn quỹ tiền mặt theo mệnh giá"
        verbose_name_plural = "Tồn quỹ tiền mặt theo mệnh giá"
        constraints = [
            models.UniqueConstraint(fields=['user', 'menh_gia'], name='uniq_cash_balance_user_menhgia'),
        ]
        ordering = ['-menh_gia']

    def __str__(self):
        return f"{self.user.username} - {self.menh_gia:,}đ x {self.so_to}"


class CashDrawerStatement(models.Model):
    """Lịch sử bảng kê thu/chi/nhập quỹ/reset của từng cán bộ (GDV)."""

    LOAI_CHOICES = [
        ('THU',      'Bảng kê thu'),
        ('CHI',      'Bảng kê chi'),
        ('NHAP_QUY', 'Nhập số tiền tiếp quỹ (thực nhận)'),
        ('DE_NGHI',  'Đề nghị tiếp quỹ'),
        ('RESET',    'Reset counter (out quỹ)'),
    ]

    user       = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='cash_statements')
    loai       = models.CharField(max_length=10, choices=LOAI_CHOICES, verbose_name="Loại")
    ghi_chu    = models.CharField(max_length=200, blank=True, verbose_name="Ghi chú")
    chi_tiet   = models.JSONField(default=dict, verbose_name="Chi tiết số tờ theo mệnh giá")
    tong_tien  = models.BigIntegerField(default=0, verbose_name="Tổng tiền")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian", db_index=True)

    class Meta:
        verbose_name = "Bảng kê tiền mặt"
        verbose_name_plural = "Bảng kê tiền mặt"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_loai_display()} - {self.user.username} - {self.tong_tien:,}đ"


class CashPrintConfigBase(models.Model):
    """Các trường tọa độ in dùng chung — mỗi loại giấy in sẵn (giấy rút tiền, giấy
    nộp tiền...) có vị trí ô khác nhau nên cần 1 bộ cấu hình riêng. Cấu hình theo
    từng user vì mỗi người dùng máy in khác nhau, khớp lệch trục khác nhau."""

    user             = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    offset_x         = models.FloatField(default=0, verbose_name="Dịch chuyển trục X (mm)")
    offset_y         = models.FloatField(default=0, verbose_name="Dịch chuyển trục Y (mm)")
    start_y          = models.FloatField(default=30.0, verbose_name="Vị trí dòng mệnh giá đầu tiên (mm từ trên)")
    row_spacing      = models.FloatField(default=7.0, verbose_name="Khoảng cách giữa các dòng mệnh giá (mm)")
    col_so_to_x      = models.FloatField(default=90.0, verbose_name="Vị trí cột Số tờ (mm từ trái)")
    col_thanh_tien_x = models.FloatField(default=130.0, verbose_name="Vị trí cột Thành tiền (mm từ trái)")
    total_x          = models.FloatField(default=130.0, verbose_name="Vị trí Tổng cộng - X (mm từ trái)")
    total_y          = models.FloatField(default=118.0, verbose_name="Vị trí Tổng cộng - Y (mm từ trên)")
    so_tien_chu_x    = models.FloatField(default=20.0, verbose_name="Vị trí Số tiền bằng chữ - X (mm từ trái)")
    so_tien_chu_y    = models.FloatField(default=130.0, verbose_name="Vị trí Số tiền bằng chữ - Y (mm từ trên)")
    font_size        = models.FloatField(default=10.0, verbose_name="Cỡ chữ (pt)")
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get_instance(cls, user):
        obj, _ = cls.objects.get_or_create(user=user)
        return obj


class CashPrintConfig(CashPrintConfigBase):
    """Cấu hình vị trí in đè lên giấy rút tiền in sẵn — chỉ in số, không vẽ khung/bảng."""

    class Meta:
        verbose_name = "Cấu hình in bảng kê tiền mặt"
        verbose_name_plural = "Cấu hình in bảng kê tiền mặt"


class CashPrintConfigNopTien(CashPrintConfigBase):
    """Cấu hình vị trí in đè lên giấy nộp tiền in sẵn (layout riêng, khác giấy rút tiền)."""

    class Meta:
        verbose_name = "Cấu hình in bảng kê trắng (giấy nộp tiền)"
        verbose_name_plural = "Cấu hình in bảng kê trắng (giấy nộp tiền)"


class CashPrintConfigChungTuBase(models.Model):
    """Cấu hình cho các chứng từ tự vẽ khung/bảng (không đè lên giấy in sẵn) —
    Bảng kê Thu, Bảng kê Chi, Đề nghị tiếp quỹ. Chỉ cần offset + cỡ chữ vì
    khung/bảng do hệ thống tự vẽ, không cần canh khớp giấy có sẵn. Cấu hình theo
    từng user vì mỗi người dùng máy in khác nhau."""

    user            = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    offset_x        = models.FloatField(default=0, verbose_name="Dịch chuyển trục X (mm)")
    offset_y        = models.FloatField(default=0, verbose_name="Dịch chuyển trục Y (mm)")
    margin          = models.FloatField(default=10.0, verbose_name="Lề trang (mm)")
    title_font_size = models.FloatField(default=14.0, verbose_name="Cỡ chữ tiêu đề (pt)")
    body_font_size  = models.FloatField(default=9.0, verbose_name="Cỡ chữ nội dung (pt)")
    row_height      = models.FloatField(default=5.5, verbose_name="Chiều cao dòng trong bảng (mm)")
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get_instance(cls, user):
        obj, _ = cls.objects.get_or_create(user=user)
        return obj


class CashPrintConfigBangKeThu(CashPrintConfigChungTuBase):
    """Cấu hình in Bảng kê Thu (chứng từ có khung/tiêu đề)."""

    class Meta:
        verbose_name = "Cấu hình in Bảng kê Thu"
        verbose_name_plural = "Cấu hình in Bảng kê Thu"


class CashPrintConfigBangKeChi(CashPrintConfigChungTuBase):
    """Cấu hình in Bảng kê Chi (chứng từ có khung/tiêu đề)."""

    class Meta:
        verbose_name = "Cấu hình in Bảng kê Chi"
        verbose_name_plural = "Cấu hình in Bảng kê Chi"


class CashPrintConfigDeNghi(CashPrintConfigChungTuBase):
    """Cấu hình in Giấy đề nghị tiếp quỹ."""

    class Meta:
        verbose_name = "Cấu hình in Đề nghị tiếp quỹ"
        verbose_name_plural = "Cấu hình in Đề nghị tiếp quỹ"
