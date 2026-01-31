from django import forms
from django.contrib.auth.models import User
from .models import Task


class UserChoiceField(forms.ModelChoiceField):
    """Custom field to display user with their position."""

    def label_from_instance(self, obj):
        """
        Hiển thị user kèm chức vụ.
        Format: "Họ tên - Chức vụ" hoặc "Username" nếu không có profile
        """
        try:
            profile = obj.profile
            name = profile.full_name or obj.username
            position = profile.get_position_display() if profile.position else ''
            if position:
                return f"{name} - {position}"
            return name
        except Exception:
            return obj.username


class TaskForm(forms.ModelForm):
    """Form để tạo và chỉnh sửa Task."""

    assigned_to = UserChoiceField(
        queryset=User.objects.filter(is_active=True).select_related('profile'),
        required=False,
        empty_label="-- Chọn người nhận việc --",
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label='Giao cho'
    )

    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'due_date',
            'priority',
            'category',
            'recurring_type',
            'assigned_to',
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
            'assigned_to': 'Để trống nếu đây là công việc cá nhân của bạn.',
        }

    def __init__(self, *args, can_assign=True, **kwargs):
        super().__init__(*args, **kwargs)

        if can_assign:
            # Sắp xếp danh sách user theo tên
            self.fields['assigned_to'].queryset = User.objects.filter(
                is_active=True
            ).select_related('profile').order_by('profile__full_name', 'username')
        else:
            # Nhân viên: xóa trường assigned_to khỏi form
            del self.fields['assigned_to']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 3:
                raise forms.ValidationError('Tiêu đề phải có ít nhất 3 ký tự.')
        return title
