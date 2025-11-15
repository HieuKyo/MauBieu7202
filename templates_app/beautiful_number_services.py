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
    (2, 'NORMAL'): (500_000, 1_000_000),
    (3, 'NORMAL'): (1_000_000, 2_000_000),
    (4, 'NORMAL'): (500_000, 1_000_000),  # Từ ví dụ: 348458484
    (5, 'NORMAL'): (2_000_000, 3_000_000),
    (6, 'NORMAL'): (3_000_000, 5_000_000),  # Từ ví dụ: 223334444
    (7, 'NORMAL'): (5_000_000, 10_000_000),
    (8, 'NORMAL'): (10_000_000, 20_000_000),  # Từ ví dụ: 223344556, 556677889
    (9, 'NORMAL'): (25_000_000, 40_000_000),  # Từ ví dụ: 333444555, 236236236

    (2, 'SPECIAL'): (1_000_000, 2_000_000),
    (3, 'SPECIAL'): (2_000_000, 3_000_000),
    (4, 'SPECIAL'): (1_000_000, 2_000_000),
    (5, 'SPECIAL'): (3_000_000, 5_000_000),
    (6, 'SPECIAL'): (5_000_000, 10_000_000),
    (7, 'SPECIAL'): (10_000_000, 20_000_000),
    (8, 'SPECIAL'): (25_000_000, 40_000_000),  # Từ ví dụ: 277777777
    (9, 'SPECIAL'): (40_000_000, 80_000_000),  # Từ ví dụ: 888888888 → VAT: 44M-88M
}

VAT_RATE = Decimal('0.1')  # 10% VAT


def apply_vat(amount):
    """Cộng 10% VAT vào số tiền"""
    return int(Decimal(amount) * (1 + VAT_RATE))


def check_uniform_9_digit_structure(digits):
    """
    Bước 1: Kiểm tra cấu trúc 9 số đồng nhất

    Các mẫu đồng nhất:
    1. Sảnh lặp tam (3-3-3): AAA-BBB-CCC (ví dụ: 333444555, 888999777)
    2. Lặp tam (3-3-3): ABC-ABC-ABC (ví dụ: 236236236)

    Args:
        digits: 9 số cần kiểm tra (string)

    Returns:
        dict hoặc None: {
            'pattern': str,
            'quantity': 9,
            'type': 'NORMAL',
            'description': str
        }
    """
    if len(digits) != 9:
        return None

    # Mẫu 1: Sảnh lặp tam AAA-BBB-CCC (3 nhóm, mỗi nhóm 3 số giống nhau)
    # Ví dụ: 333444555, 888999777
    part1 = digits[0:3]
    part2 = digits[3:6]
    part3 = digits[6:9]

    if (part1[0] == part1[1] == part1[2] and
        part2[0] == part2[1] == part2[2] and
        part3[0] == part3[1] == part3[2] and
        len(set([part1[0], part2[0], part3[0]])) == 3):  # 3 số khác nhau
        return {
            'pattern': 'UNIFORM_9_TRIPLE_HALL',
            'quantity': 9,
            'type': 'NORMAL',
            'description': f'Sảnh lặp tam: {part1[0]*3}-{part2[0]*3}-{part3[0]*3}'
        }

    # Mẫu 2: Lặp tam ABC-ABC-ABC (3 nhóm giống hệt nhau)
    # Ví dụ: 236236236
    if part1 == part2 == part3:
        return {
            'pattern': 'UNIFORM_9_TRIPLE_REPEAT',
            'quantity': 9,
            'type': 'NORMAL',
            'description': f'Lặp tam: {part1}-{part2}-{part3}'
        }

    return None


def scan_sub_patterns(digits):
    """
    Bước 2: Quét tất cả các mẫu con trong 9 số

    Tìm các mẫu:
    1. Lặp liên tiếp: 2-8 số giống nhau liên tiếp (222, 4444, 77777777...)
    2. Sảnh kép: Các cặp số liên tiếp (223344, 22334455...)
    3. Lặp rải rác: Số lặp không liên tiếp (8484, 484...)

    Args:
        digits: 9 số cần quét (string)

    Returns:
        list: Danh sách các mẫu tìm được, mỗi mẫu là dict:
        {
            'pattern': str,
            'quantity': int,
            'type': 'NORMAL' hoặc 'SPECIAL',
            'description': str,
            'position': tuple (start, end)
        }
    """
    patterns = []

    # 1. Tìm các chuỗi lặp liên tiếp (2-9 số)
    for length in range(9, 1, -1):  # Từ 9 xuống 2
        for i in range(len(digits) - length + 1):
            substring = digits[i:i+length]
            # Kiểm tra tất cả ký tự giống nhau
            if len(set(substring)) == 1:
                # Kiểm tra xem vị trí này đã được phủ bởi mẫu dài hơn chưa
                is_covered = False
                for p in patterns:
                    if p['position'][0] <= i and p['position'][1] >= i + length:
                        is_covered = True
                        break

                if not is_covered:
                    # Xác định loại: 8+ số lặp là đặc biệt, còn lại là thường
                    pattern_type = 'SPECIAL' if length >= 8 else 'NORMAL'
                    patterns.append({
                        'pattern': f'REPEAT_{length}',
                        'quantity': length,
                        'type': pattern_type,
                        'description': f'Lặp {length} số "{substring[0]}"',
                        'position': (i, i + length)
                    })

    # 2. Tìm sảnh kép (cặp số liên tiếp)
    # Ví dụ: 223344 (3 cặp), 22334455 (4 cặp)
    i = 0
    hall_start = -1
    hall_pairs = 0

    while i < len(digits) - 1:
        # Kiểm tra có cặp số giống nhau không
        if digits[i] == digits[i+1]:
            if hall_start == -1:
                hall_start = i
            hall_pairs += 1
            i += 2
        else:
            # Kết thúc chuỗi sảnh kép
            if hall_pairs >= 2:  # Tối thiểu 2 cặp (4 số)
                hall_length = hall_pairs * 2
                # Kiểm tra không bị phủ bởi mẫu lặp
                is_covered = False
                for p in patterns:
                    if p['position'][0] <= hall_start and p['position'][1] >= hall_start + hall_length:
                        is_covered = True
                        break

                if not is_covered:
                    patterns.append({
                        'pattern': f'DOUBLE_HALL_{hall_length}',
                        'quantity': hall_length,
                        'type': 'NORMAL',
                        'description': f'Sảnh kép {hall_pairs} cặp ({hall_length} số)',
                        'position': (hall_start, hall_start + hall_length)
                    })

            hall_start = -1
            hall_pairs = 0
            i += 1

    # Xử lý trường hợp sảnh kép kết thúc ở cuối
    if hall_pairs >= 2:
        hall_length = hall_pairs * 2
        is_covered = False
        for p in patterns:
            if p['position'][0] <= hall_start and p['position'][1] >= hall_start + hall_length:
                is_covered = True
                break

        if not is_covered:
            patterns.append({
                'pattern': f'DOUBLE_HALL_{hall_length}',
                'quantity': hall_length,
                'type': 'NORMAL',
                'description': f'Sảnh kép {hall_pairs} cặp ({hall_length} số)',
                'position': (hall_start, hall_start + hall_length)
            })

    # 3. Tìm lặp rải rác (ví dụ: 8484, 484)
    # Tìm các mẫu lặp 2 chữ số: ABAB, hoặc ABA
    for length in range(4, 2, -1):  # 4 hoặc 3
        for i in range(len(digits) - length + 1):
            substring = digits[i:i+length]

            # Kiểm tra ABAB (4 số)
            if length == 4 and substring[0] == substring[2] and substring[1] == substring[3]:
                # Kiểm tra không bị phủ
                is_covered = False
                for p in patterns:
                    if p['position'][0] <= i and p['position'][1] >= i + length:
                        is_covered = True
                        break

                if not is_covered:
                    patterns.append({
                        'pattern': 'SCATTERED_4',
                        'quantity': 4,
                        'type': 'NORMAL',
                        'description': f'Lặp rải rác: {substring}',
                        'position': (i, i + length)
                    })

            # Kiểm tra ABA (3 số)
            if length == 3 and substring[0] == substring[2]:
                is_covered = False
                for p in patterns:
                    if p['position'][0] <= i and p['position'][1] >= i + length:
                        is_covered = True
                        break

                if not is_covered:
                    patterns.append({
                        'pattern': 'SCATTERED_3',
                        'quantity': 3,
                        'type': 'NORMAL',
                        'description': f'Lặp rải rác: {substring}',
                        'position': (i, i + length)
                    })

    # Sắp xếp patterns theo số lượng giảm dần
    patterns.sort(key=lambda x: x['quantity'], reverse=True)

    return patterns


def get_highest_fee_pattern(patterns):
    """
    Chọn mẫu có mức phí cao nhất

    Args:
        patterns: Danh sách các mẫu tìm được

    Returns:
        dict: Mẫu có phí cao nhất
    """
    if not patterns:
        return None

    highest_pattern = None
    highest_fee = 0

    for pattern in patterns:
        key = (pattern['quantity'], pattern['type'])
        if key in FEE_TABLE:
            fee_min, fee_max = FEE_TABLE[key]
            # So sánh theo phí tối đa
            if fee_max > highest_fee:
                highest_fee = fee_max
                highest_pattern = pattern

    return highest_pattern


def analyze_account_number(account_number):
    """
    Phân tích số tài khoản Agribank Giá Rai để xác định số lượng và loại số đẹp.

    Logic mới (2 bước):
    1. Kiểm tra cấu trúc 9 số đồng nhất (Sảnh lặp tam, Lặp tam)
    2. Nếu không, quét mẫu con và chọn phí cao nhất

    Format: 7202XXXXXXXXX (13 số)
    - 4 số đầu: 7202 (cố định cho Agribank Giá Rai)
    - 9 số sau: Phần khách hàng chọn (phân tích số đẹp)

    Args:
        account_number: Số tài khoản cần phân tích (string hoặc int)

    Returns:
        dict: {
            'quantity': int,  # Số lượng số đẹp
            'is_special': bool,  # True nếu thuộc loại đặc biệt
            'pattern_type': str,  # Loại mẫu
            'description': str,  # Mô tả chi tiết
            'full_account': str,  # Số tài khoản đầy đủ (13 số)
            'selectable_part': str,  # 9 số khách hàng chọn
            'fee_min_base': int,  # Phí tối thiểu (chưa VAT)
            'fee_max_base': int,  # Phí tối đa (chưa VAT)
            'fee_min_vat': int,  # Phí tối thiểu (có VAT)
            'fee_max_vat': int,  # Phí tối đa (có VAT)
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
    uniform_pattern = check_uniform_9_digit_structure(selectable_part)

    if uniform_pattern:
        # Tìm thấy cấu trúc đồng nhất → 9 số thường
        key = (9, 'NORMAL')
        fee_min_base, fee_max_base = FEE_TABLE[key]

        return {
            'quantity': 9,
            'is_special': False,
            'pattern_type': uniform_pattern['pattern'],
            'description': uniform_pattern['description'],
            'full_account': digits,
            'selectable_part': selectable_part,
            'fee_min_base': fee_min_base,
            'fee_max_base': fee_max_base,
            'fee_min_vat': apply_vat(fee_min_base),
            'fee_max_vat': apply_vat(fee_max_base),
        }

    # ========== BƯỚC 2: QUÉT MẪU CON ==========
    sub_patterns = scan_sub_patterns(selectable_part)

    if sub_patterns:
        # Chọn mẫu có phí cao nhất
        best_pattern = get_highest_fee_pattern(sub_patterns)

        if best_pattern:
            key = (best_pattern['quantity'], best_pattern['type'])
            fee_min_base, fee_max_base = FEE_TABLE.get(key, (0, 0))

            return {
                'quantity': best_pattern['quantity'],
                'is_special': best_pattern['type'] == 'SPECIAL',
                'pattern_type': best_pattern['pattern'],
                'description': best_pattern['description'],
                'full_account': digits,
                'selectable_part': selectable_part,
                'fee_min_base': fee_min_base,
                'fee_max_base': fee_max_base,
                'fee_min_vat': apply_vat(fee_min_base),
                'fee_max_vat': apply_vat(fee_max_base),
            }

    # Không tìm thấy mẫu nào → Số thường tối thiểu (2 số)
    key = (2, 'NORMAL')
    fee_min_base, fee_max_base = FEE_TABLE[key]

    return {
        'quantity': 2,
        'is_special': False,
        'pattern_type': 'NORMAL_MIN',
        'description': 'Số thường (tối thiểu)',
        'full_account': digits,
        'selectable_part': selectable_part,
        'fee_min_base': fee_min_base,
        'fee_max_base': fee_max_base,
        'fee_min_vat': apply_vat(fee_min_base),
        'fee_max_vat': apply_vat(fee_max_base),
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
