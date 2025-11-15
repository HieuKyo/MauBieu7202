"""
Beautiful Number Analysis and Fee Lookup Services - Version 2.0

Dịch vụ phân tích số tài khoản đẹp và tra cứu phí theo logic mới:
- Bước 1: Kiểm tra cấu trúc 9 số đồng nhất
- Bước 2: Quét mẫu con và chọn phí cao nhất
- Tất cả giá cộng 10% VAT
"""

from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import DetailedFeeTier, OnRequestFeeTier


# ========== BẢNG PHÍ GỐC (THEO PDF) ==========
# Phí gốc (chưa VAT) theo số lượng và loại
FEE_TABLE = {
    # (số_lượng, loại) -> (phí_min, phí_max)
    # None = Thỏa thuận
    (3, 'SPECIAL'): (500_000, 1_000_000),
    (4, 'NORMAL'): (500_000, 1_000_000),
    (4, 'SPECIAL'): (1_000_000, 3_000_000),
    (5, 'NORMAL'): (1_000_000, 3_000_000),
    (5, 'SPECIAL'): (3_000_000, 5_000_000),
    (6, 'NORMAL'): (3_000_000, 5_000_000),
    (6, 'SPECIAL'): (8_000_000, 10_000_000),
    (7, 'NORMAL'): (8_000_000, 10_000_000),
    (7, 'SPECIAL'): (10_000_000, 20_000_000),
    (8, 'NORMAL'): (10_000_000, 20_000_000),
    (8, 'SPECIAL'): (25_000_000, 40_000_000),
    (9, 'NORMAL'): (25_000_000, 40_000_000),
    (9, 'SPECIAL'): (40_000_000, 80_000_000),
    (10, 'NORMAL'): (100_000_000, None),  # Thỏa thuận
}

VAT_RATE = Decimal('1.10')  # Nhân 1.10 (cộng 10%)


def apply_vat(amount):
    """Cộng 10% VAT vào số tiền"""
    if amount is None:
        return None
    return int(Decimal(amount) * VAT_RATE)


def is_pure_repeat(s):
    """
    Kiểm tra chuỗi có phải lặp thuần túy không (tất cả ký tự giống nhau).
    Ví dụ: '777', '888888'
    """
    if not s:
        return False
    return len(set(s)) == 1


def check_uniform_9_digit_structure(digits):
    """
    Bước 1: Kiểm tra cấu trúc 9 số đồng nhất

    Các mẫu đồng nhất:
    1. Lặp thuần 9 số: 888888888 → (9, SPECIAL)
    2. Sảnh tiến 3-3-3: 333444555 → (9, NORMAL) - 3 nhóm lặp tăng dần
    3. Lặp tam 3-3-3: 236236236 → (9, NORMAL)

    Args:
        digits: 9 số cần kiểm tra (string)

    Returns:
        tuple hoặc None: (quantity, type) hoặc None
    """
    if len(digits) != 9:
        return None

    # 1. Lặp thuần 9 số (888888888)
    if is_pure_repeat(digits):
        return (9, 'SPECIAL', 'Lặp 9 số giống nhau')

    # Chia thành 3 phần
    part1 = digits[0:3]
    part2 = digits[3:6]
    part3 = digits[6:9]

    # 2. Sảnh tiến 3-3-3 (333444555, 888999777)
    # Điều kiện: mỗi phần đều là lặp thuần + tăng dần +1
    if (is_pure_repeat(part1) and
        is_pure_repeat(part2) and
        is_pure_repeat(part3)):

        # Kiểm tra tăng dần
        if (int(part1[0]) + 1 == int(part2[0]) and
            int(part2[0]) + 1 == int(part3[0])):
            return (9, 'NORMAL', f'Sảnh tiến tam: {part1}-{part2}-{part3}')

    # 3. Lặp tam 3-3-3 (236236236)
    if part1 == part2 == part3:
        return (9, 'NORMAL', f'Lặp tam: {part1}-{part2}-{part3}')

    return None


def find_best_sub_pattern(digits):
    """
    Bước 2: Quét tất cả mẫu con (2 đến 8 chữ số) và tìm bậc phí cao nhất.

    Args:
        digits: 9 số cần quét (string)

    Returns:
        tuple hoặc None: (quantity, type, description) hoặc None
    """
    best_fee_min = 0
    best_classification = None
    best_description = None

    # Quét từ 8 xuống 2
    for length in range(8, 1, -1):
        for i in range(len(digits) - length + 1):
            substring = digits[i:i+length]

            # Phân loại: chỉ lặp thuần túy mới là SPECIAL
            if is_pure_repeat(substring):
                fee_type = 'SPECIAL' if length >= 8 else 'NORMAL'
            else:
                fee_type = 'NORMAL'

            # Quy tắc đặc biệt: 2 số luôn là NORMAL
            if length == 2:
                fee_type = 'NORMAL'

            classification = (length, fee_type)
            base_fee = FEE_TABLE.get(classification)

            if base_fee:
                # Chọn mức phí cao hơn (dựa trên phí tối thiểu)
                if base_fee[0] > best_fee_min:
                    best_fee_min = base_fee[0]
                    best_classification = classification

                    # Tạo mô tả
                    if is_pure_repeat(substring):
                        best_description = f'Lặp {length} số "{substring[0]}"'
                    else:
                        best_description = f'Mẫu {length} số: {substring}'

    if best_classification:
        return (best_classification[0], best_classification[1], best_description)

    return None


def analyze_account_number(account_number):
    """
    Phân tích số tài khoản Agribank Giá Rai để xác định số lượng và loại số đẹp.

    Logic mới (2 bước):
    1. Kiểm tra cấu trúc 9 số đồng nhất
    2. Nếu không, quét mẫu con và chọn phí cao nhất

    Format: 7202XXXXXXXXX (13 số)
    - 4 số đầu: 7202 (cố định cho Agribank Giá Rai)
    - 9 số sau: Phần khách hàng chọn (phân tích số đẹp)

    Args:
        account_number: Số tài khoản cần phân tích (string hoặc int)

    Returns:
        dict: {
            'quantity': int,
            'is_special': bool,
            'pattern_type': str,
            'description': str,
            'full_account': str,
            'selectable_part': str,
            'fee_min_base': int,
            'fee_max_base': int or None,
            'fee_min_vat': int,
            'fee_max_vat': int or None,
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
            'pattern_type': 'INVALID',
            'description': f'Số tài khoản phải có 13 số (hiện có {len(digits)} số)',
            'full_account': digits,
            'selectable_part': '',
            'fee_min_base': 0,
            'fee_max_base': 0,
            'fee_min_vat': 0,
            'fee_max_vat': 0,
            'error': 'Số tài khoản Agribank Giá Rai phải có 13 số (7202XXXXXXXXX)'
        }

    # Validate prefix: 4 số đầu phải là 7202
    if not digits.startswith('7202'):
        return {
            'quantity': 0,
            'is_special': False,
            'pattern_type': 'INVALID',
            'description': f'Số tài khoản phải bắt đầu bằng 7202 (hiện tại: {digits[:4]})',
            'full_account': digits,
            'selectable_part': '',
            'fee_min_base': 0,
            'fee_max_base': 0,
            'fee_min_vat': 0,
            'fee_max_vat': 0,
            'error': 'Số tài khoản Agribank Giá Rai phải bắt đầu bằng 7202'
        }

    # Lấy 9 số cuối (phần khách hàng chọn)
    selectable_part = digits[4:]

    # ========== BƯỚC 1: KIỂM TRA CẤU TRÚC 9 SỐ ĐỒNG NHẤT ==========
    uniform_result = check_uniform_9_digit_structure(selectable_part)

    if uniform_result:
        quantity, pattern_type, description = uniform_result
        key = (quantity, pattern_type)
        fee_min_base, fee_max_base = FEE_TABLE.get(key, (0, 0))

        return {
            'quantity': quantity,
            'is_special': pattern_type == 'SPECIAL',
            'pattern_type': pattern_type,
            'description': description,
            'full_account': digits,
            'selectable_part': selectable_part,
            'fee_min_base': fee_min_base,
            'fee_max_base': fee_max_base,
            'fee_min_vat': apply_vat(fee_min_base),
            'fee_max_vat': apply_vat(fee_max_base),
        }

    # ========== BƯỚC 2: QUÉT MẪU CON ==========
    sub_pattern_result = find_best_sub_pattern(selectable_part)

    if sub_pattern_result:
        quantity, pattern_type, description = sub_pattern_result
        key = (quantity, pattern_type)
        fee_min_base, fee_max_base = FEE_TABLE.get(key, (0, 0))

        return {
            'quantity': quantity,
            'is_special': pattern_type == 'SPECIAL',
            'pattern_type': pattern_type,
            'description': description,
            'full_account': digits,
            'selectable_part': selectable_part,
            'fee_min_base': fee_min_base,
            'fee_max_base': fee_max_base,
            'fee_min_vat': apply_vat(fee_min_base),
            'fee_max_vat': apply_vat(fee_max_base),
        }

    # Không tìm thấy mẫu nào → Trả về thông báo
    return {
        'quantity': 0,
        'is_special': False,
        'pattern_type': 'NO_PATTERN',
        'description': 'Không tìm thấy mẫu số đẹp',
        'full_account': digits,
        'selectable_part': selectable_part,
        'fee_min_base': 0,
        'fee_max_base': 0,
        'fee_min_vat': 0,
        'fee_max_vat': 0,
    }


def get_detailed_fee(account_number):
    """
    Tra cứu phí theo biểu phí chi tiết (Bảng 1).

    Args:
        account_number: Số tài khoản cần tra cứu

    Returns:
        dict: {
            'analysis': dict,  # Kết quả phân tích số
            'fee_tier': None,  # Không dùng nữa (để tương thích)
            'min_fee': int,  # Phí tối thiểu (có VAT)
            'max_fee': int,  # Phí tối đa (có VAT)
            'fee_display': str,
            'error': str hoặc None
        }
    """
    # Phân tích số tài khoản
    analysis = analyze_account_number(account_number)

    if analysis.get('error'):
        return {
            'analysis': analysis,
            'fee_tier': None,
            'min_fee': 0,
            'max_fee': 0,
            'fee_display': 'Không áp dụng',
            'error': analysis['error']
        }

    # Lấy phí (đã có VAT)
    min_fee = analysis['fee_min_vat']
    max_fee = analysis['fee_max_vat']

    # Format hiển thị phí
    if max_fee:
        fee_display = f"{intcomma(min_fee)} - {intcomma(max_fee)} VNĐ"
    else:
        fee_display = f"Từ {intcomma(min_fee)} VNĐ (Thỏa thuận)"

    return {
        'analysis': analysis,
        'fee_tier': None,  # Không dùng model nữa
        'min_fee': min_fee,
        'max_fee': max_fee,
        'fee_display': fee_display,
        'error': None
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

        fee_display = f"{intcomma(int(tier.min_fee))} - {intcomma(int(tier.max_fee))} VNĐ"

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
