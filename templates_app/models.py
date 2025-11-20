from django.db import models
from django.contrib.auth.models import Group, User
from django.core.validators import FileExtensionValidator
import unicodedata


def remove_vietnamese_diacritics(text):
    """
    Loại bỏ dấu tiếng Việt và trả về chữ không dấu
    VD: 'Nguyễn Văn A' -> 'NGUYEN VAN A'
    """
    if not text:
        return ''

    # Vietnamese character mapping
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'đ': 'd',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
        'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
        'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
        'Đ': 'D',
        'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
        'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
        'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
        'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
        'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
        'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
        'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
        'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
    }

    result = []
    for char in text:
        if char in vietnamese_map:
            result.append(vietnamese_map[char])
        else:
            result.append(char)

    return ''.join(result).upper()


class Category(models.Model):
    """Danh mục mẫu biểu (cấp cha)"""
    name = models.CharField(max_length=200, verbose_name="Tên danh mục")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")

    # Cấu hình các nhóm field hiển thị trong form
    # Possible values: customer_basic_info, customer_classification, banking, card, services, print_info
    visible_field_groups = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Nhóm trường hiển thị",
        help_text="Danh sách các nhóm trường cần hiển thị trong form. VD: ['customer_basic_info', 'banking', 'card']"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Danh mục"
        verbose_name_plural = "Danh mục"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_visible_field_groups(self):
        """Trả về danh sách field groups, mặc định hiển thị tất cả nếu không cấu hình"""
        if not self.visible_field_groups:
            # Mặc định: hiển thị tất cả field groups
            return [
                'customer_basic_info',  # Gộp: personal_info, id_documents, contact, employment
                'customer_classification',
                'banking',
                'card',
                'services',
                'joint_savings',
                'print_info'
            ]
        # Handle legacy field groups - convert old groups to new merged group
        converted_groups = []
        old_groups = ['personal_info', 'id_documents', 'contact', 'employment']
        has_old_groups = any(g in self.visible_field_groups for g in old_groups)

        for group in self.visible_field_groups:
            if group in old_groups:
                if 'customer_basic_info' not in converted_groups:
                    converted_groups.append('customer_basic_info')
            else:
                if group not in converted_groups:
                    converted_groups.append(group)

        return converted_groups if has_old_groups else self.visible_field_groups


class Variable(models.Model):
    """Biến dùng trong template Word"""
    FIELD_TYPES = [
        ('text', 'Văn bản'),
        ('textarea', 'Đoạn văn'),
        ('date', 'Ngày tháng'),
        ('number', 'Con số'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name="Tên biến (không dấu, không khoảng trắng)")
    label = models.CharField(max_length=200, verbose_name="Nhãn hiển thị")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='text', verbose_name="Kiểu dữ liệu")
    help_text = models.CharField(max_length=500, blank=True, verbose_name="Gợi ý nhập liệu")
    required = models.BooleanField(default=True, verbose_name="Bắt buộc nhập")
    default_value = models.TextField(blank=True, verbose_name="Giá trị mặc định")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    class Meta:
        verbose_name = "Biến"
        verbose_name_plural = "Biến"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.label})"


class Template(models.Model):
    """Mẫu biểu Word (cấp con)"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='templates', verbose_name="Danh mục")
    name = models.CharField(max_length=200, verbose_name="Tên mẫu biểu")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    file = models.FileField(
        upload_to='templates/docx/',
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name="File Word (.docx)"
    )
    variables = models.ManyToManyField(Variable, through='TemplateVariable', related_name='templates', verbose_name="Biến")
    allowed_groups = models.ManyToManyField(Group, blank=True, related_name='templates', verbose_name="Nhóm được phép truy cập")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Mẫu biểu"
        verbose_name_plural = "Mẫu biểu"
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def user_has_access(self, user):
        """Kiểm tra user có quyền truy cập template này không"""
        if user.is_superuser:
            return True
        if self.allowed_groups.count() == 0:
            return True  # Nếu không có group nào được gán, cho phép tất cả
        return self.allowed_groups.filter(id__in=user.groups.all()).exists()


class TemplateVariable(models.Model):
    """Liên kết giữa Template và Variable"""
    template = models.ForeignKey(Template, on_delete=models.CASCADE, verbose_name="Mẫu biểu")
    variable = models.ForeignKey(Variable, on_delete=models.CASCADE, verbose_name="Biến")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị trong form")

    class Meta:
        verbose_name = "Biến của mẫu biểu"
        verbose_name_plural = "Biến của mẫu biểu"
        ordering = ['order', 'variable__name']
        unique_together = ['template', 'variable']

    def __str__(self):
        return f"{self.template.name} - {self.variable.name}"


class Customer(models.Model):
    """Thông tin khách hàng"""

    NGHE_NGHIEP_CHOICES = [
        ('Công chức viên chức', 'Công chức viên chức'),
        ('Nông dân', 'Nông dân'),
        ('Giáo viên/Bác Sĩ', 'Giáo viên/Bác Sĩ'),
        ('Giáo viên', 'Giáo viên'),  # FIX: Thêm riêng lẻ
        ('Bác sĩ', 'Bác sĩ'),  # FIX: Thêm riêng lẻ
        ('Công nhân', 'Công nhân'),
        ('Kinh doanh tự do', 'Kinh doanh tự do'),
        ('Học sinh/Sinh viên', 'Học sinh/Sinh viên'),
        ('Nội trợ', 'Nội trợ'),
        ('Công an/Bộ đội', 'Công an/Bộ đội'),
        ('Kỹ sư', 'Kỹ sư'),
        ('Khác', 'Khác'),
    ]

    NOI_CAP_CHOICES = [
        ('Cục CSQLHC về TTXH', 'Cục CSQLHC về TTXH'),
        ('Bộ Công An', 'Bộ Công An'),
        ('Khác', 'Khác'),
    ]

    LOAI_TIEN_TE_CHOICES = [
        ('VND', 'VND - Việt Nam Đồng'),
        ('USD', 'USD - Đô la Mỹ'),
    ]

    LOAI_THE_CHOICES = [
        ('Thẻ Ghi nợ nội địa', 'Thẻ Ghi nợ nội địa'),
        ('The Plus Success', 'The Plus Success'),
        ('Agribank Debit Card', 'Agribank Debit Card'),
        ('Thẻ Visa', 'Thẻ Visa'),
        ('Thẻ MasterCard', 'Thẻ MasterCard'),
        ('Thẻ JCB', 'Thẻ JCB'),
    ]

    HANG_THE_CHOICES = [
        ('Hạng chuẩn', 'Hạng chuẩn'),
        ('Hạng vàng', 'Hạng vàng'),
        ('Classic', 'Classic'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ]

    LOAI_TAI_KHOAN_CHOICES = [
        ('Tài khoản ngẫu nhiên', 'Tài khoản ngẫu nhiên'),
        ('Tài khoản số theo yêu cầu', 'Tài khoản số theo yêu cầu'),
        ('Tài khoản chuyên dụng', 'Tài khoản chuyên dụng'),
    ]

    # Mã khách hàng và CIF
    ma_khach_hang = models.CharField(max_length=50, blank=True, verbose_name="Mã khách hàng", db_index=True)
    cif = models.CharField(max_length=20, blank=True, unique=True, null=True, verbose_name="Mã CIF", db_index=True)

    # Thông tin cá nhân cơ bản
    ho_ten = models.CharField(max_length=200, verbose_name="Họ và tên", db_index=True)
    ho_ten_tieng_anh = models.CharField(max_length=200, blank=True, verbose_name="Họ và tên tiếng Anh")
    ngay_sinh = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gioi_tinh = models.CharField(
        max_length=10,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Khác', 'Khác')],
        default='Nam',
        verbose_name="Giới tính"
    )
    dan_toc = models.CharField(max_length=50, blank=True, default='Kinh', verbose_name="Dân tộc")

    # Giấy tờ tùy thân
    so_cmnd = models.CharField(max_length=20, unique=True, verbose_name="Số CMND/CCCD", db_index=True)
    ngay_cap_cmnd = models.DateField(null=True, blank=True, verbose_name="Ngày cấp CMND/CCCD")
    ngay_het_han_cmnd = models.DateField(null=True, blank=True, verbose_name="Ngày hết hạn CMND/CCCD")
    noi_cap_cmnd = models.CharField(
        max_length=50,
        choices=NOI_CAP_CHOICES,
        default='Cục CSQLHC về TTXH',
        verbose_name="Nơi cấp CMND/CCCD"
    )
    noi_cap_cmnd_custom = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nơi cấp CMND/CCCD (tùy chỉnh)"
    )
    ma_noi_cap_cmnd = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Mã nơi cấp CMND/CCCD"
    )
    so_ho_chieu = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Số hộ chiếu"
    )

    # Liên hệ
    dia_chi = models.TextField(blank=True, verbose_name="Địa chỉ thường trú")
    ho_khau = models.TextField(blank=True, verbose_name="Hộ khẩu thường trú")
    so_dien_thoai = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại", db_index=True)
    email = models.EmailField(blank=True, verbose_name="Email")

    # Thông tin địa chỉ chi tiết (Address Selector Component)
    province = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tỉnh/Thành phố"
    )
    district = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Quận/Huyện"
    )
    ward = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Phường/Xã"
    )
    hamlet = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ấp/Khóm"
    )
    full_address = models.TextField(
        blank=True,
        verbose_name="Địa chỉ đầy đủ"
    )

    # Địa chỉ hành chính (mã)
    ma_tinh = models.CharField(max_length=10, blank=True, verbose_name="Mã tỉnh/thành phố")
    ma_quan_huyen = models.CharField(max_length=10, blank=True, verbose_name="Mã quận/huyện")
    ma_phuong_xa = models.CharField(max_length=10, blank=True, verbose_name="Mã phường/xã")

    # Thông tin quốc tịch và thuế
    quoc_tich = models.CharField(max_length=10, blank=True, default='VN', verbose_name="Quốc tịch")
    ma_so_thue = models.CharField(max_length=20, blank=True, verbose_name="Mã số thuế")

    # Thông tin nghề nghiệp
    nghe_nghiep = models.CharField(
        max_length=200,
        blank=True,
        choices=NGHE_NGHIEP_CHOICES,
        verbose_name="Nghề nghiệp"
    )
    noi_lam_viec = models.CharField(max_length=200, blank=True, verbose_name="Nơi làm việc")

    # Thông tin tài khoản
    so_tai_khoan = models.CharField(max_length=30, blank=True, verbose_name="Số tài khoản")
    loai_tai_khoan = models.CharField(max_length=100, blank=True, choices=LOAI_TAI_KHOAN_CHOICES, verbose_name="Loại tài khoản")
    so_tai_khoan_yc = models.CharField(max_length=30, blank=True, verbose_name="Số tài khoản theo yêu cầu")
    loai_tien_te = models.CharField(max_length=10, choices=LOAI_TIEN_TE_CHOICES, default='VND', verbose_name="Loại tiền tệ")

    # Thông tin thẻ
    loai_the = models.CharField(max_length=50, choices=LOAI_THE_CHOICES, blank=True, verbose_name="Loại thẻ")
    hang_the = models.CharField(max_length=20, choices=HANG_THE_CHOICES, blank=True, verbose_name="Hạng thẻ")
    so_the_atm = models.CharField(max_length=20, blank=True, verbose_name="Số thẻ ATM")
    thoi_han_the = models.CharField(max_length=50, blank=True, verbose_name="Thời hạn thẻ")
    ngay_tra_the = models.DateField(null=True, blank=True, verbose_name="Ngày trả thẻ")
    loai_phi = models.CharField(max_length=100, blank=True, verbose_name="Loại phí")
    phat_hanh_lan_dau = models.BooleanField(default=False, verbose_name="Phát hành lần đầu")
    phat_hanh_lai = models.BooleanField(default=False, verbose_name="Phát hành lại")

    # Đăng ký dịch vụ - Thủ hộ
    dv_thu_ho_tien_nuoc = models.BooleanField(default=False, verbose_name="Thủ hộ: Tiền nước")
    dv_thu_ho_tien_dien = models.BooleanField(default=False, verbose_name="Thủ hộ: Tiền điện")
    dv_thu_ho_vien_thong = models.BooleanField(default=False, verbose_name="Thủ hộ: Viễn thông")
    dv_thu_ho_hoc_phi = models.BooleanField(default=False, verbose_name="Thủ hộ: Học phí")
    dv_thu_ho_bao_hiem = models.BooleanField(default=False, verbose_name="Thủ hộ: Bảo hiểm")

    # Đăng ký dịch vụ - Ngân hàng điện tử
    dv_sms_banking = models.BooleanField(default=False, verbose_name="Dịch vụ: SMS Banking")
    dv_e_mobile = models.BooleanField(default=False, verbose_name="Dịch vụ: E-Mobile")
    dv_bankplus = models.BooleanField(default=False, verbose_name="Dịch vụ: Bankplus")
    dv_e_commerce = models.BooleanField(default=False, verbose_name="Dịch vụ: E-Commerce")
    dv_soft_otp = models.BooleanField(default=False, verbose_name="Dịch vụ: Soft OTP")
    dv_smart_otp = models.BooleanField(default=False, verbose_name="Dịch vụ: Smart OTP")
    dv_retail_ebanking = models.BooleanField(default=False, verbose_name="Dịch vụ: Retail E-banking")

    # Kênh giao dịch
    kenh_mobile = models.BooleanField(default=False, verbose_name="Kênh: Mobile")
    kenh_internet = models.BooleanField(default=False, verbose_name="Kênh: Internet Banking")

    # Thông tin thẻ bổ sung
    the_lap_nghiep = models.BooleanField(default=False, verbose_name="Thẻ lập nghiệp")
    the_lien_ket = models.BooleanField(default=False, verbose_name="Thẻ liên kết")
    the_dong_thuong_hieu = models.BooleanField(default=False, verbose_name="Thẻ đồng thương hiệu")
    ten_the_1 = models.CharField(max_length=200, blank=True, verbose_name="Tên thẻ 1")
    ten_the_2 = models.CharField(max_length=200, blank=True, verbose_name="Tên thẻ 2")  # FIX: Thêm tên thẻ 2 cho table thứ 2

    # Dịch vụ ABIC
    dv_abic = models.BooleanField(default=False, verbose_name="Dịch vụ: ABIC")

    # Kết quả phân loại khách hàng
    KET_QUA_PHAN_LOAI_CHOICES = [
        ('', '--- Chọn ---'),
        ('Cao', 'Cao'),
        ('Trung bình', 'Trung bình'),
        ('Thấp', 'Thấp'),
    ]
    ket_qua_phan_loai_kh = models.CharField(max_length=20, blank=True, choices=KET_QUA_PHAN_LOAI_CHOICES, verbose_name="Kết quả phân loại KH")

    # Tiền gửi tiết kiệm chung - Thông tin người gửi tiền thứ hai
    ho_ten_nguoi_gui_2 = models.CharField(max_length=200, blank=True, verbose_name="Họ tên người gửi tiền thứ hai")
    so_cmnd_nguoi_gui_2 = models.CharField(max_length=20, blank=True, verbose_name="CMND/CCCD/Hộ chiếu người gửi 2")
    ngay_cap_cmnd_nguoi_gui_2 = models.DateField(null=True, blank=True, verbose_name="Ngày cấp CMND người gửi 2")
    noi_cap_cmnd_nguoi_gui_2 = models.CharField(max_length=200, blank=True, verbose_name="Nơi cấp CMND người gửi 2")
    dia_chi_nguoi_gui_2 = models.TextField(blank=True, verbose_name="Địa chỉ người gửi 2")
    sdt_nguoi_gui_2 = models.CharField(max_length=20, blank=True, verbose_name="Số điện thoại người gửi 2")

    # Tiền gửi tiết kiệm chung - Giao dịch thẻ tiết kiệm
    # Rút lãi
    gd_rut_lai_tat_ca = models.BooleanField(default=False, verbose_name="Rút lãi - Tất cả người gửi tiền")
    gd_rut_lai_mot_so = models.BooleanField(default=False, verbose_name="Rút lãi - Một/một số người gửi tiền")
    # Tất toán Thẻ tiết kiệm
    gd_tat_toan_tat_ca = models.BooleanField(default=False, verbose_name="Tất toán - Tất cả người gửi tiền")
    gd_tat_toan_mot_so = models.BooleanField(default=False, verbose_name="Tất toán - Một/một số người gửi tiền")
    # Báo mất thẻ TK
    gd_bao_mat_tat_ca = models.BooleanField(default=False, verbose_name="Báo mất - Tất cả người gửi tiền")
    gd_bao_mat_mot_so = models.BooleanField(default=False, verbose_name="Báo mất - Một/một số người gửi tiền")
    # Báo hỏng thẻ TK
    gd_bao_hong_tat_ca = models.BooleanField(default=False, verbose_name="Báo hỏng - Tất cả người gửi tiền")
    gd_bao_hong_mot_so = models.BooleanField(default=False, verbose_name="Báo hỏng - Một/một số người gửi tiền")
    # Đề nghị phong tỏa TKTG tiết kiệm
    gd_phong_toa_tat_ca = models.BooleanField(default=False, verbose_name="Phong tỏa - Tất cả người gửi tiền")
    gd_phong_toa_mot_so = models.BooleanField(default=False, verbose_name="Phong tỏa - Một/một số người gửi tiền")
    # Đề nghị xác nhận số dư
    gd_xac_nhan_so_du_tat_ca = models.BooleanField(default=False, verbose_name="Xác nhận số dư - Tất cả người gửi tiền")
    gd_xac_nhan_so_du_mot_so = models.BooleanField(default=False, verbose_name="Xác nhận số dư - Một/một số người gửi tiền")

    # Thông tin in mẫu biểu
    ngay_in = models.DateField(null=True, blank=True, verbose_name="Ngày in mẫu biểu")

    # Metadata
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers',
        verbose_name="Người tạo"
    )

    class Meta:
        verbose_name = "Khách hàng"
        verbose_name_plural = "Khách hàng"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ho_ten', 'so_cmnd']),
            models.Index(fields=['so_dien_thoai']),
        ]

    def __str__(self):
        return f"{self.ho_ten} - {self.so_cmnd}"

    def clean(self):
        """Validate customer data"""
        from django.core.exceptions import ValidationError
        from datetime import datetime, date
        from dateutil.relativedelta import relativedelta

        errors = {}

        # Validate CMND/CCCD format (only allow 9 or 12 digits)
        if self.so_cmnd:
            # Remove whitespace
            cmnd_cleaned = self.so_cmnd.strip()

            # Check if it's all digits
            if not cmnd_cleaned.isdigit():
                errors['so_cmnd'] = 'Số CMND/CCCD chỉ được chứa chữ số (0-9)'
            else:
                # Check length
                cmnd_length = len(cmnd_cleaned)
                if cmnd_length not in [9, 12]:
                    errors['so_cmnd'] = f'Số CMND/CCCD phải có 9 chữ số (CMND cũ) hoặc 12 chữ số (CCCD/Căn cước). Hiện tại: {cmnd_length} chữ số'

        # Validate age (must be at least 15 years old)
        if self.ngay_sinh:
            today = date.today()
            age = relativedelta(today, self.ngay_sinh).years

            if age < 15:
                errors['ngay_sinh'] = f'Khách hàng phải từ 15 tuổi trở lên (hiện tại: {age} tuổi)'
            elif age > 120:
                errors['ngay_sinh'] = f'Ngày sinh không hợp lệ (tuổi tính được: {age})'

        # Validate CCCD expiry date
        if self.ngay_cap_cmnd and self.ngay_het_han_cmnd:
            if self.ngay_het_han_cmnd <= self.ngay_cap_cmnd:
                errors['ngay_het_han_cmnd'] = 'Ngày hết hạn phải sau ngày cấp'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """Override save to call clean()"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_age(self):
        """Tính tuổi khách hàng"""
        if not self.ngay_sinh:
            return None
        from datetime import date
        from dateutil.relativedelta import relativedelta
        return relativedelta(date.today(), self.ngay_sinh).years

    def get_cccd_days_remaining(self):
        """Tính số ngày CCCD còn hiệu lực"""
        if not self.ngay_het_han_cmnd:
            return None
        from datetime import date
        delta = self.ngay_het_han_cmnd - date.today()
        return delta.days

    def get_cccd_status(self):
        """Trả về trạng thái CCCD"""
        days = self.get_cccd_days_remaining()
        if days is None:
            return {'status': 'unknown', 'message': 'Chưa có thông tin', 'class': 'secondary'}

        if days < 0:
            return {
                'status': 'expired',
                'message': f'Đã hết hạn ({abs(days)} ngày trước)',
                'class': 'danger'
            }
        elif days < 30:
            return {
                'status': 'expiring_soon',
                'message': f'Sắp hết hạn (còn {days} ngày)',
                'class': 'warning'
            }
        elif days < 90:
            return {
                'status': 'valid',
                'message': f'Còn hiệu lực ({days} ngày)',
                'class': 'info'
            }
        else:
            years = days // 365
            return {
                'status': 'valid',
                'message': f'Còn hiệu lực (~{years} năm)',
                'class': 'success'
            }

    def get_age_status(self):
        """Trả về trạng thái độ tuổi"""
        age = self.get_age()
        if age is None:
            return {'status': 'unknown', 'message': 'Chưa có thông tin', 'class': 'secondary'}

        if age < 15:
            return {
                'status': 'too_young',
                'message': f'Chưa đủ 15 tuổi ({age} tuổi)',
                'class': 'danger'
            }
        elif age < 18:
            return {
                'status': 'minor',
                'message': f'{age} tuổi - Cần người giám hộ',
                'class': 'warning'
            }
        else:
            return {
                'status': 'adult',
                'message': f'{age} tuổi - Đủ điều kiện',
                'class': 'success'
            }

    def get_noi_cap_display_value(self):
        """Lấy giá trị nơi cấp để hiển thị (ưu tiên custom nếu chọn 'Khác')"""
        if self.noi_cap_cmnd == 'Khác' and self.noi_cap_cmnd_custom:
            return self.noi_cap_cmnd_custom
        return self.noi_cap_cmnd

    def get_data_dict(self):
        """
        Trả về dictionary chứa thông tin khách hàng
        Dùng để auto-fill form
        Checkbox: ☑ (checked) hoặc ☐ (unchecked)
        """
        # Helper function to convert boolean to checkbox character
        def checkbox(value):
            return '☑' if value else '☐'

        # Date variables for ngay_sinh
        d1, d2, m1, m2, y1, y2, y3, y4 = '', '', '', '', '', '', '', ''
        if self.ngay_sinh:
            date_str = self.ngay_sinh.strftime('%d%m%Y')
            if len(date_str) == 8:
                d1, d2 = date_str[0], date_str[1]
                m1, m2 = date_str[2], date_str[3]
                y1, y2, y3, y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables for ngay_cap_cmnd
        dcc1, dcc2, mcc1, mcc2, ycc1, ycc2, ycc3, ycc4 = '', '', '', '', '', '', '', ''
        if self.ngay_cap_cmnd:
            date_str = self.ngay_cap_cmnd.strftime('%d%m%Y')
            if len(date_str) == 8:
                dcc1, dcc2 = date_str[0], date_str[1]
                mcc1, mcc2 = date_str[2], date_str[3]
                ycc1, ycc2, ycc3, ycc4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables for ngay_het_han_cmnd
        dhh1, dhh2, mhh1, mhh2, yhh1, yhh2, yhh3, yhh4 = '', '', '', '', '', '', '', ''
        if self.ngay_het_han_cmnd:
            date_str = self.ngay_het_han_cmnd.strftime('%d%m%Y')
            if len(date_str) == 8:
                dhh1, dhh2 = date_str[0], date_str[1]
                mhh1, mhh2 = date_str[2], date_str[3]
                yhh1, yhh2, yhh3, yhh4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables for ngay_tra_the
        dtt1, dtt2, mtt1, mtt2, ytt1, ytt2, ytt3, ytt4 = '', '', '', '', '', '', '', ''
        if self.ngay_tra_the:
            date_str = self.ngay_tra_the.strftime('%d%m%Y')
            if len(date_str) == 8:
                dtt1, dtt2 = date_str[0], date_str[1]
                mtt1, mtt2 = date_str[2], date_str[3]
                ytt1, ytt2, ytt3, ytt4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables for ngay_tra_the_tinh (calculated later)
        dttt1, dttt2, mttt1, mttt2, yttt1, yttt2, yttt3, yttt4 = '', '', '', '', '', '', '', ''

        # Checkbox variables for hạng thẻ
        the_hang_chuan = checkbox(self.hang_the == 'Hạng chuẩn')
        the_hang_vang = checkbox(self.hang_the == 'Hạng vàng')
        the_hang_bach_kim = checkbox(self.hang_the == 'Hạng bạch kim')

        # Checkbox for loại thẻ
        the_ghi_no_noi_dia = checkbox(self.loai_the == 'Thẻ Ghi nợ nội địa')
        the_ghi_no_quoc_te = checkbox(self.loai_the == 'Thẻ Ghi nợ quốc tế')
        the_tin_dung = checkbox(self.loai_the == 'Thẻ tín dụng')
        loai_the_jcb = checkbox(self.loai_the == 'Thẻ JCB')
        loai_the_visa = checkbox(self.loai_the == 'Thẻ Visa')
        loai_the_mastercard = checkbox(self.loai_the == 'Thẻ MasterCard')
        loai_the_khac = checkbox(self.loai_the not in ['Thẻ Ghi nợ nội địa', 'Thẻ Ghi nợ quốc tế', 'Thẻ tín dụng', 'Thẻ JCB', 'Thẻ Visa', 'Thẻ MasterCard', 'The Plus Success', 'Agribank Debit Card'])

        # Checkbox variables for CMND vs CCCD vs Căn cước (based on ID length and issue date)
        # Logic:
        # - cmnd: CMND 9 số (old ID card)
        # - cccd: CCCD 12 số có ngày cấp ≤ 01/07/2024
        # - cancuoc: CCCD 12 số có ngày cấp > 01/07/2024
        from datetime import date as datetime_date
        cutoff_date = datetime_date(2024, 7, 1)

        id_length = len(self.so_cmnd) if self.so_cmnd else 0

        if id_length == 9:
            # CMND 9 số cũ
            cmnd = checkbox(True)
            cccd = checkbox(False)
            cancuoc = checkbox(False)
        elif id_length == 12 and self.ngay_cap_cmnd:
            # CCCD 12 số - phân biệt theo ngày cấp
            cmnd = checkbox(False)
            if self.ngay_cap_cmnd <= cutoff_date:
                cccd = checkbox(True)
                cancuoc = checkbox(False)
            else:
                cccd = checkbox(False)
                cancuoc = checkbox(True)
        else:
            # Không xác định
            cmnd = checkbox(False)
            cccd = checkbox(False)
            cancuoc = checkbox(False)

        # Checkbox variables for giới tính
        gioi_tinh_nam = checkbox(self.gioi_tinh == 'Nam')
        gioi_tinh_nu = checkbox(self.gioi_tinh == 'Nữ')

        # Checkbox variables for nghề nghiệp
        nghe_nghiep_cong_chuc = checkbox(self.nghe_nghiep == 'Công chức viên chức')
        nghe_nghiep_nong_dan = checkbox(self.nghe_nghiep == 'Nông dân')
        nghe_nghiep_giao_vien_bac_si = checkbox(self.nghe_nghiep == 'Giáo viên/Bác Sĩ')
        nghe_nghiep_giao_vien = checkbox(self.nghe_nghiep == 'Giáo viên')  # FIX: Thêm riêng lẻ
        nghe_nghiep_bac_si = checkbox(self.nghe_nghiep == 'Bác sĩ')  # FIX: Thêm riêng lẻ
        nghe_nghiep_cong_nhan = checkbox(self.nghe_nghiep == 'Công nhân')
        nghe_nghiep_kinh_doanh = checkbox(self.nghe_nghiep == 'Kinh doanh tự do')
        nghe_nghiep_hoc_sinh_sinh_vien = checkbox(self.nghe_nghiep == 'Học sinh/Sinh viên')
        nghe_nghiep_noi_tro = checkbox(self.nghe_nghiep == 'Nội trợ')
        nghe_nghiep_cong_an_bo_doi = checkbox(self.nghe_nghiep == 'Công an/Bộ đội')
        nghe_nghiep_ky_su = checkbox(self.nghe_nghiep == 'Kỹ sư')
        nghe_nghiep_khac = checkbox(self.nghe_nghiep == 'Khác')

        # Checkbox variables for loại tiền
        loai_tien_vnd = checkbox(self.loai_tien_te == 'VND')
        loai_tien_usd = checkbox(self.loai_tien_te == 'USD')
        loai_tien_eur = checkbox(self.loai_tien_te == 'EUR')

        # Checkbox variables for loại tài khoản
        tk_ngau_nhien = checkbox(self.loai_tai_khoan == 'Tài khoản ngẫu nhiên')
        tk_theo_yeu_cau = checkbox(self.loai_tai_khoan == 'Tài khoản số theo yêu cầu')
        tk_chuyen_dung = checkbox(self.loai_tai_khoan == 'Tài khoản chuyên dụng')

        # Checkbox variables for kết quả phân loại KH
        pl_cao = checkbox(self.ket_qua_phan_loai_kh == 'Cao')
        pl_trungbinh = checkbox(self.ket_qua_phan_loai_kh == 'Trung bình')
        pl_thap = checkbox(self.ket_qua_phan_loai_kh == 'Thấp')

        from datetime import datetime, date

        # Auto-generate ten_tieng_anh from ho_ten (remove diacritics and uppercase)
        ten_tieng_anh = remove_vietnamese_diacritics(self.ho_ten or '')

        data = {
            'ma_khach_hang': self.ma_khach_hang or '',
            'cif': self.cif or '',
            'ho_ten': self.ho_ten or '',
            'ho_ten_tieng_anh': self.ho_ten_tieng_anh or '',
            'ten_tieng_anh': ten_tieng_anh,  # Auto-generated from ho_ten
            'ngay_sinh': self.ngay_sinh.strftime('%d/%m/%Y') if self.ngay_sinh else '',
            'ngay_sinh_obj': self.ngay_sinh,  # Date object cho Jinja2 calculations
            'gioi_tinh': self.gioi_tinh or '',
            'dan_toc': self.dan_toc or '',
            'so_cmnd': self.so_cmnd or '',
            'ngay_cap_cmnd': self.ngay_cap_cmnd.strftime('%d/%m/%Y') if self.ngay_cap_cmnd else '',
            'ngay_cap_cmnd_obj': self.ngay_cap_cmnd,  # Date object cho Jinja2 calculations
            'ngay_het_han_cmnd': self.ngay_het_han_cmnd.strftime('%d/%m/%Y') if self.ngay_het_han_cmnd else '',
            'ngay_het_han_cmnd_obj': self.ngay_het_han_cmnd,  # Date object cho Jinja2 calculations
            'noi_cap_cmnd': self.get_noi_cap_display_value(),
            'dia_chi': self.dia_chi or '',
            'ho_khau': self.ho_khau or '',
            'so_dien_thoai': self.so_dien_thoai or '',
            'email': self.email or '',
            # Địa chỉ chi tiết từ Address Selector
            'province': self.province or '',
            'district': self.district or '',
            'ward': self.ward or '',
            'hamlet': self.hamlet or '',
            'full_address': self.full_address or '',
            'nghe_nghiep': self.nghe_nghiep or '',
            'noi_lam_viec': self.noi_lam_viec or '',
            'so_tai_khoan': self.so_tai_khoan or '',
            'loai_tai_khoan': self.loai_tai_khoan or '',
            'so_tai_khoan_yc': self.so_tai_khoan_yc or '',
            'loai_tien_te': self.loai_tien_te or '',
            'loai_the': self.loai_the or '',
            'hang_the': self.hang_the or '',
            'so_the_atm': self.so_the_atm or '',
            'thoi_han_the': self.thoi_han_the or '',
            'ngay_tra_the': self.ngay_tra_the.strftime('%d/%m/%Y') if self.ngay_tra_the else '',
            'loai_phi': self.loai_phi or '',
            'ghi_chu': self.ghi_chu or '',
            'ngay_in': self.ngay_in.strftime('%d/%m/%Y') if self.ngay_in else '',
            'ngay_in_obj': self.ngay_in,  # Date object cho Jinja2 calculations
            # Ngày hiện tại cho tính toán (Date object)
            # NOTE: Không dùng key 'ngay_hien_tai' vì đã có trong GlobalConfig với format dd/mm/yyyy
            'ngay_hien_tai_obj': datetime.now().date(),  # Date object for calculations only
            # Date variables (ngày sinh)
            'd1': d1, 'd2': d2, 'm1': m1, 'm2': m2,
            'y1': y1, 'y2': y2, 'y3': y3, 'y4': y4,
            # Date variables (ngày cấp CMND/CCCD)
            'dcc1': dcc1, 'dcc2': dcc2, 'mcc1': mcc1, 'mcc2': mcc2,
            'ycc1': ycc1, 'ycc2': ycc2, 'ycc3': ycc3, 'ycc4': ycc4,
            # Date variables (ngày hết hạn CMND/CCCD)
            'dhh1': dhh1, 'dhh2': dhh2, 'mhh1': mhh1, 'mhh2': mhh2,
            'yhh1': yhh1, 'yhh2': yhh2, 'yhh3': yhh3, 'yhh4': yhh4,
            # Date variables (ngày trả thẻ)
            'dtt1': dtt1, 'dtt2': dtt2, 'mtt1': mtt1, 'mtt2': mtt2,
            'ytt1': ytt1, 'ytt2': ytt2, 'ytt3': ytt3, 'ytt4': ytt4,
            # Date variables (ngày trả thẻ tính - will be populated below)
            'dttt1': dttt1, 'dttt2': dttt2, 'mttt1': mttt1, 'mttt2': mttt2,
            'yttt1': yttt1, 'yttt2': yttt2, 'yttt3': yttt3, 'yttt4': yttt4,
            # Checkbox variables - Dịch vụ thu hộ
            'dv_thu_ho_tien_nuoc': checkbox(self.dv_thu_ho_tien_nuoc),
            'dv_thu_ho_tien_dien': checkbox(self.dv_thu_ho_tien_dien),
            'dv_thu_ho_vien_thong': checkbox(self.dv_thu_ho_vien_thong),
            'dv_thu_ho_hoc_phi': checkbox(self.dv_thu_ho_hoc_phi),
            'dv_thu_ho_bao_hiem': checkbox(self.dv_thu_ho_bao_hiem),
            # Checkbox variables - Dịch vụ ngân hàng điện tử
            'dv_sms_banking': checkbox(self.dv_sms_banking),
            'dv_e_mobile': checkbox(self.dv_e_mobile),
            'dv_vidientu': checkbox(self.dv_e_mobile),  # Alias for dv_e_mobile (ví điện tử)
            'dv_bankplus': checkbox(self.dv_bankplus),
            'dv_e_commerce': checkbox(self.dv_e_commerce),
            'dv_soft_otp': checkbox(self.dv_soft_otp),
            'dv_smart_otp': checkbox(self.dv_smart_otp),
            'dv_retail_ebanking': checkbox(self.dv_retail_ebanking),
            # Checkbox variables - Kênh giao dịch
            'kenh_mobile': checkbox(self.kenh_mobile),
            'kenh_internet': checkbox(self.kenh_internet),
            # Checkbox variables - CMND vs CCCD vs Căn cước
            'cmnd': cmnd,
            'cccd': cccd,
            'cancuoc': cancuoc,
            # Checkbox variables - Giới tính
            'gioi_tinh_nam': gioi_tinh_nam,
            'gioi_tinh_nu': gioi_tinh_nu,
            # Checkbox variables - Nghề nghiệp
            'nghe_nghiep_cong_chuc': nghe_nghiep_cong_chuc,
            'nghe_nghiep_nong_dan': nghe_nghiep_nong_dan,
            'nghe_nghiep_giao_vien_bac_si': nghe_nghiep_giao_vien_bac_si,
            'nghe_nghiep_cong_nhan': nghe_nghiep_cong_nhan,
            'nghe_nghiep_kinh_doanh': nghe_nghiep_kinh_doanh,
            'nghe_nghiep_hoc_sinh_sinh_vien': nghe_nghiep_hoc_sinh_sinh_vien,
            'nghe_nghiep_noi_tro': nghe_nghiep_noi_tro,
            'nghe_nghiep_cong_an_bo_doi': nghe_nghiep_cong_an_bo_doi,
            'nghe_nghiep_ky_su': nghe_nghiep_ky_su,
            'nghe_nghiep_khac': nghe_nghiep_khac,
            # Checkbox variables - Thẻ
            'phat_hanh_lan_dau': checkbox(self.phat_hanh_lan_dau),
            'phat_hanh_lai': checkbox(self.phat_hanh_lai),
            'the_hang_chuan': the_hang_chuan,
            'the_hang_vang': the_hang_vang,
            'the_hang_bach_kim': the_hang_bach_kim,
            'the_ghi_no_noi_dia': the_ghi_no_noi_dia,
            'the_ghi_no_quoc_te': the_ghi_no_quoc_te,
            'the_tin_dung': the_tin_dung,
            'loai_the_jcb': loai_the_jcb,
            'loai_the_visa': loai_the_visa,
            'loai_the_mastercard': loai_the_mastercard,
            'loai_the_khac': loai_the_khac,
            # Checkbox variables - Loại tiền
            'loai_tien_vnd': loai_tien_vnd,
            'loai_tien_usd': loai_tien_usd,
            'loai_tien_eur': loai_tien_eur,
            # Checkbox variables - Tài khoản
            'tk_ngau_nhien': tk_ngau_nhien,
            'tk_theo_yeu_cau': tk_theo_yeu_cau,
            'tk_chuyen_dung': tk_chuyen_dung,
            # Checkbox variables - Kết quả phân loại KH
            'pl_cao': pl_cao,
            'pl_trungbinh': pl_trungbinh,
            'pl_thap': pl_thap,
            # Checkbox variables - Thẻ bổ sung
            'the_lap_nghiep': checkbox(self.the_lap_nghiep),
            'the_lien_ket': checkbox(self.the_lien_ket),
            'the_dong_thuong_hieu': checkbox(self.the_dong_thuong_hieu),
            # Checkbox variables - Dịch vụ ABIC
            'dv_abic': checkbox(self.dv_abic),
            # Tên thẻ
            'ten_the_1': self.ten_the_1 or '',
            'ten_the_2': self.ten_the_2 or '',  # FIX: Thêm tên thẻ 2
            # Tiền gửi tiết kiệm chung - Thông tin người gửi tiền thứ hai
            'ho_ten_nguoi_gui_2': self.ho_ten_nguoi_gui_2 or '',
            'so_cmnd_nguoi_gui_2': self.so_cmnd_nguoi_gui_2 or '',
            'ngay_cap_cmnd_nguoi_gui_2': self.ngay_cap_cmnd_nguoi_gui_2.strftime('%d/%m/%Y') if self.ngay_cap_cmnd_nguoi_gui_2 else '',
            'noi_cap_cmnd_nguoi_gui_2': self.noi_cap_cmnd_nguoi_gui_2 or '',
            'dia_chi_nguoi_gui_2': self.dia_chi_nguoi_gui_2 or '',
            'sdt_nguoi_gui_2': self.sdt_nguoi_gui_2 or '',
            # Tiền gửi tiết kiệm chung - Giao dịch thẻ tiết kiệm (Text: "Có" hoặc "Không")
            'gd_rut_lai_tat_ca': 'Có' if self.gd_rut_lai_tat_ca else 'Không',
            'gd_rut_lai_mot_so': 'Có' if self.gd_rut_lai_mot_so else 'Không',
            'gd_tat_toan_tat_ca': 'Có' if self.gd_tat_toan_tat_ca else 'Không',
            'gd_tat_toan_mot_so': 'Có' if self.gd_tat_toan_mot_so else 'Không',
            'gd_bao_mat_tat_ca': 'Có' if self.gd_bao_mat_tat_ca else 'Không',
            'gd_bao_mat_mot_so': 'Có' if self.gd_bao_mat_mot_so else 'Không',
            'gd_bao_hong_tat_ca': 'Có' if self.gd_bao_hong_tat_ca else 'Không',
            'gd_bao_hong_mot_so': 'Có' if self.gd_bao_hong_mot_so else 'Không',
            'gd_phong_toa_tat_ca': 'Có' if self.gd_phong_toa_tat_ca else 'Không',
            'gd_phong_toa_mot_so': 'Có' if self.gd_phong_toa_mot_so else 'Không',
            'gd_xac_nhan_so_du_tat_ca': 'Có' if self.gd_xac_nhan_so_du_tat_ca else 'Không',
            'gd_xac_nhan_so_du_mot_so': 'Có' if self.gd_xac_nhan_so_du_mot_so else 'Không',
        }

        # Card number variables - tách số thẻ ra từng ký tự (16 ký tự)
        # sothe_1, sothe_2, ..., sothe_16
        so_the = self.so_the_atm or ''
        # Loại bỏ khoảng trắng và ký tự đặc biệt
        so_the_cleaned = ''.join(filter(str.isdigit, so_the))
        # Pad với khoảng trống nếu ngắn hơn 16 ký tự
        so_the_padded = so_the_cleaned.ljust(16)
        for i in range(1, 17):
            data[f'sothe_{i}'] = so_the_padded[i-1] if i <= len(so_the_cleaned) else ''

        # Note: Card name (tên trên thẻ) is auto-filled into tables
        # by _render_card_name_tables() in utils.py
        # No need to generate individual character variables

        # Service-specific account and phone logic
        # If Agribank Plus is selected but NOT SMS Banking
        if self.dv_bankplus and not self.dv_sms_banking:
            data['so_tai_khoan_AP'] = self.so_tai_khoan or ''
            data['so_dien_thoai_AP'] = self.so_dien_thoai or ''
        else:
            data['so_tai_khoan_AP'] = ''
            data['so_dien_thoai_AP'] = ''

        # If SMS Banking is selected but NOT Agribank Plus
        if self.dv_sms_banking and not self.dv_bankplus:
            data['so_tai_khoan_SMS'] = self.so_tai_khoan or ''
            data['so_dien_thoai_SMS'] = self.so_dien_thoai or ''
        else:
            data['so_tai_khoan_SMS'] = ''
            data['so_dien_thoai_SMS'] = ''

        # Account number by request logic:
        # - If "Tài khoản số theo yêu cầu" is selected AND has value: show the value
        # - Otherwise: show dots "................."
        if self.loai_tai_khoan == 'Tài khoản số theo yêu cầu' and self.so_tai_khoan_yc:
            data['stk_theo_yeu_cau'] = self.so_tai_khoan_yc
            data['tk_theo_yeu_cau'] = self.so_tai_khoan_yc
            data['so_tai_khoan_yc'] = self.so_tai_khoan_yc  # Hiển thị số TK
        else:
            # Show dots when not selected or no value
            data['stk_theo_yeu_cau'] = '.................'
            data['tk_theo_yeu_cau'] = '.................'
            data['so_tai_khoan_yc'] = '.................'

        # Calculate ngay_tra_the_tinh (card return date) = ngay_in (print date) + 7 days
        # Note: ngay_lap (creation date) is assumed to be ngay_in in this context
        from datetime import timedelta
        if self.ngay_in:
            ngay_tra_the_calculated = self.ngay_in + timedelta(days=7)
            data['ngay_tra_the_tinh'] = ngay_tra_the_calculated.strftime('%d/%m/%Y')
            data['ngay_tra_the_tinh_obj'] = ngay_tra_the_calculated  # Date object

            # Add individual digit variables for ngay_tra_the_tinh
            date_str = ngay_tra_the_calculated.strftime('%d%m%Y')
            if len(date_str) == 8:
                data['dttt1'] = date_str[0]
                data['dttt2'] = date_str[1]
                data['mttt1'] = date_str[2]
                data['mttt2'] = date_str[3]
                data['yttt1'] = date_str[4]
                data['yttt2'] = date_str[5]
                data['yttt3'] = date_str[6]
                data['yttt4'] = date_str[7]
        else:
            data['ngay_tra_the_tinh'] = ''
            data['ngay_tra_the_tinh_obj'] = None

        return data


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
    dia_chi_chi_nhanh = models.TextField(verbose_name="Địa chỉ chi nhánh", blank=True)
    dien_thoai_chi_nhanh = models.CharField(max_length=50, verbose_name="Điện thoại chi nhánh", blank=True)
    so_fax = models.CharField(max_length=50, verbose_name="Số Fax", blank=True)
    dia_danh = models.CharField(max_length=200, verbose_name="Địa danh", blank=True, help_text="Ví dụ: Bạc Liêu, Đồng Tháp")

    # Nhân sự
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


# Alias để backward compatibility
BranchConfig = GlobalConfig


# ====================
# Employee Management Models
# ====================

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
        choices=BRANCH_CHOICES,
        blank=True,
        verbose_name="Chi nhánh"
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


# ====================
# E-Learning System Models
# ====================

class Course(models.Model):
    """Khóa học E-Learning"""
    name = models.CharField(
        max_length=200,
        verbose_name="Tên khóa học"
    )
    start_date = models.DateField(
        verbose_name="Ngày bắt đầu"
    )
    end_date = models.DateField(
        verbose_name="Ngày kết thúc"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Ghi chú"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Khóa học"
        verbose_name_plural = "Khóa học"
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def get_completion_stats(self):
        """Trả về thống kê hoàn thành (completed / total)"""
        total = self.enrollments.count()
        completed = self.enrollments.filter(is_completed=True).count()
        return {'completed': completed, 'total': total}


class CourseEnrollment(models.Model):
    """Ghi danh khóa học - Học viên"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Khóa học"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_enrollments',
        verbose_name="Người học"
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name="Đã hoàn thành"
    )
    completion_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ngày hoàn thành"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày ghi danh")

    class Meta:
        verbose_name = "Ghi danh khóa học"
        verbose_name_plural = "Ghi danh khóa học"
        unique_together = ['course', 'user']
        ordering = ['course', 'user__username']

    def __str__(self):
        return f"{self.course.name} - {self.user.username}"


# ====================
# Bank Statement Analyzer Models
# ====================

class BankStatement(models.Model):
    """Sao kê ngân hàng được upload"""
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày upload")
    file_name = models.CharField(max_length=255, verbose_name="Tên file")
    total_transactions = models.IntegerField(verbose_name="Tổng số giao dịch")
    total_debit = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        default=0,
        verbose_name="Tổng tiền ghi nợ"
    )
    total_credit = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        default=0,
        verbose_name="Tổng tiền ghi có"
    )
    final_balance = models.DecimalField(
        max_digits=18,
        decimal_places=0,
        default=0,
        verbose_name="Số dư cuối kỳ"
    )
    processed = models.BooleanField(default=False, verbose_name="Đã xử lý")
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bank_statements',
        verbose_name="Người upload"
    )

    class Meta:
        verbose_name = "Sao kê ngân hàng"
        verbose_name_plural = "Sao kê ngân hàng"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.file_name} - {self.uploaded_at.strftime('%d/%m/%Y %H:%M')}"


class Transaction(models.Model):
    """Giao dịch trong sao kê ngân hàng"""
    statement = models.ForeignKey(
        BankStatement,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="Sao kê"
    )
    stt = models.IntegerField(verbose_name="STT")
    transaction_date = models.DateField(verbose_name="Ngày giao dịch")
    debit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name="Số tiền ghi nợ"
    )
    credit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        default=0,
        verbose_name="Số tiền ghi có"
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="Số dư sau GD"
    )
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ngân hàng"
    )
    account_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Số tài khoản"
    )
    beneficiary_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tên người thụ hưởng"
    )
    description = models.TextField(verbose_name="Nội dung gốc")
    transaction_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Loại giao dịch"
    )

    # Raw data fields từ file Excel
    raw_trcdnm = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tên mã giao dịch (raw)"
    )
    raw_tomgntno = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tài khoản đối ứng (raw)"
    )

    class Meta:
        verbose_name = "Giao dịch"
        verbose_name_plural = "Giao dịch"
        ordering = ['statement', 'stt']
        indexes = [
            models.Index(fields=['statement', 'transaction_date']),
            models.Index(fields=['transaction_type']),
        ]

    def __str__(self):
        return f"{self.stt}. {self.transaction_date.strftime('%d/%m/%Y')} - {self.transaction_type}"
