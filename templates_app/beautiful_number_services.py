"""
Beautiful Number Analysis and Fee Lookup Services

Dịch vụ phân tích số tài khoản đẹp và tra cứu phí.
"""

from .models import DetailedFeeTier, OnRequestFeeTier


def analyze_account_number(account_number):
    """
    Phân tích số tài khoản Agribank Giá Rai để xác định số lượng và loại số đẹp.

    Format: 7202XXXXXXXXX (13 số)
    - 4 số đầu: 7202 (cố định cho Agribank Giá Rai)
    - 9 số sau: Phần khách hàng chọn (phân tích số đẹp)

    Logic phân loại:
    - Số lặp cuối: 2+ chữ số giống nhau liên tiếp ở cuối (VD: 123456777)
    - Lộc phát: Có số 6 hoặc 8 (VD: 123456888)
    - Số tiến liền: 3+ số liên tiếp tăng dần (VD: 123456789)

    Args:
        account_number: Số tài khoản cần phân tích (string hoặc int)

    Returns:
        dict: {
            'quantity': int,  # Số lượng số đẹp
            'is_special': bool,  # True nếu thuộc loại đặc biệt
            'patterns': list,  # Danh sách các mẫu tìm thấy
            'description': str,  # Mô tả chi tiết
            'full_account': str,  # Số tài khoản đầy đủ (13 số)
            'selectable_part': str  # 9 số khách hàng chọn
        }
    """
    # Chuẩn hóa số tài khoản về string
    account_str = str(account_number).strip()

    # Loại bỏ ký tự không phải số
    digits = ''.join(c for c in account_str if c.isdigit())

    # Validate format: phải có 13 số
    if len(digits) != 13:
        return {
            'quantity': 0,
            'is_special': False,
            'patterns': [],
            'description': f'Số tài khoản phải có 13 số (hiện có {len(digits)} số)',
            'full_account': digits,
            'selectable_part': '',
            'error': f'Số tài khoản Agribank Giá Rai phải có 13 số (7202XXXXXXXXX)'
        }

    # Validate prefix: 4 số đầu phải là 7202
    if not digits.startswith('7202'):
        return {
            'quantity': 0,
            'is_special': False,
            'patterns': [],
            'description': f'Số tài khoản phải bắt đầu bằng 7202 (hiện tại: {digits[:4]})',
            'full_account': digits,
            'selectable_part': '',
            'error': 'Số tài khoản Agribank Giá Rai phải bắt đầu bằng 7202'
        }

    # Lấy 9 số cuối (phần khách hàng chọn)
    selectable_part = digits[4:]  # Bỏ 7202, lấy 9 số sau

    patterns_found = []
    is_special = False

    # ========== PHÂN TÍCH CÁC MẪU SỐ ĐẸP ==========
    # Chỉ phân tích 9 số khách hàng chọn (bỏ qua 7202)

    # 1. Kiểm tra SỐ LẶP CUỐI
    repeating_count = check_repeating_suffix(selectable_part)
    if repeating_count >= 2:
        patterns_found.append(f"Số lặp cuối ({repeating_count} số '{selectable_part[-1]}')")
        is_special = True

    # 2. Kiểm tra LỘC PHÁT (số 6 và 8)
    loc_phat_count = selectable_part.count('6') + selectable_part.count('8')
    if loc_phat_count > 0:
        patterns_found.append(f"Lộc phát ({selectable_part.count('6')} số 6, {selectable_part.count('8')} số 8)")
        is_special = True

    # 3. Kiểm tra SỐ TIẾN LIỀN NHAU
    consecutive_count = check_consecutive_numbers(selectable_part)
    if consecutive_count >= 3:
        patterns_found.append(f"Số tiến liền ({consecutive_count} số)")
        is_special = True

    # 4. Kiểm tra SỐ ĐỐI XỨNG (bonus pattern)
    if is_palindrome(selectable_part):
        patterns_found.append(f"Số đối xứng")
        is_special = True

    # 5. Kiểm tra SỐ TOÀN LẺ (bonus pattern)
    if all(int(d) % 2 == 1 for d in selectable_part):
        patterns_found.append("Toàn số lẻ")

    # 6. Kiểm tra SỐ TOÀN CHẴN (bonus pattern)
    if all(int(d) % 2 == 0 for d in selectable_part):
        patterns_found.append("Toàn số chẵn")

    # ========== TÍNH SỐ LƯỢNG SỐ ĐẸP ==========
    # Số lượng = tổng các chữ số đặc biệt
    quantity = max(repeating_count, loc_phat_count, consecutive_count, 2)  # Tối thiểu 2

    # ========== TẠO MÔ TẢ ==========
    if not patterns_found:
        description = "Số thường (không phải số đẹp)"
    else:
        description = " + ".join(patterns_found)

    return {
        'quantity': quantity,
        'is_special': is_special,
        'patterns': patterns_found,
        'description': description,
        'full_account': digits,  # 13 số đầy đủ (7202XXXXXXXXX)
        'selectable_part': selectable_part  # 9 số khách hàng chọn
    }


def check_repeating_suffix(digits):
    """
    Kiểm tra số lặp ở cuối (VD: 1234555 -> 3 số 5 lặp)

    Returns:
        int: Số lượng chữ số lặp liên tiếp ở cuối
    """
    if len(digits) < 2:
        return 0

    last_digit = digits[-1]
    count = 1

    for i in range(len(digits) - 2, -1, -1):
        if digits[i] == last_digit:
            count += 1
        else:
            break

    return count


def check_consecutive_numbers(digits):
    """
    Kiểm tra chuỗi số tiến liền nhau dài nhất (VD: 123456 -> 6 số)

    Returns:
        int: Độ dài chuỗi số tiến liền nhau dài nhất
    """
    if len(digits) < 3:
        return 0

    max_length = 1
    current_length = 1

    for i in range(1, len(digits)):
        # Kiểm tra số tiếp theo có bằng số trước + 1 không
        if int(digits[i]) == int(digits[i-1]) + 1:
            current_length += 1
            max_length = max(max_length, current_length)
        else:
            current_length = 1

    return max_length if max_length >= 3 else 0


def is_palindrome(digits):
    """
    Kiểm tra số có đối xứng không (VD: 12321, 12345 4321)

    Returns:
        bool: True nếu đối xứng
    """
    return digits == digits[::-1] and len(digits) >= 3


def get_detailed_fee(account_number):
    """
    Tra cứu phí theo biểu phí chi tiết (Bảng 1).

    Args:
        account_number: Số tài khoản cần tra cứu

    Returns:
        dict: {
            'analysis': dict,  # Kết quả phân tích số
            'fee_tier': DetailedFeeTier hoặc None,
            'min_fee': Decimal,
            'max_fee': Decimal hoặc None,
            'fee_display': str,
            'error': str hoặc None
        }
    """
    # Bước 1: Phân tích số tài khoản
    analysis = analyze_account_number(account_number)

    if analysis['quantity'] == 0:
        return {
            'analysis': analysis,
            'fee_tier': None,
            'min_fee': 0,
            'max_fee': None,
            'fee_display': 'Không áp dụng',
            'error': 'Số tài khoản không hợp lệ'
        }

    # Bước 2: Xác định loại phí
    quantity = analysis['quantity']
    is_special = analysis['is_special']

    # Xử lý trường hợp đặc biệt
    if quantity >= 10:
        quantity = 10
        fee_type = DetailedFeeTier.IS_NORMAL_TYPE
    elif quantity <= 2:
        quantity = 2
        fee_type = DetailedFeeTier.IS_NORMAL_TYPE  # 2 số không có loại đặc biệt
    else:
        fee_type = DetailedFeeTier.IS_SPECIAL_TYPE if is_special else DetailedFeeTier.IS_NORMAL_TYPE

    # Bước 3: Tra cứu bậc phí
    try:
        tier = DetailedFeeTier.objects.get(
            quantity=quantity,
            fee_type=fee_type
        )

        # Format hiển thị phí
        if tier.max_fee:
            fee_display = f"{tier.min_fee:,} - {tier.max_fee:,} VNĐ"
        else:
            fee_display = f"Từ {tier.min_fee:,} VNĐ (Thỏa thuận)"

        return {
            'analysis': analysis,
            'fee_tier': tier,
            'min_fee': tier.min_fee,
            'max_fee': tier.max_fee,
            'fee_display': fee_display,
            'error': None
        }

    except DetailedFeeTier.DoesNotExist:
        return {
            'analysis': analysis,
            'fee_tier': None,
            'min_fee': 0,
            'max_fee': None,
            'fee_display': 'Chưa có biểu phí',
            'error': f'Không tìm thấy bậc phí cho {quantity} số đẹp ({fee_type})'
        }


def get_on_request_fee(quantity):
    """
    Tra cứu phí chọn số theo yêu cầu (Bảng 2).

    Args:
        quantity: Số lượng số đẹp khách hàng muốn chọn

    Returns:
        dict: {
            'fee_tier': OnRequestFeeTier hoặc None,
            'min_fee': Decimal,
            'max_fee': Decimal,
            'fee_display': str,
            'error': str hoặc None
        }
    """
    if not isinstance(quantity, int) or quantity < 2:
        return {
            'fee_tier': None,
            'min_fee': 0,
            'max_fee': 0,
            'fee_display': 'Không áp dụng',
            'error': 'Số lượng phải từ 2 trở lên'
        }

    try:
        # Tìm bậc phí mà số lượng nằm trong khoảng
        tier = OnRequestFeeTier.objects.get(
            min_quantity__lte=quantity,
            max_quantity__gte=quantity
        )

        fee_display = f"{tier.min_fee:,} - {tier.max_fee:,} VNĐ"

        return {
            'fee_tier': tier,
            'min_fee': tier.min_fee,
            'max_fee': tier.max_fee,
            'fee_display': fee_display,
            'error': None
        }

    except OnRequestFeeTier.DoesNotExist:
        return {
            'fee_tier': None,
            'min_fee': 0,
            'max_fee': 0,
            'fee_display': 'Chưa có biểu phí',
            'error': f'Không tìm thấy bậc phí cho {quantity} số đẹp'
        }
