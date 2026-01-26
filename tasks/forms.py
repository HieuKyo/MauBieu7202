from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """Form để tạo và chỉnh sửa Task."""

    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'due_date',
            'priority',
            'category',
            'recurring_type',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề công việc...',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Mô tả chi tiết công việc (tùy chọn)...',
                'rows': 3,
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'recurring_type': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'title': 'Tiêu đề',
            'description': 'Mô tả',
            'due_date': 'Hạn chót',
            'priority': 'Độ ưu tiên',
            'category': 'Phân loại',
            'recurring_type': 'Loại lặp',
        }
        help_texts = {
            'recurring_type': 'Khi hoàn thành, hệ thống sẽ tự động tạo công việc mới với hạn chót tương ứng.',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 3:
                raise forms.ValidationError('Tiêu đề phải có ít nhất 3 ký tự.')
        return title
