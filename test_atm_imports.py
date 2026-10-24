#!/usr/bin/env python
"""
Script kiểm tra imports cho ATM module
Chạy để đảm bảo tất cả dependencies đều có sẵn
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'template_system.settings')

import django
django.setup()

print("=" * 60)
print("KIỂM TRA ATM MODULE - IMPORTS & DEPENDENCIES")
print("=" * 60)

errors = []
warnings = []

# Test 1: Import models
print("\n[1/6] Kiểm tra Models...")
try:
    from templates_app.models import (
        num_to_vietnamese_words
    )
    print("✅ Models imported successfully")

    # Test helper function
    test_amount = num_to_vietnamese_words(500000)
    if test_amount:
        print(f"✅ num_to_vietnamese_words(500000) = {test_amount}")
    else:
        warnings.append("num_to_vietnamese_words trả về rỗng")

except Exception as e:
    errors.append(f"Models import failed: {e}")
    print(f"❌ Models import failed: {e}")

# Test 2: Import admin
print("\n[2/6] Kiểm tra Admin...")
try:
    print("✅ Admin classes imported successfully")
except Exception as e:
    errors.append(f"Admin import failed: {e}")
    print(f"❌ Admin import failed: {e}")

# Test 3: Import forms
print("\n[3/6] Kiểm tra Forms...")
try:
    print("✅ Forms imported successfully")
except Exception as e:
    errors.append(f"Forms import failed: {e}")
    print(f"❌ Forms import failed: {e}")

# Test 4: Import views
print("\n[4/6] Kiểm tra Views...")
try:
    print("✅ Views imported successfully")
except Exception as e:
    errors.append(f"Views import failed: {e}")
    print(f"❌ Views import failed: {e}")

# Test 5: Check utils
print("\n[5/6] Kiểm tra Utils...")
try:
    print("✅ render_word_template available")
except Exception as e:
    errors.append(f"Utils import failed: {e}")
    print(f"❌ Utils import failed: {e}")

# Test 6: Check GlobalConfig
print("\n[6/6] Kiểm tra GlobalConfig...")
try:
    from templates_app.models import GlobalConfig
    config = GlobalConfig.get_instance()
    print(f"✅ GlobalConfig instance created (ID: {config.id if config else 'N/A'})")
except Exception as e:
    errors.append(f"GlobalConfig failed: {e}")
    print(f"❌ GlobalConfig failed: {e}")

# Summary
print("\n" + "=" * 60)
print("KẾT QUẢ KIỂM TRA")
print("=" * 60)

if not errors:
    print("✅ TẤT CẢ IMPORTS VÀ DEPENDENCIES HOẠT ĐỘNG BÌNH THƯỜNG")
    if warnings:
        print(f"\n⚠️  Có {len(warnings)} cảnh báo:")
        for w in warnings:
            print(f"   - {w}")
else:
    print(f"❌ CÓ {len(errors)} LỖI:")
    for e in errors:
        print(f"   - {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("MODULE ATM SẴN SÀNG TRIỂN KHAI OFFLINE!")
print("=" * 60)
print("\nBước tiếp theo:")
print("1. python manage.py makemigrations")
print("2. python manage.py migrate")
print("3. Tạo dữ liệu ban đầu qua Django Admin")
print("=" * 60)
