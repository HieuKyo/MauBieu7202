"""
Beautiful Number Generator - Tạo số đẹp tự động

Hệ thống tạo số đẹp tự động cho Agribank Giá Rai theo các tiêu chí:
- Số lặp (Repeating)
- Số tiến (Progressive)
- Số gánh (Symmetrical)
- Số lặp kép (Double Repeat)
- Số ngẫu nhiên

Sử dụng:
    from templates_app import beautiful_number_generator as bng

    # Tạo 100 số gánh
    ganh_numbers = bng.generate_numbers(bng.gen_so_ganh, 100)

    # Tạo tất cả số lặp có thể
    lap_numbers = bng.generate_numbers(bng.gen_so_lap, 100)
"""

import random


# Định nghĩa tiền tố dựa trên logic V2.5
PREFIX_9_SO = "7202"       # Dành cho loại chọn 9 số (sàn 1.1M)
PREFIX_6_SO = "7202236"    # Dành cho loại chọn 6 số (sàn 550k)


def generate_numbers(generator_func, num_to_gen):
    """
    Hàm helper để lấy số lượng mong muốn từ generator

    Args:
        generator_func: Hàm generator (gen_so_lap, gen_so_tien, etc.)
        num_to_gen: Số lượng số cần tạo

    Returns:
        List các số tài khoản

    Example:
        numbers = generate_numbers(gen_so_lap, 20)
    """
    numbers = []
    gen = generator_func()
    try:
        for _ in range(num_to_gen):
            numbers.append(next(gen))
    except StopIteration:
        # Hết số (ví dụ: chỉ có 10 số lặp 9)
        pass
    return numbers


# --- CÁC HÀM TẠO SỐ (GENERATORS) ---

def gen_so_lap():
    """
    Tạo số lặp (VD: 888888888, 777777)

    Yields:
        - 10 số lặp 9 chữ số (0-9)
        - 10 số lặp 6 chữ số (0-9)

    Example:
        for num in gen_so_lap():
            print(num)  # 7202888888888, 7202777777777, ...
    """
    # 1. Lặp 9 số (Loại 9-số)
    for i in range(10):
        yield f"{PREFIX_9_SO}{str(i)*9}"

    # 2. Lặp 6 số (Loại 6-số)
    for i in range(10):
        yield f"{PREFIX_6_SO}{str(i)*6}"


def gen_so_tien():
    """
    Tạo số tiến (VD: 123456789, 112233)

    Yields:
        - Số tiến 9 chữ số (012345678, 123456789)
        - Số tiến 6 chữ số (012345, 123456, ..., 456789)
        - Sảnh lặp 6 chữ số (001122, 112233, ..., 778899)

    Example:
        for num in gen_so_tien():
            print(num)  # 7202123456789, 7202236123456, ...
    """
    # 1. Tiến 9 số (Loại 9-số)
    yield f"{PREFIX_9_SO}012345678"
    yield f"{PREFIX_9_SO}123456789"

    # 2. Tiến 6 số (Loại 6-số)
    for i in range(5):  # Bắt đầu từ 012345 đến 456789
        s = "".join([str(i+j) for j in range(6)])
        yield f"{PREFIX_6_SO}{s}"

    # 3. Sảnh lặp (Loại 6-số: 112233)
    for i in range(8):  # Bắt đầu từ 001122 đến 778899
        s = f"{i}{i}{(i+1)}{(i+1)}{(i+2)}{(i+2)}"
        yield f"{PREFIX_6_SO}{s}"


def gen_so_ganh(num_to_gen=100):
    """
    Tạo số gánh/đối xứng (VD: 123454321, 123321)

    Args:
        num_to_gen: Số lượng số cần tạo (mặc định 100)

    Yields:
        - Số gánh 9 chữ số (abcdXdcba)
        - Số gánh 6 chữ số (abccba)

    Example:
        for num in gen_so_ganh(50):
            print(num)  # 7202123454321, 7202236123321, ...
    """
    generated = set()
    while len(generated) < num_to_gen:
        # 1. Gánh 9 số (Loại 9-số: abcdXdcba)
        part1 = str(random.randint(1000, 9999))
        mid = str(random.randint(0, 9))
        s_9 = f"{part1}{mid}{part1[::-1]}"
        generated.add(f"{PREFIX_9_SO}{s_9}")

        # 2. Gánh 6 số (Loại 6-số: abc cba)
        part2 = str(random.randint(100, 999))
        s_6 = f"{part2}{part2[::-1]}"
        generated.add(f"{PREFIX_6_SO}{s_6}")

    for num in generated:
        yield num


def gen_so_lap_kep(num_to_gen=100):
    """
    Tạo số lặp kép (VD: 123123123, 123123)

    Args:
        num_to_gen: Số lượng số cần tạo (mặc định 100)

    Yields:
        - Số lặp kép 9 chữ số (abc-abc-abc)
        - Số lặp kép 6 chữ số (abc-abc, ab-ab-ab)

    Example:
        for num in gen_so_lap_kep(50):
            print(num)  # 7202123123123, 7202236121212, ...
    """
    generated = set()
    while len(generated) < num_to_gen:
        # 1. Lặp kép 9 số (Loại 9-số: abc-abc-abc)
        part1 = str(random.randint(100, 999))
        s_9 = f"{part1}{part1}{part1}"
        generated.add(f"{PREFIX_9_SO}{s_9}")

        # 2. Lặp kép 6 số (Loại 6-số: abc-abc)
        part2 = str(random.randint(100, 999))
        s_6_abc = f"{part2}{part2}"
        generated.add(f"{PREFIX_6_SO}{s_6_abc}")

        # 3. Lặp kép 6 số (Loại 6-số: ab-ab-ab)
        part3 = str(random.randint(10, 99))
        s_6_ab = f"{part3}{part3}{part3}"
        generated.add(f"{PREFIX_6_SO}{s_6_ab}")

    for num in generated:
        yield num


def gen_so_ngau_nhien(num_to_gen=100):
    """
    Tạo số ngẫu nhiên (để lấy phí sàn)

    Args:
        num_to_gen: Số lượng số cần tạo (mặc định 100)

    Yields:
        - Số ngẫu nhiên 9 chữ số (Sàn 1.1M)
        - Số ngẫu nhiên 6 chữ số (Sàn 550k)

    Example:
        for num in gen_so_ngau_nhien(50):
            print(num)  # 7202198273645, 7202236198472, ...
    """
    generated = set()
    while len(generated) < num_to_gen:
        # 1. Ngẫu nhiên 9 số (Sàn 1.1M)
        s_9 = str(random.randint(100_000_000, 999_999_999))
        # Đảm bảo không vô tình trúng mã '236'
        if not s_9.startswith('236'):
            generated.add(f"{PREFIX_9_SO}{s_9}")

        # 2. Ngẫu nhiên 6 số (Sàn 550k)
        s_6 = str(random.randint(100_000, 999_999))
        generated.add(f"{PREFIX_6_SO}{s_6}")

    for num in generated:
        yield num


def gen_so_loc_phat(num_to_gen=100):
    """
    Tạo số Lộc Phát - chứa nhiều số 6 và 8 (số may mắn)

    Args:
        num_to_gen: Số lượng số cần tạo (mặc định 100)

    Yields:
        - Số chứa nhiều 6 và 8 trong 9 chữ số
        - Số chứa nhiều 6 và 8 trong 6 chữ số

    Example:
        for num in gen_so_loc_phat(50):
            print(num)  # 7202688688688, 7202236686868, ...
    """
    generated = set()
    lucky_digits = ['6', '8']

    while len(generated) < num_to_gen:
        # 1. Số 9 chữ số với nhiều 6,8 (ít nhất 5 số 6 hoặc 8)
        count_lucky = random.randint(5, 9)
        count_others = 9 - count_lucky

        digits = []
        for _ in range(count_lucky):
            digits.append(random.choice(lucky_digits))
        for _ in range(count_others):
            digits.append(str(random.randint(0, 9)))

        random.shuffle(digits)
        s_9 = ''.join(digits)
        if not s_9.startswith('236'):
            generated.add(f"{PREFIX_9_SO}{s_9}")

        # 2. Số 6 chữ số với nhiều 6,8 (ít nhất 4 số 6 hoặc 8)
        count_lucky_6 = random.randint(4, 6)
        count_others_6 = 6 - count_lucky_6

        digits_6 = []
        for _ in range(count_lucky_6):
            digits_6.append(random.choice(lucky_digits))
        for _ in range(count_others_6):
            digits_6.append(str(random.randint(0, 9)))

        random.shuffle(digits_6)
        s_6 = ''.join(digits_6)
        generated.add(f"{PREFIX_6_SO}{s_6}")

    for num in generated:
        yield num


def gen_so_phong_thuy(num_to_gen=100):
    """
    Tạo số Phong Thủy - số có ý nghĩa đặc biệt

    Bao gồm:
    - Số chứa 168 (nhất lộc bát)
    - Số chứa 888 (phát phát phát)
    - Số chứa 999 (cửu cửu)
    - Số có tổng chia hết cho 9 (số toàn mỹ)

    Args:
        num_to_gen: Số lượng số cần tạo (mặc định 100)

    Yields:
        Số phong thủy theo các tiêu chí trên

    Example:
        for num in gen_so_phong_thuy(50):
            print(num)  # 7202168888168, 7202236999888, ...
    """
    generated = set()
    special_patterns = ['168', '888', '999', '688', '886', '666', '888']

    while len(generated) < num_to_gen:
        # 1. Số 9 chữ số chứa pattern đặc biệt
        pattern = random.choice(special_patterns)
        remaining = 9 - len(pattern)

        # Tạo các chữ số còn lại
        rest_digits = ''.join([str(random.randint(0, 9)) for _ in range(remaining)])

        # Chèn pattern vào vị trí ngẫu nhiên
        insert_pos = random.randint(0, remaining)
        s_9 = rest_digits[:insert_pos] + pattern + rest_digits[insert_pos:]

        if not s_9.startswith('236'):
            generated.add(f"{PREFIX_9_SO}{s_9}")

        # 2. Số 6 chữ số chứa pattern
        if len(pattern) <= 6:
            remaining_6 = 6 - len(pattern)
            rest_digits_6 = ''.join([str(random.randint(0, 9)) for _ in range(remaining_6)])
            insert_pos_6 = random.randint(0, remaining_6)
            s_6 = rest_digits_6[:insert_pos_6] + pattern + rest_digits_6[insert_pos_6:]
            generated.add(f"{PREFIX_6_SO}{s_6}")

    for num in generated:
        yield num


def gen_so_hop_tuoi(num_to_gen=100):
    """
    Tạo số Hợp Tuổi - số có các chữ số hợp tuổi theo phong thủy

    Sử dụng các con số may mắn: 1, 3, 5, 6, 8, 9

    Args:
        num_to_gen: Số lượng số cần tạo (mặc định 100)

    Yields:
        Số hợp tuổi với các chữ số may mắn

    Example:
        for num in gen_so_hop_tuoi(50):
            print(num)  # 7202138685931, 7202236689135, ...
    """
    generated = set()
    lucky_for_age = ['1', '3', '5', '6', '8', '9']

    while len(generated) < num_to_gen:
        # 1. Số 9 chữ số với các số may mắn
        s_9 = ''.join([random.choice(lucky_for_age) for _ in range(9)])
        if not s_9.startswith('236'):
            generated.add(f"{PREFIX_9_SO}{s_9}")

        # 2. Số 6 chữ số với các số may mắn
        s_6 = ''.join([random.choice(lucky_for_age) for _ in range(6)])
        generated.add(f"{PREFIX_6_SO}{s_6}")

    for num in generated:
        yield num


def gen_so_cao_cap(num_to_gen=50):
    """
    Tạo số cao cấp - có pattern phức tạp để đạt mức giá cao (10M-20M+)

    Bao gồm:
    - Số lặp 7-8 chữ số liên tiếp
    - Số tiến 7-8 chữ số liên tiếp
    - Kết hợp nhiều pattern đẹp

    Args:
        num_to_gen: Số lượng số cần tạo (mặc định 50)

    Yields:
        Số có pattern phức tạp, giá trị cao

    Example:
        for num in gen_so_cao_cap(30):
            print(num)  # 7202888888881, 7202236888888, ...
    """
    generated = set()

    while len(generated) < num_to_gen:
        # 1. Lặp 7-8 số giống nhau trong 9 chữ số
        digit = str(random.randint(0, 9))
        length = random.randint(7, 8)
        remaining = 9 - length

        repeated = digit * length
        rest = ''.join([str(random.randint(0, 9)) for _ in range(remaining)])

        # Đặt phần lặp ở đầu, giữa hoặc cuối
        position = random.choice(['start', 'end'])
        if position == 'start':
            s_9 = repeated + rest
        else:
            s_9 = rest + repeated

        if not s_9.startswith('236'):
            generated.add(f"{PREFIX_9_SO}{s_9}")

        # 2. Lặp 5-6 số trong 6 chữ số
        digit_6 = str(random.randint(0, 9))
        length_6 = random.randint(5, 6)
        remaining_6 = 6 - length_6

        repeated_6 = digit_6 * length_6
        if remaining_6 > 0:
            rest_6 = ''.join([str(random.randint(0, 9)) for _ in range(remaining_6)])
            position_6 = random.choice(['start', 'end'])
            s_6 = repeated_6 + rest_6 if position_6 == 'start' else rest_6 + repeated_6
        else:
            s_6 = repeated_6

        generated.add(f"{PREFIX_6_SO}{s_6}")

    for num in generated:
        yield num


# --- HÀM TIỆN ÍCH BỔ SUNG ---

def generate_all_types(count_per_type=20):
    """
    Tạo tất cả các loại số đẹp

    Args:
        count_per_type: Số lượng mỗi loại (mặc định 20)

    Returns:
        Dict chứa tất cả các loại số:
        {
            'lap': [...],
            'tien': [...],
            'ganh': [...],
            'lap_kep': [...],
            'ngau_nhien': [...],
            'loc_phat': [...],
            'phong_thuy': [...],
            'hop_tuoi': [...],
            'cao_cap': [...]
        }

    Example:
        all_numbers = generate_all_types(50)
        print(f"Số lặp: {len(all_numbers['lap'])}")
    """
    return {
        'lap': generate_numbers(gen_so_lap, count_per_type),
        'tien': generate_numbers(gen_so_tien, count_per_type),
        'ganh': generate_numbers(gen_so_ganh, count_per_type),
        'lap_kep': generate_numbers(gen_so_lap_kep, count_per_type),
        'loc_phat': generate_numbers(gen_so_loc_phat, count_per_type),
        'phong_thuy': generate_numbers(gen_so_phong_thuy, count_per_type),
        'hop_tuoi': generate_numbers(gen_so_hop_tuoi, count_per_type),
        'cao_cap': generate_numbers(gen_so_cao_cap, min(count_per_type, 50)),
        'ngau_nhien': generate_numbers(gen_so_ngau_nhien, count_per_type),
    }


def generate_with_analysis(generator_func, num_to_gen, analyzer=None):
    """
    Tạo số và phân tích phí ngay lập tức

    Args:
        generator_func: Hàm generator
        num_to_gen: Số lượng cần tạo
        analyzer: Hàm phân tích (mặc định là analyze_account_number từ beautiful_number_services)

    Returns:
        List các dict chứa số và phân tích:
        [
            {'number': '7202888888888', 'analysis': {...}},
            ...
        ]

    Example:
        from .beautiful_number_services import analyze_account_number
        analyzed = generate_with_analysis(gen_so_lap, 10, analyze_account_number)
    """
    if analyzer is None:
        # Import lazy để tránh circular import
        from .beautiful_number_services import analyze_account_number
        analyzer = analyze_account_number

    numbers = generate_numbers(generator_func, num_to_gen)
    analyzed_list = []

    for num in numbers:
        analysis = analyzer(num)
        analyzed_list.append({
            'number': num,
            'analysis': analysis
        })

    return analyzed_list


def refresh_all_beautiful_numbers(dry_run=False):
    """
    Tính lại category/price_tier/fee cho toàn bộ BeautifulNumber theo engine tính phí hiện tại.
    Không xóa/thêm bản ghi nào, chỉ cập nhật 3 field trên. Dùng chung cho cả management command
    (refresh_beautiful_numbers) và nút "Cập nhật lại giá" trên trang quản lý số đẹp.

    Trả về dict thống kê: {'total', 'changed_fee', 'changed_tier', 'changed_category', 'updated', 'errors'}
    """
    from .beautiful_number_services import analyze_account_number
    from .models import BeautifulNumber
    from .views import get_price_tier_from_fee

    numbers = list(BeautifulNumber.objects.all())
    stats = {
        'total': len(numbers),
        'changed_fee': 0,
        'changed_tier': 0,
        'changed_category': 0,
        'updated': 0,
        'errors': 0,
    }
    to_update = []

    for number in numbers:
        analysis = analyze_account_number(number.account_number)
        if analysis.get('error'):
            stats['errors'] += 1
            continue

        new_fee = analysis['fee_min_vat']
        new_tier = get_price_tier_from_fee(analysis['fee_max_vat'] or analysis['fee_min_vat'])

        dirty = False
        if int(number.fee) != int(new_fee):
            stats['changed_fee'] += 1
            dirty = True
        if number.price_tier != new_tier:
            stats['changed_tier'] += 1
            dirty = True

        number.fee = new_fee
        number.price_tier = new_tier

        # Chỉ nâng lên DAC_BIET nếu engine xác định là số đặc biệt
        # (không hạ cấp category cũ, vì category còn phản ánh phân loại tiếp thị đã chọn thủ công)
        if analysis['is_special'] and number.category != BeautifulNumber.CATEGORY_DAC_BIET:
            number.category = BeautifulNumber.CATEGORY_DAC_BIET
            stats['changed_category'] += 1
            dirty = True

        if dirty:
            to_update.append(number)

    stats['updated'] = len(to_update)

    if not dry_run and to_update:
        BeautifulNumber.objects.bulk_update(to_update, ['fee', 'price_tier', 'category'], batch_size=500)

    return stats
