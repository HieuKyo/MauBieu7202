"""
Test logic tính phí số đẹp
Chạy bằng: python manage.py shell < test_logic.py
"""

from templates_app.beautiful_number_services import analyze_account_number

test_cases = [
    # (số_tài_khoản, kỳ_vọng_phí_min_vat, kỳ_vọng_phí_max_vat)
    ('7202348458484', 550_000, 1_100_000),  # 4 số thường
    ('7202223334444', 3_300_000, 5_500_000),  # 6 số thường
    ('7202223344556', 11_000_000, 22_000_000),  # 8 số thường
    ('7202556677889', 11_000_000, 22_000_000),  # 8 số thường
    ('7202277777777', 27_500_000, 44_000_000),  # 8 số đặc biệt
    ('7202333444555', 27_500_000, 44_000_000),  # 9 số thường
    ('7202236236236', 27_500_000, 44_000_000),  # 9 số thường
]

print("=" * 80)
print("TEST LOGIC TÍNH PHÍ SỐ ĐẸP MỚI")
print("=" * 80)

for account, expected_min, expected_max in test_cases:
    result = analyze_account_number(account)

    status_fee = "✅" if (result['fee_min_vat'] == expected_min and result['fee_max_vat'] == expected_max) else "❌"

    print(f"\n{account} ({result['selectable_part']})")
    print(f"  {result['quantity']} số - {result['description']}")
    print(f"  Phí: {result['fee_min_vat']:,} - {result['fee_max_vat']:,} VNĐ {status_fee}")

    if status_fee == "❌":
        print(f"  Kỳ vọng: {expected_min:,} - {expected_max:,} VNĐ")

print("\n" + "=" * 80)
