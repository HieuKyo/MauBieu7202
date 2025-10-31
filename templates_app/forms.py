"""
Dynamic form generation based on Template variables
"""
from django import forms
from .models import Template, TemplateVariable


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
        Custom validation nếu cần
        """
        cleaned_data = super().clean()

        # Convert date fields to string format for Word template
        for field_name, value in cleaned_data.items():
            if hasattr(value, 'strftime'):  # If it's a date/datetime object
                cleaned_data[field_name] = value.strftime('%d/%m/%Y')

        return cleaned_data
