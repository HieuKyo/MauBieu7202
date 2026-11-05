"""
Model cho các báo cáo: theo dõi bì thư, cấu hình báo cáo, lịch sử đóng/mở TK, giao dịch nộp/rút ATM.
"""
from django.db import models
from django.contrib.auth.models import User


# ===== REPORT MODELS =====

class MailEnvelopeTracking(models.Model):
    """Model để theo dõi việc nhận bì thư"""
    envelope_code = models.CharField(max_length=50, verbose_name="Mã bì thư", unique=True)
    receive_date = models.DateField(verbose_name="Ngày nhận")
    receiver = models.CharField(max_length=200, verbose_name="Người nhận")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo record")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Bì thư"
        verbose_name_plural = "Quản lý Bì thư"
        ordering = ['-receive_date', '-created_at']

    def __str__(self):
        return f"{self.envelope_code} - {self.receive_date}"


class ReportConfiguration(models.Model):
    """Cấu hình cho các loại báo cáo"""
    REPORT_TYPES = [
        ('lai_ton_dong', 'Báo cáo Lãi tồn đọng'),
        ('phat_hanh_the', 'Báo cáo Phát hành thẻ'),
        ('luong', 'Chuyển đổi file Lương'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPES, unique=True, verbose_name="Loại báo cáo")
    config_data = models.JSONField(default=dict, verbose_name="Dữ liệu cấu hình")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Cấu hình báo cáo"
        verbose_name_plural = "Cấu hình báo cáo"

    def __str__(self):
        return self.get_report_type_display()


# ===== DONG/MO TAI KHOAN HISTORY =====

class DongMoTaiKhoanHistory(models.Model):
    """Lưu lịch sử thống kê Đóng/Mở tài khoản theo từng kỳ"""
    report_month = models.DateField(verbose_name="Kỳ báo cáo")  # Ngày đầu tháng
    tong_mo = models.IntegerField(default=0, verbose_name="Tổng mở TK")
    ca_nhan_count = models.IntegerField(default=0, verbose_name="Cá nhân")
    to_chuc_count = models.IntegerField(default=0, verbose_name="Tổ chức")
    the_mien_phi_count = models.IntegerField(default=0, verbose_name="Thẻ miễn phí")
    hssv_count = models.IntegerField(default=0, verbose_name="HSSV")
    dong_tk_count = models.IntegerField(default=0, verbose_name="Đóng TK")
    dong_he_thong_count = models.IntegerField(default=0, verbose_name="Hệ thống tự đóng")
    dong_tai_quay_count = models.IntegerField(default=0, verbose_name="Đóng tại quầy")
    # Phân loại đóng TK theo loại khách hàng
    dong_ca_nhan_count = models.IntegerField(default=0, verbose_name="Đóng TK - Cá nhân")
    dong_ca_nhan_tu_dong = models.IntegerField(default=0, verbose_name="Đóng TK - Cá nhân tự động")
    dong_ca_nhan_tai_quay = models.IntegerField(default=0, verbose_name="Đóng TK - Cá nhân tại quầy")
    dong_to_chuc_count = models.IntegerField(default=0, verbose_name="Đóng TK - Tổ chức")
    dong_to_chuc_tu_dong = models.IntegerField(default=0, verbose_name="Đóng TK - Tổ chức tự động")
    dong_to_chuc_tai_quay = models.IntegerField(default=0, verbose_name="Đóng TK - Tổ chức tại quầy")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lịch sử Đóng/Mở tài khoản"
        verbose_name_plural = "Lịch sử Đóng/Mở tài khoản"
        ordering = ['-report_month']
        unique_together = ['report_month']

    def __str__(self):
        return f"ĐMTK {self.report_month.strftime('%m/%Y')}"


# ===== ATM TRANSACTION REPORT MODELS =====

class ATMReportUpload(models.Model):
    """Model để theo dõi các file báo cáo ATM đã upload"""
    file_name = models.CharField(max_length=255, verbose_name="Tên file")
    report_period = models.DateField(verbose_name="Kỳ báo cáo")
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name="Ngày upload")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Người upload")
    record_count = models.IntegerField(default=0, verbose_name="Số lượng bản ghi")

    class Meta:
        verbose_name = "File báo cáo ATM"
        verbose_name_plural = "Lịch sử upload báo cáo ATM"
        ordering = ['-report_period', '-upload_date']
        unique_together = ['report_period']

    def __str__(self):
        return f"{self.file_name} - {self.report_period.strftime('%m/%Y')}"


class ATMTransactionReport(models.Model):
    """Model lưu trữ dữ liệu báo cáo giao dịch ATM"""
    upload = models.ForeignKey(ATMReportUpload, on_delete=models.CASCADE, related_name='transactions', verbose_name="File upload")
    branch_code = models.CharField(max_length=50, verbose_name="Mã chi nhánh", db_index=True)
    atm_no = models.CharField(max_length=50, verbose_name="Số hiệu ATM", db_index=True)
    tx_code = models.CharField(max_length=50, verbose_name="Mã giao dịch")
    tx_count = models.IntegerField(default=0, verbose_name="Số lượng giao dịch")
    tx_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Số tiền giao dịch")
    tx_fee = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="Phí giao dịch")
    vatamt = models.DecimalField(max_digits=20, decimal_places=2, default=0, verbose_name="VAT")
    report_period = models.DateField(verbose_name="Kỳ báo cáo", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Giao dịch ATM"
        verbose_name_plural = "Báo cáo giao dịch ATM"
        ordering = ['-report_period', 'atm_no']
        indexes = [
            models.Index(fields=['report_period', 'atm_no']),
            models.Index(fields=['report_period', 'branch_code']),
        ]

    def __str__(self):
        return f"ATM {self.atm_no} - {self.report_period.strftime('%m/%Y')}"
