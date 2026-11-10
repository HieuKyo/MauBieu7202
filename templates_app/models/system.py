"""
Model hệ thống: cấu hình chung, cấu hình chi nhánh, chương trình ứng dụng, hồ sơ người dùng, tin tức/khuyến mãi.
"""
from django.db import models
from django.contrib.auth.models import User


class GlobalConfig(models.Model):
    """
    Cấu hình toàn cục cho chương trình (Singleton - chỉ có 1 record duy nhất)
    Bao gồm: thông tin chi nhánh + các biến chung
    """
    # Thông tin chi nhánh
    ten_chi_nhanh = models.CharField(max_length=200, verbose_name="Tên chi nhánh", default="Chi nhánh Giá Rai Bạc Liêu")
    ten_chi_nhanh_hoa = models.CharField(max_length=200, verbose_name="Tên chi nhánh (IN HOA)", default="CHI NHÁNH GIÁ RAI BẠC LIÊU")
    ma_chi_nhanh = models.CharField(max_length=20, verbose_name="Mã chi nhánh", blank=True)
    mst = models.CharField(max_length=50, verbose_name="Mã số thuế", blank=True)
    gcndkdn = models.CharField(max_length=50, verbose_name="Giấy chứng nhận đăng ký kinh doanh", blank=True)
    mst_chi_nhanh = models.CharField(max_length=50, verbose_name="Mã số thuế chi nhánh", blank=True)
    dia_chi_chi_nhanh = models.TextField(verbose_name="Địa chỉ chi nhánh", blank=True)
    dien_thoai_chi_nhanh = models.CharField(max_length=50, verbose_name="Điện thoại chi nhánh", blank=True)
    so_fax = models.CharField(max_length=50, verbose_name="Số Fax", blank=True)
    dia_danh = models.CharField(max_length=200, verbose_name="Địa danh", blank=True, help_text="Ví dụ: Bạc Liêu, Đồng Tháp")

    # Nhân sự
    nguoi_dai_dien = models.CharField(max_length=200, verbose_name="Người đại diện", blank=True)
    chuc_vu = models.CharField(max_length=200, verbose_name="Chức vụ", blank=True)
    so_uy_quyen = models.CharField(max_length=100, verbose_name="Số uỷ quyền", blank=True)
    ngay_uy_quyen = models.DateField(verbose_name="Ngày uỷ quyền", null=True, blank=True)
    giao_dich_vien = models.CharField(max_length=200, verbose_name="Giao dịch viên", blank=True)
    kiem_soat_vien = models.CharField(max_length=200, verbose_name="Kiểm soát viên", blank=True)
    giam_doc = models.CharField(max_length=200, verbose_name="Giám đốc", blank=True)

    # Các biến tùy chỉnh chung (lưu dạng JSON)
    # Format: {"ten_bien": "gia_tri", "bien_khac": "gia_tri_khac"}
    custom_variables = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Biến tùy chỉnh",
        help_text="Các biến tùy chỉnh sẽ tự động có sẵn trong mọi mẫu biểu"
    )

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Người cập nhật"
    )

    class Meta:
        verbose_name = "Cấu hình Toàn cục"
        verbose_name_plural = "Cấu hình Toàn cục"

    def __str__(self):
        return f"Cấu hình: {self.ten_chi_nhanh}"

    def save(self, *args, **kwargs):
        """Đảm bảo chỉ có 1 instance duy nhất (Singleton pattern)"""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Không cho phép xóa"""
        pass

    @classmethod
    def get_instance(cls):
        """Lấy instance duy nhất, tạo mới nếu chưa tồn tại"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def get_all_variables(self):
        """
        Trả về dictionary chứa TẤT CẢ biến (chi nhánh + biến tùy chỉnh + biến tự động)
        để chèn vào template
        """
        from datetime import date

        # Ngày hiện tại
        today = date.today()
        day = today.day
        month = today.month
        year = today.year

        variables = {
            # Biến chi nhánh
            'ten_chi_nhanh': self.ten_chi_nhanh or '',
            'ten_chi_nhanh_hoa': self.ten_chi_nhanh_hoa or '',
            'ma_chi_nhanh': self.ma_chi_nhanh or '',
            'mst': self.mst or '',
            'dia_chi_chi_nhanh': self.dia_chi_chi_nhanh or '',
            'dien_thoai_chi_nhanh': self.dien_thoai_chi_nhanh or '',
            'so_fax': self.so_fax or '',
            'dia_danh': self.dia_danh or '',
            'giao_dich_vien': self.giao_dich_vien or '',
            'kiem_soat_vien': self.kiem_soat_vien or '',
            'giam_doc': self.giam_doc or '',

            # Biến tự động - Ngày giờ
            'ngay_hien_tai': today.strftime('%d/%m/%Y'),  # Format: dd/mm/yyyy
            'ngay_thang_nam_text': f"ngày {day:02d} tháng {month:02d} năm {year}",  # Format: ngày DD tháng MM năm YYYY
            'date_month_year': f"Date {day:02d} Month {month:02d} Year {year}",  # English format
            'nam_hien_tai': year,
            'thang_hien_tai': month,
            'ngay_hien_tai_day': day,
        }

        # Thêm các biến tùy chỉnh
        if self.custom_variables:
            variables.update(self.custom_variables)

        return variables


# ====================
# BranchConfig - Config per User/Branch
# ====================

class BranchConfig(models.Model):
    """
    Cấu hình chi nhánh/phòng giao dịch riêng cho từng đơn vị
    Mỗi đơn vị có thể có cấu hình riêng
    """

    BRANCH_TYPE_CHOICES = [
        ('CHI_NHANH', 'Chi nhánh'),
        ('PGD', 'Phòng giao dịch'),
        ('HOI_SO', 'Hội sở'),
    ]

    # Thông tin đơn vị
    branch_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã đơn vị",
        help_text="Ví dụ: HOI_SO, PGD_LANG_TRON, PGD_P1"
    )
    branch_type = models.CharField(
        max_length=20,
        choices=BRANCH_TYPE_CHOICES,
        default='CHI_NHANH',
        verbose_name="Loại đơn vị"
    )
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")

    # Thông tin chi nhánh (copy từ GlobalConfig)
    ten_chi_nhanh = models.CharField(max_length=200, verbose_name="Tên chi nhánh")
    ten_chi_nhanh_hoa = models.CharField(max_length=200, verbose_name="Tên chi nhánh (IN HOA)")
    ma_chi_nhanh = models.CharField(max_length=20, verbose_name="Mã chi nhánh", blank=True)
    mst = models.CharField(max_length=50, verbose_name="Mã số thuế", blank=True)
    gcndkdn = models.CharField(max_length=50, verbose_name="Giấy chứng nhận đăng ký kinh doanh", blank=True)
    mst_chi_nhanh = models.CharField(max_length=50, verbose_name="Mã số thuế chi nhánh", blank=True)
    dia_chi_chi_nhanh = models.TextField(verbose_name="Địa chỉ chi nhánh", blank=True)
    dien_thoai_chi_nhanh = models.CharField(max_length=50, verbose_name="Điện thoại chi nhánh", blank=True)
    so_fax = models.CharField(max_length=50, verbose_name="Số Fax", blank=True)
    dia_danh = models.CharField(max_length=200, verbose_name="Địa danh", blank=True, help_text="Ví dụ: Bạc Liêu, Đồng Tháp")

    # Nhân sự
    nguoi_dai_dien = models.CharField(max_length=200, verbose_name="Người đại diện", blank=True)
    chuc_vu = models.CharField(max_length=200, verbose_name="Chức vụ", blank=True)
    so_uy_quyen = models.CharField(max_length=100, verbose_name="Số uỷ quyền", blank=True)
    ngay_uy_quyen = models.DateField(verbose_name="Ngày uỷ quyền", null=True, blank=True)
    giao_dich_vien = models.CharField(max_length=200, verbose_name="Giao dịch viên", blank=True)
    kiem_soat_vien = models.CharField(max_length=200, verbose_name="Kiểm soát viên", blank=True)
    giam_doc = models.CharField(max_length=200, verbose_name="Giám đốc", blank=True)

    # Các biến tùy chỉnh riêng của từng chi nhánh (lưu dạng JSON)
    custom_variables = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Biến tùy chỉnh riêng",
        help_text="Các biến tùy chỉnh riêng cho chi nhánh này"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Người cập nhật"
    )

    class Meta:
        verbose_name = "Cấu hình Chi nhánh"
        verbose_name_plural = "Cấu hình Chi nhánh"
        ordering = ['branch_code']

    def __str__(self):
        return f"{self.get_branch_type_display()}: {self.ten_chi_nhanh}"

    def get_all_variables(self):
        """
        Trả về dictionary chứa TẤT CẢ biến (chi nhánh + biến tùy chỉnh + biến tự động)
        để chèn vào template
        """
        from datetime import date

        # Ngày hiện tại
        today = date.today()
        day = today.day
        month = today.month
        year = today.year

        variables = {
            # Biến chi nhánh
            'ten_chi_nhanh': self.ten_chi_nhanh or '',
            'ten_chi_nhanh_hoa': self.ten_chi_nhanh_hoa or '',
            'ma_chi_nhanh': self.ma_chi_nhanh or '',
            'mst': self.mst or '',
            'gcndkdn': self.gcndkdn or '',
            'mst_chi_nhanh': self.mst_chi_nhanh or '',
            'dia_chi_chi_nhanh': self.dia_chi_chi_nhanh or '',
            'dien_thoai_chi_nhanh': self.dien_thoai_chi_nhanh or '',
            'so_fax': self.so_fax or '',
            'dia_danh': self.dia_danh or '',
            'nguoi_dai_dien': self.nguoi_dai_dien or '',
            'chuc_vu': self.chuc_vu or '',
            'so_uy_quyen': self.so_uy_quyen or '',
            'ngay_uy_quyen': self.ngay_uy_quyen.strftime('%d/%m/%Y') if self.ngay_uy_quyen else '',
            'giao_dich_vien': self.giao_dich_vien or '',
            'kiem_soat_vien': self.kiem_soat_vien or '',
            'giam_doc': self.giam_doc or '',

            # Biến tự động - Ngày giờ
            'ngay_hien_tai': today.strftime('%d/%m/%Y'),
            'ngay_thang_nam_text': f"ngày {day:02d} tháng {month:02d} năm {year}",
            'date_month_year': f"Date {day:02d} Month {month:02d} Year {year}",
            'nam_hien_tai': year,
            'thang_hien_tai': month,
            'ngay_hien_tai_day': day,
        }

        # Thêm các biến tùy chỉnh riêng của chi nhánh này
        if self.custom_variables:
            variables.update(self.custom_variables)

        return variables

    @classmethod
    def get_for_user(cls, user):
        """
        Lấy BranchConfig cho user dựa vào UserProfile.branch
        Nếu không tìm thấy, fallback về GlobalConfig
        """
        try:
            # Lấy branch code từ UserProfile
            if hasattr(user, 'profile') and user.profile.branch:
                user_branch = user.profile.branch

                # Tìm BranchConfig tương ứng
                branch_config = cls.objects.filter(
                    branch_code=user_branch,
                    is_active=True
                ).first()

                if branch_config:
                    return branch_config
        except Exception:
            # Log error nếu cần
            pass

        # Fallback: trả về GlobalConfig
        return GlobalConfig.get_instance()
# ====================
# Employee Management Models
# ====================

class AppProgram(models.Model):
    """
    Danh sách chương trình/phần mềm có thể cấp quyền cho nhân viên
    """
    name = models.CharField(max_length=200, verbose_name="Tên chương trình")
    url = models.CharField(max_length=500, blank=True, verbose_name="Đường dẫn / Link")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự hiển thị")

    class Meta:
        verbose_name = "Chương trình"
        verbose_name_plural = "Danh sách chương trình"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """
    Thông tin mở rộng cho User - Quản lý nhân viên
    Liên kết One-to-One với django.contrib.auth.models.User
    """

    GENDER_CHOICES = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác'),
    ]

    BRANCH_CHOICES = [
        ('HOI_SO', 'Hội sở Giá Rai Bạc Liêu'),
        ('PGD_P1', 'Phòng Giao dịch Phường 1'),
        ('PGD_LANG_TRON', 'Phòng Giao dịch Láng Tròn'),
    ]

    DEPARTMENT_CHOICES = [
        ('KE_TOAN', 'Phòng Kế toán & Ngân quỹ'),
        ('KHACH_HANG', 'Phòng Khách hàng'),
        ('BAN_GIAM_DOC', 'Ban Giám đốc'),
        ('TONG_HOP', 'Phòng Tổng hợp'),
    ]

    JOB_FUNCTION_CHOICES = [
        ('GIAO_DICH_VIEN', 'Giao dịch viên'),
        ('KIEM_SOAT_VIEN', 'Kiểm soát viên'),
        ('HAU_KIEM_VIEN', 'Hậu kiểm viên'),
        ('TONG_HOP_VIEN', 'Tổng hợp viên'),
    ]

    POSITION_CHOICES = [
        ('GIAM_DOC', 'Giám đốc'),
        ('PHO_GIAM_DOC', 'Phó Giám Đốc'),
        ('TRUONG_PHONG', 'Trưởng phòng'),
        ('PHO_PHONG', 'Phó phòng'),
        ('GD_PGD', 'Giám đốc Phòng Giao dịch'),
        ('PGD_PGD', 'Phó Giám đốc Phòng giao dịch'),
        ('NHAN_VIEN', 'Nhân viên'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Tài khoản"
    )
    employee_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Mã nhân viên",
        help_text="Mã nhân viên (khác với username)"
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name="Họ và tên"
    )
    dob = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày sinh"
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='Nam',
        verbose_name="Giới tính"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Số điện thoại"
    )
    address = models.TextField(
        blank=True,
        verbose_name="Địa chỉ"
    )
    id_card_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Số CCCD"
    )
    id_card_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày cấp CCCD"
    )
    id_card_place = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nơi cấp CCCD"
    )
    branch = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Chi nhánh",
        help_text="Mã đơn vị (phải khớp với BranchConfig.branch_code)"
    )
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        verbose_name="Phòng ban"
    )
    job_function = models.CharField(
        max_length=50,
        choices=JOB_FUNCTION_CHOICES,
        blank=True,
        verbose_name="Nghiệp vụ"
    )
    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        blank=True,
        verbose_name="Chức vụ"
    )

    # Thông tin hệ thống
    ipcas_user = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tài khoản IPCAS"
    )
    csp_cuser = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Tài khoản phát hành thẻ CSP",
        help_text="VD: 7202chieutt — dùng để đối chiếu file phát hành thẻ CSP"
    )
    mac_address = models.CharField(
        max_length=17,
        blank=True,
        verbose_name="Địa chỉ MAC",
        help_text="Định dạng: XX:XX:XX:XX:XX:XX"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Địa chỉ IP"
    )

    # Chương trình được cấp quyền
    app_permissions = models.ManyToManyField(
        'AppProgram',
        blank=True,
        verbose_name="Chương trình được cấp phép",
        related_name='authorized_users'
    )

    # Digital Certificate (Chứng thư số) fields
    certificate_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Mã chứng thư số"
    )
    certificate_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Chứng thư số từ ngày"
    )
    certificate_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Chứng thư số đến ngày"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Hồ sơ nhân viên"
        verbose_name_plural = "Hồ sơ nhân viên"
        ordering = ['employee_code']

    def __str__(self):
        return f"{self.employee_code} - {self.full_name}"

    def is_certificate_expiring_soon(self):
        """Check if certificate expires within 20 days"""
        if not self.certificate_end_date:
            return False
        from datetime import date, timedelta
        today = date.today()
        warning_date = today + timedelta(days=20)
        return self.certificate_end_date <= warning_date and self.certificate_end_date >= today

    def is_certificate_expired(self):
        """Check if certificate has already expired"""
        if not self.certificate_end_date:
            return False
        from datetime import date
        return self.certificate_end_date < date.today()

    def days_until_certificate_expiry(self):
        """Return number of days until certificate expiry"""
        if not self.certificate_end_date:
            return None
        from datetime import date
        delta = self.certificate_end_date - date.today()
        return delta.days


class Promotion(models.Model):
    """Chương trình khuyến mãi / Tin tức nội bộ"""
    title = models.CharField(max_length=255, verbose_name="Tiêu đề chương trình")
    content = models.TextField(verbose_name="Nội dung chi tiết")
    image = models.ImageField(
        upload_to='promotions/',
        blank=True,
        null=True,
        verbose_name="Hình ảnh banner"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng")
    start_date = models.DateField(verbose_name="Ngày bắt đầu hiệu lực")
    end_date = models.DateField(verbose_name="Ngày hết hạn")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        verbose_name = "Chương trình khuyến mãi"
        verbose_name_plural = "Chương trình khuyến mãi"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
