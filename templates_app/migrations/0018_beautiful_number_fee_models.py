# Generated migration for Beautiful Number Fee Models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0017_add_customer_classification_to_field_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetailedFeeTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(help_text='Số lượng số đẹp trong tài khoản (2-10+)', verbose_name='Số lượng số đẹp')),
                ('fee_type', models.CharField(choices=[('NORMAL', 'Loại thường'), ('SPECIAL', 'Loại đặc biệt (Lặp, Lộc Phát, Tiến)')], default='NORMAL', max_length=10, verbose_name='Loại số đẹp')),
                ('min_fee', models.DecimalField(decimal_places=0, help_text='Mức phí tối thiểu cho loại số đẹp này', max_digits=12, verbose_name='Phí tối thiểu (VNĐ)')),
                ('max_fee', models.DecimalField(blank=True, decimal_places=0, help_text='Mức phí tối đa. Để trống = \'Thỏa thuận\'', max_digits=12, null=True, verbose_name='Phí tối đa (VNĐ)')),
            ],
            options={
                'verbose_name': 'Bậc phí chi tiết',
                'verbose_name_plural': 'Biểu phí chi tiết (Bảng 1)',
                'ordering': ['quantity', 'fee_type'],
                'unique_together': {('quantity', 'fee_type')},
            },
        ),
        migrations.CreateModel(
            name='OnRequestFeeTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_quantity', models.PositiveSmallIntegerField(help_text='Số lượng số đẹp tối thiểu trong khoảng này', verbose_name='Từ (số lượng)')),
                ('max_quantity', models.PositiveSmallIntegerField(help_text='Số lượng số đẹp tối đa trong khoảng này', verbose_name='Đến (số lượng)')),
                ('min_fee', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='Phí tối thiểu (VNĐ)')),
                ('max_fee', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='Phí tối đa (VNĐ)')),
            ],
            options={
                'verbose_name': 'Bậc phí theo yêu cầu',
                'verbose_name_plural': 'Biểu phí theo yêu cầu (Bảng 2)',
                'ordering': ['min_quantity'],
            },
        ),
    ]
