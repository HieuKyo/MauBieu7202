# Generated migration to add new variables to Variable model

from django.db import migrations


def add_new_variables(apps, schema_editor):
    """Add new variables for ID card type and card return dates"""
    Variable = apps.get_model('templates_app', 'Variable')

    # List of new variables to add
    new_variables = [
        # ID Card Type Checkboxes
        {
            'name': 'cmnd',
            'label': 'Checkbox CMND (9 số)',
            'field_type': 'text',
            'help_text': 'Tự động tích cho CMND 9 số',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'cccd',
            'label': 'Checkbox CCCD (12 số cũ)',
            'field_type': 'text',
            'help_text': 'Tự động tích cho CCCD 12 số có ngày cấp ≤ 01/07/2024',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'cancuoc',
            'label': 'Checkbox Căn cước (12 số mới)',
            'field_type': 'text',
            'help_text': 'Tự động tích cho CCCD 12 số có ngày cấp > 01/07/2024',
            'required': False,
            'default_value': ''
        },

        # Card Return Date (ngay_tra_the) - Individual digits
        {
            'name': 'dtt1',
            'label': 'Ngày trả thẻ - Chữ số ngày thứ nhất',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → dtt1 = 2',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'dtt2',
            'label': 'Ngày trả thẻ - Chữ số ngày thứ hai',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → dtt2 = 0',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'mtt1',
            'label': 'Ngày trả thẻ - Chữ số tháng thứ nhất',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → mtt1 = 1',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'mtt2',
            'label': 'Ngày trả thẻ - Chữ số tháng thứ hai',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → mtt2 = 2',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'ytt1',
            'label': 'Ngày trả thẻ - Chữ số năm thứ nhất',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → ytt1 = 2',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'ytt2',
            'label': 'Ngày trả thẻ - Chữ số năm thứ hai',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → ytt2 = 0',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'ytt3',
            'label': 'Ngày trả thẻ - Chữ số năm thứ ba',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → ytt3 = 2',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'ytt4',
            'label': 'Ngày trả thẻ - Chữ số năm thứ tư',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → ytt4 = 4',
            'required': False,
            'default_value': ''
        },

        # Card Return Date Calculated (ngay_tra_the_tinh = ngay_in + 7 days) - Individual digits
        {
            'name': 'dttt1',
            'label': 'Ngày trả thẻ tính - Chữ số ngày thứ nhất',
            'field_type': 'text',
            'help_text': 'Tự động = ngày in + 7 ngày. Ví dụ: 20/12/2024 → dttt1 = 2',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'dttt2',
            'label': 'Ngày trả thẻ tính - Chữ số ngày thứ hai',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → dttt2 = 0',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'mttt1',
            'label': 'Ngày trả thẻ tính - Chữ số tháng thứ nhất',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → mttt1 = 1',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'mttt2',
            'label': 'Ngày trả thẻ tính - Chữ số tháng thứ hai',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → mttt2 = 2',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'yttt1',
            'label': 'Ngày trả thẻ tính - Chữ số năm thứ nhất',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → yttt1 = 2',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'yttt2',
            'label': 'Ngày trả thẻ tính - Chữ số năm thứ hai',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → yttt2 = 0',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'yttt3',
            'label': 'Ngày trả thẻ tính - Chữ số năm thứ ba',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → yttt3 = 2',
            'required': False,
            'default_value': ''
        },
        {
            'name': 'yttt4',
            'label': 'Ngày trả thẻ tính - Chữ số năm thứ tư',
            'field_type': 'text',
            'help_text': 'Ví dụ: 20/12/2024 → yttt4 = 4',
            'required': False,
            'default_value': ''
        },
    ]

    # Create variables if they don't exist
    for var_data in new_variables:
        Variable.objects.get_or_create(
            name=var_data['name'],
            defaults={
                'label': var_data['label'],
                'field_type': var_data['field_type'],
                'help_text': var_data['help_text'],
                'required': var_data['required'],
                'default_value': var_data['default_value']
            }
        )


def remove_new_variables(apps, schema_editor):
    """Remove the variables if migration is reversed"""
    Variable = apps.get_model('templates_app', 'Variable')

    variable_names = [
        'cmnd', 'cccd', 'cancuoc',
        'dtt1', 'dtt2', 'mtt1', 'mtt2', 'ytt1', 'ytt2', 'ytt3', 'ytt4',
        'dttt1', 'dttt2', 'mttt1', 'mttt2', 'yttt1', 'yttt2', 'yttt3', 'yttt4'
    ]

    Variable.objects.filter(name__in=variable_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0014_customer_ket_qua_phan_loai_kh_and_more'),
    ]

    operations = [
        migrations.RunPython(add_new_variables, remove_new_variables),
    ]
