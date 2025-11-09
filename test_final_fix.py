#!/usr/bin/env python
"""
Test final fix: Update cả w14:checked, text content, và font
"""

import sys
from pathlib import Path

# Add project root to path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from templates_app.utils import JinjaWordTemplateProcessor

def test_final_checkbox_fix(template_path, output_path):
    """Test update checkbox với fix mới nhất"""

    print(f"\n{'='*80}")
    print(f"TESTING FINAL FIX")
    print(f"{'='*80}\n")

    # Test data with various checkboxes
    test_data = {
        # Gender - Nam should be checked, Nữ unchecked
        'gioi_tinh_nam': '☑',
        'gioi_tinh_nu': '☐',

        # Card type - Visa should be checked
        'loai_the_visa': '☑',
        'loai_the_mastercard': '☐',
        'loai_the_jcb': '☐',

        # Currency - VND should be checked
        'loai_tien_vnd': '☑',
        'loai_tien_usd': '☐',
        'loai_tien_eur': '☐',

        # Services - Some checked, some unchecked
        'dv_sms_banking': '☑',
        'dv_e_mobile': '☑',
        'dv_bankplus': '☑',
        'dv_e_commerce': '☐',
        'dv_soft_otp': '☐',
        'dv_smart_otp': '☑',

        # Other fields (for textboxes)
        'ho_ten': 'NGUYỄN VĂN A',
        'so_cmnd': '001234567890',
    }

    print("Test data:")
    checked_count = sum(1 for v in test_data.values() if v == '☑')
    unchecked_count = sum(1 for v in test_data.values() if v == '☐')
    print(f"  Checked (☑): {checked_count}")
    print(f"  Unchecked (☐): {unchecked_count}")
    print()

    # Render with processor
    print("Rendering template...")
    processor = JinjaWordTemplateProcessor(template_path)
    processor.render(test_data)
    processor.save(output_path)

    print(f"\n✓ Saved to: {output_path}")
    print("\n" + "="*80)
    print("VERIFICATION STEPS:")
    print("="*80)
    print(f"1. Open: {output_path}")
    print("2. Check these checkboxes:")
    print("   ✓ Nam (should be CHECKED with Wingdings 2 'R')")
    print("   ☐ Nữ (should be UNCHECKED)")
    print("   ✓ Visa (should be CHECKED)")
    print("   ✓ VND (should be CHECKED)")
    print("   ✓ SMS Banking, E-Mobile, Agribank Plus, Smart OTP (CHECKED)")
    print("   ☐ E-Commerce, Soft OTP (UNCHECKED)")
    print()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python test_final_fix.py <template.docx> <output.docx>")
        print("\nExample:")
        print("  python test_final_fix.py C:\\Users\\hoang\\motkmoi.docx C:\\Users\\hoang\\output_fixed.docx")
        sys.exit(1)

    template_path = sys.argv[1]
    output_path = sys.argv[2]

    test_final_checkbox_fix(template_path, output_path)
