"""
Script test validation CMND/CCCD
Chạy: python test_cmnd_validation.py

Test các trường hợp:
- CMND 9 số: hợp lệ ✓
- CCCD 12 số: hợp lệ ✓
- 10 số: không hợp lệ ✗
- 13 số: không hợp lệ ✗
- Có chữ cái: không hợp lệ ✗
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
from django.core.exceptions import ValidationError
from datetime import date

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_cmnd_validation(so_cmnd, should_pass, test_name):
    """Test validation for a specific CMND/CCCD number"""
    print(f"\n🔍 Test: {test_name}")
    print(f"   Số CMND/CCCD: '{so_cmnd}' ({len(so_cmnd)} ký tự)")

    # Create a test customer
    customer = Customer(
        ho_ten="Test User",
        so_cmnd=so_cmnd,
        ngay_sinh=date(1990, 1, 1),
        ngay_cap_cmnd=date(2020, 1, 1),
    )

    try:
        # Try to validate
        customer.clean()

        # If we get here, validation passed
        if should_pass:
            print_success("PASS - Validation cho phép (đúng)")
            return True
        else:
            print_error("FAIL - Validation cho phép (sai - phải reject)")
            return False

    except ValidationError as e:
        # Validation failed
        error_messages = e.message_dict.get('so_cmnd', [])

        if not should_pass:
            print_success(f"PASS - Validation reject (đúng)")
            print_info(f"Lỗi: {error_messages[0] if error_messages else 'Unknown'}")
            return True
        else:
            print_error(f"FAIL - Validation reject (sai - phải cho phép)")
            print_info(f"Lỗi: {error_messages[0] if error_messages else 'Unknown'}")
            return False

def run_validation_tests():
    """Run all validation tests"""
    print_header("🚀 BẮT ĐẦU TEST CMND/CCCD VALIDATION")

    test_cases = [
        # (số CMND, should_pass, test_name)

        # Valid cases
        ("123456789", True, "CMND 9 số (hợp lệ)"),
        ("012345678", True, "CMND 9 số bắt đầu bằng 0 (hợp lệ)"),
        ("123456789012", True, "CCCD 12 số (hợp lệ)"),
        ("001234567890", True, "CCCD 12 số bắt đầu bằng 00 (hợp lệ)"),

        # Invalid cases
        ("12345", False, "5 số (không hợp lệ)"),
        ("12345678", False, "8 số (không hợp lệ)"),
        ("1234567890", False, "10 số (không hợp lệ)"),
        ("12345678901", False, "11 số (không hợp lệ)"),
        ("1234567890123", False, "13 số (không hợp lệ)"),
        ("123456ABC", False, "9 ký tự có chữ cái (không hợp lệ)"),
        ("12345678901X", False, "12 ký tự có chữ cái (không hợp lệ)"),
        ("123 456 789", False, "9 số có khoảng trắng (không hợp lệ)"),
        ("123-456-789-012", False, "12 số có dấu gạch ngang (không hợp lệ)"),
        ("", False, "Chuỗi rỗng (không hợp lệ)"),
    ]

    results = []

    for so_cmnd, should_pass, test_name in test_cases:
        result = test_cmnd_validation(so_cmnd, should_pass, test_name)
        results.append((test_name, result))

    # Summary
    print_header("📊 KẾT QUẢ TỔNG HỢP")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print("\nChi tiết:")
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print(f"\n{'='*60}")
    print(f"Tổng: {passed}/{total} tests passed")

    if passed == total:
        print_success("🎉 TẤT CẢ VALIDATION TESTS ĐỀU PASS!")
        print_info("CMND/CCCD validation đang hoạt động đúng")
    else:
        print_error(f"⚠️  {total - passed} test(s) thất bại")
        print_info("Cần kiểm tra lại logic validation")

    # Additional info
    print_header("ℹ️  THÔNG TIN VALIDATION")
    print("Quy tắc validation CMND/CCCD:")
    print("  ✓ Chỉ chấp nhận 9 hoặc 12 chữ số")
    print("  ✓ Chỉ được chứa số (0-9)")
    print("  ✗ Không chấp nhận chữ cái")
    print("  ✗ Không chấp nhận ký tự đặc biệt")
    print("  ✗ Không chấp nhận khoảng trắng")
    print("\nĐịnh nghĩa:")
    print("  - CMND cũ: 9 chữ số")
    print("  - CCCD mới: 12 chữ số")
    print("  - Căn cước: 12 chữ số (phân biệt bằng ngày cấp)")

    return passed == total

if __name__ == "__main__":
    try:
        success = run_validation_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_error(f"Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
