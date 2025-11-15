#!/usr/bin/env python
"""
Script test logic tính phí số đẹp mới
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from templates_app.beautiful_number_services import analyze_account_number, get_detailed_fee


def test_examples():
    """Test với các ví dụ từ user"""

    test_cases = [
        # (số_tài_khoản, kỳ_vọng_mô_tả, kỳ_vọng_phí_min_vat, kỳ_vọng_phí_max_vat)
        ('7202348458484', 'Lặp rải rác: 8484', 550_000, 1_100_000),  # 4 số thường
        ('7202223334444', 'Sảnh kép', 3_300_000, 5_500_000),  # 6 số thường (333444)
        ('7202223344556', 'Sảnh kép', 11_000_000, 22_000_000),  # 8 số thường (22334455)
        ('7202556677889', 'Sảnh kép', 11_000_000, 22_000_000),  # 8 số thường (55667788)
        ('7202277777777', 'Lặp 8', 27_500_000, 44_000_000),  # 8 số đặc biệt
        ('7202333444555', 'Sảnh lặp tam: 333-444-555', 27_500_000, 44_000_000),  # 9 số thường
        ('7202236236236', 'Lặp tam: 236-236-236', 27_500_000, 44_000_000),  # 9 số thường
        ('7202888999777', 'Sảnh lặp tam', 27_500_000, 44_000_000),  # 9 số thường
    ]

    print("=" * 80)
    print("TEST LOGIC TÍNH PHÍ SỐ ĐẸP MỚI")
    print("=" * 80)
    print()

    for account, expected_desc_part, expected_min, expected_max in test_cases:
        print(f"\n{'─' * 80}")
        print(f"Số tài khoản: {account}")
        print(f"{'─' * 80}")

        # Phân tích
        result = analyze_account_number(account)

        print(f"  Phần chọn (9 số):  {result['selectable_part']}")
        print(f"  Số lượng:          {result['quantity']} số")
        print(f"  Loại:              {'Đặc biệt' if result['is_special'] else 'Thường'}")
        print(f"  Mẫu:               {result['pattern_type']}")
        print(f"  Mô tả:             {result['description']}")
        print()
        print(f"  Phí gốc (PDF):     {result['fee_min_base']:,} - {result['fee_max_base']:,} VNĐ")
        print(f"  Phí cuối (VAT):    {result['fee_min_vat']:,} - {result['fee_max_vat']:,} VNĐ")
        print()

        # Kiểm tra kết quả
        if expected_desc_part.lower() in result['description'].lower():
            print(f"  ✅ Mô tả đúng")
        else:
            print(f"  ❌ Mô tả sai - Kỳ vọng: {expected_desc_part}")

        if result['fee_min_vat'] == expected_min and result['fee_max_vat'] == expected_max:
            print(f"  ✅ Phí đúng")
        else:
            print(f"  ❌ Phí sai - Kỳ vọng: {expected_min:,} - {expected_max:,} VNĐ")

    print(f"\n{'=' * 80}")
    print("KẾT THÚC TEST")
    print("=" * 80)


if __name__ == '__main__':
    test_examples()
