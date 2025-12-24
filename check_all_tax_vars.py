import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from templates_app.models import Variable

expected_vars = [
    'ten_nguoi_nop_thue',
    'ma_so_thue',
    'dia_chi_nguoi_nop_thue',
    'ngay_lap_bang_ke',
    'tinh_thanh_pho',
    'co_quan_thue',
    'xa_phuong_nop_thue',
    'ma_co_quan_thu',
    'ten_co_quan_thu',
    'ma_dia_ban',
    'kho_bac_nha_nuoc',
    'tong_so_tien_nop_thue',
    'ma_tieu_muc_thue',
    'noi_dung_tieu_muc',
    'so_tien_tieu_muc',
]

print('=== KIỂM TRA 15 BIẾN TAX PAYMENT ===\n')

found = 0
missing = []

for var_name in expected_vars:
    exists = Variable.objects.filter(name=var_name).exists()
    if exists:
        v = Variable.objects.get(name=var_name)
        print(f'✓ {var_name}: {v.label}')
        found += 1
    else:
        print(f'✗ {var_name}: THIẾU')
        missing.append(var_name)

print(f'\n=== KẾT QUẢ ===')
print(f'Tìm thấy: {found}/15')
print(f'Thiếu: {len(missing)}/15')

if missing:
    print(f'\nCác biến bị thiếu: {", ".join(missing)}')
    print('\nChạy lệnh: python manage.py add_tax_variables')
