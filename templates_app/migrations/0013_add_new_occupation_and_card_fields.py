# Generated manually for adding new occupation and card fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0012_customer_dan_toc_customer_ho_khau_and_more'),
    ]

    operations = [
        # Update NGHE_NGHIEP_CHOICES to include new occupations
        migrations.AlterField(
            model_name='customer',
            name='nghe_nghiep',
            field=models.CharField(
                blank=True,
                choices=[
                    ('Công chức viên chức', 'Công chức viên chức'),
                    ('Nông dân', 'Nông dân'),
                    ('Giáo viên/Bác Sĩ', 'Giáo viên/Bác Sĩ'),
                    ('Công nhân', 'Công nhân'),
                    ('Kinh doanh tự do', 'Kinh doanh tự do'),
                    ('Học sinh/Sinh viên', 'Học sinh/Sinh viên'),
                    ('Nội trợ', 'Nội trợ'),
                    ('Công an/Bộ đội', 'Công an/Bộ đội'),
                    ('Kỹ sư', 'Kỹ sư'),
                    ('Khác', 'Khác'),
                ],
                max_length=200,
                verbose_name='Nghề nghiệp'
            ),
        ),
        # Add new card type boolean fields
        migrations.AddField(
            model_name='customer',
            name='the_lap_nghiep',
            field=models.BooleanField(default=False, verbose_name='Thẻ lập nghiệp'),
        ),
        migrations.AddField(
            model_name='customer',
            name='the_lien_ket',
            field=models.BooleanField(default=False, verbose_name='Thẻ liên kết'),
        ),
        migrations.AddField(
            model_name='customer',
            name='the_dong_thuong_hieu',
            field=models.BooleanField(default=False, verbose_name='Thẻ đồng thương hiệu'),
        ),
        # Add card name field
        migrations.AddField(
            model_name='customer',
            name='ten_the_1',
            field=models.CharField(blank=True, max_length=200, verbose_name='Tên thẻ 1'),
        ),
        # Add ABIC service field
        migrations.AddField(
            model_name='customer',
            name='dv_abic',
            field=models.BooleanField(default=False, verbose_name='Dịch vụ: ABIC'),
        ),
    ]
