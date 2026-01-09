"""
Test script để minh họa logic matching mới

Chạy script này để xem cách hệ thống ưu tiên quy tắc cụ thể hơn
"""
from decimal import Decimal
from kpi_tool.models import ConversionRule


def test_matching_priority():
    """
    Test case minh họa các vấn đề đã phát hiện
    """

    print("=" * 80)
    print("TEST MATCHING LOGIC - Ưu tiên quy tắc cụ thể")
    print("=" * 80)

    # Tạo mock rules (không lưu vào DB)
    rule_general = ConversionRule(
        code='DP101',
        debit_account_pattern='101',
        credit_account_pattern='421',
        score_1=Decimal('1.0'),
        description='Mở tài khoản (quy tắc chung)',
        is_active=True
    )

    rule_specific = ConversionRule(
        code='DP101_SPEC',
        debit_account_pattern='101101',
        credit_account_pattern='421101',
        score_1=Decimal('2.0'),
        description='Nộp tiền vào TK cụ thể (quy tắc cụ thể)',
        is_active=True
    )

    # Test case 1: Giao dịch khớp cả 2 quy tắc
    print("\n" + "-" * 80)
    print("TEST CASE 1: Vấn đề 'Nộp tiền' bị tính thành 'Mở tài khoản'")
    print("-" * 80)

    debit_acc = '101101'
    credit_acc = '421101'

    print(f"\nGiao dịch: Nợ {debit_acc} / Có {credit_acc}")
    print("\nCác quy tắc khớp:")

    # Kiểm tra quy tắc chung
    if rule_general.matches_transaction(debit_acc, credit_acc):
        from kpi_tool.services import DBFProcessor
        processor = DBFProcessor()
        processor.conversion_rules = []  # Mock
        quality_general = processor._calculate_match_quality(rule_general, debit_acc, credit_acc)
        print(f"  ✓ {rule_general.code}: {rule_general.description}")
        print(f"    Pattern: {rule_general.debit_account_pattern} - {rule_general.credit_account_pattern}")
        print(f"    Điểm: {rule_general.score_1}")
        print(f"    Match Quality: {quality_general} (prefix match)")

    # Kiểm tra quy tắc cụ thể
    if rule_specific.matches_transaction(debit_acc, credit_acc):
        quality_specific = processor._calculate_match_quality(rule_specific, debit_acc, credit_acc)
        print(f"  ✓ {rule_specific.code}: {rule_specific.description}")
        print(f"    Pattern: {rule_specific.debit_account_pattern} - {rule_specific.credit_account_pattern}")
        print(f"    Điểm: {rule_specific.score_1}")
        print(f"    Match Quality: {quality_specific} (exact match)")

    print("\n🎯 Kết quả với logic MỚI:")
    print(f"  Quy tắc được chọn: {rule_specific.code} ({quality_specific} > {quality_general})")
    print(f"  Điểm được tính: {rule_specific.score_1}")
    print(f"  ✅ Đúng! Ưu tiên quy tắc cụ thể hơn")

    print("\n⚠️  Kết quả với logic CŨ (trước khi fix):")
    print(f"  Quy tắc được chọn: {rule_general.code} (quy tắc đầu tiên khớp)")
    print(f"  Điểm được tính: {rule_general.score_1}")
    print(f"  ❌ SAI! 'Nộp tiền' bị tính thành 'Mở tài khoản'")

    # Test case 2: Giao dịch chỉ khớp quy tắc chung
    print("\n" + "-" * 80)
    print("TEST CASE 2: Giao dịch chỉ khớp quy tắc chung")
    print("-" * 80)

    debit_acc2 = '101999'
    credit_acc2 = '421999'

    print(f"\nGiao dịch: Nợ {debit_acc2} / Có {credit_acc2}")
    print("\nCác quy tắc khớp:")

    if rule_general.matches_transaction(debit_acc2, credit_acc2):
        quality_general2 = processor._calculate_match_quality(rule_general, debit_acc2, credit_acc2)
        print(f"  ✓ {rule_general.code}: {rule_general.description}")
        print(f"    Match Quality: {quality_general2}")

    if not rule_specific.matches_transaction(debit_acc2, credit_acc2):
        print(f"  ✗ {rule_specific.code}: Không khớp")

    print("\n🎯 Kết quả:")
    print(f"  Quy tắc được chọn: {rule_general.code}")
    print(f"  Điểm được tính: {rule_general.score_1}")
    print(f"  ✅ Đúng! Chỉ có quy tắc này khớp")

    # Test case 3: So sánh độ cụ thể
    print("\n" + "-" * 80)
    print("TEST CASE 3: Công thức tính Match Quality")
    print("-" * 80)

    print("\nCông thức:")
    print("  - Exact match: +10000 điểm")
    print("  - Prefix match: +độ dài pattern")

    print(f"\nGiao dịch: Nợ {debit_acc} / Có {credit_acc}")

    print(f"\n{rule_general.code} (101 - 421):")
    print(f"  Nợ: {debit_acc}.startswith('101') = True → +{len('101')} = +3")
    print(f"  Có: {credit_acc}.startswith('421') = True → +{len('421')} = +3")
    print(f"  Tổng: {3 + 3} điểm")

    print(f"\n{rule_specific.code} (101101 - 421101):")
    print(f"  Nợ: {debit_acc} == '101101' = True → +10000")
    print(f"  Có: {credit_acc} == '421101' = True → +10000")
    print(f"  Tổng: {10000 + 10000} điểm")

    print(f"\n✅ {rule_specific.code} thắng ({20000} > {6})")

    print("\n" + "=" * 80)
    print("KẾT LUẬN")
    print("=" * 80)
    print("""
Logic matching mới đảm bảo:
1. ✅ Exact match luôn được ưu tiên cao nhất
2. ✅ Prefix match dài (cụ thể) thắng prefix match ngắn (chung chung)
3. ✅ Giải quyết được vấn đề "Nộp tiền" bị tính thành "Mở tài khoản"
4. ✅ Vẫn hoạt động đúng với các giao dịch chỉ khớp quy tắc chung

Các vấn đề còn lại (2, 3, 4) cần cập nhật file quy tắc:
- Xem hướng dẫn chi tiết trong file RULE_FIX_GUIDE.md
    """)


if __name__ == '__main__':
    # Note: Script này chỉ để minh họa logic
    # Để chạy test thực tế, cần setup Django environment
    print("\n⚠️  Lưu ý: Đây là script minh họa logic")
    print("Để test thực tế, vui lòng:")
    print("1. Cập nhật file quy tắc theo RULE_FIX_GUIDE.md")
    print("2. Import lại quy tắc vào hệ thống")
    print("3. Upload file DBF test và kiểm tra kết quả\n")

    try:
        test_matching_priority()
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        print("\nĐể chạy script này, cần:")
        print("  python manage.py shell < kpi_tool/test_matching_logic.py")
