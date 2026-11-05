"""
Xử lý QR CCCD / Căn cước phía máy chủ (dùng khi nhập danh sách học sinh tự đăng ký).
Giữ ĐÚNG logic với static/js/cccd_qr_scanner.js (parseCccdQr, tinhNgayHetHanCccd, convertToNewAddress).
"""
import json
import re
import unicodedata
from datetime import date
from pathlib import Path

from dateutil.relativedelta import relativedelta

CONVERSION_FILE = Path(__file__).resolve().parent / 'static' / 'data' / 'chuyen_doi.json'


# ---------------------------------------------------------------- Ngày hết hạn / nơi cấp
def tinh_ngay_het_han(ngay_sinh, ngay_cap):
    """Luật Căn cước: đổi thẻ khi đủ 14, 25, 40, 60 tuổi; cấp trong vòng 2 năm trước mốc tuổi thì
    có giá trị đến mốc tiếp theo; từ 58 tuổi trở đi không thời hạn (None)."""
    if not ngay_sinh or not ngay_cap:
        return None
    for tuoi in (14, 25, 40, 60):
        if ngay_cap < ngay_sinh + relativedelta(years=tuoi - 2):
            return ngay_sinh + relativedelta(years=tuoi)
    return None


def _ddmmyyyy(s):
    s = (s or '').strip()
    if not re.fullmatch(r'\d{8}', s):
        return None
    try:
        return date(int(s[4:]), int(s[2:4]), int(s[:2]))
    except ValueError:
        return None


def parse_cccd_qr(text):
    """Chuỗi QR mặt trước CCCD → dict, hoặc None nếu không phải QR CCCD.
    Định dạng: SốCCCD|SốCMND|Họ tên|NgàySinh(ddmmyyyy)|Giới tính|Địa chỉ|NgàyCấp(ddmmyyyy)|..."""
    p = [s.strip() for s in (text or '').strip().split('|')]
    if len(p) < 7 or not re.fullmatch(r'\d{12}', p[0]):
        return None
    ngay_sinh, ngay_cap = _ddmmyyyy(p[3]), _ddmmyyyy(p[6])
    return {
        'so_cmnd': p[0],
        'cmnd_cu': p[1],
        'ho_ten': p[2],
        'ngay_sinh': ngay_sinh,
        'gioi_tinh': 'Nam' if p[4].lower() == 'nam' else 'Nữ',
        'dia_chi_tren_the': p[5],
        'ngay_cap_cmnd': ngay_cap,
        'ngay_het_han_cmnd': tinh_ngay_het_han(ngay_sinh, ngay_cap),
        # Căn cước mẫu mới (từ 01/07/2024) do Bộ Công an cấp
        'noi_cap_cmnd': 'Bộ Công An' if ngay_cap and ngay_cap >= date(2024, 7, 1) else 'Cục CSQLHC về TTXH',
    }


# ---------------------------------------------------------------- Đổi địa chỉ cũ → mới
def _norm_part(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('đ', 'd').replace('Đ', 'd').lower()
    s = re.sub(r'^(ap|khom|xa|phuong|thi tran|huyen|quan|thi xa|thanh pho|tinh|tp\.?)\s+', '', s)
    s = re.sub(r'\b0+(\d)', r'\1', s)
    return re.sub(r'\s+', ' ', s).strip()


def _clean_new(addr):
    parts = [x.strip() for x in re.sub(r'\s*\(mới\)\s*$', '', addr).split(',') if x.strip()]
    return [x for i, x in enumerate(parts) if i == len(parts) - 1 or not re.match(r'^(Huyện|Quận|Thị xã|Thành phố) ', x)]


_index = None


def _build_index():
    data = json.loads(CONVERSION_FILE.read_text(encoding='utf-8'))
    hamlet, ward = {}, {}

    def add(m, k, v):
        m.setdefault(k, set()).add(v)

    for old, new in data.items():
        o = [x.strip() for x in old.split(',')]
        n = _clean_new(new)
        if len(o) == 4 and o[0]:
            h, w, d, p = map(_norm_part, o)
            add(hamlet, f'{h}|{w}|{d}|{p}', ', '.join(n)); add(hamlet, f'{h}|{w}|{p}', ', '.join(n))
            add(ward, f'{w}|{d}|{p}', ', '.join(n[1:])); add(ward, f'{w}|{p}', ', '.join(n[1:]))
        elif len(o) >= 3:
            w, d, p = map(_norm_part, o[-3:])
            add(ward, f'{w}|{d}|{p}', ', '.join(n)); add(ward, f'{w}|{p}', ', '.join(n))
    return hamlet, ward


def convert_address(addr):
    """→ (địa chỉ mới, chắc_chắn) hoặc None. Chắc chắn: khớp ấp + xã + huyện + tỉnh
    (thẻ không ghi ấp: khớp xã + huyện + tỉnh). Không chắc: chỉ dùng làm gợi ý."""
    global _index
    if _index is None:
        _index = _build_index()
    hamlet, ward = _index
    parts = [x.strip() for x in (addr or '').split(',') if x.strip()]
    if len(parts) < 3:
        return None

    def get(m, k):
        s = m.get(k)
        return next(iter(s)) if s and len(s) == 1 else None

    p, d, w = (_norm_part(x) for x in (parts[-1], parts[-2], parts[-3]))
    has_hamlet = len(parts) >= 4
    if has_hamlet:
        h = _norm_part(parts[-4])
        exact = get(hamlet, f'{h}|{w}|{d}|{p}')
        if exact:
            return ', '.join(parts[:-4] + [exact]), True
        no_district = get(hamlet, f'{h}|{w}|{p}')
        if no_district:
            return ', '.join(parts[:-4] + [no_district]), False
    ward_exact = get(ward, f'{w}|{d}|{p}')
    found = ward_exact or get(ward, f'{w}|{p}')
    if found:
        return ', '.join(parts[:-3] + [found]), bool(ward_exact) and not has_hamlet
    return None
