from django import forms

from savings_calculator.models import InterestRate

from .models import RATE_FIELDS, BoardSetting, ExchangeRate, LedSlide

MAX_IMAGE_BYTES = 10 * 1024 * 1024


class ExchangeRateForm(forms.ModelForm):
    class Meta:
        model = ExchangeRate
        fields = ('code', *RATE_FIELDS, 'order')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in RATE_FIELDS:
            self.fields[name].required = True
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control form-control-sm'

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()

    def clean(self):
        data = super().clean()
        for buy, sell in (('buy_cash', 'sell_cash'), ('buy_transfer', 'sell_transfer')):
            if data.get(buy) and data.get(sell) and data[buy] > data[sell]:
                self.add_error(sell, 'Giá bán phải lớn hơn hoặc bằng giá mua.')
        return data


class SavingsProductPickForm(forms.ModelForm):
    class Meta:
        model = BoardSetting
        fields = ('savings_product',)
        widgets = {
            'savings_product': forms.Select(attrs={
                'class': 'form-select', 'onchange': 'this.form.submit()',
            }),
        }


class SavingsRateForm(forms.ModelForm):
    class Meta:
        model = InterestRate
        fields = (
            'term_month_min', 'term_month_max', 'description',
            'interest_rate_yearly', 'effective_date', 'is_active',
        )
        widgets = {
            'effective_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'is_active':
                field.widget.attrs['class'] = 'form-control form-control-sm'

    def clean_interest_rate_yearly(self):
        value = self.cleaned_data['interest_rate_yearly']
        if not 0 < value <= 100:
            raise forms.ValidationError('Lãi suất phải lớn hơn 0 và không quá 100.')
        return value

    def clean(self):
        data = super().clean()
        low, high = data.get('term_month_min'), data.get('term_month_max')
        if low is not None and high is not None and high < low:
            self.add_error('term_month_max', 'Kỳ hạn đến phải lớn hơn hoặc bằng kỳ hạn từ.')
        return data


class BoardSettingForm(forms.ModelForm):
    class Meta:
        model = BoardSetting
        fields = (
            'rate_seconds', 'savings_seconds', 'slide_seconds',
            'board_width', 'board_height', 'remind_time', 'shutdown_time', 'ticker_text',
        )
        widgets = {
            'remind_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'shutdown_time': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class SlideUploadForm(forms.ModelForm):
    class Meta:
        model = LedSlide
        fields = ('image',)
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control', 'accept': '.jpg,.jpeg,.png,.webp',
            }),
        }

    def clean_image(self):
        image = self.cleaned_data['image']
        if image.size > MAX_IMAGE_BYTES:
            raise forms.ValidationError('Ảnh không được lớn hơn 10 MB.')
        return image


class SlideEditForm(forms.ModelForm):
    class Meta:
        model = LedSlide
        fields = ('order', 'seconds', 'start_date', 'end_date', 'is_active')
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'seconds': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'start_date': forms.DateInput(
                format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control form-control-sm'},
            ),
            'end_date': forms.DateInput(
                format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control form-control-sm'},
            ),
        }

    def clean(self):
        data = super().clean()
        start, end = data.get('start_date'), data.get('end_date')
        if start and end and end < start:
            self.add_error('end_date', 'Ngày kết thúc phải sau ngày bắt đầu.')
        return data
