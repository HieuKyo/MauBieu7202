#!/usr/bin/env python3
"""
Script test để kiểm tra Content Control checkbox rendering
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, '/home/user/MauBieu7202')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agribank_project.settings')
django.setup()

from templates_app.utils import JinjaWordTemplateProcessor
from templates_app.models import Customer

def test_checkbox_rendering(template_path):
    """
    Test checkbox rendering với template cụ thể
    """
    print("=" * 80)
    print("TEST CHECKBOX RENDERING")
    print("=" * 80)

    # Lấy customer đầu tiên từ database (hoặc tạo dummy data)
    try:
        customer = Customer.objects.first()
        if customer:
            print(f"\n✅ Using customer: {customer.ho_ten}")
            context = customer.get_data_dict()
        else:
            print("\n⚠️  No customers in database, using dummy data")
            context = {
                'ho_ten': 'Nguyễn Văn A',
                'gioi_tinh': 'Nam',
                'gioi_tinh_nam': '☑',  # Checked
                'gioi_tinh_nu': '☐',   # Unchecked
                'dv_e_mobile': '☑',    # Checked
                'dv_sms_banking': '☐', # Unchecked
            }
    except Exception as e:
        print(f"\n⚠️  Error getting customer: {e}")
        print("Using dummy data instead")
        context = {
            'ho_ten': 'Nguyễn Văn A',
            'gioi_tinh': 'Nam',
            'gioi_tinh_nam': '☑',
            'gioi_tinh_nu': '☐',
            'dv_e_mobile': '☑',
            'dv_sms_banking': '☐',
        }

    print(f"\n📋 Context có {len(context)} biến")
    print(f"   Checkbox variables:")
    for key in ['gioi_tinh_nam', 'gioi_tinh_nu', 'dv_e_mobile', 'dv_sms_banking']:
        if key in context:
            print(f"   - {key}: {repr(context[key])}")
        else:
            print(f"   - {key}: NOT FOUND")

    print(f"\n📄 Template: {template_path}")

    # Check if template exists
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return

    print("\n🔄 Processing template...")
    print("-" * 80)

    try:
        # Process template
        processor = JinjaWordTemplateProcessor(template_path)
        processor.render(context)

        # Save output
        output_path = template_path.replace('.docx', '_output.docx')
        processor.save(output_path)

        print("-" * 80)
        print(f"\n✅ Success! Output saved to: {output_path}")
        print("\nHãy mở file output và kiểm tra checkbox!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Cách dùng: python test_checkbox.py <path_to_template.docx>")
        print("\nVí dụ:")
        print("  python test_checkbox.py media/templates/test_checkbox.docx")
        sys.exit(1)

    template_path = sys.argv[1]
    test_checkbox_rendering(template_path)
