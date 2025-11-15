# Data migration to seed Beautiful Number Fee tiers

from django.db import migrations


def seed_detailed_fee_tiers(apps, schema_editor):
    """Nạp dữ liệu mẫu cho Biểu phí chi tiết (Bảng 1)"""
    DetailedFeeTier = apps.get_model('templates_app', 'DetailedFeeTier')

    # Data from Bảng 1 in the PDF
    tiers_data = [
        # Loại thường
        {'quantity': 2, 'fee_type': 'NORMAL', 'min_fee': 300000, 'max_fee': 500000},
        {'quantity': 3, 'fee_type': 'NORMAL', 'min_fee': 300000, 'max_fee': 500000},
        {'quantity': 4, 'fee_type': 'NORMAL', 'min_fee': 500000, 'max_fee': 1000000},
        {'quantity': 5, 'fee_type': 'NORMAL', 'min_fee': 1000000, 'max_fee': 3000000},
        {'quantity': 6, 'fee_type': 'NORMAL', 'min_fee': 3000000, 'max_fee': 5000000},
        {'quantity': 7, 'fee_type': 'NORMAL', 'min_fee': 8000000, 'max_fee': 10000000},
        {'quantity': 8, 'fee_type': 'NORMAL', 'min_fee': 10000000, 'max_fee': 20000000},
        {'quantity': 9, 'fee_type': 'NORMAL', 'min_fee': 25000000, 'max_fee': 40000000},
        {'quantity': 10, 'fee_type': 'NORMAL', 'min_fee': 100000000, 'max_fee': None},  # Thỏa thuận

        # Loại đặc biệt (Lặp, Lộc Phát, Tiến)
        {'quantity': 3, 'fee_type': 'SPECIAL', 'min_fee': 500000, 'max_fee': 1000000},
        {'quantity': 4, 'fee_type': 'SPECIAL', 'min_fee': 1000000, 'max_fee': 3000000},
        {'quantity': 5, 'fee_type': 'SPECIAL', 'min_fee': 3000000, 'max_fee': 5000000},
        {'quantity': 6, 'fee_type': 'SPECIAL', 'min_fee': 8000000, 'max_fee': 10000000},
        {'quantity': 7, 'fee_type': 'SPECIAL', 'min_fee': 10000000, 'max_fee': 20000000},
        {'quantity': 8, 'fee_type': 'SPECIAL', 'min_fee': 25000000, 'max_fee': 40000000},
        {'quantity': 9, 'fee_type': 'SPECIAL', 'min_fee': 40000000, 'max_fee': 80000000},
    ]

    for tier_data in tiers_data:
        DetailedFeeTier.objects.get_or_create(**tier_data)


def seed_on_request_fee_tiers(apps, schema_editor):
    """Nạp dữ liệu mẫu cho Biểu phí theo yêu cầu (Bảng 2)"""
    OnRequestFeeTier = apps.get_model('templates_app', 'OnRequestFeeTier')

    # Data from Bảng 2 in the PDF
    tiers_data = [
        {'min_quantity': 2, 'max_quantity': 5, 'min_fee': 300000, 'max_fee': 500000},
        {'min_quantity': 6, 'max_quantity': 6, 'min_fee': 500000, 'max_fee': 1000000},
        {'min_quantity': 7, 'max_quantity': 9, 'min_fee': 1000000, 'max_fee': 3000000},
    ]

    for tier_data in tiers_data:
        OnRequestFeeTier.objects.get_or_create(**tier_data)


def reverse_seed(apps, schema_editor):
    """Xóa dữ liệu đã seed"""
    DetailedFeeTier = apps.get_model('templates_app', 'DetailedFeeTier')
    OnRequestFeeTier = apps.get_model('templates_app', 'OnRequestFeeTier')

    DetailedFeeTier.objects.all().delete()
    OnRequestFeeTier.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0018_beautiful_number_fee_models'),
    ]

    operations = [
        migrations.RunPython(seed_detailed_fee_tiers, reverse_seed),
        migrations.RunPython(seed_on_request_fee_tiers, reverse_seed),
    ]
