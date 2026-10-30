from django import forms
from .models import OutgoingDocument, IncomingDocument


class OutgoingDocumentForm(forms.ModelForm):
    noi_nhan_truong_phong = forms.BooleanField(
        required=False,
        label='Trưởng các phòng',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    noi_nhan_giam_doc_pgd = forms.BooleanField(
        required=False,
        label='Giám đốc phòng Giao dịch',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = OutgoingDocument
        fields = [
            'so_ky_hieu', 'ngay_van_ban', 'ten_loai_trich_yeu',
            'nguoi_ky', 'nguoi_ky_khac',
            'noi_nhan_truong_phong', 'noi_nhan_giam_doc_pgd', 'noi_nhan_khac',
            'don_vi_nhan_ban_luu', 'so_luong_ban',
            'ngay_chuyen', 'ky_nhan', 'ghi_chu',
            'loai_chuyen_phat', 'so_luong_bi', 'ky_nhan_buu_dien',
        ]
        widgets = {
            'so_ky_hieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 01/CV-NHNN'}),
            'ngay_van_ban': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ten_loai_trich_yeu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'nguoi_ky': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'nguoi_ky_khac': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên người ký'}),
            'noi_nhan_khac': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Nhập nơi nhận khác (mỗi nơi 1 dòng)'}),
            'don_vi_nhan_ban_luu': forms.TextInput(attrs={'class': 'form-control'}),
            'so_luong_ban': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'ngay_chuyen': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ky_nhan': forms.TextInput(attrs={'class': 'form-control'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'loai_chuyen_phat': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'so_luong_bi': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'ky_nhan_buu_dien': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nguoi_ky = cleaned_data.get('nguoi_ky')
        nguoi_ky_khac = cleaned_data.get('nguoi_ky_khac', '').strip()
        if nguoi_ky == 'other' and not nguoi_ky_khac:
            self.add_error('nguoi_ky_khac', 'Vui lòng nhập tên người ký.')

        loai_chuyen_phat = cleaned_data.get('loai_chuyen_phat')
        if loai_chuyen_phat == 'buu_dien':
            so_luong_bi = cleaned_data.get('so_luong_bi')
            if not so_luong_bi:
                self.add_error('so_luong_bi', 'Vui lòng nhập số lượng bì khi chọn chuyển phát bưu điện.')

        noi_nhan_truong_phong = cleaned_data.get('noi_nhan_truong_phong')
        noi_nhan_giam_doc_pgd = cleaned_data.get('noi_nhan_giam_doc_pgd')
        noi_nhan_khac = cleaned_data.get('noi_nhan_khac', '').strip()
        if not noi_nhan_truong_phong and not noi_nhan_giam_doc_pgd and not noi_nhan_khac:
            self.add_error(None, 'Vui lòng chọn ít nhất một nơi nhận văn bản.')

        return cleaned_data


class IncomingDocumentForm(forms.ModelForm):
    class Meta:
        model = IncomingDocument
        fields = [
            'ngay_den', 'so_den', 'tac_gia',
            'so_ky_hieu', 'ngay_van_ban', 'ten_loai_trich_yeu',
            'don_vi_nguoi_nhan', 'ngay_chuyen', 'ky_nhan', 'ghi_chu',
        ]
        widgets = {
            'ngay_den': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'so_den': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 01'}),
            'tac_gia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên cơ quan/cá nhân gửi văn bản'}),
            'so_ky_hieu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: 01/CV-NHNN'}),
            'ngay_van_ban': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ten_loai_trich_yeu': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'don_vi_nguoi_nhan': forms.TextInput(attrs={'class': 'form-control'}),
            'ngay_chuyen': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ky_nhan': forms.TextInput(attrs={'class': 'form-control'}),
            'ghi_chu': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
