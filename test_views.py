import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from tax_payment.models import TaxLocation

print('=== TEST CASCADING DROPDOWN LOGIC ===\n')

# Test 1: Get Cơ quan thuế theo Tỉnh
print('Test 1: Get Cơ quan thuế cho Tỉnh = "Cà Mau"')
tinh = 'Cà Mau'
co_quan_list = TaxLocation.objects.filter(tinh=tinh).values_list('co_quan_thue_group', flat=True).distinct()
print(f'Kết quả: {co_quan_list.count()} cơ quan thuế')
for cq in co_quan_list:
    print(f'  - "{cq}"')

# Test 2: Get Xã/Phường theo Tỉnh + Cơ quan thuế (Cơ sở 1)
print('\nTest 2: Get Xã/Phường cho "Thuế cơ sở 1 tỉnh Cà Mau"')
tinh = 'Cà Mau'
co_quan_thue = 'Thuế cơ sở 1 tỉnh Cà Mau'
xa_list = TaxLocation.objects.filter(tinh=tinh, co_quan_thue_group=co_quan_thue).values_list('xa_phuong', flat=True).distinct()
print(f'Kết quả: {xa_list.count()} xã/phường')
for xa in xa_list:
    print(f'  - "{xa}"')

# Test 3: Get Xã/Phường theo Tỉnh + Cơ quan thuế (Cơ sở 7)
print('\nTest 3: Get Xã/Phường cho "Thuế cơ sở 7 tỉnh Cà Mau"')
tinh = 'Cà Mau'
co_quan_thue = 'Thuế cơ sở 7 tỉnh Cà Mau'
xa_list = TaxLocation.objects.filter(tinh=tinh, co_quan_thue_group=co_quan_thue).values_list('xa_phuong', flat=True).distinct()
print(f'Kết quả: {xa_list.count()} xã/phường')
for xa in xa_list:
    print(f'  - "{xa}"')

# Test 4: Get Location Details
print('\nTest 4: Get Location Details cho Xã Phú Mỹ (Cơ sở 7)')
tinh = 'Cà Mau'
co_quan_thue = 'Thuế cơ sở 7 tỉnh Cà Mau'
xa_phuong = 'Xã Phú Mỹ'
try:
    location = TaxLocation.objects.get(tinh=tinh, co_quan_thue_group=co_quan_thue, xa_phuong=xa_phuong)
    print(f'Mã CQ thu: {location.ma_co_quan_thu}')
    print(f'Tên CQ thu: {location.ten_co_quan_thu}')
    print(f'Mã DB: {location.ma_dia_ban}')
    print(f'KBNN: {location.kho_bac}')
except TaxLocation.DoesNotExist:
    print('KHÔNG TÌM THẤY!')
