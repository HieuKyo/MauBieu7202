"""
Script để sửa dữ liệu Customer ID 3 - CMND từ 13 số về 12 số
Chạy: python fix_customer_data.py
"""
import os
import sys
import django

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from templates_app.models import Customer
from datetime import date

customer_id = 3

try:
    customer = Customer.objects.get(id=customer_id)

    print("="*60)
    print(f"TRƯỚC KHI SỬA - Customer ID: {customer_id}")
    print("="*60)
    print(f"  - Họ tên: {customer.ho_ten}")
    print(f"  - CMND/CCCD: {customer.so_cmnd} ({len(customer.so_cmnd)} chữ số)")
    print(f"  - Ngày cấp: {customer.ngay_cap_cmnd}")

    # Sửa từ 13 số về 12 số
    old_cmnd = customer.so_cmnd
    new_cmnd = customer.so_cmnd[:12]  # Lấy 12 số đầu

    customer.so_cmnd = new_cmnd
    customer.save()

    print("\n" + "="*60)
    print("SAU KHI SỬA")
    print("="*60)
    print(f"  - CMND/CCCD cũ: {old_cmnd} ({len(old_cmnd)} chữ số)")
    print(f"  - CMND/CCCD mới: {new_cmnd} ({len(new_cmnd)} chữ số)")

    # Test lại data
    data = customer.get_data_dict()
    print(f"\n✅ Checkbox CMND/CCCD/Căn cước:")
    print(f"  - cmnd: {data['cmnd']}")
    print(f"  - cccd: {data['cccd']}")
    print(f"  - cancuoc: {data['cancuoc']}")

    print("\n" + "="*60)
    print("✅ SỬA DỮ LIỆU THÀNH CÔNG!")
    print("="*60)
    print(f"\nGhi chú: Với ngày cấp {customer.ngay_cap_cmnd}:")
    if customer.ngay_cap_cmnd <= date(2024, 7, 1):
        print("  → Sẽ check vào ô 'CCCD' (ngày cấp ≤ 01/07/2024)")
    else:
        print("  → Sẽ check vào ô 'Căn cước' (ngày cấp > 01/07/2024)")

except Customer.DoesNotExist:
    print(f"❌ Không tìm thấy Customer với ID: {customer_id}")
except Exception as e:
    print(f"❌ LỖI: {e}")
    import traceback
    traceback.print_exc()
