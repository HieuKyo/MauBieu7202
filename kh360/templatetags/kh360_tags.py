from django import template

register = template.Library()

# Phân quyền Khách hàng 360
QUYEN_TRA_CUU, QUYEN_QUAN_LY, QUYEN_ADMIN = 1, 2, 3
# Được Tra cứu + Biến động + Thống kê: Ban giám đốc, GĐ/PGĐ phòng giao dịch, trưởng/phó phòng, hậu kiểm
CHUC_VU_QUAN_LY = ('GIAM_DOC', 'PHO_GIAM_DOC', 'GD_PGD', 'PGD_PGD', 'TRUONG_PHONG', 'PHO_PHONG')
PHONG_QUAN_LY = ('BAN_GIAM_DOC',)
NGHIEP_VU_QUAN_LY = ('HAU_KIEM_VIEN',)


@register.filter
def muc_quyen(user):
    """3 = admin (toàn quyền, cập nhật dữ liệu); 2 = BGĐ / trưởng, phó phòng / hậu kiểm;
    1 = còn lại (nhân viên, GDV, cán bộ tín dụng…) chỉ tra cứu; 0 = chưa đăng nhập."""
    if not user.is_authenticated:
        return 0
    if user.is_superuser:
        return QUYEN_ADMIN
    p = getattr(user, 'profile', None)
    if p and (p.position in CHUC_VU_QUAN_LY or p.department in PHONG_QUAN_LY
              or p.job_function in NGHIEP_VU_QUAN_LY):
        return QUYEN_QUAN_LY
    return QUYEN_TRA_CUU


def _so(v, le):
    t = f'{v:,.{le}f}'.replace(',', ' ').replace('.', ',').replace(' ', '.')
    return t[:-2] if le and t.endswith(',0') else t


@register.filter
def tien_gon(v):
    """2.150.000.000 → '2,2 tỷ đ'; 54.300.000 → '54 tr đ'; 74.000 → '74.000 đ'."""
    try:
        v = float(v or 0)
    except (TypeError, ValueError):
        return v
    a = abs(v)
    if a >= 1e9:
        return f'{_so(v / 1e9, 1)} tỷ đ'
    if a >= 1e6:
        return f'{_so(v / 1e6, 0)} tr đ'
    return f'{_so(v, 0)} đ'


@register.filter
def tien(v):
    """Số tiền đầy đủ, dấu chấm phân cách nghìn."""
    try:
        return _so(float(v or 0), 0)
    except (TypeError, ValueError):
        return v


HANG_MAU = {'Platinum': 'hang-platinum', 'Titanium': 'hang-titanium', 'Gold': 'hang-gold', 'Silver': 'hang-silver'}


def lop_hang(nhom, hang):
    """Lớp CSS cho huy hiệu hạng."""
    if hang:
        return HANG_MAU.get(hang, 'hang-silver')
    return 'hang-than-thiet' if nhom == 'Thân thiết' else 'hang-pho-thong'


@register.filter
def hang_css(xh):
    """Lớp CSS cho huy hiệu hạng của XepHangKH (hoặc None)."""
    return lop_hang(xh.nhom_cn, xh.hang_cn) if xh else ''
