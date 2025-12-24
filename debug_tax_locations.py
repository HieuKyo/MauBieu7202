import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from tax_payment.models import TaxLocation

print('=== KIỂM TRA DỮ LIỆU CƠ QUAN THU ===\n')

# Kiểm tra Cà Mau
ca_mau = TaxLocation.objects.filter(tinh='Cà Mau')
print(f'Tổng số records cho Cà Mau: {ca_mau.count()}\n')

# Nhóm theo cơ quan thuế
co_quan_list = ca_mau.values_list('co_quan_thue_group', flat=True).distinct()
print(f'Các cơ quan thuế ở Cà Mau ({len(co_quan_list)}):')
for i, cq in enumerate(co_quan_list, 1):
    count = ca_mau.filter(co_quan_thue_group=cq).count()
    print(f'  {i}. "{cq}" - {count} xã/phường')

print('\n=== CHI TIẾT THUẾ CƠ SỞ 1 ===')
cs1 = ca_mau.filter(co_quan_thue_group__icontains='cơ sở 1')
if cs1.exists():
    print(f'Tìm thấy: {cs1.count()} records')
    print(f'Tên chính xác: "{cs1.first().co_quan_thue_group}"')
    for loc in cs1[:3]:
        print(f'  - {loc.xa_phuong}')
else:
    print('Không tìm thấy!')

print('\n=== CHI TIẾT THUẾ CƠ SỞ 7 ===')
cs7 = ca_mau.filter(co_quan_thue_group__icontains='cơ sở 7')
if cs7.exists():
    print(f'Tìm thấy: {cs7.count()} records')
    print(f'Tên chính xác: "{cs7.first().co_quan_thue_group}"')
    for loc in cs7[:3]:
        print(f'  - {loc.xa_phuong}')
else:
    print('Không tìm thấy!')

print('\n=== KIỂM TRA KÝ TỰ ĐẶC BIỆT ===')
# Kiểm tra có khoảng trắng thừa không
for cq in co_quan_list[:5]:
    has_extra_space = cq != cq.strip()
    has_multiple_spaces = '  ' in cq
    print(f'"{cq}"')
    print(f'  - Length: {len(cq)}')
    print(f'  - Extra spaces: {has_extra_space or has_multiple_spaces}')
    if has_extra_space or has_multiple_spaces:
        print(f'  - Cleaned: "{cq.strip()}"')
