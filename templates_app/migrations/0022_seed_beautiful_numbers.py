# Generated migration for seeding Beautiful Numbers

from django.db import migrations


def seed_beautiful_numbers(apps, schema_editor):
    """Nạp dữ liệu mẫu cho danh sách số đẹp"""
    BeautifulNumber = apps.get_model('templates_app', 'BeautifulNumber')

    # Danh sách số đẹp mẫu
    beautiful_numbers = [
        # ===== LỘC PHÁT (Số 6, 8) =====
        # Mức 500K - 1M
        {'account_number': '7202123456688', 'category': 'LOC_PHAT', 'price_tier': '500K-1M', 'fee': 600000, 'description': '2 số 6, 2 số 8'},
        {'account_number': '7202456788888', 'category': 'LOC_PHAT', 'price_tier': '500K-1M', 'fee': 800000, 'description': '5 số 8 cuối - Lộc Phát Phát Phát'},
        {'account_number': '7202369666666', 'category': 'LOC_PHAT', 'price_tier': '500K-1M', 'fee': 900000, 'description': '6 số 6 cuối - Lộc Lộc Lộc'},
        {'account_number': '7202147888888', 'category': 'LOC_PHAT', 'price_tier': '500K-1M', 'fee': 950000, 'description': '6 số 8 cuối - Phát Phát Phát'},

        # Mức 1M - 3M
        {'account_number': '7202686868686', 'category': 'LOC_PHAT', 'price_tier': '1M-3M', 'fee': 1800000, 'description': 'Lộc Phát đan xen'},
        {'account_number': '7202868686868', 'category': 'LOC_PHAT', 'price_tier': '1M-3M', 'fee': 1900000, 'description': 'Phát Lộc đan xen'},
        {'account_number': '7202688688688', 'category': 'LOC_PHAT', 'price_tier': '1M-3M', 'fee': 2000000, 'description': 'Lộc Phát Phát - lặp 3'},
        {'account_number': '7202866866866', 'category': 'LOC_PHAT', 'price_tier': '1M-3M', 'fee': 2100000, 'description': 'Phát Lộc Lộc - lặp 3'},

        # ===== SỐ LẶP =====
        # Mức 500K - 1M
        {'account_number': '7202123455555', 'category': 'SO_LAP', 'price_tier': '500K-1M', 'fee': 650000, 'description': '5 số 5 cuối'},
        {'account_number': '7202987777777', 'category': 'SO_LAP', 'price_tier': '500K-1M', 'fee': 700000, 'description': '7 số 7 cuối'},
        {'account_number': '7202456999999', 'category': 'SO_LAP', 'price_tier': '500K-1M', 'fee': 750000, 'description': '6 số 9 cuối'},
        {'account_number': '7202111111111', 'category': 'SO_LAP', 'price_tier': '500K-1M', 'fee': 800000, 'description': '9 số 1 - Nhất nhất nhất'},

        # Mức 1M - 3M
        {'account_number': '7202222222222', 'category': 'SO_LAP', 'price_tier': '1M-3M', 'fee': 1500000, 'description': '9 số 2 - Song song song'},
        {'account_number': '7202333333333', 'category': 'SO_LAP', 'price_tier': '1M-3M', 'fee': 1400000, 'description': '9 số 3 - Tam tam tam'},
        {'account_number': '7202999999999', 'category': 'SO_LAP', 'price_tier': '1M-3M', 'fee': 1800000, 'description': '9 số 9 - Cửu cửu cửu'},

        # ===== SỐ TIẾN (Liên tiếp) =====
        # Mức 500K - 1M
        {'account_number': '7202123456789', 'category': 'SO_TIEN', 'price_tier': '500K-1M', 'fee': 800000, 'description': 'Tiến thẳng 1-9'},
        {'account_number': '7202987654321', 'category': 'SO_TIEN', 'price_tier': '500K-1M', 'fee': 750000, 'description': 'Lùi thẳng 9-1'},
        {'account_number': '7202234567890', 'category': 'SO_TIEN', 'price_tier': '500K-1M', 'fee': 700000, 'description': 'Tiến 2-9-0'},

        # Mức 1M - 3M
        {'account_number': '7202012345678', 'category': 'SO_TIEN', 'price_tier': '1M-3M', 'fee': 1200000, 'description': 'Tiến từ 0-8'},
        {'account_number': '7202876543210', 'category': 'SO_TIEN', 'price_tier': '1M-3M', 'fee': 1100000, 'description': 'Lùi từ 8-0'},

        # ===== SỐ ĐỐI XỨNG =====
        # Mức 500K - 1M
        {'account_number': '7202121212121', 'category': 'SO_DOI_XUNG', 'price_tier': '500K-1M', 'fee': 700000, 'description': 'Đối xứng 121212121'},
        {'account_number': '7202123454321', 'category': 'SO_DOI_XUNG', 'price_tier': '500K-1M', 'fee': 800000, 'description': 'Đối xứng 123454321'},
        {'account_number': '7202987656789', 'category': 'SO_DOI_XUNG', 'price_tier': '500K-1M', 'fee': 650000, 'description': 'Đối xứng 987656789'},

        # Mức 1M - 3M
        {'account_number': '7202123321123', 'category': 'SO_DOI_XUNG', 'price_tier': '1M-3M', 'fee': 1300000, 'description': 'Hoàn hảo đối xứng'},
        {'account_number': '7202111222111', 'category': 'SO_DOI_XUNG', 'price_tier': '1M-3M', 'fee': 1400000, 'description': 'Đối xứng kép'},

        # ===== TÀI LỘC =====
        # Mức 1M - 3M
        {'account_number': '7202168168168', 'category': 'TAI_LOC', 'price_tier': '1M-3M', 'fee': 1600000, 'description': 'Nhất lộc phát - lặp 3 lần'},
        {'account_number': '7202186186186', 'category': 'TAI_LOC', 'price_tier': '1M-3M', 'fee': 1700000, 'description': 'Nhất phát lộc - lặp 3 lần'},
        {'account_number': '7202268268268', 'category': 'TAI_LOC', 'price_tier': '1M-3M', 'fee': 1500000, 'description': 'Song lộc phát - lặp 3 lần'},

        # Mức 3M - 5M
        {'account_number': '7202888168168', 'category': 'TAI_LOC', 'price_tier': '3M-5M', 'fee': 3800000, 'description': 'Phát phát phát - Nhất lộc phát'},
        {'account_number': '7202666186186', 'category': 'TAI_LOC', 'price_tier': '3M-5M', 'fee': 3500000, 'description': 'Lộc lộc lộc - Nhất phát lộc'},

        # ===== HỢP TUỔI =====
        # Mức 500K - 1M
        {'account_number': '7202195419541', 'category': 'HOP_TUOI', 'price_tier': '500K-1M', 'fee': 600000, 'description': 'Hợp tuổi 1954 (Giáp Ngọ)'},
        {'account_number': '7202196219621', 'category': 'HOP_TUOI', 'price_tier': '500K-1M', 'fee': 600000, 'description': 'Hợp tuổi 1962 (Nhâm Dần)'},
        {'account_number': '7202197019701', 'category': 'HOP_TUOI', 'price_tier': '500K-1M', 'fee': 600000, 'description': 'Hợp tuổi 1970 (Canh Tuất)'},
        {'account_number': '7202197819781', 'category': 'HOP_TUOI', 'price_tier': '500K-1M', 'fee': 600000, 'description': 'Hợp tuổi 1978 (Mậu Ngọ)'},
        {'account_number': '7202198619861', 'category': 'HOP_TUOI', 'price_tier': '500K-1M', 'fee': 600000, 'description': 'Hợp tuổi 1986 (Bính Dần)'},

        # Mức 1M - 3M
        {'account_number': '7202199019901', 'category': 'HOP_TUOI', 'price_tier': '1M-3M', 'fee': 1200000, 'description': 'Hợp tuổi 1990 (Canh Ngọ)'},
        {'account_number': '7202199819981', 'category': 'HOP_TUOI', 'price_tier': '1M-3M', 'fee': 1200000, 'description': 'Hợp tuổi 1998 (Mậu Dần)'},

        # ===== PHONG THỦY =====
        # Mức 1M - 3M
        {'account_number': '7202135135135', 'category': 'PHONG_THUY', 'price_tier': '1M-3M', 'fee': 1400000, 'description': 'Tam hợp 135 - Hỏa sinh Thổ'},
        {'account_number': '7202147147147', 'category': 'PHONG_THUY', 'price_tier': '1M-3M', 'fee': 1500000, 'description': 'Tam hợp 147 - Mộc sinh Hỏa'},
        {'account_number': '7202369369369', 'category': 'PHONG_THUY', 'price_tier': '1M-3M', 'fee': 1600000, 'description': 'Tam hợp 369 - Thủy sinh Mộc'},

        # Mức 3M - 5M
        {'account_number': '7202159159159', 'category': 'PHONG_THUY', 'price_tier': '3M-5M', 'fee': 3500000, 'description': 'Tam hợp 159 - Kim sinh Thủy'},
        {'account_number': '7202258258258', 'category': 'PHONG_THUY', 'price_tier': '3M-5M', 'fee': 3800000, 'description': 'Tam hợp 258 - Thổ sinh Kim'},

        # ===== ĐẶC BIỆT =====
        # Mức 3M - 5M
        {'account_number': '7202168888888', 'category': 'DAC_BIET', 'price_tier': '3M-5M', 'fee': 4500000, 'description': 'Nhất Lộc Phát x 7 - Siêu VIP'},
        {'account_number': '7202186666666', 'category': 'DAC_BIET', 'price_tier': '3M-5M', 'fee': 4200000, 'description': 'Nhất Phát Lộc x 7 - Siêu VIP'},

        # Mức 5M - 10M
        {'account_number': '7202888888168', 'category': 'DAC_BIET', 'price_tier': '5M-10M', 'fee': 7500000, 'description': 'Phát x 6 + Nhất Lộc Phát'},
        {'account_number': '7202666666186', 'category': 'DAC_BIET', 'price_tier': '5M-10M', 'fee': 7000000, 'description': 'Lộc x 6 + Nhất Phát Lộc'},
        {'account_number': '7202999888777', 'category': 'DAC_BIET', 'price_tier': '5M-10M', 'fee': 6500000, 'description': 'Cửu Phát Thất - Tam hợp VIP'},

        # Mức 10M - 20M
        {'account_number': '7202888666888', 'category': 'DAC_BIET', 'price_tier': '10M-20M', 'fee': 12000000, 'description': 'Phát Lộc Phát - Cực phẩm'},
        {'account_number': '7202686888666', 'category': 'DAC_BIET', 'price_tier': '10M-20M', 'fee': 13000000, 'description': 'Lộc Phát kết hợp hoàn hảo'},

        # Mức 20M+
        {'account_number': '7202888888888', 'category': 'DAC_BIET', 'price_tier': '20M+', 'fee': 25000000, 'description': '9 số 8 - Bá chủ Phát Phát Phát', 'is_available': False},
        {'account_number': '7202666666666', 'category': 'DAC_BIET', 'price_tier': '20M+', 'fee': 22000000, 'description': '9 số 6 - Bá chủ Lộc Lộc Lộc', 'is_available': False},

        # ===== THÊM CÁC SỐ ĐẸP KHÁC =====
        # Lộc Phát mức thấp
        {'account_number': '7202123468999', 'category': 'LOC_PHAT', 'price_tier': '500K-1M', 'fee': 550000, 'description': '1 số 6, 1 số 8, 3 số 9'},
        {'account_number': '7202789666333', 'category': 'LOC_PHAT', 'price_tier': '500K-1M', 'fee': 600000, 'description': '1 số 8, 3 số 6'},
        {'account_number': '7202456688123', 'category': 'LOC_PHAT', 'price_tier': '500K-1M', 'fee': 650000, 'description': '2 số 6, 2 số 8'},

        # Số lặp thêm
        {'account_number': '7202147000000', 'category': 'SO_LAP', 'price_tier': '500K-1M', 'fee': 700000, 'description': '6 số 0 cuối'},
        {'account_number': '7202258444444', 'category': 'SO_LAP', 'price_tier': '500K-1M', 'fee': 650000, 'description': '6 số 4 cuối'},
        {'account_number': '7202369222222', 'category': 'SO_LAP', 'price_tier': '500K-1M', 'fee': 680000, 'description': '6 số 2 cuối'},

        # Số tiến thêm
        {'account_number': '7202345678901', 'category': 'SO_TIEN', 'price_tier': '500K-1M', 'fee': 720000, 'description': 'Tiến 3-9-0-1'},
        {'account_number': '7202456789012', 'category': 'SO_TIEN', 'price_tier': '500K-1M', 'fee': 740000, 'description': 'Tiến 4-9-0-1-2'},
        {'account_number': '7202543210987', 'category': 'SO_TIEN', 'price_tier': '500K-1M', 'fee': 700000, 'description': 'Lùi 5-4-3-2-1-0-9-8-7'},

        # Số đối xứng thêm
        {'account_number': '7202147787741', 'category': 'SO_DOI_XUNG', 'price_tier': '500K-1M', 'fee': 680000, 'description': 'Đối xứng 147787741'},
        {'account_number': '7202258885852', 'category': 'SO_DOI_XUNG', 'price_tier': '500K-1M', 'fee': 700000, 'description': 'Đối xứng 258885852'},

        # Tài Lộc thêm
        {'account_number': '7202168888168', 'category': 'TAI_LOC', 'price_tier': '1M-3M', 'fee': 1400000, 'description': 'Nhất Lộc Phát x 4 kẹp'},
        {'account_number': '7202789789789', 'category': 'TAI_LOC', 'price_tier': '1M-3M', 'fee': 1600000, 'description': '789 lặp 3 lần - Thất phát cửu'},

        # Hợp tuổi thêm
        {'account_number': '7202200020002', 'category': 'HOP_TUOI', 'price_tier': '1M-3M', 'fee': 1300000, 'description': 'Hợp tuổi 2000 (Canh Thìn)'},
        {'account_number': '7202199219921', 'category': 'HOP_TUOI', 'price_tier': '500K-1M', 'fee': 600000, 'description': 'Hợp tuổi 1992 (Nhâm Thân)'},

        # Phong thủy thêm
        {'account_number': '7202123123123', 'category': 'PHONG_THUY', 'price_tier': '1M-3M', 'fee': 1200000, 'description': 'Nhất nhị tam - Tiến bộ'},
        {'account_number': '7202321321321', 'category': 'PHONG_THUY', 'price_tier': '1M-3M', 'fee': 1100000, 'description': 'Tam nhị nhất - Trụ vững'},

        # Đặc biệt thêm
        {'account_number': '7202168168888', 'category': 'DAC_BIET', 'price_tier': '3M-5M', 'fee': 4000000, 'description': 'Nhất Lộc Phát x 2 + Phát x 4'},
        {'account_number': '7202999999888', 'category': 'DAC_BIET', 'price_tier': '5M-10M', 'fee': 6800000, 'description': 'Cửu x 6 + Phát x 3'},
        {'account_number': '7202777777666', 'category': 'DAC_BIET', 'price_tier': '5M-10M', 'fee': 6200000, 'description': 'Thất x 6 + Lộc x 3'},
    ]

    # Tạo các số đẹp
    for num_data in beautiful_numbers:
        if 'is_available' not in num_data:
            num_data['is_available'] = True
        BeautifulNumber.objects.get_or_create(
            account_number=num_data['account_number'],
            defaults=num_data
        )


def remove_beautiful_numbers(apps, schema_editor):
    """Xóa dữ liệu mẫu khi rollback"""
    BeautifulNumber = apps.get_model('templates_app', 'BeautifulNumber')
    BeautifulNumber.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('templates_app', '0021_merge_20251115_1653'),
    ]

    operations = [
        migrations.RunPython(seed_beautiful_numbers, remove_beautiful_numbers),
    ]
