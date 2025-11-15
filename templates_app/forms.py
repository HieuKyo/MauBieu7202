"""
Dynamic form generation based on Template variables
"""
from django import forms
from .models import Template, TemplateVariable, Customer, GlobalConfig, Category


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
            'nghe_nghiep': forms.Select(attrs={'class': 'form-select'}),
            'noi_lam_viec': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nơi làm việc'}),
            'so_tai_khoan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số tài khoản'}),
            'loai_tai_khoan': forms.Select(attrs={'class': 'form-select'}),
            'so_tai_khoan_yc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số tài khoản theo yêu cầu'}),
            'loai_tien_te': forms.Select(attrs={'class': 'form-select'}),
            'loai_the': forms.Select(attrs={'class': 'form-select'}),
            'hang_the': forms.Select(attrs={'class': 'form-select'}),
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
            'dia_chi_chi_nhanh': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Địa chỉ đầy đủ chi nhánh'}),
            'dien_thoai_chi_nhanh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 0291.3822.079'}),
            'so_fax': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: 0291.3822.080'}),
            'dia_danh': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Bạc Liêu, Đồng Tháp'}),
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
        ('personal_info', 'Thông tin cá nhân (Mã KH, Họ tên, Ngày sinh, Giới tính)'),
        ('id_documents', 'Giấy tờ tùy thân (CMND/CCCD, Ngày cấp, Nơi cấp)'),
        ('contact', 'Thông tin liên hệ (Địa chỉ, SĐT, Email)'),
        ('employment', 'Thông tin nghề nghiệp (Nghề nghiệp, Nơi làm việc)'),
        ('banking', 'Thông tin tài khoản (Số TK, Loại TK, Loại tiền tệ)'),
        ('card', 'Thông tin thẻ (Loại thẻ, Hạng thẻ, Phát hành)'),
        ('services', 'Đăng ký dịch vụ (SMS Banking, Agribank Plus, Liên kết ví)'),
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
