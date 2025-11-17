# Generated manually for Bank Statement Analyzer feature

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('templates_app', '0025_customer_district_customer_full_address_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankStatement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày upload')),
                ('file_name', models.CharField(max_length=255, verbose_name='Tên file')),
                ('total_transactions', models.IntegerField(verbose_name='Tổng số giao dịch')),
                ('total_debit', models.DecimalField(decimal_places=0, default=0, max_digits=18, verbose_name='Tổng tiền ghi nợ')),
                ('total_credit', models.DecimalField(decimal_places=0, default=0, max_digits=18, verbose_name='Tổng tiền ghi có')),
                ('final_balance', models.DecimalField(decimal_places=0, default=0, max_digits=18, verbose_name='Số dư cuối kỳ')),
                ('processed', models.BooleanField(default=False, verbose_name='Đã xử lý')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bank_statements', to=settings.AUTH_USER_MODEL, verbose_name='Người upload')),
            ],
            options={
                'verbose_name': 'Sao kê ngân hàng',
                'verbose_name_plural': 'Sao kê ngân hàng',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stt', models.IntegerField(verbose_name='STT')),
                ('transaction_date', models.DateField(verbose_name='Ngày giao dịch')),
                ('debit_amount', models.DecimalField(decimal_places=0, default=0, max_digits=15, verbose_name='Số tiền ghi nợ')),
                ('credit_amount', models.DecimalField(decimal_places=0, default=0, max_digits=15, verbose_name='Số tiền ghi có')),
                ('balance', models.DecimalField(decimal_places=0, max_digits=15, verbose_name='Số dư sau GD')),
                ('bank_name', models.CharField(blank=True, max_length=100, verbose_name='Ngân hàng')),
                ('account_number', models.CharField(blank=True, max_length=50, verbose_name='Số tài khoản')),
                ('beneficiary_name', models.CharField(blank=True, max_length=200, verbose_name='Tên người thụ hưởng')),
                ('description', models.TextField(verbose_name='Nội dung gốc')),
                ('transaction_type', models.CharField(blank=True, max_length=100, verbose_name='Loại giao dịch')),
                ('raw_trcdnm', models.CharField(blank=True, max_length=200, verbose_name='Tên mã giao dịch (raw)')),
                ('raw_tomgntno', models.CharField(blank=True, max_length=50, verbose_name='Tài khoản đối ứng (raw)')),
                ('statement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='templates_app.bankstatement', verbose_name='Sao kê')),
            ],
            options={
                'verbose_name': 'Giao dịch',
                'verbose_name_plural': 'Giao dịch',
                'ordering': ['statement', 'stt'],
            },
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['statement', 'transaction_date'], name='templates_a_stateme_cc7929_idx'),
        ),
        migrations.AddIndex(
            model_name='transaction',
            index=models.Index(fields=['transaction_type'], name='templates_a_transac_d8c5c0_idx'),
        ),
    ]
