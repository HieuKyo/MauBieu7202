"""
Script test chức năng Print Preview
Chạy: python test_print_preview.py

Prerequisites:
1. Django server đang chạy (python manage.py runserver)
2. Đã có Template và Customer trong database
3. Đã cài requests: pip install requests
"""
import os
import sys
import django
import requests
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')
django.setup()

from templates_app.models import Template, Customer
from django.contrib.auth import get_user_model

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_TEMPLATE_ID = None  # Will auto-detect first template
TEST_CUSTOMER_ID = None  # Will auto-detect first customer

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def test_database_setup():
    """Test 1: Check database has required data"""
    print_header("TEST 1: Kiểm tra dữ liệu trong database")

    global TEST_TEMPLATE_ID, TEST_CUSTOMER_ID

    # Check templates
    templates = Template.objects.all()
    if templates.count() == 0:
        print_error("Không tìm thấy Template nào trong database")
        print_info("Hãy upload ít nhất 1 template file (.docx) trong admin")
        return False

    template = templates.first()
    TEST_TEMPLATE_ID = template.id
    print_success(f"Tìm thấy {templates.count()} template(s)")
    print_info(f"Sử dụng template: '{template.name}' (ID: {template.id})")

    # Check customers
    customers = Customer.objects.all()
    if customers.count() == 0:
        print_error("Không tìm thấy Customer nào trong database")
        print_info("Hãy tạo ít nhất 1 customer trong admin")
        return False

    customer = customers.first()
    TEST_CUSTOMER_ID = customer.id
    print_success(f"Tìm thấy {customers.count()} customer(s)")
    print_info(f"Sử dụng customer: '{customer.ho_ten}' (ID: {customer.id}, CMND: {customer.so_cmnd})")

    return True

def test_template_form_page():
    """Test 2: Check template form page loads"""
    print_header("TEST 2: Kiểm tra trang form template")

    url = f"{BASE_URL}/template/{TEST_TEMPLATE_ID}/form/"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            print_success(f"Trang form tải thành công (Status: {response.status_code})")

            # Check for preview button
            if 'Xem trước' in response.text or 'preview' in response.text.lower():
                print_success("Tìm thấy nút 'Xem trước' trong form")
            else:
                print_error("Không tìm thấy nút 'Xem trước' trong form")
                return False

            return True
        else:
            print_error(f"Trang form không tải được (Status: {response.status_code})")
            return False

    except requests.exceptions.ConnectionError:
        print_error("Không thể kết nối đến server")
        print_info("Hãy chạy: python manage.py runserver")
        return False
    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_print_preview_page():
    """Test 3: Check print preview page loads"""
    print_header("TEST 3: Kiểm tra trang Print Preview")

    # First, create session data by submitting form
    form_url = f"{BASE_URL}/template/{TEST_TEMPLATE_ID}/form/"
    preview_url = f"{BASE_URL}/template/{TEST_TEMPLATE_ID}/preview/"

    try:
        # Start session
        session = requests.Session()

        # Get form page to get CSRF token
        form_response = session.get(form_url, timeout=10)

        # Submit form to create session data (simplified - just pass customer_id)
        form_data = {
            'customer_id': TEST_CUSTOMER_ID,
        }

        # Try to access preview directly (it should auto-create session data)
        preview_response = session.get(preview_url, timeout=10)

        if preview_response.status_code == 200:
            print_success(f"Trang preview tải thành công (Status: {preview_response.status_code})")

            # Check for preview features
            content = preview_response.text

            checks = [
                ('highlighted-field', 'Chức năng highlight fields'),
                ('Chế độ chỉnh sửa', 'Nút chế độ chỉnh sửa'),
                ('Lưu thay đổi', 'Nút lưu thay đổi'),
                ('toggleEditMode', 'JavaScript toggle edit mode'),
                ('saveChanges', 'JavaScript save changes'),
            ]

            for keyword, description in checks:
                if keyword in content:
                    print_success(f"✓ {description}")
                else:
                    print_error(f"✗ {description} - Không tìm thấy '{keyword}'")

            return True
        else:
            print_error(f"Trang preview không tải được (Status: {preview_response.status_code})")
            if preview_response.status_code == 404:
                print_info("Route preview có thể chưa được cấu hình đúng trong urls.py")
            return False

    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_update_preview_endpoint():
    """Test 4: Check update preview endpoint"""
    print_header("TEST 4: Kiểm tra endpoint cập nhật preview")

    update_url = f"{BASE_URL}/template/{TEST_TEMPLATE_ID}/preview/update/"

    try:
        session = requests.Session()

        # Get CSRF token
        form_url = f"{BASE_URL}/template/{TEST_TEMPLATE_ID}/form/"
        session.get(form_url, timeout=10)

        # Try to update data
        test_data = {
            'ho_ten': 'Nguyễn Văn Test',
            'so_cmnd': '123456789012',
        }

        response = session.post(
            update_url,
            json=test_data,
            headers={
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
            },
            timeout=10
        )

        if response.status_code == 200:
            print_success(f"Endpoint update hoạt động (Status: {response.status_code})")

            try:
                json_response = response.json()
                if json_response.get('success'):
                    print_success("API trả về success: true")
                else:
                    print_error(f"API trả về lỗi: {json_response.get('message')}")
                    return False
            except:
                print_error("Response không phải JSON")
                return False

            return True
        else:
            print_error(f"Endpoint update không hoạt động (Status: {response.status_code})")
            return False

    except Exception as e:
        print_error(f"Lỗi: {e}")
        return False

def test_mammoth_installed():
    """Test 5: Check mammoth library is installed"""
    print_header("TEST 5: Kiểm tra thư viện mammoth")

    try:
        import mammoth
        print_success(f"Mammoth đã được cài đặt (version: {mammoth.__version__ if hasattr(mammoth, '__version__') else 'unknown'})")
        return True
    except ImportError:
        print_error("Mammoth chưa được cài đặt")
        print_info("Chạy: pip install mammoth==1.8.0")
        return False

def run_all_tests():
    """Run all tests"""
    print_header("🚀 BẮT ĐẦU TEST PRINT PREVIEW FUNCTIONALITY")
    print_info(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Server: {BASE_URL}")

    tests = [
        ("Database Setup", test_database_setup),
        ("Mammoth Library", test_mammoth_installed),
        ("Template Form Page", test_template_form_page),
        ("Print Preview Page", test_print_preview_page),
        ("Update Preview Endpoint", test_update_preview_endpoint),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))

            # Stop if critical test fails
            if not result and test_name in ["Database Setup", "Mammoth Library"]:
                print_info(f"Dừng testing vì '{test_name}' thất bại (critical test)")
                break

        except Exception as e:
            print_error(f"Exception trong test '{test_name}': {e}")
            results.append((test_name, False))

    # Summary
    print_header("📊 KẾT QUẢ TỔNG HỢP")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTổng: {passed}/{total} tests passed")

    if passed == total:
        print_success("🎉 TẤT CẢ TESTS ĐỀU PASS!")
        print_info("Print Preview functionality đang hoạt động tốt")
    else:
        print_error(f"⚠️  {total - passed} test(s) thất bại")
        print_info("Kiểm tra lại cấu hình và code")

    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test bị gián đoạn bởi user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
