from django.db import models


class TaxLocation(models.Model):
    """
    Model lưu trữ thông tin Cơ quan thu thuế
    Dữ liệu từ file: CO QUAN THU.xlsx
    """
    tinh = models.CharField(max_length=100, verbose_name="Tỉnh/Thành phố", db_index=True)
    co_quan_thue_group = models.CharField(max_length=200, verbose_name="Cơ quan thuế", db_index=True)
    xa_phuong = models.CharField(max_length=100, verbose_name="Xã/Phường", db_index=True)
    ma_co_quan_thu = models.CharField(max_length=50, verbose_name="Mã cơ quan thu", unique=True)
    ten_co_quan_thu = models.TextField(verbose_name="Tên cơ quan thu")
    kho_bac = models.CharField(max_length=200, verbose_name="Kho bạc nhà nước (KBNN)")
    ma_dia_ban = models.CharField(max_length=50, verbose_name="Mã địa bàn")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Cơ quan thu"
        verbose_name_plural = "Danh mục Cơ quan thu"
        ordering = ['tinh', 'co_quan_thue_group', 'xa_phuong']
        indexes = [
            models.Index(fields=['tinh', 'co_quan_thue_group', 'xa_phuong']),
        ]

    def __str__(self):
        return f"{self.xa_phuong} - {self.ten_co_quan_thu}"


class TaxSubEntry(models.Model):
    """
    Model lưu trữ danh mục Tiểu mục nộp thuế
    Dữ liệu từ file: MA TIEU MUC.xlsx
    """
    ma_tieu_muc = models.CharField(max_length=50, verbose_name="Mã tiểu mục", unique=True)
    ten_tieu_muc = models.TextField(verbose_name="Tên gọi (Nội dung kinh tế)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Tiểu mục thuế"
        verbose_name_plural = "Danh mục Tiểu mục thuế"
        ordering = ['ma_tieu_muc']

    def __str__(self):
        return f"{self.ma_tieu_muc} - {self.ten_tieu_muc[:50]}"


class TaxPaymentStatement(models.Model):
    """
    Model lưu trữ thông tin Bảng kê nộp thuế đã tạo
    """
    # Thông tin người nộp thuế
    ten_nguoi_nop = models.CharField(max_length=200, verbose_name="Tên người nộp thuế")
    ma_so_thue = models.CharField(max_length=50, verbose_name="Mã số thuế", blank=True)
    dia_chi = models.TextField(verbose_name="Địa chỉ", blank=True)
    nguoi_nop_thay = models.CharField(max_length=200, verbose_name="Người nộp thay", blank=True)

    # Thông tin cơ quan thu
    tax_location = models.ForeignKey(
        TaxLocation,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Cơ quan thu"
    )

    # Thông tin bảng kê
    ngay_lap = models.DateField(verbose_name="Ngày lập bảng kê")
    tong_so_tien = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Tổng số tiền", default=0)

    # File đã xuất
    exported_file = models.FileField(upload_to='tax_statements/', blank=True, null=True, verbose_name="File đã xuất")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Bảng kê nộp thuế"
        verbose_name_plural = "Danh sách Bảng kê nộp thuế"
        ordering = ['-created_at']

    def __str__(self):
        return f"Bảng kê {self.ten_nguoi_nop} - {self.ngay_lap}"


class TaxPaymentItem(models.Model):
    """
    Model lưu trữ các dòng tiểu mục trong bảng kê
    """
    statement = models.ForeignKey(
        TaxPaymentStatement,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Bảng kê"
    )
    tax_sub_entry = models.ForeignKey(
        TaxSubEntry,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Tiểu mục"
    )
    ma_tieu_muc = models.CharField(max_length=50, verbose_name="Mã tiểu mục")
    noi_dung = models.TextField(verbose_name="Nội dung")
    so_tien = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Số tiền")

    stt = models.IntegerField(verbose_name="STT", default=1)

    class Meta:
        verbose_name = "Dòng tiểu mục"
        verbose_name_plural = "Các dòng tiểu mục"
        ordering = ['stt']

    def __str__(self):
        return f"STT {self.stt}: {self.ma_tieu_muc} - {self.so_tien:,}"
