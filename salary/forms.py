"""
Forms cho app Salary
"""
from django import forms
from .models import Beneficiary, CompanyAccount


class BeneficiaryForm(forms.ModelForm):
    """Form quản lý Beneficiary"""

    class Meta:
        model = Beneficiary
        fields = ['full_name', 'account_number', 'bank', 'bank_code', 'company', 'note']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập họ và tên'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số tài khoản'
            }),
            'bank': forms.Select(attrs={
                'class': 'form-select'
            }),
            'bank_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mã ngân hàng (nếu có)'
            }),
            'company': forms.Select(attrs={
                'class': 'form-select'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ghi chú (nếu có)'
            }),
        }


class CompanyAccountForm(forms.ModelForm):
    """Form quản lý Company Account"""

    class Meta:
        model = CompanyAccount
        fields = ['account_number', 'account_name', 'bank', 'is_active']
        widgets = {
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số tài khoản công ty'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên tài khoản công ty'
            }),
            'bank': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class FileUploadForm(forms.Form):
    """Form upload file Excel/CSV"""
    TRANSACTION_TYPES = [
        ('PAYROLL', 'Chi trả lương'),
        ('COLLECTION', 'Thu hộ'),
    ]

    file = forms.FileField(
        label='File Excel/CSV',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        }),
        help_text='Chọn file Excel hoặc CSV chứa dữ liệu chi lương/thu hộ'
    )

    transaction_type = forms.ChoiceField(
        label='Loại giao dịch',
        choices=TRANSACTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    company_account = forms.ModelChoiceField(
        label='Tài khoản công ty',
        queryset=CompanyAccount.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Chọn tài khoản công ty (tùy chọn)'
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1].lower()
            if ext not in ['xlsx', 'xls', 'csv']:
                raise forms.ValidationError('Chỉ hỗ trợ file Excel (.xlsx, .xls) hoặc CSV')
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File không được lớn hơn 10MB')
        return file
