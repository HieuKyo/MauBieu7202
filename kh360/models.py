"""
Khách hàng 360 — dữ liệu nạp từ file IPCAS (CN05, DP01, LN01) và các file theo dõi
(Loa Thần tài, QR, Ebanking tổ chức).

Chỉ giữ TRẠNG THÁI HIỆN TẠI; mỗi lần cập nhật (Ky) so với lần trước và ghi BienDong
(mới / mất). Lần đầu nạp một nguồn chỉ làm mốc, không ghi biến động.
"""
from django.contrib.auth.models import User
from django.db import models


NGUON_CHOICES = [
    ('CN05', 'CN05 – Sản phẩm dịch vụ KH cá nhân'),
    ('DP01', 'DP01 – Tài khoản tiền gửi'),
    ('LN01', 'LN01 – Khoản vay'),
    ('LOA', 'Loa Thần tài'),
    ('QR', 'QR code'),
    ('KHTC', 'Ebanking tổ chức'),
    ('BC06', 'BC06 – Phân hạng khách hàng'),
]


class Ky(models.Model):
    """Một lần cập nhật dữ liệu (bắt buộc có CN05 + DP01)."""
    ngay_du_lieu = models.DateField('Ngày dữ liệu')
    thoi_diem = models.DateTimeField('Thời điểm cập nhật', auto_now_add=True)
    nguoi_cap_nhat = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người cập nhật'
    )
    tong_hop = models.JSONField('Số liệu tổng hợp', default=dict)

    class Meta:
        verbose_name = 'Kỳ cập nhật KH 360'
        verbose_name_plural = 'Kỳ cập nhật KH 360'
        ordering = ['-thoi_diem']

    def __str__(self):
        return f'{self.thoi_diem:%d/%m/%Y %H:%M} – dữ liệu {self.ngay_du_lieu:%d/%m/%Y}'


class NguonFile(models.Model):
    """File của từng nguồn đã nạp trong một kỳ."""
    ky = models.ForeignKey(Ky, on_delete=models.CASCADE, related_name='files')
    nguon = models.CharField(max_length=10, choices=NGUON_CHOICES)
    ten_file = models.CharField(max_length=255)
    ngay_du_lieu = models.DateField()
    so_dong = models.IntegerField(default=0)
    la_moc = models.BooleanField('Lần đầu (mốc)', default=False)
    # Danh sách dòng không khớp được mã KH (STK không có trong DP01, tổ chức không tìm thấy...)
    khong_khop = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['ky', 'nguon']


class KhachHang(models.Model):
    ma_kh = models.CharField('Mã KH', max_length=20, primary_key=True)
    ten = models.CharField('Tên KH', max_length=255, blank=True)
    loai_kh = models.CharField('Loại KH', max_length=10, blank=True)
    ten_loai_kh = models.CharField('Tên loại KH', max_length=100, blank=True)
    la_to_chuc = models.BooleanField('Tổ chức', default=False)
    cccd = models.CharField('CCCD/Giấy tờ', max_length=30, blank=True)
    ngay_cap = models.DateField('Ngày cấp', null=True, blank=True)
    ngay_sinh = models.DateField('Ngày sinh', null=True, blank=True)
    gioi_tinh = models.CharField('Giới tính', max_length=10, blank=True)
    sdt = models.CharField('Số điện thoại', max_length=30, blank=True)
    dia_chi = models.CharField('Địa chỉ', max_length=300, blank=True)
    pgd = models.CharField('Điểm giao dịch', max_length=100, blank=True)
    co_cn05 = models.BooleanField(default=False)
    dich_vu = models.JSONField('Dịch vụ (CN05)', default=dict, blank=True)
    tong_so_du = models.DecimalField('Tổng số dư VND', max_digits=20, decimal_places=2, default=0)
    tong_du_no = models.DecimalField('Tổng dư nợ', max_digits=20, decimal_places=2, default=0)
    con_hoat_dong = models.BooleanField(default=True)
    tim_kiem = models.TextField(blank=True)  # tên không dấu + mã KH + CCCD + SĐT

    class Meta:
        verbose_name = 'Khách hàng 360'
        verbose_name_plural = 'Khách hàng 360'

    def __str__(self):
        return f'{self.ma_kh} - {self.ten}'


class TaiKhoanTG(models.Model):
    so_tk = models.CharField('Số TK', max_length=30, primary_key=True)
    ma_kh = models.CharField(max_length=20, db_index=True)
    ten_kh = models.CharField(max_length=255, blank=True)
    tk_hach_toan = models.CharField('TK hạch toán', max_length=10, blank=True)
    loai_tg = models.CharField('Loại tiền gửi', max_length=100, blank=True)
    ccy = models.CharField(max_length=5, blank=True)
    so_du = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    lai_suat = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    ky_han = models.IntegerField('Kỳ hạn (tháng)', default=0)
    ngay_mo = models.DateField(null=True, blank=True)
    ngay_den_han = models.DateField(null=True, blank=True)
    trang_thai = models.CharField(max_length=20, blank=True)
    pgd = models.CharField(max_length=100, blank=True)
    so_so = models.CharField('Số sổ', max_length=30, blank=True)
    can_bo = models.CharField('Cán bộ', max_length=100, blank=True)
    con_hoat_dong = models.BooleanField(default=True)

    class Meta:
        ordering = ['-con_hoat_dong', 'so_tk']


class KhoanVay(models.Model):
    so_giai_ngan = models.CharField('Số giải ngân', max_length=30, primary_key=True)
    ma_kh = models.CharField(max_length=20, db_index=True)
    ten_kh = models.CharField(max_length=255, blank=True)
    loai_kh = models.CharField(max_length=10, blank=True)
    tk_hach_toan = models.CharField(max_length=10, blank=True)
    loai_vay = models.CharField(max_length=100, blank=True)
    muc_dich = models.CharField(max_length=150, blank=True)
    du_no = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    so_tien_giai_ngan = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    ngay_giai_ngan = models.DateField(null=True, blank=True)
    ngay_dao_han = models.DateField(null=True, blank=True)
    lai_suat = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    nhom_no = models.CharField(max_length=5, blank=True)
    can_bo = models.CharField('Cán bộ tín dụng', max_length=100, blank=True)
    tk_nhan_giai_ngan = models.CharField(max_length=30, blank=True)
    ngay_tra_tiep = models.DateField(null=True, blank=True)
    so_tien_tra_tiep = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    pgd = models.CharField(max_length=100, blank=True)
    cccd = models.CharField(max_length=30, blank=True)
    ngay_sinh = models.DateField(null=True, blank=True)
    dia_chi = models.CharField(max_length=300, blank=True)
    con_du_no = models.BooleanField(default=True)

    class Meta:
        ordering = ['-con_du_no', '-ngay_giai_ngan']


class LoaThanTai(models.Model):
    """Doanh số Loa theo kỳ (giữ lịch sử). Kỳ xác định theo 'Từ ngày' trong file."""
    tk_ao = models.CharField('TK ảo', max_length=40)
    so_tk = models.CharField('TK Agribank', max_length=30, db_index=True)
    ma_kh = models.CharField(max_length=20, blank=True, db_index=True)
    ten_kh = models.CharField(max_length=255, blank=True)
    nha_cung_cap = models.CharField(max_length=100, blank=True)
    tu_ngay = models.DateField(db_index=True)
    den_ngay = models.DateField()
    so_giao_dich = models.IntegerField(default=0)
    doanh_so = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    class Meta:
        ordering = ['-tu_ngay', 'so_tk']


class MaQR(models.Model):
    so_tk = models.CharField(max_length=30, db_index=True)
    ma_kh = models.CharField(max_length=20, blank=True, db_index=True)
    ho_ten = models.CharField(max_length=255, blank=True)
    ten_cua_hang = models.CharField(max_length=255, blank=True)
    phong = models.CharField('Phòng phát sinh', max_length=100, blank=True)
    ngay_lam = models.DateField(null=True, blank=True)
    ngay_lam_goc = models.CharField(max_length=50, blank=True)
    ghi_chu = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['so_tk']


class EbankingToChuc(models.Model):
    ma_to_chuc = models.CharField('Mã tổ chức', max_length=50, primary_key=True)
    ten = models.CharField(max_length=255)
    ma_kh = models.CharField(max_length=20, blank=True, db_index=True)
    trang_thai = models.CharField(max_length=50, blank=True)
    ngay_dang_ky = models.DateField(null=True, blank=True)
    nguoi_tao = models.CharField(max_length=100, blank=True)
    ngay_dong_bo = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['ten']


class XepHangKH(models.Model):
    """Phân hạng KH theo BC06 (MSPL09). Ghi đè toàn bộ mỗi lần nạp. Tiền tính bằng đồng."""
    ma_kh = models.CharField(max_length=20, primary_key=True)
    thang = models.CharField('Tháng phân loại', max_length=6, blank=True)
    nhom_cn = models.CharField('Nhóm tại CN', max_length=20, blank=True)
    hang_cn = models.CharField('Hạng tại CN', max_length=20, blank=True)
    nhom_tt_cn = models.CharField(max_length=20, blank=True)
    hang_tt_cn = models.CharField(max_length=20, blank=True)
    nhom_agr = models.CharField('Nhóm toàn Agribank', max_length=20, blank=True)
    hang_agr = models.CharField('Hạng toàn Agribank', max_length=20, blank=True)
    nhom_tt_agr = models.CharField(max_length=20, blank=True)
    hang_tt_agr = models.CharField(max_length=20, blank=True)
    diem_kh = models.IntegerField('Điểm KH tại CN', default=0)
    diem_loi_ich = models.IntegerField(default=0)
    diem_sdbq = models.IntegerField(default=0)
    diem_dinh_tinh = models.IntegerField(default=0)
    loi_ich_tg = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    loi_ich_tv = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    loi_ich_dv = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    sdbq_tg_co_ky_han = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    sdbq_tg_khong_ky_han = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    sdbq_tien_vay = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    don_vi_dau_moi = models.CharField(max_length=100, blank=True)

    @staticmethod
    def nhan(nhom, hang):
        """'Platinum VIP', 'Thân thiết', 'Phổ thông'."""
        if hang:
            return f'{hang} {nhom.upper()}' if nhom else hang
        return nhom

    @property
    def nhan_cn(self):
        return self.nhan(self.nhom_cn, self.hang_cn)

    @property
    def nhan_agr(self):
        return self.nhan(self.nhom_agr, self.hang_agr)

    @property
    def nhan_tt_cn(self):
        return self.nhan(self.nhom_tt_cn, self.hang_tt_cn)

    @property
    def nhan_tt_agr(self):
        return self.nhan(self.nhom_tt_agr, self.hang_tt_agr)

    @property
    def tong_loi_ich(self):
        return self.loi_ich_tg + self.loi_ich_tv + self.loi_ich_dv


class GhiChuKH(models.Model):
    """Ghi chú của cán bộ về khách hàng — bảng riêng để không mất khi cập nhật dữ liệu."""
    ma_kh = models.CharField(max_length=20, primary_key=True)
    noi_dung = models.TextField('Ghi chú', blank=True)
    nguoi_sua = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ngay_sua = models.DateTimeField(auto_now=True)


class GanMaToChuc(models.Model):
    """Gán tay mã KH cho tổ chức Ebanking không khớp được theo tên (nhớ cho các lần sau)."""
    ma_to_chuc = models.CharField(max_length=50, primary_key=True)
    ma_kh = models.CharField(max_length=20)


class BienDong(models.Model):
    LOAI_CHOICES = [
        ('KH_MOI', 'KH mới'),
        ('KH_MAT', 'KH mất'),
        ('TK_MOI', 'TK mở mới'),
        ('TK_DONG', 'TK đóng'),
        ('VAY_MOI', 'Vay mới giải ngân'),
        ('VAY_TAT_TOAN', 'Vay tất toán'),
        ('DV_DANG_KY', 'Đăng ký dịch vụ'),
        ('DV_HUY', 'Hủy dịch vụ'),
        ('LOA_MOI', 'Loa mới'),
        ('LOA_MAT', 'Loa mất'),
        ('QR_MOI', 'QR mới'),
        ('QR_MAT', 'QR mất'),
        ('EB_MOI', 'Ebanking tổ chức mới'),
        ('EB_MAT', 'Ebanking tổ chức mất'),
    ]
    LOAI_MOI = {'KH_MOI', 'TK_MOI', 'VAY_MOI', 'DV_DANG_KY', 'LOA_MOI', 'QR_MOI', 'EB_MOI'}

    ky = models.ForeignKey(Ky, on_delete=models.CASCADE, related_name='bien_dong')
    loai = models.CharField(max_length=15, choices=LOAI_CHOICES, db_index=True)
    ma_kh = models.CharField(max_length=20, blank=True, db_index=True)
    ten_kh = models.CharField(max_length=255, blank=True)
    doi_tuong = models.CharField('Đối tượng', max_length=100, blank=True)
    chi_tiet = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['ky', 'loai', 'ma_kh']

    @property
    def la_moi(self):
        return self.loai in self.LOAI_MOI
