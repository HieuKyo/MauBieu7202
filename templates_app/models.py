from django.db import models
from django.contrib.auth.models import Group, User
from django.core.validators import FileExtensionValidator
import unicodedata
from .storage import HybridTemplateStorage


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
                'foreign_currency',
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
        storage=HybridTemplateStorage(),
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

    # Ngoại tệ - Nhận tiền nước ngoài
    quan_he_nguoi_gui_nhan = models.CharField(max_length=200, blank=True, verbose_name="Quan hệ giữa người gửi và người nhận")
    MUC_DICH_GIAO_DICH_CHOICES = [
        ('Hỗ trợ gia đình', 'Hỗ trợ gia đình'),
        ('Quà tặng', 'Quà tặng'),
    ]
    muc_dich_giao_dich = models.CharField(max_length=50, blank=True, choices=MUC_DICH_GIAO_DICH_CHOICES, verbose_name="Mục đích giao dịch")
    ho_ten_nguoi_gui_tien = models.CharField(max_length=200, blank=True, verbose_name="Họ tên người gửi tiền")
    quoc_gia_gui_tien = models.CharField(max_length=100, blank=True, verbose_name="Quốc gia gửi tiền")
    ma_so_nhan_tien = models.CharField(max_length=50, blank=True, verbose_name="Mã số nhận tiền")
    so_tien_ngoai_te = models.CharField(max_length=50, blank=True, verbose_name="Số tiền ngoại tệ")
    loai_tien_ngoai_te = models.CharField(max_length=20, blank=True, verbose_name="Loại tiền ngoại tệ")

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
        # If Agribank Plus is selected, show account and phone for AP
        if self.dv_bankplus:
            data['so_tai_khoan_AP'] = self.so_tai_khoan or ''
            data['so_dien_thoai_AP'] = self.so_dien_thoai or ''
        else:
            data['so_tai_khoan_AP'] = ''
            data['so_dien_thoai_AP'] = ''

        # If SMS Banking is selected, show account and phone for SMS
        if self.dv_sms_banking:
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


class Business(models.Model):
    """Thông tin doanh nghiệp"""

    LOAI_GIAY_TO_CHOICES = [
        ('GCN', 'Giấy chứng nhận đăng ký doanh nghiệp'),
        ('DKKD', 'Giấy đăng ký kinh doanh'),
        ('QD', 'Quyết định thành lập'),
    ]

    LOAI_GIAY_TO_DANH_DANH_CHOICES = [
        ('CCCD', 'Căn cước công dân'),
        ('CCCD_CHIP', 'CCCD gắn chip điện tử'),
        ('CMND', 'Chứng minh nhân dân'),
        ('HC', 'Hộ chiếu'),
    ]

    GIOI_TINH_CHOICES = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác'),
    ]

    # ===== THÔNG TIN DOANH NGHIỆP =====
    # Mã CIF và Tài khoản
    cif = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Mã CIF",
        db_index=True
    )
    so_tai_khoan = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Số tài khoản"
    )

    # Thông tin cơ bản
    ten_doanh_nghiep = models.CharField(
        max_length=255,
        verbose_name="Tên doanh nghiệp",
        db_index=True
    )
    ten_bang_hieu = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Tên bảng hiệu"
    )

    # Giấy tờ định danh
    loai_giay_to = models.CharField(
        max_length=10,
        choices=LOAI_GIAY_TO_CHOICES,
        default='GCN',
        verbose_name="Loại giấy tờ định danh"
    )
    so_gcn = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Số GCN đăng ký DN/Giấy ĐKKD/QĐ thành lập"
    )
    ngay_cap_gcn = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày cấp GCN"
    )
    noi_cap_gcn = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nơi cấp GCN"
    )

    # Mã số thuế
    ma_so_thue = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Mã số thuế"
    )
    ngay_cap_mst = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày cấp MST"
    )
    noi_cap_mst = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nơi cấp MST"
    )

    # Liên hệ
    dia_chi = models.TextField(
        blank=True,
        verbose_name="Địa chỉ"
    )
    dien_thoai = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Điện thoại"
    )

    # Thông tin kinh doanh
    linh_vuc_kinh_doanh = models.TextField(
        blank=True,
        verbose_name="Lĩnh vực hoạt động kinh doanh"
    )
    von_dieu_le = models.DecimalField(
        max_digits=20,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="Vốn điều lệ (VND)"
    )

    # ===== THÔNG TIN NGƯỜI ĐẠI DIỆN PHÁP LUẬT =====
    nguoi_dai_dien_ho_ten = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Người đại diện - Họ và tên"
    )
    nguoi_dai_dien_ngay_sinh = models.DateField(
        null=True,
        blank=True,
        verbose_name="Người đại diện - Ngày sinh"
    )
    nguoi_dai_dien_gioi_tinh = models.CharField(
        max_length=10,
        choices=GIOI_TINH_CHOICES,
        default='Nam',
        blank=True,
        verbose_name="Người đại diện - Giới tính"
    )
    nguoi_dai_dien_nghe_nghiep = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Người đại diện - Nghề nghiệp"
    )
    nguoi_dai_dien_dien_thoai = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Người đại diện - Điện thoại"
    )

    # Giấy tờ tùy thân người đại diện
    nguoi_dai_dien_loai_giay_to = models.CharField(
        max_length=20,
        choices=LOAI_GIAY_TO_DANH_DANH_CHOICES,
        default='CCCD',
        blank=True,
        verbose_name="Người đại diện - Loại giấy tờ"
    )
    nguoi_dai_dien_so_cccd = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Người đại diện - Số CCCD/CMND"
    )
    nguoi_dai_dien_ngay_cap = models.DateField(
        null=True,
        blank=True,
        verbose_name="Người đại diện - Ngày cấp"
    )
    nguoi_dai_dien_noi_cap = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Người đại diện - Nơi cấp"
    )
    nguoi_dai_dien_ngay_het_han = models.DateField(
        null=True,
        blank=True,
        verbose_name="Người đại diện - Ngày hết hạn"
    )
    nguoi_dai_dien_noi_o_hien_tai = models.TextField(
        blank=True,
        verbose_name="Người đại diện - Nơi ở hiện tại"
    )

    # ===== THÔNG TIN KẾ TOÁN TRƯỞNG =====
    ke_toan_truong_ho_ten = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Kế toán trưởng - Họ và tên"
    )
    ke_toan_truong_ngay_sinh = models.DateField(
        null=True,
        blank=True,
        verbose_name="Kế toán trưởng - Ngày sinh"
    )
    ke_toan_truong_gioi_tinh = models.CharField(
        max_length=10,
        choices=GIOI_TINH_CHOICES,
        default='Nam',
        blank=True,
        verbose_name="Kế toán trưởng - Giới tính"
    )
    ke_toan_truong_nghe_nghiep = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Kế toán trưởng - Nghề nghiệp"
    )
    ke_toan_truong_dien_thoai = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Kế toán trưởng - Điện thoại"
    )

    # Giấy tờ tùy thân kế toán trưởng
    ke_toan_truong_loai_giay_to = models.CharField(
        max_length=20,
        choices=LOAI_GIAY_TO_DANH_DANH_CHOICES,
        default='CCCD',
        blank=True,
        verbose_name="Kế toán trưởng - Loại giấy tờ"
    )
    ke_toan_truong_so_cccd = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Kế toán trưởng - Số CCCD/CMND"
    )
    ke_toan_truong_ngay_cap = models.DateField(
        null=True,
        blank=True,
        verbose_name="Kế toán trưởng - Ngày cấp"
    )
    ke_toan_truong_noi_cap = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Kế toán trưởng - Nơi cấp"
    )
    ke_toan_truong_ngay_het_han = models.DateField(
        null=True,
        blank=True,
        verbose_name="Kế toán trưởng - Ngày hết hạn"
    )
    ke_toan_truong_noi_o_hien_tai = models.TextField(
        blank=True,
        verbose_name="Kế toán trưởng - Nơi ở hiện tại"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Doanh nghiệp"
        verbose_name_plural = "Doanh nghiệp"
        ordering = ['ten_doanh_nghiep']

    def get_data_dict(self):
        """
        Trả về dictionary chứa thông tin doanh nghiệp
        Dùng để auto-fill form và render template
        """
        from datetime import datetime
        import re
        import unicodedata

        EMPTY_VALUE = '...........................'

        def checkbox(value):
            return '☑' if value else '☐'

        # Helper function để format số tiền
        def format_money(amount):
            if amount is None:
                return EMPTY_VALUE
            try:
                return f"{int(amount):,}".replace(',', '.')
            except (ValueError, TypeError):
                return str(amount)

        # Helper: Tạo tên viết tắt (HKD Nguyễn Văn A -> HKDNVA)
        def create_acronym(name):
            if not name:
                return EMPTY_VALUE
            # Remove diacritics and convert to uppercase
            normalized = unicodedata.normalize('NFD', name)
            without_diacritics = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
            # Get first letter of each word
            words = without_diacritics.upper().split()
            return ''.join(word[0] for word in words if word)

        # Helper: Bỏ tiền tố HKD (HKD Nguyễn Văn A -> Nguyễn Văn A)
        def remove_prefix(name):
            if not name:
                return EMPTY_VALUE
            # Remove common prefixes
            prefixes = ['HKD', 'DNTN', 'CTCP', 'TNHH', 'CT']
            name_stripped = name.strip()
            for prefix in prefixes:
                if name_stripped.upper().startswith(prefix + ' '):
                    return name_stripped[len(prefix):].strip()
            return name_stripped

        # Helper: Tách từng chữ số
        def split_digits(number_str, length=13):
            if not number_str:
                return [EMPTY_VALUE] * length
            digits = str(number_str).zfill(length)
            return list(digits[:length])

        # Logic nơi cấp CCCD dựa vào ngày cấp (> 08/2024)
        cutoff_date = datetime(2024, 8, 1)

        # Người đại diện
        ndd_noi_cap = self.nguoi_dai_dien_noi_cap or EMPTY_VALUE
        ndd_is_new_cccd = False
        if self.nguoi_dai_dien_ngay_cap:
            ndd_is_new_cccd = self.nguoi_dai_dien_ngay_cap > cutoff_date.date()
            if ndd_is_new_cccd:
                ndd_noi_cap = "Bộ Công An"
            else:
                ndd_noi_cap = "Cục CSQLHC về TTXH"

        # Kế toán trưởng
        ktt_noi_cap = self.ke_toan_truong_noi_cap or EMPTY_VALUE
        ktt_is_new_cccd = False
        if self.ke_toan_truong_ngay_cap:
            ktt_is_new_cccd = self.ke_toan_truong_ngay_cap > cutoff_date.date()
            if ktt_is_new_cccd:
                ktt_noi_cap = "Bộ Công An"
            else:
                ktt_noi_cap = "Cục CSQLHC về TTXH"

        # Tách số GCN và MST thành từng chữ số
        so_gcn_digits = split_digits(self.so_gcn, 13)
        ma_so_thue_digits = split_digits(self.ma_so_thue, 13)  # HKD có 13 số

        data = {
            # Thông tin doanh nghiệp cơ bản
            'dn_cif': self.cif or EMPTY_VALUE,
            'dn_so_tai_khoan': self.so_tai_khoan or EMPTY_VALUE,
            'dn_ten': self.ten_doanh_nghiep or EMPTY_VALUE,
            'dn_ten_doanh_nghiep': self.ten_doanh_nghiep or EMPTY_VALUE,
            'dn_ten_bang_hieu': self.ten_bang_hieu or EMPTY_VALUE,
            'dn_ten_viet_tat': create_acronym(self.ten_doanh_nghiep),  # HKD Nguyễn Văn A -> HKDNVA
            'dn_ten_khong_tien_to': remove_prefix(self.ten_doanh_nghiep),  # HKD Nguyễn Văn A -> Nguyễn Văn A

            # Giấy tờ định danh
            'dn_loai_giay_to': self.get_loai_giay_to_display() if self.loai_giay_to else EMPTY_VALUE,
            'dn_so_gcn': self.so_gcn or EMPTY_VALUE,
            'dn_ngay_cap_gcn': self.ngay_cap_gcn.strftime('%d/%m/%Y') if self.ngay_cap_gcn else EMPTY_VALUE,
            'dn_ngay_cap_gcn_obj': self.ngay_cap_gcn,
            'dn_noi_cap_gcn': self.noi_cap_gcn or EMPTY_VALUE,
            # Từng chữ số của GCN (13 chữ số)
            'dn_so_gcn_1': so_gcn_digits[0], 'dn_so_gcn_2': so_gcn_digits[1], 'dn_so_gcn_3': so_gcn_digits[2],
            'dn_so_gcn_4': so_gcn_digits[3], 'dn_so_gcn_5': so_gcn_digits[4], 'dn_so_gcn_6': so_gcn_digits[5],
            'dn_so_gcn_7': so_gcn_digits[6], 'dn_so_gcn_8': so_gcn_digits[7], 'dn_so_gcn_9': so_gcn_digits[8],
            'dn_so_gcn_10': so_gcn_digits[9], 'dn_so_gcn_11': so_gcn_digits[10], 'dn_so_gcn_12': so_gcn_digits[11],
            'dn_so_gcn_13': so_gcn_digits[12],

            # Mã số thuế
            'dn_ma_so_thue': self.ma_so_thue or EMPTY_VALUE,
            'dn_mst': self.ma_so_thue or EMPTY_VALUE,  # Alias
            'dn_ngay_cap_mst': self.ngay_cap_mst.strftime('%d/%m/%Y') if self.ngay_cap_mst else EMPTY_VALUE,
            'dn_ngay_cap_mst_obj': self.ngay_cap_mst,
            'dn_noi_cap_mst': self.noi_cap_mst or EMPTY_VALUE,
            # Từng chữ số của MST (13 chữ số - HKD thường dùng 13 số)
            'dn_mst_1': ma_so_thue_digits[0], 'dn_mst_2': ma_so_thue_digits[1], 'dn_mst_3': ma_so_thue_digits[2],
            'dn_mst_4': ma_so_thue_digits[3], 'dn_mst_5': ma_so_thue_digits[4], 'dn_mst_6': ma_so_thue_digits[5],
            'dn_mst_7': ma_so_thue_digits[6], 'dn_mst_8': ma_so_thue_digits[7], 'dn_mst_9': ma_so_thue_digits[8],
            'dn_mst_10': ma_so_thue_digits[9], 'dn_mst_11': ma_so_thue_digits[10], 'dn_mst_12': ma_so_thue_digits[11],
            'dn_mst_13': ma_so_thue_digits[12],

            # Liên hệ
            'dn_dia_chi': self.dia_chi or EMPTY_VALUE,
            'dn_dien_thoai': self.dien_thoai or EMPTY_VALUE,

            # Thông tin kinh doanh
            'dn_linh_vuc_kinh_doanh': self.linh_vuc_kinh_doanh or EMPTY_VALUE,
            'dn_von_dieu_le': format_money(self.von_dieu_le),
            'dn_von_dieu_le_raw': self.von_dieu_le or 0,

            # Người đại diện pháp luật
            'dn_nguoi_dai_dien_ho_ten': self.nguoi_dai_dien_ho_ten or EMPTY_VALUE,
            'dn_ndd_ho_ten': self.nguoi_dai_dien_ho_ten or EMPTY_VALUE,  # Alias ngắn
            'dn_nguoi_dai_dien_ngay_sinh': self.nguoi_dai_dien_ngay_sinh.strftime('%d/%m/%Y') if self.nguoi_dai_dien_ngay_sinh else EMPTY_VALUE,
            'dn_nguoi_dai_dien_ngay_sinh_obj': self.nguoi_dai_dien_ngay_sinh,
            'dn_ndd_ngay_sinh': self.nguoi_dai_dien_ngay_sinh.strftime('%d/%m/%Y') if self.nguoi_dai_dien_ngay_sinh else EMPTY_VALUE,
            'dn_nguoi_dai_dien_gioi_tinh': self.nguoi_dai_dien_gioi_tinh or EMPTY_VALUE,
            'dn_ndd_gioi_tinh': self.nguoi_dai_dien_gioi_tinh or EMPTY_VALUE,
            'dn_nguoi_dai_dien_nghe_nghiep': self.nguoi_dai_dien_nghe_nghiep or EMPTY_VALUE,
            'dn_ndd_nghe_nghiep': self.nguoi_dai_dien_nghe_nghiep or EMPTY_VALUE,
            'dn_nguoi_dai_dien_dien_thoai': self.nguoi_dai_dien_dien_thoai or EMPTY_VALUE,
            'dn_ndd_dien_thoai': self.nguoi_dai_dien_dien_thoai or EMPTY_VALUE,

            # Giấy tờ người đại diện (với logic tự động nơi cấp)
            'dn_nguoi_dai_dien_loai_giay_to': self.get_nguoi_dai_dien_loai_giay_to_display() if self.nguoi_dai_dien_loai_giay_to else EMPTY_VALUE,
            'dn_ndd_loai_giay_to': self.get_nguoi_dai_dien_loai_giay_to_display() if self.nguoi_dai_dien_loai_giay_to else EMPTY_VALUE,
            'dn_nguoi_dai_dien_so_cccd': self.nguoi_dai_dien_so_cccd or EMPTY_VALUE,
            'dn_ndd_so_cccd': self.nguoi_dai_dien_so_cccd or EMPTY_VALUE,
            'dn_nguoi_dai_dien_ngay_cap': self.nguoi_dai_dien_ngay_cap.strftime('%d/%m/%Y') if self.nguoi_dai_dien_ngay_cap else EMPTY_VALUE,
            'dn_nguoi_dai_dien_ngay_cap_obj': self.nguoi_dai_dien_ngay_cap,
            'dn_ndd_ngay_cap': self.nguoi_dai_dien_ngay_cap.strftime('%d/%m/%Y') if self.nguoi_dai_dien_ngay_cap else EMPTY_VALUE,
            'dn_nguoi_dai_dien_noi_cap': ndd_noi_cap,  # Auto: "Bộ Công An" nếu > 08/2024
            'dn_ndd_noi_cap': ndd_noi_cap,
            'dn_nguoi_dai_dien_ngay_het_han': self.nguoi_dai_dien_ngay_het_han.strftime('%d/%m/%Y') if self.nguoi_dai_dien_ngay_het_han else EMPTY_VALUE,
            'dn_nguoi_dai_dien_ngay_het_han_obj': self.nguoi_dai_dien_ngay_het_han,
            'dn_ndd_ngay_het_han': self.nguoi_dai_dien_ngay_het_han.strftime('%d/%m/%Y') if self.nguoi_dai_dien_ngay_het_han else EMPTY_VALUE,
            'dn_nguoi_dai_dien_noi_o_hien_tai': self.nguoi_dai_dien_noi_o_hien_tai or EMPTY_VALUE,
            'dn_ndd_noi_o_hien_tai': self.nguoi_dai_dien_noi_o_hien_tai or EMPTY_VALUE,

            # Kế toán trưởng
            'dn_ke_toan_truong_ho_ten': self.ke_toan_truong_ho_ten or EMPTY_VALUE,
            'dn_ktt_ho_ten': self.ke_toan_truong_ho_ten or EMPTY_VALUE,  # Alias ngắn
            'dn_ke_toan_truong_ngay_sinh': self.ke_toan_truong_ngay_sinh.strftime('%d/%m/%Y') if self.ke_toan_truong_ngay_sinh else EMPTY_VALUE,
            'dn_ke_toan_truong_ngay_sinh_obj': self.ke_toan_truong_ngay_sinh,
            'dn_ktt_ngay_sinh': self.ke_toan_truong_ngay_sinh.strftime('%d/%m/%Y') if self.ke_toan_truong_ngay_sinh else EMPTY_VALUE,
            'dn_ke_toan_truong_gioi_tinh': self.ke_toan_truong_gioi_tinh or EMPTY_VALUE,
            'dn_ktt_gioi_tinh': self.ke_toan_truong_gioi_tinh or EMPTY_VALUE,
            'dn_ke_toan_truong_nghe_nghiep': self.ke_toan_truong_nghe_nghiep or EMPTY_VALUE,
            'dn_ktt_nghe_nghiep': self.ke_toan_truong_nghe_nghiep or EMPTY_VALUE,
            'dn_ke_toan_truong_dien_thoai': self.ke_toan_truong_dien_thoai or EMPTY_VALUE,
            'dn_ktt_dien_thoai': self.ke_toan_truong_dien_thoai or EMPTY_VALUE,

            # Giấy tờ kế toán trưởng (với logic tự động nơi cấp)
            'dn_ke_toan_truong_loai_giay_to': self.get_ke_toan_truong_loai_giay_to_display() if self.ke_toan_truong_loai_giay_to else EMPTY_VALUE,
            'dn_ktt_loai_giay_to': self.get_ke_toan_truong_loai_giay_to_display() if self.ke_toan_truong_loai_giay_to else EMPTY_VALUE,
            'dn_ke_toan_truong_so_cccd': self.ke_toan_truong_so_cccd or EMPTY_VALUE,
            'dn_ktt_so_cccd': self.ke_toan_truong_so_cccd or EMPTY_VALUE,
            'dn_ke_toan_truong_ngay_cap': self.ke_toan_truong_ngay_cap.strftime('%d/%m/%Y') if self.ke_toan_truong_ngay_cap else EMPTY_VALUE,
            'dn_ke_toan_truong_ngay_cap_obj': self.ke_toan_truong_ngay_cap,
            'dn_ktt_ngay_cap': self.ke_toan_truong_ngay_cap.strftime('%d/%m/%Y') if self.ke_toan_truong_ngay_cap else EMPTY_VALUE,
            'dn_ke_toan_truong_noi_cap': ktt_noi_cap,  # Auto: "Bộ Công An" nếu > 08/2024
            'dn_ktt_noi_cap': ktt_noi_cap,
            'dn_ke_toan_truong_ngay_het_han': self.ke_toan_truong_ngay_het_han.strftime('%d/%m/%Y') if self.ke_toan_truong_ngay_het_han else EMPTY_VALUE,
            'dn_ke_toan_truong_ngay_het_han_obj': self.ke_toan_truong_ngay_het_han,
            'dn_ktt_ngay_het_han': self.ke_toan_truong_ngay_het_han.strftime('%d/%m/%Y') if self.ke_toan_truong_ngay_het_han else EMPTY_VALUE,
            'dn_ke_toan_truong_noi_o_hien_tai': self.ke_toan_truong_noi_o_hien_tai or EMPTY_VALUE,
            'dn_ktt_noi_o_hien_tai': self.ke_toan_truong_noi_o_hien_tai or EMPTY_VALUE,

            # Checkbox cho giới tính người đại diện
            'dn_ndd_gioi_tinh_nam': checkbox(self.nguoi_dai_dien_gioi_tinh == 'Nam'),
            'dn_ndd_gioi_tinh_nu': checkbox(self.nguoi_dai_dien_gioi_tinh == 'Nữ'),

            # Checkbox cho giới tính kế toán trưởng
            'dn_ktt_gioi_tinh_nam': checkbox(self.ke_toan_truong_gioi_tinh == 'Nam'),
            'dn_ktt_gioi_tinh_nu': checkbox(self.ke_toan_truong_gioi_tinh == 'Nữ'),

            # Checkbox cho loại giấy tờ người đại diện (tự động dựa vào ngày cấp)
            'dn_ndd_loai_giay_to_cccd': checkbox(not ndd_is_new_cccd and self.nguoi_dai_dien_loai_giay_to in ['CCCD', 'CCCD_CHIP']),
            'dn_ndd_loai_giay_to_cccd_chip': checkbox(ndd_is_new_cccd and self.nguoi_dai_dien_loai_giay_to in ['CCCD', 'CCCD_CHIP']),
            'dn_ndd_loai_giay_to_cmnd': checkbox(self.nguoi_dai_dien_loai_giay_to == 'CMND'),
            'dn_ndd_loai_giay_to_passport': checkbox(self.nguoi_dai_dien_loai_giay_to == 'Passport'),

            # Checkbox cho loại giấy tờ kế toán trưởng (tự động dựa vào ngày cấp)
            'dn_ktt_loai_giay_to_cccd': checkbox(not ktt_is_new_cccd and self.ke_toan_truong_loai_giay_to in ['CCCD', 'CCCD_CHIP']),
            'dn_ktt_loai_giay_to_cccd_chip': checkbox(ktt_is_new_cccd and self.ke_toan_truong_loai_giay_to in ['CCCD', 'CCCD_CHIP']),
            'dn_ktt_loai_giay_to_cmnd': checkbox(self.ke_toan_truong_loai_giay_to == 'CMND'),
            'dn_ktt_loai_giay_to_passport': checkbox(self.ke_toan_truong_loai_giay_to == 'Passport'),
        }

        return data

    def __str__(self):
        return f"{self.cif} - {self.ten_doanh_nghiep}"


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
        except Exception as e:
            # Log error nếu cần
            pass

        # Fallback: trả về GlobalConfig
        return GlobalConfig.get_instance()


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


<<<<<<< HEAD
# Alias để backward compatibility
#BranchConfig = GlobalConfig


=======
>>>>>>> 3456b931c171791f8711fd3eb1cef13a9b465e97
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


# ============================================================================
# ATM Management Models
# ============================================================================

class ATM(models.Model):
    """Quản lý máy ATM"""
    machine_id = models.CharField(
        max_length=50,
        primary_key=True,
        verbose_name="ID Máy ATM"
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Số Serial máy"
    )
    address = models.CharField(
        max_length=500,
        verbose_name="Địa chỉ máy"
    )
    machine_type = models.CharField(
        max_length=100,
        verbose_name="Loại máy"
    )
    machine_line = models.CharField(
        max_length=100,
        verbose_name="Dòng máy"
    )
    installation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày lắp đặt"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Máy ATM"
        verbose_name_plural = "Máy ATM"
        ordering = ['machine_id']

    def __str__(self):
        return f"{self.machine_id} - {self.address}"


class ATMManagementBoard(models.Model):
    """Ban quản lý ATM"""
    POSITION_CHOICES = [
        ('team_leader', 'Trưởng Ban'),
        ('treasury_head', 'Trưởng phòng KTNQ'),
        ('atm_officer', 'Cán bộ phụ trách ATM'),
    ]

    position = models.CharField(
        max_length=50,
        choices=POSITION_CHOICES,
        unique=True,
        verbose_name="Chức vụ"
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name="Họ và tên"
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Chức danh"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Ban quản lý ATM"
        verbose_name_plural = "Ban quản lý ATM"
        ordering = ['position']

    def __str__(self):
        return f"{self.get_position_display()} - {self.full_name}"


class Vehicle(models.Model):
    """Phương tiện vận chuyển tiền"""
    license_plate = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Biển số xe"
    )
    vehicle_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Loại xe"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Phương tiện"
        verbose_name_plural = "Phương tiện"
        ordering = ['license_plate']

    def __str__(self):
        return self.license_plate


class Person(models.Model):
    """Base model cho nhân viên vận chuyển (tài xế, bảo vệ)"""
    PERSON_TYPE_CHOICES = [
        ('driver', 'Tài xế'),
        ('guard', 'Bảo vệ'),
    ]

    person_type = models.CharField(
        max_length=20,
        choices=PERSON_TYPE_CHOICES,
        verbose_name="Loại nhân viên"
    )
    full_name = models.CharField(
        max_length=200,
        verbose_name="Họ và tên"
    )
    id_number = models.CharField(
        max_length=50,
        verbose_name="Số CCCD"
    )
    id_issue_date = models.DateField(
        verbose_name="Ngày cấp"
    )
    id_issue_place = models.CharField(
        max_length=200,
        verbose_name="Nơi cấp"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Đang hoạt động"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Nhân viên vận chuyển"
        verbose_name_plural = "Nhân viên vận chuyển"
        ordering = ['person_type', 'full_name']
        unique_together = ['id_number', 'person_type']

    def __str__(self):
        return f"{self.get_person_type_display()} - {self.full_name}"


class ATMReplenishment(models.Model):
    """Phiếu tiếp quỹ ATM"""
    atm = models.ForeignKey(
        ATM,
        on_delete=models.PROTECT,
        verbose_name="Máy ATM"
    )
    replenishment_date = models.DateField(
        verbose_name="Ngày tiếp quỹ"
    )

    # Số lượng tờ tiền theo mệnh giá
    bills_50k = models.IntegerField(
        default=0,
        verbose_name="Số tờ 50.000đ"
    )
    bills_100k = models.IntegerField(
        default=0,
        verbose_name="Số tờ 100.000đ"
    )
    bills_200k = models.IntegerField(
        default=0,
        verbose_name="Số tờ 200.000đ"
    )
    bills_500k = models.IntegerField(
        default=0,
        verbose_name="Số tờ 500.000đ"
    )

    # Lệnh điều chuyển
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        verbose_name="Phương tiện"
    )
    driver = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name='replenishments_as_driver',
        limit_choices_to={'person_type': 'driver'},
        verbose_name="Tài xế"
    )
    guard = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name='replenishments_as_guard',
        limit_choices_to={'person_type': 'guard'},
        verbose_name="Bảo vệ"
    )

    # Thông tin người tạo
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Người tạo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Phiếu tiếp quỹ ATM"
        verbose_name_plural = "Phiếu tiếp quỹ ATM"
        ordering = ['-replenishment_date', '-created_at']

    def __str__(self):
        return f"Tiếp quỹ {self.atm.machine_id} - {self.replenishment_date.strftime('%d/%m/%Y')}"

    @property
    def total_amount(self):
        """Tính tổng số tiền tiếp quỹ"""
        return (
            self.bills_50k * 50000 +
            self.bills_100k * 100000 +
            self.bills_200k * 200000 +
            self.bills_500k * 500000
        )

    def get_amount_in_words(self):
        """Chuyển số tiền sang chữ"""
        return num_to_vietnamese_words(self.total_amount)

    def get_data_dict(self):
        """
        Trả về dictionary chứa thông tin phiếu tiếp quỹ ATM
        Dùng để tạo mẫu biểu Word
        """
        # Date variables cho ngày tiếp quỹ
        tq_d1, tq_d2, tq_m1, tq_m2, tq_y1, tq_y2, tq_y3, tq_y4 = '', '', '', '', '', '', '', ''
        if self.replenishment_date:
            date_str = self.replenishment_date.strftime('%d%m%Y')
            if len(date_str) == 8:
                tq_d1, tq_d2 = date_str[0], date_str[1]
                tq_m1, tq_m2 = date_str[2], date_str[3]
                tq_y1, tq_y2, tq_y3, tq_y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables cho ngày lắp đặt ATM
        ld_d1, ld_d2, ld_m1, ld_m2, ld_y1, ld_y2, ld_y3, ld_y4 = '', '', '', '', '', '', '', ''
        if self.atm.installation_date:
            date_str = self.atm.installation_date.strftime('%d%m%Y')
            if len(date_str) == 8:
                ld_d1, ld_d2 = date_str[0], date_str[1]
                ld_m1, ld_m2 = date_str[2], date_str[3]
                ld_y1, ld_y2, ld_y3, ld_y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables cho ngày cấp CCCD tài xế
        tx_d1, tx_d2, tx_m1, tx_m2, tx_y1, tx_y2, tx_y3, tx_y4 = '', '', '', '', '', '', '', ''
        if self.driver.id_issue_date:
            date_str = self.driver.id_issue_date.strftime('%d%m%Y')
            if len(date_str) == 8:
                tx_d1, tx_d2 = date_str[0], date_str[1]
                tx_m1, tx_m2 = date_str[2], date_str[3]
                tx_y1, tx_y2, tx_y3, tx_y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Date variables cho ngày cấp CCCD bảo vệ
        bv_d1, bv_d2, bv_m1, bv_m2, bv_y1, bv_y2, bv_y3, bv_y4 = '', '', '', '', '', '', '', ''
        if self.guard.id_issue_date:
            date_str = self.guard.id_issue_date.strftime('%d%m%Y')
            if len(date_str) == 8:
                bv_d1, bv_d2 = date_str[0], date_str[1]
                bv_m1, bv_m2 = date_str[2], date_str[3]
                bv_y1, bv_y2, bv_y3, bv_y4 = date_str[4], date_str[5], date_str[6], date_str[7]

        # Lấy thông tin ban quản lý ATM
        team_leader = ATMManagementBoard.objects.filter(position='team_leader', is_active=True).first()
        treasury_head = ATMManagementBoard.objects.filter(position='treasury_head', is_active=True).first()
        atm_officer = ATMManagementBoard.objects.filter(position='atm_officer', is_active=True).first()

        # Tính tiền cho từng mệnh giá
        amount_50k = self.bills_50k * 50000
        amount_100k = self.bills_100k * 100000
        amount_200k = self.bills_200k * 200000
        amount_500k = self.bills_500k * 500000

        data = {
            # Thông tin máy ATM
            'atm_machine_id': self.atm.machine_id,
            'atm_serial_number': self.atm.serial_number or '',
            'atm_address': self.atm.address,
            'atm_machine_type': self.atm.machine_type,
            'atm_machine_line': self.atm.machine_line,
            'atm_installation_date': self.atm.installation_date.strftime('%d/%m/%Y') if self.atm.installation_date else '',

            # Date variables cho ngày lắp đặt
            'atm_ld_d1': ld_d1, 'atm_ld_d2': ld_d2,
            'atm_ld_m1': ld_m1, 'atm_ld_m2': ld_m2,
            'atm_ld_y1': ld_y1, 'atm_ld_y2': ld_y2, 'atm_ld_y3': ld_y3, 'atm_ld_y4': ld_y4,

            # Thông tin tiếp quỹ
            'replenishment_date': self.replenishment_date.strftime('%d/%m/%Y'),

            # Date variables cho ngày tiếp quỹ
            'tq_d1': tq_d1, 'tq_d2': tq_d2,
            'tq_m1': tq_m1, 'tq_m2': tq_m2,
            'tq_y1': tq_y1, 'tq_y2': tq_y2, 'tq_y3': tq_y3, 'tq_y4': tq_y4,

            # Số lượng tờ tiền
            'bills_50k': str(self.bills_50k),
            'bills_100k': str(self.bills_100k),
            'bills_200k': str(self.bills_200k),
            'bills_500k': str(self.bills_500k),

            # Thành tiền từng mệnh giá
            'amount_50k': f"{amount_50k:,}",
            'amount_100k': f"{amount_100k:,}",
            'amount_200k': f"{amount_200k:,}",
            'amount_500k': f"{amount_500k:,}",

            # Tổng tiền
            'total_amount': f"{self.total_amount:,}",
            'total_amount_words': self.get_amount_in_words(),

            # Thông tin phương tiện
            'vehicle_license_plate': self.vehicle.license_plate,
            'vehicle_type': self.vehicle.vehicle_type or '',

            # Thông tin tài xế
            'driver_full_name': self.driver.full_name,
            'driver_id_number': self.driver.id_number,
            'driver_id_issue_date': self.driver.id_issue_date.strftime('%d/%m/%Y'),
            'driver_id_issue_place': self.driver.id_issue_place,

            # Date variables cho tài xế
            'tx_d1': tx_d1, 'tx_d2': tx_d2,
            'tx_m1': tx_m1, 'tx_m2': tx_m2,
            'tx_y1': tx_y1, 'tx_y2': tx_y2, 'tx_y3': tx_y3, 'tx_y4': tx_y4,

            # Thông tin bảo vệ
            'guard_full_name': self.guard.full_name,
            'guard_id_number': self.guard.id_number,
            'guard_id_issue_date': self.guard.id_issue_date.strftime('%d/%m/%Y'),
            'guard_id_issue_place': self.guard.id_issue_place,

            # Date variables cho bảo vệ
            'bv_d1': bv_d1, 'bv_d2': bv_d2,
            'bv_m1': bv_m1, 'bv_m2': bv_m2,
            'bv_y1': bv_y1, 'bv_y2': bv_y2, 'bv_y3': bv_y3, 'bv_y4': bv_y4,

            # Ban quản lý ATM
            'team_leader_name': team_leader.full_name if team_leader else '',
            'team_leader_title': team_leader.title if team_leader else '',
            'treasury_head_name': treasury_head.full_name if treasury_head else '',
            'treasury_head_title': treasury_head.title if treasury_head else '',
            'atm_officer_name': atm_officer.full_name if atm_officer else '',
            'atm_officer_title': atm_officer.title if atm_officer else '',

            # Thông tin người tạo
            'created_by': self.created_by.username,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
        }

        return data


class ATMDiscrepancy(models.Model):
    """Quản lý các giao dịch thừa/thiếu quỹ ATM"""

    DISCREPANCY_TYPES = [
        ('surplus', 'Thừa'),
        ('deficit', 'Thiếu'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('resolved', 'Đã xử lý'),
        ('escalated', 'Đã báo cáo lên'),
    ]

    atm = models.ForeignKey(
        ATM,
        on_delete=models.PROTECT,
        related_name='discrepancies',
        verbose_name="Máy ATM"
    )
    full_name = models.CharField(max_length=200, verbose_name="Họ tên")
    account_number = models.CharField(max_length=50, verbose_name="Số tài khoản")
    card_number = models.CharField(max_length=50, verbose_name="Số thẻ")
    trace_number = models.CharField(max_length=100, verbose_name="Số trace")
    transaction_id = models.CharField(max_length=100, verbose_name="ID giao dịch")

    discrepancy_type = models.CharField(
        max_length=10,
        choices=DISCREPANCY_TYPES,
        verbose_name="Loại"
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name="Số tiền"
    )

    audit_cycle_start = models.DateField(verbose_name="Chu kỳ kiểm quỹ từ ngày")
    audit_cycle_end = models.DateField(verbose_name="Chu kỳ kiểm quỹ đến ngày")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Trạng thái"
    )
    notes = models.TextField(blank=True, verbose_name="Ghi chú")

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='atm_discrepancies_created',
        verbose_name="Người tạo"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Giao dịch thừa/thiếu quỹ ATM"
        verbose_name_plural = "Giao dịch thừa/thiếu quỹ ATM"
        ordering = ['-audit_cycle_end', '-created_at']

    def __str__(self):
        type_display = "Thừa" if self.discrepancy_type == 'surplus' else "Thiếu"
        return f"{self.atm.machine_id} - {type_display} {self.amount:,}đ - {self.full_name}"

    def get_amount_in_words(self):
        """Chuyển số tiền thành chữ"""
        return num_to_vietnamese_words(int(self.amount))

    def get_data_dict(self):
        """Trả về dictionary chứa tất cả biến cho Word template"""
        # Phân tách ngày bắt đầu chu kỳ
        acs_d1 = self.audit_cycle_start.strftime('%d')[0]
        acs_d2 = self.audit_cycle_start.strftime('%d')[1]
        acs_m1 = self.audit_cycle_start.strftime('%m')[0]
        acs_m2 = self.audit_cycle_start.strftime('%m')[1]
        acs_y1 = self.audit_cycle_start.strftime('%Y')[0]
        acs_y2 = self.audit_cycle_start.strftime('%Y')[1]
        acs_y3 = self.audit_cycle_start.strftime('%Y')[2]
        acs_y4 = self.audit_cycle_start.strftime('%Y')[3]

        # Phân tách ngày kết thúc chu kỳ
        ace_d1 = self.audit_cycle_end.strftime('%d')[0]
        ace_d2 = self.audit_cycle_end.strftime('%d')[1]
        ace_m1 = self.audit_cycle_end.strftime('%m')[0]
        ace_m2 = self.audit_cycle_end.strftime('%m')[1]
        ace_y1 = self.audit_cycle_end.strftime('%Y')[0]
        ace_y2 = self.audit_cycle_end.strftime('%Y')[1]
        ace_y3 = self.audit_cycle_end.strftime('%Y')[2]
        ace_y4 = self.audit_cycle_end.strftime('%Y')[3]

        # Lấy thông tin ban quản lý ATM
        team_leader = ATMManagementBoard.objects.filter(
            position='team_leader', is_active=True
        ).first()
        treasury_head = ATMManagementBoard.objects.filter(
            position='treasury_head', is_active=True
        ).first()
        atm_officer = ATMManagementBoard.objects.filter(
            position='atm_officer', is_active=True
        ).first()

        data = {
            # Thông tin máy ATM
            'disc_atm_machine_id': self.atm.machine_id,
            'disc_atm_serial_number': self.atm.serial_number or '',
            'disc_atm_address': self.atm.address,
            'disc_atm_machine_type': self.atm.machine_type,
            'disc_atm_machine_line': self.atm.machine_line,

            # Thông tin khách hàng/giao dịch
            'disc_full_name': self.full_name,
            'disc_account_number': self.account_number,
            'disc_card_number': self.card_number,
            'disc_trace_number': self.trace_number,
            'disc_transaction_id': self.transaction_id,

            # Thông tin số tiền
            'disc_type': self.get_discrepancy_type_display(),
            'disc_amount': f"{self.amount:,}",
            'disc_amount_words': self.get_amount_in_words(),

            # Chu kỳ kiểm quỹ
            'disc_audit_cycle_start': self.audit_cycle_start.strftime('%d/%m/%Y'),
            'disc_audit_cycle_end': self.audit_cycle_end.strftime('%d/%m/%Y'),

            # Date variables cho ngày bắt đầu chu kỳ
            'acs_d1': acs_d1, 'acs_d2': acs_d2,
            'acs_m1': acs_m1, 'acs_m2': acs_m2,
            'acs_y1': acs_y1, 'acs_y2': acs_y2, 'acs_y3': acs_y3, 'acs_y4': acs_y4,

            # Date variables cho ngày kết thúc chu kỳ
            'ace_d1': ace_d1, 'ace_d2': ace_d2,
            'ace_m1': ace_m1, 'ace_m2': ace_m2,
            'ace_y1': ace_y1, 'ace_y2': ace_y2, 'ace_y3': ace_y3, 'ace_y4': ace_y4,

            # Trạng thái
            'disc_status': self.get_status_display(),
            'disc_notes': self.notes or '',

            # Ban quản lý ATM
            'disc_team_leader_name': team_leader.full_name if team_leader else '',
            'disc_team_leader_title': team_leader.title if team_leader else '',
            'disc_treasury_head_name': treasury_head.full_name if treasury_head else '',
            'disc_treasury_head_title': treasury_head.title if treasury_head else '',
            'disc_atm_officer_name': atm_officer.full_name if atm_officer else '',
            'disc_atm_officer_title': atm_officer.title if atm_officer else '',

            # Thông tin người tạo
            'disc_created_by': self.created_by.username,
            'disc_created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
        }

        return data


def num_to_vietnamese_words(num):
    """Chuyển đổi số thành chữ tiếng Việt"""
    if num == 0:
        return "Không đồng"

    units = ["", "nghìn", "triệu", "tỷ"]

    def read_group(n):
        """Đọc nhóm 3 chữ số"""
        hundred = n // 100
        ten = (n % 100) // 10
        unit = n % 10

        result = []

        if hundred > 0:
            result.append(f"{read_digit(hundred)} trăm")

        if ten > 1:
            result.append(f"{read_digit(ten)} mươi")
            if unit == 1:
                result.append("mốt")
            elif unit > 0:
                result.append(read_digit(unit))
        elif ten == 1:
            result.append("mười")
            if unit > 0:
                result.append(read_digit(unit))
        else:
            if hundred > 0 and unit > 0:
                result.append("lẻ")
            if unit > 0:
                result.append(read_digit(unit))

        return " ".join(result)

    def read_digit(d):
        """Đọc một chữ số"""
        digits = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
        return digits[d]

    # Chia số thành các nhóm 3 chữ số
    groups = []
    temp = num
    while temp > 0:
        groups.append(temp % 1000)
        temp //= 1000

    # Đọc từng nhóm
    result = []
    for i in range(len(groups) - 1, -1, -1):
        if groups[i] > 0:
            group_text = read_group(groups[i])
            if i > 0:
                group_text += f" {units[i]}"
            result.append(group_text)

    # Viết hoa chữ cái đầu và thêm "đồng"
    final_result = " ".join(result)
    return final_result.capitalize() + " đồng"


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
