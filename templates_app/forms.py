"""
Dynamic form generation based on Template variables
"""
from django import forms
from .models import Template, TemplateVariable, Customer, Business, GlobalConfig, Category


class DynamicTemplateForm(forms.Form):
    """
    Form động được tạo dựa trên các biến của Template
    """

    def __init__(self, *args, template=None, **kwargs):
        super().__init__(*args, **kwargs)

        if template is None:
            raise ValueError("Template is required for DynamicTemplateForm")

        # Lấy danh sách biến của template (theo thứ tự)
        template_variables = TemplateVariable.objects.filter(
            template=template
        ).select_related('variable').order_by('order', 'variable__name')

        # Tạo field cho từng biến
        for tv in template_variables:
            variable = tv.variable
            field_name = variable.name

            # Xác định field type dựa trên kiểu biến
            if variable.field_type == 'text':
                field = forms.CharField(
                    label=variable.label,
                    required=variable.required,
                    initial=variable.default_value if variable.default_value else None,
                    help_text=variable.help_text,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control',
                        'placeholder': variable.help_text or variable.label
                    })
                )

            elif variable.field_type == 'textarea':
                field = forms.CharField(
                    label=variable.label,
                    required=variable.required,
                    initial=variable.default_value if variable.default_value else None,
                    help_text=variable.help_text,
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 4,
                        'placeholder': variable.help_text or variable.label
                    })
                )

            elif variable.field_type == 'date':
                field = forms.DateField(
                    label=variable.label,
                    required=variable.required,
                    initial=variable.default_value if variable.default_value else None,
                    help_text=variable.help_text,
                    widget=forms.DateInput(attrs={
                        'class': 'form-control',
                        'type': 'date',
                        'placeholder': 'dd/mm/yyyy'
                    }),
                    input_formats=['%Y-%m-%d', '%d/%m/%Y']
                )

            elif variable.field_type == 'number':
                field = forms.DecimalField(
                    label=variable.label,
                    required=variable.required,
                    initial=variable.default_value if variable.default_value else None,
                    help_text=variable.help_text,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control',
                        'placeholder': variable.help_text or variable.label
                    })
                )

            else:
                # Default to text field
                field = forms.CharField(
                    label=variable.label,
                    required=variable.required,
                    initial=variable.default_value if variable.default_value else None,
                    help_text=variable.help_text,
                    widget=forms.TextInput(attrs={
                        'class': 'form-control'
                    })
                )

            # Thêm field vào form
            self.fields[field_name] = field

    def clean(self):
        """
        Custom validation và convert data types cho serialization
        """
        from decimal import Decimal

        cleaned_data = super().clean()

        # Convert data types to string format for Word template and session storage
        for field_name, value in list(cleaned_data.items()):
            if value is None:
                continue

            # Convert date/datetime to string
            if hasattr(value, 'strftime'):
                cleaned_data[field_name] = value.strftime('%d/%m/%Y')

            # Convert Decimal to string (fixes JSON serialization error)
            elif isinstance(value, Decimal):
                cleaned_data[field_name] = str(value)

        return cleaned_data


class CustomerForm(forms.ModelForm):
    """Form cho quản lý khách hàng"""

    class Meta:
        model = Customer
        exclude = ['created_at', 'updated_at', 'created_by']
        widgets = {
            'ma_khach_hang': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã khách hàng (tùy chọn)'}),
            'cif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã CIF (tùy chọn)'}),
            'ho_ten': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ và tên'}),
            'ngay_sinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gioi_tinh': forms.Select(attrs={'class': 'form-select'}),
            'so_cmnd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số CMND/CCCD'}),
            'ngay_cap_cmnd': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ngay_het_han_cmnd': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'noi_cap_cmnd': forms.Select(attrs={'class': 'form-select', 'id': 'noi-cap-select'}),
            'noi_cap_cmnd_custom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập nơi cấp khác', 'id': 'noi-cap-custom', 'style': 'display:none;'}),
            'dia_chi': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Địa chỉ thường trú'}),
            'so_dien_thoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            # Address Selector Component - Hidden fields
            'province': forms.HiddenInput(),
            'district': forms.HiddenInput(),
            'ward': forms.HiddenInput(),
            'hamlet': forms.HiddenInput(),
            'full_address': forms.HiddenInput(),
            'nghe_nghiep': forms.Select(attrs={'class': 'form-select'}),
            'noi_lam_viec': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nơi làm việc'}),
            'so_tai_khoan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số tài khoản'}),
            'loai_tai_khoan': forms.Select(attrs={'class': 'form-select'}),
            'so_tai_khoan_yc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số tài khoản theo yêu cầu'}),
            'loai_tien_te': forms.Select(attrs={'class': 'form-select'}),
            'loai_the': forms.Select(attrs={'class': 'form-select'}),
            'hang_the': forms.Select(attrs={'class': 'form-select'}),
            'so_the_atm': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số thẻ ATM'}),
            'thoi_han_the': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Thời hạn thẻ (MM/YY)'}),
            'ngay_tra_the': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'loai_phi': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Loại phí'}),
            'phat_hanh_lan_dau': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'phat_hanh_lai': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ngay_in': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            # Dịch vụ thu hộ
            'dv_thu_ho_tien_nuoc': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_thu_ho_tien_dien': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_thu_ho_vien_thong': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_thu_ho_hoc_phi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_thu_ho_bao_hiem': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Dịch vụ ngân hàng điện tử
            'dv_sms_banking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_e_mobile': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_bankplus': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_e_commerce': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_soft_otp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_smart_otp': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'dv_retail_ebanking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Kênh giao dịch
            'kenh_mobile': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'kenh_internet': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Thông tin thẻ bổ sung
            'the_lap_nghiep': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'the_lien_ket': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'the_dong_thuong_hieu': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ten_the_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên trên thẻ 1'}),
            'ten_the_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên trên thẻ 2'}),  # FIX: Thêm tên thẻ 2
            # Dịch vụ ABIC
            'dv_abic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Phân loại khách hàng
            'ket_qua_phan_loai_kh': forms.Select(attrs={'class': 'form-select'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ghi chú thêm'}),
            # Tiền gửi tiết kiệm chung - Thông tin người gửi tiền thứ hai
            'ho_ten_nguoi_gui_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ tên người gửi tiền thứ hai'}),
            'so_cmnd_nguoi_gui_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số CMND/CCCD/Hộ chiếu'}),
            'ngay_cap_cmnd_nguoi_gui_2': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'noi_cap_cmnd_nguoi_gui_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nơi cấp'}),
            'dia_chi_nguoi_gui_2': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Địa chỉ'}),
            'sdt_nguoi_gui_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),
            # Tiền gửi tiết kiệm chung - Giao dịch
            'gd_rut_lai_tat_ca': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_rut_lai_mot_so': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_tat_toan_tat_ca': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_tat_toan_mot_so': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_bao_mat_tat_ca': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_bao_mat_mot_so': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_bao_hong_tat_ca': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_bao_hong_mot_so': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_phong_toa_tat_ca': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_phong_toa_mot_so': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_xac_nhan_so_du_tat_ca': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gd_xac_nhan_so_du_mot_so': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # Ngoại tệ - Nhận tiền nước ngoài
            'quan_he_nguoi_gui_nhan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quan hệ giữa người gửi và người nhận'}),
            'muc_dich_giao_dich': forms.Select(attrs={'class': 'form-select'}),
            'ho_ten_nguoi_gui_tien': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ tên người gửi tiền'}),
            'quoc_gia_gui_tien': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quốc gia gửi tiền'}),
            'ma_so_nhan_tien': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã số nhận tiền'}),
            'so_tien_ngoai_te': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số tiền'}),
            'loai_tien_ngoai_te': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Loại tiền (USD, EUR, ...)'}),
        }


class BusinessForm(forms.ModelForm):
    """Form cho quản lý doanh nghiệp"""

    class Meta:
        model = Business
        exclude = ['created_at', 'updated_at']
        widgets = {
            # Thông tin doanh nghiệp
            'cif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã CIF'}),
            'so_tai_khoan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số tài khoản'}),
            'ten_doanh_nghiep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên doanh nghiệp'}),

            # Giấy tờ định danh
            'loai_giay_to': forms.Select(attrs={'class': 'form-select'}),
            'so_gcn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số giấy chứng nhận'}),
            'ngay_cap_gcn': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'noi_cap_gcn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nơi cấp'}),

            # Mã số thuế
            'ma_so_thue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã số thuế'}),
            'ngay_cap_mst': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'noi_cap_mst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nơi cấp MST'}),

            # Liên hệ
            'dia_chi': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Địa chỉ doanh nghiệp'}),
            'dien_thoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),

            # Thông tin kinh doanh
            'linh_vuc_kinh_doanh': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Lĩnh vực kinh doanh'}),
            'von_dieu_le': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Vốn điều lệ (VND)'}),

            # Người đại diện pháp luật
            'nguoi_dai_dien_ho_ten': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ và tên'}),
            'nguoi_dai_dien_ngay_sinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nguoi_dai_dien_gioi_tinh': forms.Select(attrs={'class': 'form-select'}),
            'nguoi_dai_dien_nghe_nghiep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nghề nghiệp'}),
            'nguoi_dai_dien_dien_thoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),
            'nguoi_dai_dien_loai_giay_to': forms.Select(attrs={'class': 'form-select'}),
            'nguoi_dai_dien_so_cccd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số CCCD/CMND'}),
            'nguoi_dai_dien_ngay_cap': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nguoi_dai_dien_noi_cap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nơi cấp'}),
            'nguoi_dai_dien_ngay_het_han': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nguoi_dai_dien_noi_o_hien_tai': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Nơi ở hiện tại'}),

            # Kế toán trưởng
            'ke_toan_truong_ho_ten': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ và tên'}),
            'ke_toan_truong_ngay_sinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ke_toan_truong_gioi_tinh': forms.Select(attrs={'class': 'form-select'}),
            'ke_toan_truong_nghe_nghiep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nghề nghiệp'}),
            'ke_toan_truong_dien_thoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),
            'ke_toan_truong_loai_giay_to': forms.Select(attrs={'class': 'form-select'}),
            'ke_toan_truong_so_cccd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số CCCD/CMND'}),
            'ke_toan_truong_ngay_cap': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ke_toan_truong_noi_cap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nơi cấp'}),
            'ke_toan_truong_ngay_het_han': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ke_toan_truong_noi_o_hien_tai': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Nơi ở hiện tại'}),
        }


class GlobalConfigForm(forms.ModelForm):
    """Form cho cấu hình toàn cục (thông tin chi nhánh + biến chung)"""

    class Meta:
        model = GlobalConfig
        exclude = ['updated_at', 'updated_by', 'custom_variables']  # custom_variables quản lý riêng qua UI động
        widgets = {
            'ten_chi_nhanh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Chi nhánh Giá Rai Bạc Liêu'}),
            'ten_chi_nhanh_hoa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: CHI NHÁNH GIÁ RAI BẠC LIÊU'}),
            'ma_chi_nhanh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 100'}),
            'mst': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã số thuế'}),
            'gcndkdn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số giấy chứng nhận đăng ký kinh doanh'}),
            'mst_chi_nhanh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã số thuế chi nhánh'}),
            'dia_chi_chi_nhanh': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Địa chỉ đầy đủ chi nhánh'}),
            'dien_thoai_chi_nhanh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 0291.3822.079'}),
            'so_fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 0291.3822.080'}),
            'dia_danh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Bạc Liêu, Đồng Tháp'}),
            'nguoi_dai_dien': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ tên người đại diện'}),
            'chuc_vu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chức vụ người đại diện'}),
            'so_uy_quyen': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 123/UQ-HĐQT'}),
            'giao_dich_vien': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ tên giao dịch viên'}),
            'kiem_soat_vien': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ tên kiểm soát viên'}),
            'giam_doc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Họ tên giám đốc'}),
        }


# Alias để backward compatibility
BranchConfigForm = GlobalConfigForm


class CategoryAdminForm(forms.ModelForm):
    """Form cho admin Category với UI tốt hơn cho visible_field_groups"""

    # Define all available field groups with descriptions
    FIELD_GROUP_CHOICES = [
        ('customer_basic_info', 'Thông tin cơ bản khách hàng (Mã KH, Họ tên, CMND/CCCD, Địa chỉ, SĐT, Nghề nghiệp)'),
        ('banking', 'Thông tin tài khoản (Số TK, Loại TK, Loại tiền tệ)'),
        ('card', 'Thông tin thẻ (Số thẻ, Loại thẻ, Hạng thẻ, Phát hành)'),
        ('services', 'Đăng ký dịch vụ (SMS Banking, Agribank Plus, Liên kết ví)'),
        ('joint_savings', 'Tiền gửi tiết kiệm chung (Người gửi thứ 2, Giao dịch thẻ TK)'),
        ('foreign_currency', 'Ngoại tệ - Nhận tiền nước ngoài'),
        ('customer_classification', 'Phân loại khách hàng (Kết quả phân loại KH)'),
        ('print_info', 'Thông tin in mẫu biểu (Ngày in)'),
    ]

    visible_field_groups = forms.MultipleChoiceField(
        choices=FIELD_GROUP_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Nhóm trường hiển thị",
        help_text="Chọn các nhóm trường sẽ hiển thị trong form khi chọn danh mục này. Để trống để hiển thị tất cả."
    )

    class Meta:
        model = Category
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-select existing values
        if self.instance and self.instance.visible_field_groups:
            self.initial['visible_field_groups'] = self.instance.visible_field_groups


# ====================
# ATM Management Forms
# ====================

from .models import ATM, ATMManagementBoard, Vehicle, Person, ATMReplenishment, ATMDiscrepancy


class ATMReplenishmentForm(forms.ModelForm):
    """Form cho tạo phiếu tiếp quỹ ATM"""

    class Meta:
        model = ATMReplenishment
        fields = ['atm', 'replenishment_date', 'bills_50k', 'bills_100k',
                  'bills_200k', 'bills_500k', 'vehicle', 'driver', 'guard']
        widgets = {
            'atm': forms.Select(attrs={'class': 'form-select'}),
            'replenishment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'bills_50k': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Số tờ 50.000đ', 'min': '0'}),
            'bills_100k': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Số tờ 100.000đ', 'min': '0'}),
            'bills_200k': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Số tờ 200.000đ', 'min': '0'}),
            'bills_500k': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Số tờ 500.000đ', 'min': '0'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'guard': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lọc chỉ hiển thị các mục active
        self.fields['atm'].queryset = ATM.objects.filter(is_active=True)
        self.fields['vehicle'].queryset = Vehicle.objects.filter(is_active=True)
        self.fields['driver'].queryset = Person.objects.filter(person_type='driver', is_active=True)
        self.fields['guard'].queryset = Person.objects.filter(person_type='guard', is_active=True)


class ATMDiscrepancyForm(forms.ModelForm):
    """Form cho tạo giao dịch thừa/thiếu quỹ ATM"""

    class Meta:
        model = ATMDiscrepancy
        fields = [
            'atm', 'full_name', 'account_number', 'card_number',
            'trace_number', 'transaction_id', 'discrepancy_type', 'amount',
            'audit_cycle_start', 'audit_cycle_end', 'status', 'notes'
        ]
        widgets = {
            'atm': forms.Select(attrs={'class': 'form-select'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ tên'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số tài khoản'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số thẻ'}),
            'trace_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số trace'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID giao dịch'}),
            'discrepancy_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Số tiền', 'min': '0', 'step': '1000'}),
            'audit_cycle_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'audit_cycle_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ghi chú'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lọc chỉ hiển thị các máy ATM active
        self.fields['atm'].queryset = ATM.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        audit_cycle_start = cleaned_data.get('audit_cycle_start')
        audit_cycle_end = cleaned_data.get('audit_cycle_end')

        # Kiểm tra ngày kết thúc phải sau ngày bắt đầu
        if audit_cycle_start and audit_cycle_end:
            if audit_cycle_end < audit_cycle_start:
                raise forms.ValidationError(
                    'Ngày kết thúc chu kỳ phải sau ngày bắt đầu'
                )

        return cleaned_data
