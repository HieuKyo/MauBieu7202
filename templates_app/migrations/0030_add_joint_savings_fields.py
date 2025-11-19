# Generated migration for joint savings fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0029_userprofile_certificate_code_and_more'),
    ]

    operations = [
        # Thông tin người gửi tiền thứ hai
        migrations.AddField(
            model_name='customer',
            name='ho_ten_nguoi_gui_2',
            field=models.CharField(blank=True, max_length=200, verbose_name='Họ tên người gửi tiền thứ hai'),
        ),
        migrations.AddField(
            model_name='customer',
            name='so_cmnd_nguoi_gui_2',
            field=models.CharField(blank=True, max_length=20, verbose_name='CMND/CCCD/Hộ chiếu người gửi 2'),
        ),
        migrations.AddField(
            model_name='customer',
            name='ngay_cap_cmnd_nguoi_gui_2',
            field=models.DateField(blank=True, null=True, verbose_name='Ngày cấp CMND người gửi 2'),
        ),
        migrations.AddField(
            model_name='customer',
            name='noi_cap_cmnd_nguoi_gui_2',
            field=models.CharField(blank=True, max_length=200, verbose_name='Nơi cấp CMND người gửi 2'),
        ),
        migrations.AddField(
            model_name='customer',
            name='dia_chi_nguoi_gui_2',
            field=models.TextField(blank=True, verbose_name='Địa chỉ người gửi 2'),
        ),
        migrations.AddField(
            model_name='customer',
            name='sdt_nguoi_gui_2',
            field=models.CharField(blank=True, max_length=20, verbose_name='Số điện thoại người gửi 2'),
        ),
        # Giao dịch thẻ tiết kiệm - Rút lãi
        migrations.AddField(
            model_name='customer',
            name='gd_rut_lai_tat_ca',
            field=models.BooleanField(default=False, verbose_name='Rút lãi - Tất cả người gửi tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='gd_rut_lai_mot_so',
            field=models.BooleanField(default=False, verbose_name='Rút lãi - Một/một số người gửi tiền'),
        ),
        # Tất toán
        migrations.AddField(
            model_name='customer',
            name='gd_tat_toan_tat_ca',
            field=models.BooleanField(default=False, verbose_name='Tất toán - Tất cả người gửi tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='gd_tat_toan_mot_so',
            field=models.BooleanField(default=False, verbose_name='Tất toán - Một/một số người gửi tiền'),
        ),
        # Báo mất
        migrations.AddField(
            model_name='customer',
            name='gd_bao_mat_tat_ca',
            field=models.BooleanField(default=False, verbose_name='Báo mất - Tất cả người gửi tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='gd_bao_mat_mot_so',
            field=models.BooleanField(default=False, verbose_name='Báo mất - Một/một số người gửi tiền'),
        ),
        # Báo hỏng
        migrations.AddField(
            model_name='customer',
            name='gd_bao_hong_tat_ca',
            field=models.BooleanField(default=False, verbose_name='Báo hỏng - Tất cả người gửi tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='gd_bao_hong_mot_so',
            field=models.BooleanField(default=False, verbose_name='Báo hỏng - Một/một số người gửi tiền'),
        ),
        # Phong tỏa
        migrations.AddField(
            model_name='customer',
            name='gd_phong_toa_tat_ca',
            field=models.BooleanField(default=False, verbose_name='Phong tỏa - Tất cả người gửi tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='gd_phong_toa_mot_so',
            field=models.BooleanField(default=False, verbose_name='Phong tỏa - Một/một số người gửi tiền'),
        ),
        # Xác nhận số dư
        migrations.AddField(
            model_name='customer',
            name='gd_xac_nhan_so_du_tat_ca',
            field=models.BooleanField(default=False, verbose_name='Xác nhận số dư - Tất cả người gửi tiền'),
        ),
        migrations.AddField(
            model_name='customer',
            name='gd_xac_nhan_so_du_mot_so',
            field=models.BooleanField(default=False, verbose_name='Xác nhận số dư - Một/một số người gửi tiền'),
        ),
    ]
