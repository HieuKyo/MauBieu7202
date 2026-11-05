"""
Beautiful Number Analysis and Fee Lookup Services - Version 3.0

Engine nhận diện mẫu số đẹp + tính phí, port từ bộ luật đầy đủ theo Phụ lục 02
QĐ 479/QĐ-NHNo-TCKT (tham khảo "Tra_Cuu_Phi_TK_So_Dep_Agribank_V2.2.html").

Cấu trúc số tài khoản Agribank Giá Rai: 7202 + 9 số chọn (nhóm X).
- TH1 (chọn đủ 9 số): phân tích cả 9 số + mẫu vắt qua ranh giới mã chi nhánh "7202", sàn phí 1.1M.
- TH2 (chọn 6 số, 9 số bắt đầu bằng mã PGD phụ "236"): chỉ phân tích 6 số cuối, sàn phí 550k.
Mức phí hiển thị đã cộng 10% VAT (giữ nguyên quy ước cũ của chi nhánh).
"""

from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import OnRequestFeeTier


VAT_RATE = Decimal('1.10')


def apply_vat(amount):
    """Cộng 10% VAT vào số tiền"""
    if amount is None:
        return None
    return int(Decimal(amount) * VAT_RATE)


# ========== BẢNG PHÍ CHÍNH THỨC THEO QĐ 479 (chưa VAT), Phụ lục 01 ==========
# count -> {False: (min,max) loại thường, True: (min,max) loại đặc biệt}
OFFICIAL_FEE_TABLE = {
    2: {False: (300_000, 500_000), True: (300_000, 500_000)},
    3: {False: (300_000, 500_000), True: (500_000, 1_000_000)},
    4: {False: (500_000, 1_000_000), True: (1_000_000, 3_000_000)},
    5: {False: (1_000_000, 3_000_000), True: (3_000_000, 5_000_000)},
    6: {False: (3_000_000, 5_000_000), True: (8_000_000, 10_000_000)},
    7: {False: (8_000_000, 10_000_000), True: (10_000_000, 20_000_000)},
    8: {False: (10_000_000, 20_000_000), True: (25_000_000, 40_000_000)},
    9: {False: (25_000_000, 40_000_000), True: (40_000_000, 80_000_000)},
}


def official_fee(count, special):
    """Khung phí (min,max) theo số lượng chữ số đẹp `count` và cờ `special` (loại đặc biệt)"""
    if count >= 10:
        return (100_000_000, None)
    row = OFFICIAL_FEE_TABLE[max(2, min(count, 9))]
    return row[bool(special)]


def _fee_sort_key(pattern):
    """So sánh 2 mẫu: ưu tiên khung phí cao hơn (max rồi min), giống feeKey() trong bản JS"""
    fee_min, fee_max = official_fee(pattern['length'], pattern['special'])
    return ((fee_max if fee_max is not None else 10**12), fee_min)


def _digit_range(start, end):
    return list(range(start, end + 1))


# ========== NHẬN DIỆN MẪU TRÊN 1 DÃY SỐ (9 số cuối, hoặc 6 số với TH2) ==========

LUCKY_PAIRS = [
    ('6', '8', 'Lộc phát (6 & 8)', True),
    ('7', '9', 'Thần tài (7 & 9)', False),
    ('8', '9', 'Trường cửu phát (8 & 9)', False),
    ('6', '9', 'Trường cửu lộc (6 & 9)', False),
]

SPECIAL_TAILS = [
    ('1368', 'Sinh tài lộc phát'),
    ('68368', 'Phát tài phát lộc'),
    ('151618', 'Mỗi năm mỗi lộc mỗi phát'),
    ('4078', 'Đuôi đẹp 4078 (bốn mùa không thất bát)'),
    ('1102', 'Đuôi đẹp 1102 (độc nhất vô nhị)'),
    ('2204', 'Đuôi đẹp 2204'),
]


def detect_patterns(s):
    """
    Nhận diện mọi loại mẫu số đẹp trong dãy số `s` (chuỗi chữ số).
    Trả về list dict {'name', 'length', 'special'} — length dùng làm `count` tra official_fee.
    """
    out = []
    n = len(s)
    if n == 0:
        return out
    d = [int(c) for c in s]

    def add(name, length, special=False):
        out.append({'name': name, 'length': length, 'special': bool(special)})

    # 1. Số lặp (chuỗi cùng chữ số, >=3)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and s[j + 1] == s[i]:
            j += 1
        length = j - i + 1
        if length >= 3:
            end = (j == n - 1)
            add(f'Số lặp {"cuối" if end else "giữa"} {length} số ({s[i:j+1]})', length, end)
        i = j + 1

    # 2. Số tiến liền nhau (tăng dần 1 đơn vị, >=3)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and d[j + 1] == d[j] + 1:
            j += 1
        length = j - i + 1
        if length >= 3:
            end = (j == n - 1)
            add(f'Số tiến liền nhau {"cuối" if end else "giữa"} {length} số ({s[i:j+1]})', length, end)
        i = j + 1

    # 2b. Số tiến chẵn / lẻ (bước 2, >=3)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and d[j + 1] == d[j] + 2:
            j += 1
        length = j - i + 1
        if length >= 3:
            kind = 'chẵn' if d[i] % 2 == 0 else 'lẻ'
            add(f'Số tiến {kind} {length} số ({s[i:j+1]})', length, False)
        i = j + 1

    # 3. Cặp số may mắn: Lộc phát 6-8, Thần tài 7-9, Trường cửu phát 8-9, Trường cửu lộc 6-9
    for a, b, label, is_loc_phat in LUCKY_PAIRS:
        i = 0
        while i < n:
            if s[i] not in (a, b):
                i += 1
                continue
            j = i
            while j + 1 < n and s[j + 1] in (a, b):
                j += 1
            length = j - i + 1
            seg = s[i:j + 1]
            has_both = a in seg and b in seg
            if has_both:
                end = (j == n - 1)
                if end and length >= 2:
                    add(f'{label} cuối {length} số ({seg})', length, is_loc_phat)
                elif not end and length >= 3:
                    add(f'{label} trong dãy {length} số ({seg})', length, False)
            i = j + 1

    # 4. Tam hoa kép aaabbb (a!=b) và 3 cặp tam hoa aaabbbccc
    for i in range(n - 5):
        a, b = s[i], s[i + 3]
        if a != b and s[i + 1] == a and s[i + 2] == a and s[i + 4] == b and s[i + 5] == b:
            end = (i + 5 == n - 1)
            add(f'Tam hoa kép {"cuối" if end else "giữa"} ({s[i:i+6]})', 6, False)
    if n == 9:
        a, b, c = s[0], s[3], s[6]
        if s[1] == a and s[2] == a and s[4] == b and s[5] == b and s[7] == c and s[8] == c and len({a, b, c}) > 1:
            add(f'3 cặp tam hoa ({a}{a}{a}{b}{b}{b}{c}{c}{c})', 9, False)

    # 5. Tài khoản gánh aaaa x aaaa (4 đầu = 4 cuối cùng chữ số, dạng 0000x0000)
    if n == 9:
        q1, q2 = s[0:4], s[5:9]
        if len(set(q1)) == 1 and q1 == q2:
            add(f'Tài khoản gánh ({q1} {s[4]} {q2})', 8, False)

    # 6. Tứ quý kép aaaabbbb (a!=b)
    for i in range(n - 7):
        a, b = s[i], s[i + 4]
        if a != b and s[i:i + 4] == a * 4 and s[i + 4:i + 8] == b * 4:
            add(f'Tứ quý kép ({a * 4}{b * 4})', 8, False)

    # 7. Đối xứng abab / ababab / abababab, lặp 3 số 2/3 lần
    def scan_rep(unit, times, label):
        length = unit * times
        for i in range(0, n - length + 1):
            seg = s[i:i + length]
            u = seg[:unit]
            if len(set(u)) < 2:
                continue
            if all(seg[k * unit:(k + 1) * unit] == u for k in range(1, times)):
                end = (i + length == n)
                add(f'{label} {"cuối" if end else "giữa"} ({seg})', length, False)

    scan_rep(2, 4, '4 cặp abababab')
    scan_rep(2, 3, '3 cặp ababab')
    scan_rep(2, 2, '2 cặp abab')
    scan_rep(3, 3, 'Lặp 3 số 3 lần')
    scan_rep(3, 2, 'Lặp 3 số 2 lần')

    # 8. Số đảo: abba cuối; abccba cuối
    if n >= 4:
        t = s[-4:]
        if t[0] == t[3] and t[1] == t[2] and t[0] != t[1]:
            add(f'Cặp 2 số đảo cuối ({t})', 4, False)
    if n >= 6:
        t = s[-6:]
        if t[0] == t[5] and t[1] == t[4] and t[2] == t[3] and len(set(t)) >= 2 and not (t[0] == t[1] == t[2]):
            add(f'Cặp 3 số đảo cuối ({t})', 6, False)

    # 9. Kép từng đôi một aabbcc... (>=2 cặp, các cặp liền kề khác nhau)
    i = 0
    while i < n - 3:
        pairs = 0
        j = i
        while j + 1 < n and s[j] == s[j + 1] and (pairs == 0 or s[j] != s[j - 2]):
            pairs += 1
            j += 2
        if pairs >= 2:
            seg = s[i:i + pairs * 2]
            if len(set(seg)) >= 2:
                end = (i + pairs * 2 == n)
                add(f'Kép từng đôi một {"cuối" if end else "giữa"} {pairs} cặp ({seg})', pairs * 2, False)
            i = j - 1
        i += 1

    # 10. Cặp 2 số tiến bước 1/2/5/10 (nhóm 2 chữ số: 1213, 1315, 0510, 1020...)
    for step in (1, 2, 5, 10):
        found = False
        for k in range(4, 1, -1):
            if found:
                break
            length = k * 2
            if length > n:
                continue
            for i in range(n - length, -1, -1):
                if found:
                    break
                seg = s[i:i + length]
                nums = [int(seg[x:x + 2]) for x in range(0, length, 2)]
                ok = all(nums[x] - nums[x - 1] == step for x in range(1, len(nums)))
                if ok and step == 5:
                    ok = all(x % 5 == 0 for x in nums)
                if ok and step == 10:
                    ok = all(x % 10 == 0 for x in nums)
                if ok and len(set(seg)) >= 2:
                    end = (i + length == n)
                    add(f'Cặp {k} số tiến {step} đơn vị {"cuối" if end else "giữa"} ({seg})', length, False)
                    found = True

    # 11. Đuôi đặc biệt
    for tail, label in SPECIAL_TAILS:
        if s.endswith(tail):
            add(f'{label} — đuôi {tail}', len(tail), False)

    return out


# ========== NHẬN DIỆN MẪU VẮT QUA RANH GIỚI MÃ CHI NHÁNH ==========

def detect_combos(branch, suffix):
    """
    Tìm mẫu số đẹp vắt qua ranh giới mã chi nhánh (branch, 4 số) + 9 số chọn (suffix).
    `length` trả về là TỔNG chiều dài (gồm cả phần mã chi nhánh), dùng làm `count`.
    """
    full = branch + suffix
    out = []
    seen = set()

    def push(label, start, end, min_len, special):
        length = end - start + 1
        if length < min_len or start > 3 or end < 4:
            return
        key = (label, start, end)
        if key in seen:
            return
        seen.add(key)
        out.append({'name': f'{label} {length} số ({full[start:end+1]}) — kết hợp mã chi nhánh',
                    'length': length, 'special': bool(special)})

    # 1. Số lặp vắt qua ranh giới (từ 3 số)
    i = 0
    while i < 13:
        j = i
        while j + 1 < 13 and full[j + 1] == full[i]:
            j += 1
        push('Số lặp', i, j, 3, True)
        i = j + 1

    # 2. Số tiến liền nhau vắt qua ranh giới (từ 3 số)
    i = 0
    while i < 13:
        j = i
        while j + 1 < 13 and ord(full[j + 1]) == ord(full[j]) + 1:
            j += 1
        push('Số tiến liền nhau', i, j, 3, True)
        i = j + 1

    # 3. Cặp số may mắn vắt qua ranh giới (từ 2 số, phải chứa cả 2 chữ số)
    for a, b, label, is_loc_phat in LUCKY_PAIRS:
        i = 0
        while i < 13:
            if full[i] not in (a, b):
                i += 1
                continue
            j = i
            while j + 1 < 13 and full[j + 1] in (a, b):
                j += 1
            seg = full[i:j + 1]
            if a in seg and b in seg:
                push(label, i, j, 2, is_loc_phat)
            i = j + 1

    # 4. Cặp 2 số tiến bước 1/2/5/10 vắt qua ranh giới (từ 2 cặp)
    for step in (1, 2, 5, 10):
        found = False
        for k in range(6, 1, -1):
            if found:
                break
            length = 2 * k
            for i in range(0, 13 - length + 1):
                if found:
                    break
                if i > 3 or i + length - 1 < 4:
                    continue
                seg = full[i:i + length]
                nums = [int(seg[x:x + 2]) for x in range(0, length, 2)]
                ok = all(nums[x] - nums[x - 1] == step for x in range(1, len(nums)))
                if ok and step == 5:
                    ok = all(x % 5 == 0 for x in nums)
                if ok and step == 10:
                    ok = all(x % 10 == 0 for x in nums)
                if ok and len(set(seg)) >= 2:
                    push(f'Cặp {k} số tiến {step} đơn vị', i, i + length - 1, 4, False)
                    found = True

    return out


def _best_pattern(patterns, default_length, default_fee):
    """Chọn mẫu có khung phí cao nhất trong `patterns`; so với mức sàn mặc định, lấy cái cao hơn"""
    best_length, best_special, best_name, best_fee = default_length, False, 'Số thường (phí tối thiểu)', default_fee

    if patterns:
        top = max(patterns, key=_fee_sort_key)
        fee = official_fee(top['length'], top['special'])
        if fee[0] > best_fee[0]:
            best_length, best_special, best_name, best_fee = top['length'], top['special'], top['name'], fee

    return best_length, best_special, best_name, best_fee


def analyze_account_number(account_number):
    """
    Phân tích số tài khoản Agribank Giá Rai (loại 13 số / chọn 9 số).
    Phân biệt trường hợp 6-số (sàn 550k) và 9-số (sàn 1.1M).
    """
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

    branch = digits[:4]
    selectable_part = digits[4:]  # 9 số cuối
    BANK_SUB_PREFIX = "236"

    if selectable_part.startswith(BANK_SUB_PREFIX):
        # --- TH2: khách chọn 6 số (sàn 550k) ---
        analysis_part = selectable_part[3:]  # 6 số cuối
        default_fee = (500_000, 1_000_000)
        patterns = detect_patterns(analysis_part)
        length, is_special, description, (fee_min_base, fee_max_base) = _best_pattern(
            patterns, 4, default_fee
        )
        if fee_min_base == default_fee[0] and description == 'Số thường (phí tối thiểu)':
            description = 'Số thường (phí tối thiểu 6 số)'
        quantity = length
    else:
        # --- TH1: khách chọn 9 số (sàn 1.1M) ---
        analysis_part = selectable_part
        default_fee = (1_000_000, 3_000_000)
        patterns = detect_patterns(analysis_part) + detect_combos(branch, analysis_part)
        length, is_special, description, (fee_min_base, fee_max_base) = _best_pattern(
            patterns, 5, default_fee
        )
        if fee_min_base == default_fee[0] and description == 'Số thường (phí tối thiểu)':
            description = 'Số thường (phí tối thiểu 9 số)'
        quantity = length

    return {
        'quantity': quantity,
        'is_special': is_special,
        'pattern_type': 'SPECIAL' if is_special else 'NORMAL',
        'description': description,
        'full_account': digits,
        'selectable_part': selectable_part,
        'fee_min_base': fee_min_base,
        'fee_max_base': fee_max_base,
        'fee_min_vat': apply_vat(fee_min_base),
        'fee_max_vat': apply_vat(fee_max_base),
    }


def get_detailed_fee(account_number):
    """Tra cứu phí theo biểu phí chi tiết (Bảng 1)."""
    analysis = analyze_account_number(account_number)

    if analysis.get('error'):
        return {
            'analysis': analysis, 'fee_tier': None,
            'min_fee': 0, 'max_fee': 0,
            'fee_display': 'Không áp dụng', 'error': analysis['error']
        }

    min_fee = analysis['fee_min_vat']
    max_fee = analysis['fee_max_vat']

    if max_fee:
        fee_display = f"{intcomma(min_fee)} - {intcomma(max_fee)} VNĐ"
    elif min_fee > 0:
        fee_display = f"Từ {intcomma(min_fee)} VNĐ (Thỏa thuận)"
    else:
        fee_display = "Không tính phí"

    return {
        'analysis': analysis, 'fee_tier': None,
        'min_fee': min_fee, 'max_fee': max_fee,
        'fee_display': fee_display, 'error': None
    }


def get_on_request_fee(quantity):
    """Tra cứu phí chọn số theo yêu cầu (Bảng 2)."""
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


def generate_menh_candidates(hop_digits):
    """
    Sinh các dãy 9 số ứng viên (nhóm X) từ các chữ số hợp mệnh `hop_digits`,
    dùng cho tính năng "gợi ý số hợp mệnh theo yêu cầu" — số chưa chắc có sẵn trong kho,
    cần tự kiểm tra IPCAS trước khi cấp cho khách.
    """
    digits = sorted({str(d) for d in hop_digits})
    if not digits:
        return set()

    cands = set()
    for a in digits:
        cands.add(a * 9)

    for a in digits:
        for b in digits:
            if a == b:
                continue
            cands.add(a * 4 + b + a * 4)          # gánh aaaa b aaaa
            cands.add((a + b) * 4 + a)             # ababababa
            cands.add(a * 6 + b * 3)               # aaaaaabbb
            cands.add(a * 3 + b * 6)               # aaabbbbbb
            cands.add(a * 5 + b * 4)               # aaaaabbbb
            cands.add(a * 4 + b * 5)               # aaaabbbbb
            cands.add(a + b * 8)                   # lặp cuối 8
            cands.add(a * 2 + b * 7)               # lặp cuối 7
            cands.add(a * 3 + b * 3 + a * 3)       # tam hoa xen kẽ
            cands.add(a + b + a + b + b * 5)

    for a in digits:
        for b in digits:
            for c in digits:
                if a == b or b == c or a == c:
                    continue
                cands.add(a * 3 + b * 3 + c * 3)   # 3 cặp tam hoa
                cands.add((a + b + c) * 3)         # lặp 3 số 3 lần

    # Số lặp ngắn (3-8 số) ở đầu hoặc cuối dãy + phần đệm không lặp, để phủ đủ các bậc phí thấp/vừa
    filler_pool = '0123456789'

    def filler(exclude_digit, length):
        seq = []
        i = 0
        while len(seq) < length:
            d = filler_pool[i % 10]
            if d != exclude_digit and (not seq or seq[-1] != d):
                seq.append(d)
            i += 1
        return ''.join(seq)

    for a in digits:
        for length in range(3, 9):
            pad = filler(a, 9 - length)
            cands.add(pad + a * length)  # lặp cuối `length` số -> đặc biệt
            cands.add(a * length + pad)  # lặp giữa `length` số -> thường

    return cands
