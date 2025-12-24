import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from tax_payment.models import TaxLocation, TaxSubEntry

print('=== KIỂM TRA DỮ LIỆU TAX PAYMENT ===\n')

print(f'TaxLocation (Cơ quan thu): {TaxLocation.objects.count()} records')
print(f'TaxSubEntry (Tiểu mục): {TaxSubEntry.objects.count()} records')

if TaxLocation.objects.count() == 0:
    print('\n⚠️  CẢNH BÁO: CHƯA CÓ DỮ LIỆU CƠ QUAN THU!')
    print('\nCách import dữ liệu:')
    print('1. Qua Django Admin:')
    print('   - Vào http://localhost:8000/admin/tax_payment/taxlocation/')
    print('   - Nhấn "Import từ Excel"')
    print('   - Upload file CO QUAN THU.xlsx')
    print('\n2. Qua Command Line:')
    print('   python manage.py import_tax_data --locations path/to/CO_QUAN_THU.xlsx')

if TaxSubEntry.objects.count() == 0:
    print('\n⚠️  CẢNH BÁO: CHƯA CÓ DỮ LIỆU TIỂU MỤC!')
    print('\nCách import dữ liệu:')
    print('1. Qua Django Admin:')
    print('   - Vào http://localhost:8000/admin/tax_payment/taxsubentry/')
    print('   - Nhấn "Import từ Excel"')
    print('   - Upload file MA TIEU MUC.xlsx')
    print('\n2. Qua Command Line:')
    print('   python manage.py import_tax_data --subentries path/to/MA_TIEU_MUC.xlsx')

if TaxLocation.objects.count() > 0:
    print('\n=== MẪU DỮ LIỆU CƠ QUAN THU ===')
    for loc in TaxLocation.objects.all()[:5]:
        print(f'\nTỉnh: {loc.tinh}')
        print(f'Cơ quan thuế: {loc.co_quan_thue_group}')
        print(f'Xã/Phường: {loc.xa_phuong}')
        print(f'Mã CQ thu: {loc.ma_co_quan_thu}')

if TaxSubEntry.objects.count() > 0:
    print('\n=== MẪU DỮ LIỆU TIỂU MỤC ===')
    for sub in TaxSubEntry.objects.all()[:5]:
        print(f'\nMã: {sub.ma_tieu_muc}')
        print(f'Tên: {sub.ten_tieu_muc[:50]}...')
