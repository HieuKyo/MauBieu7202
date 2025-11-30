# Generated manually - Add Transaction model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll_statistics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('payroll', 'Chi lương'), ('collection', 'Thu hộ/Khoản trừ')], max_length=20, verbose_name='Loại giao dịch')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Số tiền')),
                ('transaction_date', models.DateField(blank=True, null=True, verbose_name='Ngày giao dịch')),
                ('remark', models.TextField(blank=True, verbose_name='Nội dung giao dịch')),
                ('facno', models.CharField(blank=True, max_length=50, verbose_name='Facno (gốc)')),
                ('tacno', models.CharField(blank=True, max_length=50, verbose_name='Tacno (gốc)')),
                ('rsltremark', models.CharField(blank=True, max_length=50, verbose_name='Rsltremark (gốc)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('beneficiary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='payroll_statistics.beneficiaryaccount', verbose_name='Nhân viên/Người hưởng')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='payroll_statistics.payingunit', verbose_name='Đơn vị')),
            ],
            options={
                'verbose_name': 'Giao dịch',
                'verbose_name_plural': 'Giao dịch',
                'ordering': ['-transaction_date', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_date'], name='payroll_sta_transac_76d4e5_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_type'], name='payroll_sta_transac_a1b2c3_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['unit', 'transaction_date'], name='payroll_sta_unit_id_d4e5f6_idx'),
        ),
    ]
