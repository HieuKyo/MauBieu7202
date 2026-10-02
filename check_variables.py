import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from templates_app.models import Variable  # noqa: E402

print('=== KIỂM TRA BIẾN TRONG VARIABLE LIBRARY ===\n')
print(f'Tổng số biến: {Variable.objects.count()}\n')

print('Các biến có chứa "thue" hoặc "tax":')
tax_vars = Variable.objects.filter(name__icontains='thue') | Variable.objects.filter(name__icontains='tax')
tax_vars = tax_vars.order_by('name')

if tax_vars.exists():
    for v in tax_vars:
        print(f'  ✓ {v.name}: {v.label}')
else:
    print('  ✗ KHÔNG TÌM THẤY BIẾN NÀO!')
    print('\n  → Cần chạy: python manage.py add_tax_variables')
