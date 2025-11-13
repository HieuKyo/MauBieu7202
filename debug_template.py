"""
Script debug để kiểm tra template rendering
Chạy: python debug_template.py
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

from templates_app.models import Template
from django.template.loader import get_template

print("="*60)
print("DEBUG TEMPLATE LOADING")
print("="*60)

# Check all templates
templates = Template.objects.all()
for tpl in templates:
    print(f"\nTemplate ID: {tpl.id}")
    print(f"Tên: {tpl.name}")
    print(f"File: {tpl.file.name if tpl.file else 'N/A'}")
    print(f"Active: {tpl.is_active}")

print("\n" + "="*60)
print("KIỂM TRA DJANGO TEMPLATE FILES")
print("="*60)

# Check if template files exist
template_files = [
    'templates_app/template_form.html',
    'templates_app/print_preview.html',
]

for template_file in template_files:
    try:
        tpl = get_template(template_file)
        print(f"\n✅ {template_file}: Tìm thấy")
        print(f"   Path: {tpl.origin.name if hasattr(tpl, 'origin') else 'Unknown'}")
    except Exception as e:
        print(f"\n❌ {template_file}: KHÔNG tìm thấy")
        print(f"   Error: {e}")

print("\n" + "="*60)
print("KIỂM TRA FILE TEMPLATE_FORM.HTML")
print("="*60)

try:
    tpl = get_template('templates_app/template_form.html')
    template_source = tpl.template.source

    if 'Xem trước' in template_source:
        print("✅ Nút 'Xem trước' CÓ trong template")
    else:
        print("❌ Nút 'Xem trước' KHÔNG có trong template")

    if 'previewDocument' in template_source:
        print("✅ Function 'previewDocument()' CÓ trong template")
    else:
        print("❌ Function 'previewDocument()' KHÔNG có trong template")

except Exception as e:
    print(f"❌ Lỗi: {e}")

print("\n" + "="*60)
print("KIỂM TRA FILE PRINT_PREVIEW.HTML")
print("="*60)

try:
    tpl = get_template('templates_app/print_preview.html')
    template_source = tpl.template.source

    checks = [
        'highlighted-field',
        'Chế độ chỉnh sửa',
        'Lưu thay đổi',
        'toggleEditMode',
        'saveChanges',
    ]

    for check in checks:
        if check in template_source:
            print(f"✅ '{check}' CÓ trong template")
        else:
            print(f"❌ '{check}' KHÔNG có trong template")

except Exception as e:
    print(f"❌ Lỗi: {e}")

print("\n" + "="*60)
print("✅ DEBUG HOÀN TẤT")
print("="*60)
