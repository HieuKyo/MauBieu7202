"""
Model đăng ký chỉ tiêu huy động vốn (HĐV) và đăng ký bảng QR.
"""
from django.db import models


# ---------------------------------------------------------------------------
# Đăng ký chỉ tiêu Huy động vốn
# ---------------------------------------------------------------------------

class HDVRegistration(models.Model):
    """Cán bộ đăng ký chỉ tiêu huy động vốn cho khách hàng (số tiền mới/tăng thêm)."""

    KY_HAN_CHOICES = [
        ('KKH', 'Không kỳ hạn'),
        ('1T', '1 tháng'),
        ('2T', '2 tháng'),
        ('3T', '3 tháng'),
        ('6T', '6 tháng'),
        ('9T', '9 tháng'),
        ('12T', '12 tháng'),
        ('13T', '13 tháng'),
        ('18T', '18 tháng'),
        ('24T', '24 tháng'),
        ('36T', '36 tháng'),
    ]

    LOAI_GIAO_DICH_CHOICES = [
        ('GUI_MOI', 'Gửi mới'),
        ('DOI_NHAP_GUI_THEM', 'Đổi/Nhập/gửi thêm sổ'),
    ]

    ten_kh      = models.CharField(max_length=200, verbose_name="Tên KH/Tên KHPN")
    sdt         = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại")
    cccd        = models.CharField(
        max_length=30, db_index=True,
        verbose_name="CCCD/GPĐKKD/GCNĐT/Mã số DN/MST",
    )
    dia_chi     = models.CharField(max_length=300, blank=True, verbose_name="Địa chỉ")
    ngay_dk_huy_dong = models.DateField(verbose_name="Ngày dự kiến gửi tiền", db_index=True)
    ky_han      = models.CharField(
        max_length=10, blank=True, choices=KY_HAN_CHOICES, verbose_name="Kỳ hạn gửi tiết kiệm",
    )
    so_tien     = models.BigIntegerField(verbose_name="Số tiền")
    loai_tien   = models.CharField(max_length=10, default='VND', verbose_name="Loại tiền")
    loai_giao_dich = models.CharField(
        max_length=20, choices=LOAI_GIAO_DICH_CHOICES, default='GUI_MOI',
        verbose_name="Loại giao dịch",
    )
    ma_can_bo   = models.CharField(max_length=30, db_index=True, verbose_name="Mã cán bộ")
    ten_can_bo  = models.CharField(max_length=200, blank=True, verbose_name="Tên cán bộ")
    chi_nhanh   = models.CharField(max_length=20, blank=True, verbose_name="Chi nhánh")
    user_dk     = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE,
        related_name='hdv_registrations', verbose_name="Người đăng ký",
    )
    ngay_gui_dk = models.DateTimeField(auto_now_add=True, verbose_name="Ngày gửi đăng ký")
    updated_at  = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    # Phê duyệt (Kiểm soát viên cùng PGD với người đăng ký)
    nguoi_duyet = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='hdv_da_duyet', verbose_name="Người phê duyệt",
    )
    ngay_duyet  = models.DateTimeField(null=True, blank=True, verbose_name="Ngày giờ phê duyệt")

    # Xác nhận đã "Add chỉ tiêu huy động vốn" vào hệ thống lõi (có thể do 1 GDV
    # khác thực hiện, không nhất thiết là người đăng ký) — chỉ 1 người/1 lần.
    nguoi_add_chi_tieu = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='hdv_da_add_chi_tieu', verbose_name="Người add chỉ tiêu",
    )
    ngay_add_chi_tieu  = models.DateTimeField(null=True, blank=True, verbose_name="Ngày giờ add chỉ tiêu")

    class Meta:
        verbose_name = "Đăng ký chỉ tiêu huy động vốn"
        verbose_name_plural = "Đăng ký chỉ tiêu huy động vốn"
        ordering = ['-ngay_gui_dk']

    def __str__(self):
        return f"{self.ten_kh} - {self.so_tien:,} {self.loai_tien}"


class HDVImportRecord(models.Model):
    """Bản ghi huy động vốn import trực tiếp từ file xuất IPCAS (số dư thực tế,
    không phải đăng ký chỉ tiêu). Mỗi lần upload cập nhật theo SO_TAI_KHOAN để
    tránh cộng trùng khi upload lại file mới/cập nhật."""

    ma_cn           = models.CharField(max_length=20, blank=True, verbose_name="Mã chi nhánh")
    ma_kh           = models.CharField(max_length=30, blank=True, db_index=True, verbose_name="Mã khách hàng")
    ten_kh          = models.CharField(max_length=200, verbose_name="Tên khách hàng")
    id_number       = models.CharField(max_length=30, db_index=True, verbose_name="CCCD/GPĐKKD/GCNĐT/Mã số DN/MST")
    ccy             = models.CharField(max_length=10, default='VND', verbose_name="Loại tiền")
    current_balance = models.BigIntegerField(default=0, verbose_name="Số dư hiện tại")
    so_tai_khoan    = models.CharField(max_length=30, unique=True, verbose_name="Số tài khoản")
    opening_date    = models.DateField(null=True, blank=True, db_index=True, verbose_name="Ngày mở/gửi")
    maturity_date   = models.DateField(null=True, blank=True, verbose_name="Ngày đáo hạn")
    month_term      = models.IntegerField(default=0, verbose_name="Kỳ hạn (tháng)")
    account_status  = models.CharField(max_length=20, blank=True, verbose_name="Trạng thái sổ")
    employee_number = models.CharField(max_length=30, db_index=True, verbose_name="Mã cán bộ")
    employee_name   = models.CharField(max_length=200, blank=True, verbose_name="Tên cán bộ")
    uploaded_at     = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")
    uploaded_by     = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='hdv_imports', verbose_name="Người upload",
    )

    class Meta:
        verbose_name = "Bản ghi HĐV import từ IPCAS"
        verbose_name_plural = "Bản ghi HĐV import từ IPCAS"
        ordering = ['-opening_date']

    def __str__(self):
        return f"{self.ten_kh} - {self.current_balance:,} {self.ccy}"


# ---------------------------------------------------------------------------
# Đăng ký bảng QR (Kế toán Ngân quỹ)
# ---------------------------------------------------------------------------

class QRRegistration(models.Model):
    """Đăng ký bảng QR cho khách hàng/cửa hàng — Phòng Kế toán & Ngân quỹ."""

    ten_kh          = models.CharField(max_length=200, verbose_name="Tên khách hàng")
    so_tai_khoan    = models.CharField(max_length=30, db_index=True, verbose_name="Số tài khoản")
    ten_cua_hang    = models.CharField(max_length=200, blank=True, verbose_name="Tên cửa hàng (nếu có)")
    ten_can_bo      = models.CharField(max_length=200, blank=True, verbose_name="Tên cán bộ đăng ký")
    phong_giao_dich = models.CharField(max_length=200, blank=True, verbose_name="Phòng giao dịch")
    user_dk         = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE,
        related_name='qr_registrations', verbose_name="Người đăng ký",
    )
    ngay_dang_ky    = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng ký", db_index=True)
    updated_at      = models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")

    class Meta:
        verbose_name = "Đăng ký bảng QR"
        verbose_name_plural = "Đăng ký bảng QR"
        ordering = ['-ngay_dang_ky']

    def __str__(self):
        return f"{self.ten_kh} - {self.so_tai_khoan}"
