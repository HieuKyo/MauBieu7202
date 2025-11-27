# Generated manually for foreign currency fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0030_add_joint_savings_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='quan_he_nguoi_gui_nhan',
            field=models.CharField(blank=True, max_length=200, verbose_name='Quan hệ giữa người gửi và người nhận'),
        ),
        migrations.AddField(
            model_name='customer',
            name='muc_dich_giao_dich',
            field=models.CharField(blank=True, choices=[('Hỗ trợ gia đình', 'Hỗ trợ gia đình'), ('Quà tặng', 'Quà tặng')], max_length=50, verbose_name='Mục đích giao dịch'),
        ),
        migrations.AddField(
            model_name='customer',
            name='ho_ten_nguoi_gui_tien',
            field=models.CharField(blank=True, max_length=200, verbose_name='Họ tên người gửi tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='quoc_gia_gui_tien',
            field=models.CharField(blank=True, max_length=100, verbose_name='Quốc gia gửi tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='ma_so_nhan_tien',
            field=models.CharField(blank=True, max_length=50, verbose_name='Mã số nhận tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='so_tien_ngoai_te',
            field=models.CharField(blank=True, max_length=50, verbose_name='Số tiền ngoại tệ'),
        ),
        migrations.AddField(
            model_name='customer',
            name='loai_tien_ngoai_te',
            field=models.CharField(blank=True, max_length=20, verbose_name='Loại tiền ngoại tệ'),
        ),
    ]
