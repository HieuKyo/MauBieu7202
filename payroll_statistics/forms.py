"""
Forms cho app Payroll Statistics
"""
from django import forms


class PayrollUploadForm(forms.Form):
    """Form upload file Excel/CSV để import dữ liệu"""
    file = forms.FileField(
        label='Chọn file Excel/CSV',
        help_text='Chấp nhận file .xls, .xlsx, .csv',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xls,.xlsx,.csv'
        })
    )

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Kiểm tra extension
            file_name = file.name.lower()
            valid_extensions = ['.xls', '.xlsx', '.csv']
            if not any(file_name.endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError(
                    'File không đúng định dạng. Chỉ chấp nhận .xls, .xlsx, .csv'
                )
            # Kiểm tra kích thước (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File quá lớn. Kích thước tối đa 10MB')
        return file
