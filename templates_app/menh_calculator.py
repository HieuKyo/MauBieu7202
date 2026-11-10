"""
Tính mệnh (Can Chi + Nạp âm) theo ngày sinh dương lịch, dùng để tư vấn số tài khoản hợp mệnh.
Thuật toán chuyển đổi dương lịch -> âm lịch: Hồ Ngọc Đức (múi giờ Việt Nam +7).
"""
import math

CAN = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý']
CHI = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']

# 30 cặp Nạp âm, bắt đầu từ Giáp Tý
NAP_AM = [
    ('Hải Trung Kim', 'Kim'), ('Lư Trung Hỏa', 'Hỏa'), ('Đại Lâm Mộc', 'Mộc'), ('Lộ Bàng Thổ', 'Thổ'), ('Kiếm Phong Kim', 'Kim'),
    ('Sơn Đầu Hỏa', 'Hỏa'), ('Giản Hạ Thủy', 'Thủy'), ('Thành Đầu Thổ', 'Thổ'), ('Bạch Lạp Kim', 'Kim'), ('Dương Liễu Mộc', 'Mộc'),
    ('Tuyền Trung Thủy', 'Thủy'), ('Ốc Thượng Thổ', 'Thổ'), ('Tích Lịch Hỏa', 'Hỏa'), ('Tùng Bách Mộc', 'Mộc'), ('Trường Lưu Thủy', 'Thủy'),
    ('Sa Trung Kim', 'Kim'), ('Sơn Hạ Hỏa', 'Hỏa'), ('Bình Địa Mộc', 'Mộc'), ('Bích Thượng Thổ', 'Thổ'), ('Kim Bạch Kim', 'Kim'),
    ('Phú Đăng Hỏa', 'Hỏa'), ('Thiên Hà Thủy', 'Thủy'), ('Đại Trạch Thổ', 'Thổ'), ('Thoa Xuyến Kim', 'Kim'), ('Tang Đố Mộc', 'Mộc'),
    ('Đại Khê Thủy', 'Thủy'), ('Sa Trung Thổ', 'Thổ'), ('Thiên Thượng Hỏa', 'Hỏa'), ('Thạch Lựu Mộc', 'Mộc'), ('Đại Hải Thủy', 'Thủy'),
]

# Ngũ hành chữ số theo Hậu thiên bát quái / Lạc Thư: 1 Khảm-Thủy, 2 Khôn-Thổ, 3 Chấn-Mộc,
# 4 Tốn-Mộc, 5 trung cung-Thổ, 6 Càn-Kim, 7 Đoài-Kim, 8 Cấn-Thổ, 9 Ly-Hỏa, 0 quy về Thủy
HA_DO = {'Thủy': [1, 0], 'Mộc': [3, 4], 'Hỏa': [9], 'Thổ': [2, 5, 8], 'Kim': [6, 7]}
SINH = {'Kim': 'Thủy', 'Thủy': 'Mộc', 'Mộc': 'Hỏa', 'Hỏa': 'Thổ', 'Thổ': 'Kim'}  # A sinh B
KHAC = {'Kim': 'Mộc', 'Mộc': 'Thổ', 'Thổ': 'Thủy', 'Thủy': 'Hỏa', 'Hỏa': 'Kim'}  # A khắc B


def _inv(mapping, target):
    for k, v in mapping.items():
        if v == target:
            return k
    return None


def _jd_from_date(dd, mm, yy):
    a = math.floor((14 - mm) / 12)
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + math.floor((153 * m + 2) / 5) + 365 * y + math.floor(y / 4) - math.floor(y / 100) + math.floor(y / 400) - 32045
    if jd < 2299161:
        jd = dd + math.floor((153 * m + 2) / 5) + 365 * y + math.floor(y / 4) - 32083
    return jd


def _new_moon(k):
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = math.pi / 180
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
    C1 = C1 - 0.4068 * math.sin(Mpr * dr) + 0.0161 * math.sin(dr * 2 * Mpr)
    C1 = C1 - 0.0004 * math.sin(dr * 3 * Mpr)
    C1 = C1 + 0.0104 * math.sin(dr * 2 * F) - 0.0051 * math.sin(dr * (M + Mpr))
    C1 = C1 - 0.0074 * math.sin(dr * (M - Mpr)) + 0.0004 * math.sin(dr * (2 * F + M))
    C1 = C1 - 0.0004 * math.sin(dr * (2 * F - M)) - 0.0006 * math.sin(dr * (2 * F + Mpr))
    C1 = C1 + 0.0010 * math.sin(dr * (2 * F - Mpr)) + 0.0005 * math.sin(dr * (2 * Mpr + M))
    if T < -11:
        deltat = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
    else:
        deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
    return Jd1 + C1 - deltat


def _sun_longitude(jdn):
    T = (jdn - 2451545.0) / 36525
    T2 = T * T
    dr = math.pi / 180
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    DL = DL + (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(dr * 3 * M)
    L = (L0 + DL) * dr
    L = L - math.pi * 2 * math.floor(L / (math.pi * 2))
    return L


def _get_new_moon_day(k, tz):
    return math.floor(_new_moon(k) + 0.5 + tz / 24)


def _get_sun_longitude(day_number, tz):
    return math.floor(_sun_longitude(day_number - 0.5 - tz / 24) / math.pi * 6)


def _get_lunar_month_11(yy, tz):
    off = _jd_from_date(31, 12, yy) - 2415021
    k = math.floor(off / 29.530588853)
    nm = _get_new_moon_day(k, tz)
    if _get_sun_longitude(nm, tz) >= 9:
        nm = _get_new_moon_day(k - 1, tz)
    return nm


def _get_leap_month_offset(a11, tz):
    k = math.floor((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    last = 0
    i = 1
    arc = _get_sun_longitude(_get_new_moon_day(k + i, tz), tz)
    while arc != last and i < 14:
        last = arc
        i += 1
        arc = _get_sun_longitude(_get_new_moon_day(k + i, tz), tz)
    return i - 1


def convert_solar_to_lunar(dd, mm, yy, tz=7):
    """Trả về (ngày âm, tháng âm, năm âm, nhuận 0/1)"""
    day_number = _jd_from_date(dd, mm, yy)
    k = math.floor((day_number - 2415021.076998695) / 29.530588853)
    month_start = _get_new_moon_day(k + 1, tz)
    if month_start > day_number:
        month_start = _get_new_moon_day(k, tz)
    a11 = _get_lunar_month_11(yy, tz)
    b11 = a11
    if a11 >= month_start:
        lunar_year = yy
        a11 = _get_lunar_month_11(yy - 1, tz)
    else:
        lunar_year = yy + 1
        b11 = _get_lunar_month_11(yy + 1, tz)
    lunar_day = day_number - month_start + 1
    diff = math.floor((month_start - a11) / 29)
    lunar_leap = 0
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = _get_leap_month_offset(a11, tz)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = 1
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return lunar_day, lunar_month, lunar_year, lunar_leap


def calculate_menh(dob):
    """
    dob: datetime.date (dương lịch)
    Trả về dict: lunar_date, can_chi, nap_am, hanh, hop_digits, ky_digits, sinh_menh, khac_menh
    """
    ld, lm, ly, _leap = convert_solar_to_lunar(dob.day, dob.month, dob.year, 7)
    idx = ((ly - 4) % 60 + 60) % 60
    can_chi = f"{CAN[idx % 10]} {CHI[idx % 12]}"
    nap_am, hanh = NAP_AM[idx // 2]
    sinh_menh = _inv(SINH, hanh)  # hành sinh cho mệnh
    khac_menh = _inv(KHAC, hanh)  # hành khắc mệnh
    hop_digits = sorted(set(HA_DO[sinh_menh] + HA_DO[hanh]))
    ky_digits = sorted(set(HA_DO[khac_menh]))
    return {
        'lunar_date': (ld, lm, ly),
        'lunar_year': ly,
        'can_chi': can_chi,
        'nap_am': nap_am,
        'hanh': hanh,
        'sinh_menh': sinh_menh,
        'khac_menh': khac_menh,
        'hop_digits': hop_digits,
        'ky_digits': ky_digits,
    }


def menh_verdict(hanh, hop_count, ky_count):
    """Xếp hạng mức độ hợp mệnh dựa trên số chữ số hợp/kỵ trong dãy số"""
    if hop_count >= 6 and ky_count == 0:
        return f'Rất hợp mệnh {hanh}'
    if hop_count >= 5 and ky_count <= 1:
        return f'Hợp mệnh {hanh}'
    if hop_count > ky_count:
        return f'Khá hợp mệnh {hanh}'
    if ky_count > hop_count:
        return 'Chưa hợp'
    return f'Trung tính với mệnh {hanh}'
