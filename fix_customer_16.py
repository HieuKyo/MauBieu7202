"""
Script sửa Customer ID 16 - CMND từ 13 số về 12 số
Chạy: python fix_customer_16.py
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

customer_id = 16

try:
    customer = Customer.objects.get(id=customer_id)

    print("="*60)
    print(f"Customer ID: {customer_id}")
    print("="*60)
    print(f"Họ tên: {customer.ho_ten}")
    print(f"CMND/CCCD cũ: {customer.so_cmnd} ({len(customer.so_cmnd)} chữ số)")

    # Sửa từ 13 về 12 số
    old_cmnd = customer.so_cmnd
    new_cmnd = customer.so_cmnd[:12]  # Lấy 12 số đầu

    customer.so_cmnd = new_cmnd
    customer.save()

    print(f"CMND/CCCD mới: {new_cmnd} ({len(new_cmnd)} chữ số)")
    print("\n✅ Đã sửa thành công!")

except Customer.DoesNotExist:
    print(f"❌ Không tìm thấy Customer ID {customer_id}")
except Exception as e:
    print(f"❌ Lỗi: {e}")
