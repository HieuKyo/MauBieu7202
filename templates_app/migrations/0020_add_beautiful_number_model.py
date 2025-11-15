# Generated migration for Beautiful Number Model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0019_seed_beautiful_number_fee_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='BeautifulNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(help_text='Số tài khoản 13 số (7202XXXXXXXXX)', max_length=13, unique=True, verbose_name='Số tài khoản')),
                ('category', models.CharField(choices=[('LOC_PHAT', 'Lộc Phát (Số 6, 8)'), ('TAI_LOC', 'Tài Lộc'), ('HOP_TUOI', 'Hợp Tuổi'), ('PHONG_THUY', 'Phong Thủy'), ('SO_LAP', 'Số Lặp'), ('SO_TIEN', 'Số Tiến'), ('SO_DOI_XUNG', 'Số Đối Xứng'), ('DAC_BIET', 'Đặc Biệt')], db_index=True, max_length=20, verbose_name='Loại số đẹp')),
                ('price_tier', models.CharField(choices=[('500K-1M', '500.000 - 1.000.000 VNĐ'), ('1M-3M', '1.000.000 - 3.000.000 VNĐ'), ('3M-5M', '3.000.000 - 5.000.000 VNĐ'), ('5M-10M', '5.000.000 - 10.000.000 VNĐ'), ('10M-20M', '10.000.000 - 20.000.000 VNĐ'), ('20M+', 'Trên 20.000.000 VNĐ')], db_index=True, max_length=20, verbose_name='Mức giá')),
                ('fee', models.DecimalField(decimal_places=0, help_text='Phí cụ thể cho số này', max_digits=12, verbose_name='Phí (VNĐ)')),
                ('is_available', models.BooleanField(db_index=True, default=True, verbose_name='Còn số')),
                ('description', models.TextField(blank=True, help_text='Mô tả đặc điểm của số đẹp này', verbose_name='Mô tả')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày thêm')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
            ],
            options={
                'verbose_name': 'Số đẹp có sẵn',
                'verbose_name_plural': 'Danh sách số đẹp có sẵn',
                'ordering': ['price_tier', 'category', 'account_number'],
                'indexes': [
                    models.Index(fields=['category', 'price_tier', 'is_available'], name='templates_a_categor_idx'),
                ],
            },
        ),
    ]
