"""
Beautiful Number Analysis and Fee Lookup Services - Version 2.8 (Sửa lỗi Tam hoa & Sảnh tiến)

Dịch vụ phân tích số tài khoản đẹp và tra cứu phí theo logic mới:
- Sửa lỗi 1: Tam hoa (XXX-YYY-ZZZ) phải là (9, NORMAL) 27.5M.
- Sửa lỗi 2: Sảnh tiến (12345) phải là (5, SPECIAL) 3.3M.
- TH1 (Chọn 9 số): 7202 + [9 số] -> Phí sàn 1.1M
- TH2 (Chọn 6 số): 7202 + 236 + [6 số] -> Phí sàn 550k
- Logic tính phí cao nhất vẫn được áp dụng.
"""

from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import OnRequestFeeTier


# ========== BẢNG PHÍ GỐC (THEO PDF) ==========
FEE_TABLE = {
    # (số_lượng, loại) -> (phí_min, phí_max)
    (3, 'SPECIAL'): (500_000, 1_000_000), # Phí sàn 550k
    (4, 'NORMAL'): (500_000, 1_000_000), # Phí sàn 550k
    (4, 'SPECIAL'): (1_000_000, 3_000_000),
    (5, 'NORMAL'): (1_000_000, 3_000_000), # Phí sàn 1.1M (9 số)
    (5, 'SPECIAL'): (3_000_000, 5_000_000), # <<< SẢNH TIẾN 12345 SẼ VÀO ĐÂY (3.3M)
    (6, 'NORMAL'): (3_000_000, 5_000_000),
    (6, 'SPECIAL'): (8_000_000, 10_000_000),
    (7, 'NORMAL'): (8_000_000, 10_000_000),
    (7, 'SPECIAL'): (10_000_000, 20_000_000),
    (8, 'NORMAL'): (10_000_000, 20_000_000),
    (8, 'SPECIAL'): (25_000_000, 40_000_000),
    (9, 'NORMAL'): (25_000_000, 40_000_000), # <<< TAM HOA SẼ VÀO ĐÂY (27.5M)
    (9, 'SPECIAL'): (40_000_000, 80_000_000),
    (10, 'NORMAL'): (100_000_000, None),
}

VAT_RATE = Decimal('1.10')


def apply_vat(amount):
    """Cộng 10% VAT vào số tiền"""
    if amount is None:
        return None
    return int(Decimal(amount) * VAT_RATE)


# ========== CÁC HÀM KIỂM TRA MẪU (V2.7) ==========

def is_pure_repeat(s):
    """Kiểm tra lặp thuần túy (VD: '777')"""
    if not s: return False
    return len(set(s)) == 1

def is_sanh_tien(s):
    """Kiểm tra sảnh tiến liền kề (VD: '2345', '678')"""
    if not s or len(s) < 2: return False
    for i in range(len(s) - 1):
        if int(s[i+1]) != int(s[i]) + 1:
            return False
    return True

def is_sanh_lap(s):
    """Kiểm tra sảnh lặp tăng dần (VD: '223344', '55667788')"""
    if not s or len(s) % 2 != 0 or len(s) < 4: return False
    # Kiểm tra cặp đầu tiên
    if s[0] != s[1]: return False
    # Kiểm tra các cặp tiếp theo
    for i in range(2, len(s), 2):
        # Phải là lặp
        if s[i] != s[i+1]: return False
        # Phải tăng dần
        if int(s[i]) != int(s[i-1]) + 1: return False
    return True

def is_lap_kep(s):
    """Kiểm tra lặp kép (VD: '8484', '112112')"""
    if not s or len(s) % 2 != 0 or len(s) < 4: return False
    half = len(s) // 2
    return s[:half] == s[half:]

# ========== KẾT THÚC HÀM KIỂM TRA ==========


# ========== [START] CẬP NHẬT V2.8 (Sửa lỗi Tam hoa) ==========
def check_uniform_9_digit_structure(digits):
    """
    Bước 1: Kiểm tra cấu trúc 9 số đồng nhất
    """
    if len(digits) != 9:
        return None

    # 1. Lặp thuần 9 số (888888888)
    if is_pure_repeat(digits):
        return (9, 'SPECIAL', 'Lặp 9 số giống nhau')

    part1, part2, part3 = digits[0:3], digits[3:6], digits[6:9]

    # 2. Sảnh tiến (111222333) HOẶC Tam hoa (555666888, 555666555)
    #    Miễn là 3 cụm lặp thuần, đều là (9, NORMAL)
    if (is_pure_repeat(part1) and
        is_pure_repeat(part2) and
        is_pure_repeat(part3)):

        # Kiểm tra tăng dần (để hiển thị mô tả)
        if (int(part1[0]) + 1 == int(part2[0]) and
            int(part2[0]) + 1 == int(part3[0])):
            description = f'Sảnh tiến tam: {part1}-{part2}-{part3}'
        else:
            description = f'Tam hoa (3 cụm): {part1}-{part2}-{part3}'
            
        return (9, 'NORMAL', description) # Trả về (9, NORMAL) cho cả 2 trường hợp

    # 3. Lặp tam 3-3-3 (236236236)
    if part1 == part2 == part3:
        return (9, 'NORMAL', f'Lặp tam: {part1}-{part2}-{part3}')

    return None
# ========== [END] CẬP NHẬT V2.8 (Sửa lỗi Tam hoa) ==========


def find_best_sub_pattern(digits_to_scan):
    """
    Bước 2: Quét tất cả mẫu con HỢP LỆ (2 đến 8 chữ số) và tìm bậc phí cao nhất.
    """
    best_fee_min = 0
    best_classification = None
    best_description = "Không tìm thấy mẫu con"

    max_len = min(8, len(digits_to_scan)) 
    
    for length in range(max_len, 1, -1):
        for i in range(len(digits_to_scan) - length + 1):
            substring = digits_to_scan[i:i+length]
            fee_type = None
            description = ""

            # ========== [START] CẬP NHẬT V2.8 (Sửa lỗi Sảnh tiến) ==========
            
            # 1. Kiểm tra mẫu 'SPECIAL' (Lặp thuần túy)
            if is_pure_repeat(substring):
                fee_type = 'SPECIAL' if length >= 3 else 'NORMAL' # '22' là normal
                description = f'Lặp {length} số "{substring[0]}"'
            
            # 2. Kiểm tra mẫu 'SPECIAL' (Sảnh tiến)
            # "số tiến liền nhau" được xếp vào loại đặc biệt
            elif is_sanh_tien(substring):
                fee_type = 'SPECIAL'
                description = f'Sảnh tiến {length} số: {substring}'

            # 3. Kiểm tra các mẫu 'NORMAL' (Sảnh lặp, Lặp kép)
            elif is_sanh_lap(substring):
                fee_type = 'NORMAL'
                description = f'Sảnh lặp {length} số: {substring}'
            elif is_lap_kep(substring):
                fee_type = 'NORMAL'
                description = f'Lặp kép {length} số: {substring}'
            
            # ========== [END] CẬP NHẬT V2.8 (Sửa lỗi Sảnh tiến) ==========

            # 4. Nếu là mẫu hợp lệ (fee_type != None), tra cứu phí
            if fee_type:
                classification = (length, fee_type)
                base_fee = FEE_TABLE.get(classification)

                if base_fee:
                    # Chọn mức phí cao hơn
                    if base_fee[0] > best_fee_min:
                        best_fee_min = base_fee[0]
                        best_classification = classification
                        best_description = description

    if best_classification:
        return (best_classification[0], best_classification[1], best_description)

    return None


def analyze_account_number(account_number):
    """
    Phân tích số tài khoản Agribank Giá Rai (Loại 13 số / Chọn 9 số).
    Phân biệt trường hợp 6-số (sàn 550k) và 9-số (sàn 1.1M).
    """
    # Chuẩn hóa số tài khoản về string
    account_str = str(account_number).strip()
    digits = ''.join(c for c in account_str if c.isdigit())

    if len(digits) != 13:
        return {
            'quantity': 0, 'is_special': False, 'pattern_type': 'INVALID',
            'description': f'Số tài khoản phải có 13 số (hiện có {len(digits)} số)',
            'full_account': digits, 'selectable_part': '',
            'fee_min_base': 0, 'fee_max_base': 0, 'fee_min_vat': 0, 'fee_max_vat': 0,
            'error': 'Số tài khoản Agribank Giá Rai phải có 13 số (7202XXXXXXXXX)'
        }

    if not digits.startswith('7202'):
        return {
            'quantity': 0, 'is_special': False, 'pattern_type': 'INVALID',
            'description': f'Số tài khoản phải bắt đầu bằng 7202 (hiện tại: {digits[:4]})',
            'full_account': digits, 'selectable_part': '',
            'fee_min_base': 0, 'fee_max_base': 0, 'fee_min_vat': 0, 'fee_max_vat': 0,
            'error': 'Số tài khoản Agribank Giá Rai phải bắt đầu bằng 7202'
        }

    selectable_part = digits[4:] # 9 số cuối
    best_result = {}

    # ========== [START] LOGIC V2.5 (6-số vs 9-số) ==========
    
    BANK_SUB_PREFIX = "236"
    
    if selectable_part.startswith(BANK_SUB_PREFIX):
        # --- TH 2: Khách chọn 6 số (Phí sàn 550k) ---
        analysis_part = selectable_part[3:] # Lấy 6 số cuối
        
        # Phí sàn cho 6-số là 550k (gốc 500k)
        key_default = (4, 'NORMAL') # (3, 'SPECIAL') cũng là 500k
        fee_min_base_default, fee_max_base_default = FEE_TABLE.get(key_default, (500_000, 1_000_000))
        best_result = {
            'quantity': 4, 'is_special': False, 'pattern_type': 'DEFAULT_6_DIGIT',
            'description': 'Số thường (phí tối thiểu 6 số)',
            'fee_min_base': fee_min_base_default, 'fee_max_base': fee_max_base_default
        }

        # Quét mẫu con trong 6 số (ĐÃ SỬA V2.8)
        sub_pattern_result = find_best_sub_pattern(analysis_part) # Chỉ quét 6 số
        if sub_pattern_result:
            quantity, pattern_type, description = sub_pattern_result
            key = (quantity, pattern_type)
            fee_min_base, fee_max_base = FEE_TABLE.get(key, (0, 0))

            # So sánh phí mẫu con với phí sàn 550k
            if fee_min_base > best_result['fee_min_base']:
                best_result = {
                    'quantity': quantity, 'is_special': pattern_type == 'SPECIAL',
                    'pattern_type': pattern_type, 'description': description,
                    'fee_min_base': fee_min_base, 'fee_max_base': fee_max_base
                }
    
    else:
        # --- TH 1: Khách chọn 9 số (Phí sàn 1.1M) ---
        analysis_part = selectable_part # Phân tích tất cả 9 số
        
        # Phí sàn cho 9-số là 1.1M (gốc 1M)
        key_default = (5, 'NORMAL')
        fee_min_base_default, fee_max_base_default = FEE_TABLE.get(key_default, (1_000_000, 3_000_000))
        best_result = {
            'quantity': 5, 'is_special': False, 'pattern_type': 'DEFAULT_9_DIGIT',
            'description': 'Số thường (phí tối thiểu 9 số)',
            'fee_min_base': fee_min_base_default, 'fee_max_base': fee_max_base_default
        }

        # BƯỚC 1: KIỂM TRA 9 SỐ ĐỒNG NHẤT (ĐÃ SỬA V2.8)
        uniform_result = check_uniform_9_digit_structure(analysis_part)
        if uniform_result:
            quantity, pattern_type, description = uniform_result
            key = (quantity, pattern_type)
            fee_min_base, fee_max_base = FEE_TABLE.get(key, (0, 0))
            if fee_min_base > best_result['fee_min_base']:
                best_result = {
                    'quantity': quantity, 'is_special': pattern_type == 'SPECIAL',
                    'pattern_type': pattern_type, 'description': description,
                    'fee_min_base': fee_min_base, 'fee_max_base': fee_max_base
                }

        # BƯỚC 2: QUÉT MẪU CON (trong 9 số) (ĐÃ SỬA V2.8)
        
        # Kiểm tra xem B1 có tìm thấy (9, SPECIAL) 40M không
        is_highest_tier = (uniform_result and uniform_result[0] == 9 and uniform_result[1] == 'SPECIAL')

        if not is_highest_tier:
            sub_pattern_result = find_best_sub_pattern(analysis_part)
            if sub_pattern_result:
                quantity, pattern_type, description = sub_pattern_result
                key = (quantity, pattern_type)
                fee_min_base, fee_max_base = FEE_TABLE.get(key, (0, 0))
                if fee_min_base > best_result['fee_min_base']:
                    best_result = {
                        'quantity': quantity, 'is_special': pattern_type == 'SPECIAL',
                        'pattern_type': pattern_type, 'description': description,
                        'fee_min_base': fee_min_base, 'fee_max_base': fee_max_base
                    }

    # ========== [END] LOGIC MỚI V2.8 ==========

    # Trả về kết quả tốt nhất
    return {
        'quantity': best_result['quantity'],
        'is_special': best_result['is_special'],
        'pattern_type': best_result['pattern_type'],
        'description': best_result['description'],
        'full_account': digits,
        'selectable_part': selectable_part,
        'fee_min_base': best_result['fee_min_base'],
        'fee_max_base': best_result['fee_max_base'],
        'fee_min_vat': apply_vat(best_result['fee_min_base']),
        'fee_max_vat': apply_vat(best_result['fee_max_base']),
    }


def get_detailed_fee(account_number):
    """
    Tra cứu phí theo biểu phí chi tiết (Bảng 1).
    (Giữ nguyên code của bạn)
    """
    analysis = analyze_account_number(account_number)

    if analysis.get('error'):
        return {
            'analysis': analysis, 'fee_tier': None,
            'min_fee': 0, 'max_fee': 0,
            'fee_display': 'Không áp dụng', 'error': analysis['error']
        }

    min_fee = analysis['fee_min_vat']
    max_fee = analysis['fee_max_vat']
    
    # Format hiển thị phí
    if max_fee:
        fee_display = f"{intcomma(min_fee)} - {intcomma(max_fee)} VNĐ"
    elif min_fee > 0:
        fee_display = f"Từ {intcomma(min_fee)} VNĐ (Thỏa thuận)"
    else:
        fee_display = "Không tính phí" # Trường hợp lỗi (không nên xảy ra)

    return {
        'analysis': analysis, 'fee_tier': None,
        'min_fee': min_fee, 'max_fee': max_fee,
        'fee_display': fee_display, 'error': None
    }


def get_on_request_fee(quantity):
    """
    Tra cứu phí chọn số theo yêu cầu (Bảng 2).
    (Giữ nguyên code của bạn)
    """
    if not isinstance(quantity, int) or quantity < 2:
        return {
            'fee_tier': None, 'min_fee': 0, 'max_fee': 0,
            'fee_display': 'Không áp dụng', 'error': 'Số lượng phải từ 2 trở lên'
        }

    try:
        tier = OnRequestFeeTier.objects.get(
            min_quantity__lte=quantity,
            max_quantity__gte=quantity
        )
        fee_display = f"{intcomma(int(tier.min_fee))} - {intcomma(int(tier.max_fee))} VNĐ"
        return {
            'fee_tier': tier, 'min_fee': tier.min_fee,
            'max_fee': tier.max_fee, 'fee_display': fee_display, 'error': None
        }
    except OnRequestFeeTier.DoesNotExist:
        return {
            'fee_tier': None, 'min_fee': 0, 'max_fee': 0,
            'fee_display': 'Chưa có biểu phí',
            'error': f'Không tìm thấy bậc phí cho {quantity} số đẹp'
        }