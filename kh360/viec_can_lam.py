"""
Việc cần làm (Khách hàng 360): 3 danh sách để cán bộ liên hệ KH và ghi kết quả.

- Sổ tiết kiệm đến hạn       (TaiKhoanTG.ngay_den_han)
- Khoản vay sắp đến kỳ trả   (KhoanVay.ngay_tra_tiep)
- KH chưa dùng dịch vụ        (KH cá nhân có tiền gửi nhưng CN05 không có thẻ / Agribank Plus / SMS)

Phạm vi xem theo PGD (Nghị định 13/2023 — chỉ xử lý dữ liệu KH trong phạm vi công việc):
cấp quản lý KH 360 (BGĐ, trưởng/phó phòng, hậu kiểm) và Superuser xem toàn chi nhánh;
nhân viên chỉ xem KH của PGD mình (UserProfile.branch).
"""
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import OuterRef, Q, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from .models import KhachHang, KhoanVay, Ky, LienHeKH, TaiKhoanTG
from .parsers import khong_dau
from .templatetags.kh360_tags import QUYEN_QUAN_LY, muc_quyen

# UserProfile.branch → tên PGD trong dữ liệu IPCAS (TEN_PGD)
PGD_THEO_DON_VI = {
    'HOI_SO': 'Hội sở',
    'PGD_P1': 'PGD Phường 1',
    'PGD_LANG_TRON': 'PGD Láng Tròn',
}

# Dịch vụ CN05 tính là "đã dùng dịch vụ" (không tính TK thanh toán / tiền gửi)
DICH_VU_SO = [
    'the_gn_noi_dia', 'the_gn_quoc_te', 'the_td_noi_dia', 'the_td_quoc_te', 'the_visa', 'the_master',
    'the_jcb', 'agribank_plus', 'agribank_plus_ott', 'sms_banking', 'tg_sms', 'tg_truc_tuyen',
]

TABS = [
    ('den_han', 'Sổ đến hạn'),
    ('tra_no', 'Khoản vay sắp trả'),
    ('ngu_dong', 'KH chưa dùng dịch vụ'),
]
SO_NGAY = [('7', '7 ngày tới'), ('15', '15 ngày tới'), ('30', '30 ngày tới'), ('da_qua', 'Đã qua (từ ngày dữ liệu)')]
LIEN_HE_LOC = [('chua', 'Chưa liên hệ'), ('da', 'Đã liên hệ')] + LienHeKH.KET_QUA_CHOICES
NGUONG_NGU_DONG = 10_000_000


def _pham_vi(user):
    """→ (None = toàn chi nhánh | tên PGD | '' = không xác định được PGD)."""
    if muc_quyen(user) >= QUYEN_QUAN_LY:
        return None
    p = getattr(user, 'profile', None)
    return PGD_THEO_DON_VI.get(getattr(p, 'branch', ''), '')


def _chuan_ten(v):
    return ' '.join(khong_dau(v).split())


def _sdt_kh():
    return Subquery(KhachHang.objects.filter(ma_kh=OuterRef('ma_kh')).values('sdt')[:1])


def _qs(tab, g, pgd_scope):
    """Queryset theo tab + bộ lọc (chưa lọc theo kết quả liên hệ)."""
    hom_nay = date.today()
    ky = Ky.objects.order_by('-ngay_du_lieu').first()
    so_ngay = g.get('so_ngay', '7')
    if tab == 'den_han':
        qs = TaiKhoanTG.objects.filter(con_hoat_dong=True, ky_han__gt=0).annotate(sdt=_sdt_kh())
        truong = 'ngay_den_han'
    elif tab == 'tra_no':
        qs = KhoanVay.objects.filter(con_du_no=True).annotate(sdt=_sdt_kh())
        truong = 'ngay_tra_tiep'
    else:
        qs = KhachHang.objects.filter(con_hoat_dong=True, co_cn05=True,
                                      tong_so_du__gte=_so(g.get('nguong'), NGUONG_NGU_DONG))
        for k in DICH_VU_SO:
            qs = qs.exclude(dich_vu__has_key=k)
        qs = qs.annotate(can_bo=Subquery(
            TaiKhoanTG.objects.filter(ma_kh=OuterRef('ma_kh'), con_hoat_dong=True)
            .order_by('-so_du').values('can_bo')[:1]))
        truong = None

    if truong:
        if so_ngay == 'da_qua':
            tu = ky.ngay_du_lieu if ky else hom_nay - timedelta(days=30)
            qs = qs.filter(**{f'{truong}__gte': tu, f'{truong}__lt': hom_nay})
        else:
            n = int(so_ngay) if so_ngay in ('7', '15', '30') else 7
            qs = qs.filter(**{f'{truong}__gte': hom_nay, f'{truong}__lte': hom_nay + timedelta(days=n)})

    if pgd_scope is not None:
        qs = qs.filter(pgd=pgd_scope)
    elif g.get('pgd'):
        qs = qs.filter(pgd=g['pgd'])
    if g.get('q'):
        q = g['q'].strip()
        qs = qs.filter(Q(ma_kh__icontains=q) | Q(ten__icontains=q) if tab == 'ngu_dong'
                       else Q(ma_kh__icontains=q) | Q(ten_kh__icontains=q))
    order = {'den_han': ('ngay_den_han', '-so_du'), 'tra_no': ('ngay_tra_tiep', '-so_tien_tra_tiep'),
             'ngu_dong': ('-tong_so_du',)}[tab]
    return qs.order_by(*order)


def _so(v, mac_dinh):
    try:
        return int(str(v).replace('.', '').replace(',', '').strip())
    except (TypeError, ValueError):
        return mac_dinh


def _khoa(tab, obj):
    if tab == 'den_han':
        return obj.so_tk, obj.ngay_den_han
    if tab == 'tra_no':
        return obj.so_giai_ngan, obj.ngay_tra_tiep
    return obj.ma_kh, None


def _lien_he_moi_nhat(tab):
    kq = {}
    for lh in LienHeKH.objects.filter(loai=tab).select_related('nguoi').order_by('thoi_diem'):
        kq[(lh.doi_tuong, lh.moc)] = lh
    return kq


def _danh_sach(request, tab):
    """→ (list đối tượng đã gắn .lien_he, pgd_scope, danh sách cán bộ để lọc)."""
    g = request.GET
    pgd_scope = _pham_vi(request.user)
    qs = _qs(tab, g, pgd_scope)
    rows = list(qs)
    ds_can_bo = sorted({r.can_bo or '' for r in rows} - {''})

    can_bo = g.get('can_bo', '')
    if g.get('cua_toi') == '1':
        p = getattr(request.user, 'profile', None)
        ten = _chuan_ten(getattr(p, 'full_name', '') or request.user.get_full_name())
        rows = [r for r in rows if ten and _chuan_ten(r.can_bo or '') == ten]
    elif can_bo == '(chưa gán)':
        rows = [r for r in rows if not r.can_bo]
    elif can_bo:
        rows = [r for r in rows if r.can_bo == can_bo]

    lien_he = _lien_he_moi_nhat(tab)
    for r in rows:
        r.lien_he = lien_he.get(_khoa(tab, r))
    loc = g.get('lien_he', '')
    if loc == 'chua':
        rows = [r for r in rows if not r.lien_he]
    elif loc == 'da':
        rows = [r for r in rows if r.lien_he]
    elif loc in dict(LienHeKH.KET_QUA_CHOICES):
        rows = [r for r in rows if r.lien_he and r.lien_he.ket_qua == loc]
    return rows, pgd_scope, ds_can_bo


def _tien_do(rows):
    """Tổng hợp theo cán bộ (KH chưa gán cán bộ → theo PGD)."""
    nhom = {}
    for r in rows:
        key = r.can_bo or f'(chưa gán) {r.pgd}'.strip()
        d = nhom.setdefault(key, {'ten': key, 'tong': 0, 'da': 0, 'thanh_cong': 0})
        d['tong'] += 1
        if r.lien_he:
            d['da'] += 1
            d['thanh_cong'] += r.lien_he.ket_qua == 'thanh_cong'
    out = sorted(nhom.values(), key=lambda d: -d['tong'])
    for d in out:
        d['pct'] = round(d['da'] * 100 / d['tong']) if d['tong'] else 0
    return out


@login_required
def viec_can_lam(request):
    tab = request.GET.get('tab', 'den_han')
    if tab not in dict(TABS):
        tab = 'den_han'
    rows, pgd_scope, ds_can_bo = _danh_sach(request, tab)
    if pgd_scope == '':
        messages.warning(request, 'Tài khoản chưa khai báo đơn vị (Hội sở / PGD) trong hồ sơ người dùng — '
                                  'liên hệ Admin để được xem danh sách khách hàng của đơn vị mình.')
    if request.GET.get('xuat') == 'excel':
        return _xuat_excel(tab, rows)

    page = Paginator(rows, 50).get_page(request.GET.get('page'))
    tham_so = request.GET.copy()
    for k in ('page', 'xuat'):
        tham_so.pop(k, None)
    tham_so_tab = tham_so.copy()
    tham_so_tab.pop('tab', None)
    return render(request, 'kh360/viec_can_lam.html', {
        'ky': Ky.objects.order_by('-ngay_du_lieu').first(),
        'tab': tab, 'tabs': TABS, 'page': page, 'so_dong': len(rows),
        'tien_do': _tien_do(rows),
        'g': request.GET, 'tham_so': tham_so.urlencode(), 'tham_so_tab': tham_so_tab.urlencode(),
        'so_ngay_loc': SO_NGAY, 'lien_he_loc': LIEN_HE_LOC, 'ket_qua_choices': LienHeKH.KET_QUA_CHOICES,
        'pgd_scope': pgd_scope,
        'ds_pgd': [] if pgd_scope is not None else list(PGD_THEO_DON_VI.values()) + ['PGD Tân Phong'],
        'ds_can_bo': ds_can_bo,
        'nguong_mac_dinh': NGUONG_NGU_DONG,
    })


@login_required
@require_POST
def ghi_lien_he(request):
    """Ghi kết quả liên hệ (gọi bằng fetch). Chỉ ghi cho KH trong phạm vi PGD được xem."""
    tab = request.POST.get('loai')
    doi_tuong = request.POST.get('doi_tuong', '').strip()
    ket_qua = request.POST.get('ket_qua')
    if tab not in dict(TABS) or ket_qua not in dict(LienHeKH.KET_QUA_CHOICES) or not doi_tuong:
        return JsonResponse({'ok': False, 'loi': 'Dữ liệu không hợp lệ'}, status=400)
    model, truong = {'den_han': (TaiKhoanTG, 'so_tk'), 'tra_no': (KhoanVay, 'so_giai_ngan'),
                     'ngu_dong': (KhachHang, 'ma_kh')}[tab]
    obj = model.objects.filter(**{truong: doi_tuong}).first()
    pgd_scope = _pham_vi(request.user)
    if not obj or (pgd_scope is not None and obj.pgd != pgd_scope):
        return JsonResponse({'ok': False, 'loi': 'Không tìm thấy hoặc ngoài phạm vi đơn vị'}, status=403)
    _, moc = _khoa(tab, obj)
    lh = LienHeKH.objects.create(
        loai=tab, doi_tuong=doi_tuong, moc=moc, ma_kh=obj.ma_kh, ket_qua=ket_qua,
        ghi_chu=request.POST.get('ghi_chu', '').strip()[:300], nguoi=request.user,
    )
    return JsonResponse({'ok': True, 'ket_qua': lh.get_ket_qua_display(),
                         'nguoi': request.user.get_full_name() or request.user.username,
                         'thoi_diem': lh.thoi_diem.strftime('%H:%M %d/%m/%Y')})


def _xuat_excel(tab, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = dict(TABS)[tab][:31]
    if tab == 'den_han':
        header = ['STT', 'Mã KH', 'Tên KH', 'SĐT', 'Số TK', 'Số sổ', 'Số dư', 'Loại tiền', 'Kỳ hạn (tháng)',
                  'Lãi suất', 'Ngày đến hạn', 'Cán bộ', 'PGD']
        val = lambda r: [r.ma_kh, r.ten_kh, r.sdt or '', r.so_tk, r.so_so, float(r.so_du), r.ccy, r.ky_han,  # noqa: E731
                         float(r.lai_suat), r.ngay_den_han, r.can_bo, r.pgd]
    elif tab == 'tra_no':
        header = ['STT', 'Mã KH', 'Tên KH', 'SĐT', 'Số giải ngân', 'Dư nợ', 'Ngày trả tiếp', 'Số tiền trả tiếp',
                  'Nhóm nợ', 'Cán bộ tín dụng', 'PGD']
        val = lambda r: [r.ma_kh, r.ten_kh, r.sdt or '', r.so_giai_ngan, float(r.du_no), r.ngay_tra_tiep,  # noqa: E731
                         float(r.so_tien_tra_tiep), r.nhom_no, r.can_bo, r.pgd]
    else:
        header = ['STT', 'Mã KH', 'Tên KH', 'SĐT', 'Tổng số dư', 'Số dư KKH', 'Số dư CKH', 'Cán bộ', 'PGD']
        val = lambda r: [r.ma_kh, r.ten, r.sdt, float(r.tong_so_du), float(r.so_du_kkh), float(r.so_du_ckh),  # noqa: E731
                         r.can_bo or '', r.pgd]
    header += ['Kết quả liên hệ', 'Ghi chú', 'Người ghi', 'Thời điểm']
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='AE1C3F')
    for i, r in enumerate(rows, 1):
        lh = r.lien_he
        ws.append([i] + val(r) + ([lh.get_ket_qua_display(), lh.ghi_chu,
                                   (lh.nguoi.get_full_name() or lh.nguoi.username) if lh.nguoi else '',
                                   lh.thoi_diem.strftime('%d/%m/%Y %H:%M')] if lh else ['', '', '', '']))
    for j in range(1, len(header) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 28 if j in (3, len(header) - 2) else 15
        if header[j - 1].startswith(('Số dư', 'Dư nợ', 'Số tiền', 'Tổng số dư')):
            for row in ws.iter_rows(min_row=2, min_col=j, max_col=j):
                row[0].number_format = '#,##0'
        if header[j - 1].startswith('Ngày'):
            for row in ws.iter_rows(min_row=2, min_col=j, max_col=j):
                row[0].number_format = 'DD/MM/YYYY'
    ws.freeze_panes = 'C2'
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="ViecCanLam_{tab}_{date.today():%Y%m%d}.xlsx"'
    wb.save(resp)
    return resp
