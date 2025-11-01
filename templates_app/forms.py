"""
Dynamic form generation based on Template variables
"""
from django import forms
from .models import Template, TemplateVariable, Customer


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
            'ho_ten': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ và tên'}),
            'ngay_sinh': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gioi_tinh': forms.Select(attrs={'class': 'form-select'}),
            'so_cmnd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số CMND/CCCD'}),
            'ngay_cap_cmnd': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'noi_cap_cmnd': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Công an TP. HCM'}),
            'dia_chi': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Địa chỉ thường trú'}),
            'so_dien_thoai': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số điện thoại'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'nghe_nghiep': forms.Select(attrs={'class': 'form-select'}),
            'noi_lam_viec': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nơi làm việc'}),
            'so_tai_khoan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Số tài khoản'}),
            'loai_tai_khoan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Loại tài khoản'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ghi chú thêm'}),
        }
