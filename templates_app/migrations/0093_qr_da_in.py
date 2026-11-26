from django.db import migrations, models


def giu_ban_ghi_da_in(apps, schema_editor):
    QRRegistration = apps.get_model('templates_app', 'QRRegistration')
    QRRegistration.objects.filter(trang_thai='da_in').update(da_in=True)


class Migration(migrations.Migration):
    """Bỏ bước gửi duyệt: trạng thái 3 bước thay bằng một ô Đã in."""

    dependencies = [
        ('templates_app', '0092_qr_loa_than_tai'),
    ]

    operations = [
        migrations.AddField(
            model_name='qrregistration',
            name='da_in',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Đã in'),
        ),
        migrations.RunPython(giu_ban_ghi_da_in, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='qrregistration',
            name='trang_thai',
        ),
        migrations.RemoveField(
            model_name='qrregistration',
            name='ngay_gui_duyet',
        ),
    ]
