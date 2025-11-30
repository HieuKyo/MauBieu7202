# Generated manually for payroll_statistics app

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PayingUnit',
            fields=[
                ('account_number', models.CharField(max_length=50, primary_key=True, serialize=False, unique=True, verbose_name='Số tài khoản đơn vị')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='Tên đơn vị')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
            ],
            options={
                'verbose_name': 'Đơn vị',
                'verbose_name_plural': 'Đơn vị',
                'ordering': ['account_number'],
            },
        ),
        migrations.CreateModel(
            name='BeneficiaryAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(max_length=50, verbose_name='Số tài khoản nhân viên')),
                ('remark_ref', models.TextField(blank=True, verbose_name='Nội dung giao dịch mẫu')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='beneficiaries', to='payroll_statistics.payingunit', verbose_name='Đơn vị')),
            ],
            options={
                'verbose_name': 'Nhân viên/Người hưởng',
                'verbose_name_plural': 'Nhân viên/Người hưởng',
                'ordering': ['unit', 'account_number'],
                'unique_together': {('unit', 'account_number')},
            },
        ),
    ]
