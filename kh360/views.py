import logging
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

import openpyxl
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, F, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from . import parsers
from .importer import NhapKy
from .models import (
    BienDong, EbankingToChuc, GanMaToChuc, GhiChuKH, KhachHang, KhoanVay, Ky, LoaThanTai, MaQR,
    NguonFile, TaiKhoanTG, XepHangKH,
)
from .templatetags.kh360_tags import QUYEN_ADMIN, QUYEN_QUAN_LY, lop_hang, muc_quyen

logger = logging.getLogger(__name__)

NGUON_UPLOAD = [  # (khoá, nhãn, bắt buộc, đuôi file)
    ('CN05', 'CN05 – Sản phẩm dịch vụ KH cá nhân', True, '.zip,.csv'),
    ('DP01', 'DP01 – Tài khoản tiền gửi', True, '.zip,.csv'),
    ('LN01', 'LN01 – Khoản vay', False, '.zip,.csv'),
    ('LOA', 'Thống kê doanh số Loa Thần tài', False, '.xlsx'),
    ('QR', 'Tổng hợp QR', False, '.xlsx'),
    ('KHTC', 'Quản trị khách hàng tổ chức (Ebanking)', False, '.xlsx'),
    ('BC06', 'BC06 – Phân hạng khách hàng (MSPL09)', False, '.zip,.csv'),
]


def _yeu_cau_quyen(muc):
    """Chặn view nếu user không đủ quyền KH 360 (xem kh360_tags.QUYEN_*)."""
    def deco(view):
        @login_required
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if muc_quyen(request.user) < muc:
                messages.error(request, 'Bạn không có quyền dùng chức năng này của Khách hàng 360.')
                return redirect('kh360:tra_cuu')
            return view(request, *args, **kwargs)
        return wrapper
    return deco


def _ky_moi_nhat():
    return Ky.objects.select_related('nguoi_cap_nhat').first()


def _cap_nhat_nguon():
    """{nguồn: NguonFile mới nhất} — để hiện 'dữ liệu ngày ...' từng nguồn."""
    kq = {}
    for nf in NguonFile.objects.select_related('ky').order_by('-ky__thoi_diem'):
        kq.setdefault(nf.nguon, nf)
    return kq


COT_SAP_XEP = {  # tham số ?sort= → trường sắp xếp
    'ma_kh': 'ma_kh', 'ten': 'ten', 'loai': 'la_to_chuc', 'hang': 'diem_hang',
    'so_du': 'tong_so_du', 'kkh': 'so_du_kkh', 'ckh': 'so_du_ckh', 'du_no': 'tong_du_no', 'pgd': 'pgd',
}


COT_BANG = [  # Tra cứu: (khoá, nhãn, lớp ẩn trên màn hẹp — xem _bang_kh.html, sắp xếp được)
    ('ma_kh', 'Mã KH', 'an-md', True), ('ten', 'Tên KH', '', True), ('loai', 'Loại', 'an-lg', True),
    ('hang', 'Hạng', '', True), ('so_du', 'Số dư TG', '', True), ('du_no', 'Dư nợ', 'an-sm', True),
    ('pgd', 'Điểm GD', 'an-xxl', True), ('cccd', 'CCCD/Giấy tờ', 'an-xl', False), ('sdt', 'SĐT', 'an-lg', False),
]
COT_BANG_TK = [  # Thống kê theo KH: tách số dư không kỳ hạn / tiết kiệm
    ('ma_kh', 'Mã KH', 'an-md', True), ('ten', 'Tên KH', '', True), ('loai', 'Loại', 'an-xl', True),
    ('hang', 'Hạng', '', True), ('so_du', 'Tổng số dư TG', '', True), ('kkh', 'TK thanh toán', 'an-lg', True),
    ('ckh', 'Tiết kiệm', 'an-lg', True), ('du_no', 'Dư nợ', 'an-sm', True), ('pgd', 'Điểm GD', 'an-xxl', True),
    ('sdt', 'SĐT', 'an-xl', False),
]


def _gan_hang(qs):
    """Thêm điểm/nhóm/hạng BC06 vào queryset KhachHang (để lọc và sắp xếp)."""
    xh = XepHangKH.objects.filter(ma_kh=OuterRef('ma_kh'))
    return qs.annotate(
        diem_hang=Coalesce(Subquery(xh.values('diem_kh')[:1]), Value(-1)),
        nhom_hang=Subquery(xh.values('nhom_cn')[:1]),
        ten_hang=Subquery(xh.values('hang_cn')[:1]),
    )


def _sap_xep(request, qs):
    sort = request.GET.get('sort', '-so_du')
    if sort.lstrip('-') not in COT_SAP_XEP:
        sort = '-so_du'
    truong = COT_SAP_XEP[sort.lstrip('-')]
    return sort, qs.order_by('-con_hoat_dong', f'-{truong}' if sort.startswith('-') else truong, 'ma_kh')


def _bang_kh(request, qs, cot=COT_BANG):
    """Ngữ cảnh cho bảng KH dùng chung (_bang_kh.html): sắp xếp + 10 dòng/trang."""
    sort, qs = _sap_xep(request, qs)
    page = Paginator(qs, 10).get_page(request.GET.get('page'))
    for kh in page.object_list:
        kh.nhan_hang = XepHangKH.nhan(kh.nhom_hang or '', kh.ten_hang or '')
        kh.css_hang = lop_hang(kh.nhom_hang, kh.ten_hang) if kh.nhom_hang else ''
    tham_so = request.GET.copy()
    for k in ('page', 'sort', 'xuat'):
        tham_so.pop(k, None)
    return {'page': page, 'sort': sort, 'cot': cot, 'qs_base': tham_so.urlencode()}


@login_required
def tra_cuu(request):
    q = request.GET.get('q', '').strip()
    ctx = {'q': q, 'page': None, 'ky': _ky_moi_nhat()}
    if q:
        so = re.sub(r'\D', '', q)
        dk = Q(tim_kiem__icontains=parsers.khong_dau(q))
        if so and len(so) >= 6:
            ma_theo_tk = TaiKhoanTG.objects.filter(so_tk__contains=so).values('ma_kh')
            dk |= Q(ma_kh__in=ma_theo_tk) | Q(tim_kiem__contains=so)
        ctx.update(_bang_kh(request, _gan_hang(KhachHang.objects.filter(dk))))
    return render(request, 'kh360/tra_cuu.html', ctx)


# ── Thống kê ──────────────────────────────────────────────────────────────────

HANG_LOC = [  # (giá trị, nhãn) cho bộ lọc hạng BC06 tại CN
    ('vip', 'Tất cả VIP'), ('Platinum', 'Platinum VIP'), ('Gold', 'Gold VIP'), ('Titanium', 'Titanium VIP'),
    ('Silver', 'Silver VIP'), ('than_thiet', 'Thân thiết'), ('pho_thong', 'Phổ thông'), ('chua_xep', 'Chưa có trong BC06'),
]

MAU_THONG_KE = [  # (nhãn, chuỗi tham số) — các mẫu lọc nhanh
    ('Tiền gửi ≥ 1 tỷ, chưa có Agribank Plus', 'so_du_tu=1000000000&loai=ca_nhan&dv_agribank_plus=chua'),
    ('Vừa đăng ký OTT vừa có SMS Banking', 'dv_agribank_plus_ott=co&dv_sms_banking=co'),
    ('Có SMS Banking nhưng chưa dùng OTT', 'dv_sms_banking=co&dv_agribank_plus_ott=chua'),
    ('Đang vay nhưng chưa có Agribank Plus', 'du_no=co&loai=ca_nhan&dv_agribank_plus=chua'),
    ('VIP chưa có thẻ ghi nợ nội địa', 'hang=vip&loai=ca_nhan&dv_the_gn_noi_dia=chua'),
    ('Có TK thanh toán nhưng chưa có thẻ', 'dv_tktt=co&dv_the_gn_noi_dia=chua&dv_the_gn_quoc_te=chua'),
    ('Từ 60 tuổi, tiền gửi ≥ 500 triệu', 'tuoi_tu=60&so_du_tu=500000000'),
    ('Có Loa Thần tài nhưng chưa có QR', 'loa=co&qr=khong'),
    ('TK thanh toán ≥ 50 triệu, chưa có sổ tiết kiệm', 'kkh_tu=50000000&ckh_den=0'),
]


def _so_tien(v):
    so = re.sub(r'\D', '', v or '')
    return int(so) if so else None


def _so_nguyen(v):
    return int(v) if (v or '').strip().isdigit() else None


def _loc_thong_ke(g):
    """Áp bộ lọc từ request.GET → (queryset KH đang hoạt động, có lọc gì không)."""
    qs = _gan_hang(KhachHang.objects.filter(con_hoat_dong=True))
    co_loc = False
    for ten, truong in (('so_du', 'tong_so_du'), ('kkh', 'so_du_kkh'), ('ckh', 'so_du_ckh')):
        tu, den = _so_tien(g.get(f'{ten}_tu')), _so_tien(g.get(f'{ten}_den'))
        if tu is not None:
            qs, co_loc = qs.filter(**{f'{truong}__gte': tu}), True
        if den is not None:
            qs, co_loc = qs.filter(**{f'{truong}__lte': den}), True
    if g.get('du_no') == 'co':
        qs, co_loc = qs.filter(tong_du_no__gt=0), True
    elif g.get('du_no') == 'khong':
        qs, co_loc = qs.filter(tong_du_no=0), True
    if g.get('loai') in ('ca_nhan', 'to_chuc'):
        qs, co_loc = qs.filter(la_to_chuc=g['loai'] == 'to_chuc'), True
    hang = g.get('hang')
    if hang:
        co_loc = True
        if hang == 'vip':
            qs = qs.filter(nhom_hang='Vip')
        elif hang == 'than_thiet':
            qs = qs.filter(nhom_hang='Thân thiết')
        elif hang == 'pho_thong':
            qs = qs.filter(nhom_hang='Phổ thông')
        elif hang == 'chua_xep':
            qs = qs.filter(nhom_hang__isnull=True)
        else:
            qs = qs.filter(ten_hang=hang)
    if g.get('pgd'):
        qs, co_loc = qs.filter(pgd=g['pgd']), True
    hom_nay = date.today()
    tuoi_tu, tuoi_den = _so_nguyen(g.get('tuoi_tu')), _so_nguyen(g.get('tuoi_den'))
    if tuoi_tu is not None:
        qs, co_loc = qs.filter(ngay_sinh__lte=hom_nay - relativedelta(years=tuoi_tu)), True
    if tuoi_den is not None:
        qs, co_loc = qs.filter(ngay_sinh__gt=hom_nay - relativedelta(years=tuoi_den + 1)), True
    for _, k, _ in parsers.CN05_DICH_VU:   # dịch vụ: co / chua (chỉ KH cá nhân có trong CN05)
        v = g.get(f'dv_{k}')
        if v == 'co':
            qs, co_loc = qs.filter(co_cn05=True, dich_vu__has_key=k), True
        elif v == 'chua':
            qs, co_loc = qs.filter(co_cn05=True).exclude(dich_vu__has_key=k), True
    ky_loa = LoaThanTai.objects.order_by('-tu_ngay').values_list('tu_ngay', flat=True).first()
    co_loa = LoaThanTai.objects.filter(tu_ngay=ky_loa).exclude(ma_kh='').values('ma_kh')
    co_qr = MaQR.objects.exclude(ma_kh='').values('ma_kh')
    co_eb = EbankingToChuc.objects.exclude(ma_kh='').values('ma_kh')
    for ten, sub in (('loa', co_loa), ('qr', co_qr), ('ebanking', co_eb)):
        if g.get(ten) == 'co':
            qs, co_loc = qs.filter(ma_kh__in=sub), True
        elif g.get(ten) == 'khong':
            qs, co_loc = qs.exclude(ma_kh__in=sub), True
    return qs, co_loc


@_yeu_cau_quyen(QUYEN_QUAN_LY)
def thong_ke(request):
    qs, co_loc = _loc_thong_ke(request.GET)
    if request.GET.get('xuat') == 'excel':
        return _xuat_excel_thong_ke(_sap_xep(request, qs)[1])
    ctx = {
        'ky': _ky_moi_nhat(),
        'co_loc': co_loc,
        'g': request.GET,
        'hang_loc': HANG_LOC,
        'mau': MAU_THONG_KE,
        'muc_tien': [(100000000, '100 tr'), (500000000, '500 tr'), (1000000000, '1 tỷ'), (5000000000, '5 tỷ')],
        'dich_vu': [(k, nhan, request.GET.get(f'dv_{k}', '')) for _, k, nhan in parsers.CN05_DICH_VU],
        'ds_pgd': (KhachHang.objects.filter(con_hoat_dong=True).exclude(pgd='')
                   .values_list('pgd', flat=True).distinct().order_by('pgd')),
    }
    if co_loc:
        ctx['tong'] = qs.aggregate(so_kh=Count('ma_kh'), so_du=Sum('tong_so_du'), kkh=Sum('so_du_kkh'),
                                   ckh=Sum('so_du_ckh'), du_no=Sum('tong_du_no'),
                                   to_chuc=Count('ma_kh', filter=Q(la_to_chuc=True)))
        ctx.update(_bang_kh(request, qs, COT_BANG_TK))
    return render(request, 'kh360/thong_ke.html', ctx)


def _xuat_excel_thong_ke(qs):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet('Thống kê KH 360')
    ws.append(['STT', 'Mã KH', 'Tên KH', 'Loại', 'Hạng (BC06)', 'CCCD/Giấy tờ', 'Ngày sinh', 'SĐT', 'Địa chỉ',
               'Điểm GD', 'Tổng số dư TG (VND)', 'Số dư TK thanh toán', 'Số dư tiết kiệm / có kỳ hạn',
               'Dư nợ', 'Dịch vụ đã có'])
    nhan_dv = parsers.NHAN_DICH_VU
    for i, kh in enumerate(qs.iterator(chunk_size=2000), 1):
        ws.append([
            i, kh.ma_kh, kh.ten, 'Tổ chức' if kh.la_to_chuc else 'Cá nhân',
            XepHangKH.nhan(kh.nhom_hang or '', kh.ten_hang or ''), kh.cccd,
            kh.ngay_sinh.strftime('%d/%m/%Y') if kh.ngay_sinh else '', kh.sdt, kh.dia_chi, kh.pgd,
            float(kh.tong_so_du), float(kh.so_du_kkh), float(kh.so_du_ckh), float(kh.tong_du_no),
            ', '.join(nhan_dv[k] for k in kh.dich_vu if k in nhan_dv),
        ])
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="ThongKe_KH360_{date.today():%Y%m%d}.xlsx"'
    wb.save(resp)
    return resp


def _tuoi(ngay_sinh):
    if not ngay_sinh:
        return None
    hom_nay = date.today()
    return hom_nay.year - ngay_sinh.year - ((hom_nay.month, hom_nay.day) < (ngay_sinh.month, ngay_sinh.day))


@login_required
def ho_so(request, ma_kh):
    """Chi tiết KH. ?modal=1 → chỉ trả nội dung bảng nổi (gọi bằng fetch từ trang tra cứu)."""
    kh = get_object_or_404(KhachHang, ma_kh=ma_kh)
    tai_khoan = list(TaiKhoanTG.objects.filter(ma_kh=ma_kh))
    so_tk = [t.so_tk for t in tai_khoan]
    khoan_vay = list(KhoanVay.objects.filter(ma_kh=ma_kh))
    loa = list(LoaThanTai.objects.filter(Q(ma_kh=ma_kh) | Q(so_tk__in=so_tk)))
    loa_theo_ky = {}
    for l in loa:
        k = loa_theo_ky.setdefault(l.tu_ngay, {'tu_ngay': l.tu_ngay, 'den_ngay': l.den_ngay,
                                                'so_gd': 0, 'doanh_so': 0, 'loa': []})
        k['so_gd'] += l.so_giao_dich
        k['doanh_so'] += l.doanh_so
        k['loa'].append(l)
    dich_vu = [
        {'nhan': nhan, 'so': kh.dich_vu.get(k, 0)} for _, k, nhan in parsers.CN05_DICH_VU
    ]
    tk_active = [t for t in tai_khoan if t.con_hoat_dong]
    ten_cuoi = kh.ten.split()[-1] if kh.ten.split() else '?'
    template = 'kh360/_ho_so.html' if request.GET.get('modal') else 'kh360/ho_so.html'
    return render(request, template, {
        'kh': kh,
        'xh': XepHangKH.objects.filter(ma_kh=ma_kh).first(),
        'ghi_chu': GhiChuKH.objects.filter(ma_kh=ma_kh).select_related('nguoi_sua').first(),
        'tuoi': _tuoi(kh.ngay_sinh),
        'danh_xung': '' if kh.la_to_chuc else {'Nam': 'Ông', 'Nữ': 'Bà'}.get(kh.gioi_tinh, ''),
        'chu_dau': ten_cuoi[0].upper(),
        'so_vay_active': sum(1 for v in khoan_vay if v.con_du_no),
        'so_dv': sum(1 for d in dich_vu if d['so']),
        'dich_vu': dich_vu,
        'tai_khoan': tai_khoan,
        'tong_so_du': sum(t.so_du for t in tk_active if t.ccy == 'VND' and t.so_du > 0),
        'so_tk_active': len(tk_active),
        'khoan_vay': khoan_vay,
        'tong_du_no': sum(v.du_no for v in khoan_vay if v.con_du_no),
        'loa_theo_ky': sorted(loa_theo_ky.values(), key=lambda x: x['tu_ngay'], reverse=True),
        'qr': MaQR.objects.filter(Q(ma_kh=ma_kh) | Q(so_tk__in=so_tk)),
        'ebanking': EbankingToChuc.objects.filter(ma_kh=ma_kh),
        'bien_dong': BienDong.objects.filter(ma_kh=ma_kh).select_related('ky').order_by('-ky__thoi_diem')[:200],
        'ky': _ky_moi_nhat(),
    })


@login_required
@require_POST
def luu_ghi_chu(request, ma_kh):
    get_object_or_404(KhachHang, ma_kh=ma_kh)
    gc, _ = GhiChuKH.objects.update_or_create(
        ma_kh=ma_kh, defaults={'noi_dung': request.POST.get('noi_dung', '').strip(), 'nguoi_sua': request.user})
    nguoi = request.user.get_full_name() or request.user.username
    return JsonResponse({'ok': True, 'thong_tin': f'Sửa lần cuối {timezone.localtime(gc.ngay_sua):%d/%m/%Y %H:%M} – {nguoi}'})


@_yeu_cau_quyen(QUYEN_ADMIN)
def cap_nhat(request):
    if request.method == 'POST':
        files = {k: request.FILES.get(k) for k, *_ in NGUON_UPLOAD}
        try:
            ky = NhapKy(files, request.user).chay()
        except parsers.FileLoi as e:
            messages.error(request, str(e))
        except Exception:
            logger.exception('Lỗi cập nhật KH 360')
            messages.error(request, 'Lỗi khi cập nhật dữ liệu — xem logs/errors.log.')
        else:
            so_bd = ky.bien_dong.count()
            moc = [nf.nguon for nf in ky.files.all() if nf.la_moc]
            msg = f'Đã cập nhật dữ liệu ngày {ky.ngay_du_lieu:%d/%m/%Y}: {so_bd} biến động.'
            if moc:
                msg += f' Lần đầu nạp {", ".join(moc)} — chỉ làm mốc, chưa tính biến động.'
            messages.success(request, msg)
        return redirect('kh360:cap_nhat')

    ky_list = Ky.objects.select_related('nguoi_cap_nhat').prefetch_related('files')[:30]
    ky_moi = ky_list[0] if ky_list else None
    return render(request, 'kh360/cap_nhat.html', {
        'nguon_upload': NGUON_UPLOAD,
        'nguon_moi': _cap_nhat_nguon(),
        'ky_list': ky_list,
        'ky': ky_moi,
        'chua_gan': EbankingToChuc.objects.filter(ma_kh=''),
    })


@_yeu_cau_quyen(QUYEN_ADMIN)
@require_POST
def gan_to_chuc(request):
    ma_to_chuc = request.POST.get('ma_to_chuc', '').strip()
    ma_kh = parsers.s(request.POST.get('ma_kh', ''))
    eb = get_object_or_404(EbankingToChuc, ma_to_chuc=ma_to_chuc)
    kh = KhachHang.objects.filter(ma_kh=ma_kh).first()
    if not kh:
        messages.error(request, f'Không tìm thấy mã KH {ma_kh}.')
    else:
        GanMaToChuc.objects.update_or_create(ma_to_chuc=ma_to_chuc, defaults={'ma_kh': ma_kh})
        eb.ma_kh = ma_kh
        eb.save(update_fields=['ma_kh'])
        BienDong.objects.filter(loai__in=['EB_MOI', 'EB_MAT'], doi_tuong=ma_to_chuc, ma_kh='').update(ma_kh=ma_kh)
        messages.success(request, f'Đã gán {eb.ten} → {kh.ma_kh} – {kh.ten}.')
    return redirect('kh360:cap_nhat')


def _loc_bien_dong(request):
    ky_list = list(Ky.objects.all()[:100])
    ky_id = request.GET.get('ky')
    ky = next((k for k in ky_list if str(k.pk) == ky_id), ky_list[0] if ky_list else None)
    loai = request.GET.get('loai', '')
    qs = BienDong.objects.filter(ky=ky) if ky else BienDong.objects.none()
    if loai:
        qs = qs.filter(loai=loai)
    return ky_list, ky, loai, qs


@_yeu_cau_quyen(QUYEN_QUAN_LY)
def bien_dong(request):
    ky_list, ky, loai, qs = _loc_bien_dong(request)
    if request.GET.get('xuat') == 'excel':
        return _xuat_excel(ky, qs)
    dem = {}
    if ky:
        dem = dict(BienDong.objects.filter(ky=ky).values('loai').annotate(n=Count('id')).values_list('loai', 'n'))
    page = Paginator(qs, 100).get_page(request.GET.get('page'))
    return render(request, 'kh360/bien_dong.html', {
        'ky_list': ky_list, 'ky_chon': ky, 'loai': loai, 'page': page,
        'loai_choices': [(k, v, dem.get(k, 0)) for k, v in BienDong.LOAI_CHOICES],
        'tong': sum(dem.values()),
        'ky': _ky_moi_nhat(),
    })


def _xuat_excel(ky, qs):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Biến động'
    header = ['STT', 'Loại biến động', 'Mã KH', 'Tên KH', 'Đối tượng', 'Chi tiết']
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='AE1C3F')
    for i, b in enumerate(qs, 1):
        ws.append([i, b.get_loai_display(), b.ma_kh, b.ten_kh, b.doi_tuong, b.chi_tiet])
    for j, w in enumerate([6, 22, 14, 35, 26, 60], 1):
        ws.column_dimensions[get_column_letter(j)].width = w
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    ten = f'BienDong_KH360_{ky.ngay_du_lieu:%Y%m%d}.xlsx' if ky else 'BienDong_KH360.xlsx'
    resp['Content-Disposition'] = f'attachment; filename="{ten}"'
    wb.save(resp)
    return resp


# ── Bộ lọc dùng chung cho thống kê Sổ tiết kiệm / Tiền vay ─────────────────────

def _so_thap_phan(v):
    v = (v or '').strip().replace(',', '.')
    try:
        return Decimal(v) if v else None
    except InvalidOperation:
        return None


def _ngay_iso(v):
    try:
        return date.fromisoformat((v or '').strip())
    except ValueError:
        return None


def _gan_chu(qs):
    """Thêm hạng BC06 và loại (tổ chức) của chủ TK / khoản vay để lọc và hiển thị."""
    xh = XepHangKH.objects.filter(ma_kh=OuterRef('ma_kh'))
    kh = KhachHang.objects.filter(ma_kh=OuterRef('ma_kh'))
    return qs.annotate(nhom_hang=Subquery(xh.values('nhom_cn')[:1]), ten_hang=Subquery(xh.values('hang_cn')[:1]),
                       la_to_chuc=Subquery(kh.values('la_to_chuc')[:1]))


def _loc_chu(qs, g):
    """Lọc theo khách hàng chủ sở hữu: loại, hạng, điểm GD, đã có / chưa có dịch vụ."""
    co_loc = False
    if g.get('pgd'):
        qs, co_loc = qs.filter(pgd=g['pgd']), True
    if g.get('loai') in ('ca_nhan', 'to_chuc'):
        qs, co_loc = qs.filter(la_to_chuc=g['loai'] == 'to_chuc'), True
    hang = g.get('hang')
    if hang:
        co_loc = True
        if hang == 'vip':
            qs = qs.filter(nhom_hang='Vip')
        elif hang == 'than_thiet':
            qs = qs.filter(nhom_hang='Thân thiết')
        elif hang == 'pho_thong':
            qs = qs.filter(nhom_hang='Phổ thông')
        elif hang == 'chua_xep':
            qs = qs.filter(nhom_hang__isnull=True)
        else:
            qs = qs.filter(ten_hang=hang)
    dv, dv_tt = g.get('dv'), g.get('dv_tt')
    if dv in parsers.NHAN_DICH_VU and dv_tt in ('co', 'chua'):
        co_dv = KhachHang.objects.filter(co_cn05=True, dich_vu__has_key=dv).values('ma_kh')
        chua_dv = KhachHang.objects.filter(co_cn05=True).exclude(dich_vu__has_key=dv).values('ma_kh')
        qs, co_loc = qs.filter(ma_kh__in=co_dv if dv_tt == 'co' else chua_dv), True
    return qs, co_loc


def _loc_ngay(qs, truong, chon, tu=None, den=None):
    """Lọc 1 trường ngày theo lựa chọn nhanh (tương lai / quá khứ / khoảng). Ngày tính theo hôm nay."""
    hom_nay = date.today()
    dau_thang = hom_nay.replace(day=1)
    khoang = {
        '7': (hom_nay, hom_nay + relativedelta(days=7)),
        '30': (hom_nay, hom_nay + relativedelta(days=30)),
        'qua_7': (hom_nay - relativedelta(days=7), hom_nay),
        'qua_30': (hom_nay - relativedelta(days=30), hom_nay),
        'thang_nay': (dau_thang, dau_thang + relativedelta(months=1, days=-1)),
        'thang_sau': (dau_thang + relativedelta(months=1), dau_thang + relativedelta(months=2, days=-1)),
        'thang_truoc': (dau_thang - relativedelta(months=1), dau_thang - relativedelta(days=1)),
        'qua_han': (None, hom_nay - relativedelta(days=1)),
        'khoang': (_ngay_iso(tu), _ngay_iso(den)),
    }.get(chon)
    if not khoang:
        return qs, False
    if khoang[0]:
        qs = qs.filter(**{f'{truong}__gte': khoang[0]})
    if khoang[1]:
        qs = qs.filter(**{f'{truong}__lte': khoang[1]})
    return qs, True


def _loc_khoang(qs, truong, tu, den, doi=None):
    """Lọc từ … đến … cho một trường số; doi = hàm đổi chuỗi nhập sang số."""
    doi = doi or _so_tien
    tu, den, co_loc = doi(tu), doi(den), False
    if tu is not None:
        qs, co_loc = qs.filter(**{f'{truong}__gte': tu}), True
    if den is not None:
        qs, co_loc = qs.filter(**{f'{truong}__lte': den}), True
    return qs, co_loc


def _loc_so_thang_tu_ngay(qs, truong, tu, den):
    """Số tháng tính từ một ngày (ngày gửi / ngày giải ngân) đến hôm nay, từ … đến …"""
    hom_nay, co_loc = date.today(), False
    tu, den = _so_nguyen(tu), _so_nguyen(den)
    if tu is not None:
        qs, co_loc = qs.filter(**{f'{truong}__lte': hom_nay - relativedelta(months=tu)}), True
    if den is not None:
        qs, co_loc = qs.filter(**{f'{truong}__gt': hom_nay - relativedelta(months=den + 1)}), True
    return qs, co_loc


def _trang(request, qs, sap_xep, mac_dinh, khoa_phu):
    """Sắp xếp + 10 dòng/trang; trả (sort, page, qs_base giữ điều kiện lọc)."""
    sort = request.GET.get('sort', mac_dinh)
    if sort.lstrip('-') not in sap_xep:
        sort = mac_dinh
    truong = sap_xep[sort.lstrip('-')]
    qs = qs.order_by(f'-{truong}' if sort.startswith('-') else truong, khoa_phu)
    page = Paginator(qs, 10).get_page(request.GET.get('page'))
    tham_so = request.GET.copy()
    for k in ('page', 'sort', 'xuat'):
        tham_so.pop(k, None)
    return sort, page, tham_so.urlencode()


def _ctx_chu(ds_pgd):
    """Danh sách chọn cho phần lọc khách hàng chủ sở hữu (dùng chung template _loc_chu.html)."""
    return {'hang_loc': HANG_LOC, 'ds_pgd': ds_pgd, 'dich_vu': [(k, nhan) for _, k, nhan in parsers.CN05_DICH_VU]}


def _them_hang(obj):
    obj.nhan_hang = XepHangKH.nhan(obj.nhom_hang or '', obj.ten_hang or '')
    obj.css_hang = lop_hang(obj.nhom_hang, obj.ten_hang) if obj.nhom_hang else ''


def _excel(ten_sheet, ten_file, header, rows):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet(ten_sheet)
    ws.append(header)
    for r in rows:
        ws.append(r)
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="{ten_file}_{date.today():%Y%m%d}.xlsx"'
    wb.save(resp)
    return resp


def _d(x):
    return x.strftime('%d/%m/%Y') if x else ''


# ── Thống kê sổ tiết kiệm (tiền gửi có kỳ hạn) ────────────────────────────────

COT_SO = [  # (khoá sắp xếp, nhãn, lớp ẩn trên màn hẹp)
    ('so_tk', 'Số TK / Sổ', ''), ('ten', 'Khách hàng', ''), ('ky_han', 'Kỳ hạn', ''),
    ('so_du', 'Số dư', ''), ('lai_suat', 'Lãi suất', 'an-lg'), ('ngay_mo', 'Ngày gửi', 'an-xl'),
    ('den_han', 'Đến hạn', ''), ('pgd', 'Điểm GD', 'an-xxl'),
]
SAP_XEP_SO = {'so_tk': 'so_tk', 'ten': 'ten_kh', 'ky_han': 'ky_han', 'so_du': 'so_du', 'lai_suat': 'lai_suat',
              'ngay_mo': 'ngay_mo', 'den_han': 'ngay_den_han', 'pgd': 'pgd'}

DEN_HAN_LOC = [
    ('7', 'Trong 7 ngày tới'), ('30', 'Trong 30 ngày tới'), ('thang_nay', 'Trong tháng này'),
    ('thang_sau', 'Trong tháng sau'), ('qua_han', 'Đã qua ngày đến hạn'), ('khoang', 'Chọn khoảng ngày…'),
]

MAU_SO = [
    ('Đến hạn trong 7 ngày tới', 'den_han=7'),
    ('Đến hạn trong tháng này', 'den_han=thang_nay'),
    ('Đến hạn tháng sau', 'den_han=thang_sau'),
    ('Sổ ≥ 500 triệu đến hạn trong 30 ngày', 'den_han=30&so_du_tu=500000000'),
    ('Đến hạn tháng này, KH chưa có Agribank Plus', 'den_han=thang_nay&dv=agribank_plus&dv_tt=chua'),
    ('Kỳ hạn ngắn (1–3 tháng)', 'ky_han=1&ky_han=2&ky_han=3'),
    ('Kỳ hạn từ 12 tháng, sổ ≥ 1 tỷ', 'ky_han_tu=12&so_du_tu=1000000000'),
    ('Gửi lâu năm (đã gửi từ 36 tháng)', 'gui_tu=36'),
    ('Tiết kiệm gửi góp', 'hinh_thuc=gui_gop'),
]


def _loc_so(g):
    """Bộ lọc sổ tiết kiệm (TK đang hoạt động, kỳ hạn > 0) → (queryset, có lọc gì không)."""
    qs = _gan_chu(TaiKhoanTG.objects.filter(con_hoat_dong=True, ky_han__gt=0))
    loc = []
    qs, c = _loc_ngay(qs, 'ngay_den_han', g.get('den_han'), g.get('dh_tu'), g.get('dh_den')); loc.append(c)
    ky_han = [int(k) for k in g.getlist('ky_han') if k.isdigit()]
    if ky_han:
        qs = qs.filter(ky_han__in=ky_han); loc.append(True)
    qs, c = _loc_khoang(qs, 'ky_han', g.get('ky_han_tu'), None, _so_nguyen); loc.append(c)
    qs, c = _loc_so_thang_tu_ngay(qs, 'ngay_mo', g.get('gui_tu'), g.get('gui_den')); loc.append(c)
    qs, c = _loc_khoang(qs, 'so_du', g.get('so_du_tu'), g.get('so_du_den')); loc.append(c)
    qs, c = _loc_khoang(qs, 'lai_suat', g.get('ls_tu'), g.get('ls_den'), _so_thap_phan); loc.append(c)
    hinh_thuc = g.get('hinh_thuc')
    if hinh_thuc == 'gui_gop':          # mẫu nhanh: mọi hình thức gửi góp
        qs = qs.filter(hinh_thuc__icontains='góp'); loc.append(True)
    elif hinh_thuc:
        qs = qs.filter(hinh_thuc=hinh_thuc); loc.append(True)
    qs, c = _loc_chu(qs, g); loc.append(c)
    return qs, any(loc)


def _them_thong_tin_so(tk, hom_nay):
    tk.con_ngay = (tk.ngay_den_han - hom_nay).days if tk.ngay_den_han else None
    tk.da_gui_thang = parsers.so_thang(tk.ngay_mo, hom_nay) if tk.ngay_mo else None
    _them_hang(tk)


@_yeu_cau_quyen(QUYEN_QUAN_LY)
def thong_ke_so(request):
    qs, co_loc = _loc_so(request.GET)
    tat_ca = TaiKhoanTG.objects.filter(con_hoat_dong=True, ky_han__gt=0)
    hom_nay = date.today()
    if request.GET.get('xuat') == 'excel':
        def dong():
            for i, tk in enumerate(qs.order_by('ngay_den_han', 'so_tk').iterator(chunk_size=2000), 1):
                _them_thong_tin_so(tk, hom_nay)
                yield [i, tk.so_tk, tk.so_so, tk.ma_kh, tk.ten_kh, tk.nhan_hang, tk.loai_tg, tk.hinh_thuc, tk.ky_han,
                       float(tk.so_du), tk.ccy, float(tk.lai_suat), _d(tk.ngay_mo), _d(tk.ngay_den_han),
                       tk.con_ngay, tk.da_gui_thang, tk.pgd, tk.can_bo]
        return _excel('Sổ tiết kiệm', 'SoTietKiem_KH360',
                      ['STT', 'Số TK', 'Số sổ', 'Mã KH', 'Tên KH', 'Hạng KH (BC06)', 'Loại tiền gửi', 'Hình thức',
                       'Kỳ hạn (tháng)', 'Số dư', 'Loại tiền', 'Lãi suất (%)', 'Ngày gửi', 'Ngày đến hạn',
                       'Còn (ngày)', 'Đã gửi (tháng)', 'Điểm GD', 'Cán bộ'], dong())
    ky_han_chon = request.GET.getlist('ky_han')
    ctx = {
        'ky': _ky_moi_nhat(), 'co_loc': co_loc, 'g': request.GET, 'mau': MAU_SO, 'hom_nay': hom_nay,
        'den_han_loc': DEN_HAN_LOC,
        'ds_ky_han': [(k, str(k) in ky_han_chon) for k in
                      tat_ca.order_by('ky_han').values_list('ky_han', flat=True).distinct()],
        'ds_hinh_thuc': tat_ca.exclude(hinh_thuc='').order_by('hinh_thuc').values_list('hinh_thuc', flat=True).distinct(),
        'muc_tien': [(100000000, '100 tr'), (500000000, '500 tr'), (1000000000, '1 tỷ')],
        **_ctx_chu(tat_ca.exclude(pgd='').order_by('pgd').values_list('pgd', flat=True).distinct()),
    }
    if co_loc:
        tong = qs.aggregate(so_so=Count('so_tk'), so_kh=Count('ma_kh', distinct=True), tong_du=Sum('so_du'),
                            lai_x_du=Sum(F('so_du') * F('lai_suat')))
        tong['ls_bq'] = tong['lai_x_du'] / tong['tong_du'] if tong['tong_du'] else None
        ctx['tong'] = tong
        ctx['theo_ky_han'] = (qs.order_by().values('ky_han').annotate(n=Count('so_tk'), t=Sum('so_du'))
                              .order_by('ky_han'))
        dau_thang = hom_nay.replace(day=1)   # sổ đến hạn trước tháng này gộp 1 dòng, còn lại theo từng tháng
        ctx['truoc_thang'] = qs.filter(ngay_den_han__lt=dau_thang).aggregate(n=Count('so_tk'), t=Sum('so_du'))
        ctx['theo_thang'] = (qs.filter(ngay_den_han__gte=dau_thang).order_by()
                             .annotate(thang=TruncMonth('ngay_den_han'))
                             .values('thang').annotate(n=Count('so_tk'), t=Sum('so_du')).order_by('thang')[:24])
        sort, page, qs_base = _trang(request, qs, SAP_XEP_SO, 'den_han', 'so_tk')
        for tk in page.object_list:
            _them_thong_tin_so(tk, hom_nay)
        ctx.update({'page': page, 'sort': sort, 'cot': COT_SO, 'qs_base': qs_base})
    return render(request, 'kh360/thong_ke_so.html', ctx)


# ── Thống kê tiền vay ─────────────────────────────────────────────────────────

COT_VAY = [  # (khoá sắp xếp, nhãn, lớp ẩn trên màn hẹp)
    ('so_gn', 'Số giải ngân', 'an-xl'), ('ten', 'Khách hàng', ''), ('du_no', 'Dư nợ', ''),
    ('giai_ngan', 'Giải ngân', 'an-lg'), ('thoi_han', 'Thời hạn', ''), ('lai_suat', 'Lãi suất', 'an-xl'),
    ('nhom_no', 'Nhóm nợ', ''), ('dao_han', 'Đáo hạn', ''), ('tra_tiep', 'Kỳ trả tiếp', 'an-lg'),
    ('can_bo', 'CB tín dụng', 'an-xxl'),
]
SAP_XEP_VAY = {'so_gn': 'so_giai_ngan', 'ten': 'ten_kh', 'du_no': 'du_no', 'giai_ngan': 'ngay_giai_ngan',
               'thoi_han': 'thoi_han_thang', 'lai_suat': 'lai_suat', 'nhom_no': 'nhom_no',
               'dao_han': 'ngay_dao_han', 'tra_tiep': 'ngay_tra_tiep', 'can_bo': 'can_bo'}

GIAI_NGAN_LOC = [('qua_7', '7 ngày qua'), ('qua_30', '30 ngày qua'), ('thang_nay', 'Trong tháng này'),
                 ('thang_truoc', 'Tháng trước'), ('khoang', 'Chọn khoảng ngày…')]
DAO_HAN_LOC = [('30', 'Trong 30 ngày tới'), ('thang_nay', 'Trong tháng này'), ('thang_sau', 'Trong tháng sau'),
               ('qua_han', 'Đã quá ngày đáo hạn'), ('khoang', 'Chọn khoảng ngày…')]
TRA_TIEP_LOC = [('7', 'Trong 7 ngày tới'), ('30', 'Trong 30 ngày tới'), ('thang_nay', 'Trong tháng này'),
                ('qua_han', 'Đã qua kỳ trả'), ('khoang', 'Chọn khoảng ngày…')]
NHOM_NO = [('01', 'Nhóm 1 – Đủ tiêu chuẩn'), ('02', 'Nhóm 2 – Cần chú ý'), ('03', 'Nhóm 3 – Dưới tiêu chuẩn'),
           ('04', 'Nhóm 4 – Nghi ngờ'), ('05', 'Nhóm 5 – Có khả năng mất vốn')]
THOI_HAN_LOC = [('ngan', 'Ngắn hạn (≤ 12 tháng)'), ('trung', 'Trung hạn (13–60 tháng)'), ('dai', 'Dài hạn (> 60 tháng)')]

MAU_VAY = [
    ('Giải ngân 30 ngày qua, KH chưa có Agribank Plus', 'giai_ngan=qua_30&dv=agribank_plus&dv_tt=chua'),
    ('Giải ngân trong tháng này', 'giai_ngan=thang_nay'),
    ('Kỳ trả nợ trong 7 ngày tới', 'tra_tiep=7'),
    ('Đáo hạn trong 30 ngày tới', 'dao_han=30'),
    ('Đã quá ngày đáo hạn (còn dư nợ)', 'dao_han=qua_han'),
    ('Nợ nhóm 2 trở lên', 'nhom_no=02&nhom_no=03&nhom_no=04&nhom_no=05'),
    ('Nợ xấu (nhóm 3–5)', 'nhom_no=03&nhom_no=04&nhom_no=05'),
    ('Dư nợ ≥ 1 tỷ', 'du_no_tu=1000000000'),
    ('Vay ngắn hạn (≤ 12 tháng)', 'thoi_han_loai=ngan'),
    ('Vay trung, dài hạn (> 12 tháng)', 'thoi_han_tu=13'),
    ('Thấu chi', 'san_pham=thau_chi'),
]


def _loc_vay(g):
    """Bộ lọc khoản vay → (queryset, có lọc gì không). Mặc định chỉ khoản còn dư nợ."""
    qs = KhoanVay.objects.all()
    tinh_trang = g.get('tinh_trang', '')
    if tinh_trang == 'tat_toan':
        qs = qs.filter(con_du_no=False)
    elif tinh_trang != 'tat_ca':
        qs = qs.filter(con_du_no=True)
    qs = _gan_chu(qs)
    loc = [tinh_trang in ('tat_toan', 'tat_ca')]
    qs, c = _loc_khoang(qs, 'du_no', g.get('du_no_tu'), g.get('du_no_den')); loc.append(c)
    qs, c = _loc_khoang(qs, 'thoi_han_thang', g.get('thoi_han_tu'), g.get('thoi_han_den'), _so_nguyen); loc.append(c)
    th = {'ngan': (None, 12), 'trung': (13, 60), 'dai': (61, None)}.get(g.get('thoi_han_loai'))
    if th:
        if th[0]:
            qs = qs.filter(thoi_han_thang__gte=th[0])
        if th[1]:
            qs = qs.filter(thoi_han_thang__lte=th[1])
        loc.append(True)
    qs, c = _loc_so_thang_tu_ngay(qs, 'ngay_giai_ngan', g.get('da_vay_tu'), g.get('da_vay_den')); loc.append(c)
    qs, c = _loc_ngay(qs, 'ngay_giai_ngan', g.get('giai_ngan'), g.get('gn_tu'), g.get('gn_den')); loc.append(c)
    qs, c = _loc_ngay(qs, 'ngay_dao_han', g.get('dao_han'), g.get('dh_tu'), g.get('dh_den')); loc.append(c)
    qs, c = _loc_ngay(qs, 'ngay_tra_tiep', g.get('tra_tiep'), g.get('tt_tu'), g.get('tt_den')); loc.append(c)
    nhom = [n for n in g.getlist('nhom_no') if n in dict(NHOM_NO)]
    if nhom:
        qs = qs.filter(nhom_no__in=nhom); loc.append(True)
    if g.get('san_pham') == 'thau_chi':
        qs = qs.filter(tk_hach_toan=TaiKhoanTG.TK_THAU_CHI); loc.append(True)
    elif g.get('san_pham') == 'vay':
        qs = qs.exclude(tk_hach_toan=TaiKhoanTG.TK_THAU_CHI); loc.append(True)
    for ten in ('loai_vay', 'muc_dich', 'can_bo'):
        if g.get(ten):
            qs = qs.filter(**{ten: g[ten]}); loc.append(True)
    qs, c = _loc_khoang(qs, 'lai_suat', g.get('ls_tu'), g.get('ls_den'), _so_thap_phan); loc.append(c)
    qs, c = _loc_chu(qs, g); loc.append(c)
    return qs, any(loc)


def _them_thong_tin_vay(v, hom_nay):
    v.con_ngay = (v.ngay_dao_han - hom_nay).days if v.ngay_dao_han else None
    v.da_vay_thang = parsers.so_thang(v.ngay_giai_ngan, hom_nay) if v.ngay_giai_ngan else None
    v.la_thau_chi = v.tk_hach_toan == TaiKhoanTG.TK_THAU_CHI
    _them_hang(v)


@_yeu_cau_quyen(QUYEN_QUAN_LY)
def thong_ke_vay(request):
    qs, co_loc = _loc_vay(request.GET)
    hom_nay = date.today()
    if request.GET.get('xuat') == 'excel':
        def dong():
            for i, v in enumerate(qs.order_by('-du_no', 'so_giai_ngan').iterator(chunk_size=2000), 1):
                _them_thong_tin_vay(v, hom_nay)
                yield [i, v.so_giai_ngan, v.ma_kh, v.ten_kh, v.nhan_hang, 'Thấu chi' if v.la_thau_chi else v.loai_vay,
                       v.muc_dich, float(v.du_no), float(v.so_tien_giai_ngan), _d(v.ngay_giai_ngan), v.thoi_han_thang,
                       v.da_vay_thang, float(v.lai_suat), v.nhom_no, _d(v.ngay_dao_han), v.con_ngay,
                       _d(v.ngay_tra_tiep), float(v.so_tien_tra_tiep), v.can_bo, v.tk_nhan_giai_ngan, v.pgd]
        return _excel('Tiền vay', 'TienVay_KH360',
                      ['STT', 'Số giải ngân', 'Mã KH', 'Tên KH', 'Hạng KH (BC06)', 'Loại vay', 'Mục đích', 'Dư nợ',
                       'Số tiền giải ngân', 'Ngày giải ngân', 'Thời hạn (tháng)', 'Đã vay (tháng)', 'Lãi suất (%)',
                       'Nhóm nợ', 'Ngày đáo hạn', 'Còn (ngày)', 'Kỳ trả tiếp', 'Số tiền trả tiếp', 'CB tín dụng',
                       'TK nhận giải ngân', 'Điểm GD'], dong())
    tat_ca = KhoanVay.objects.filter(con_du_no=True)
    ds = lambda f: tat_ca.exclude(**{f: ''}).order_by(f).values_list(f, flat=True).distinct()
    ctx = {
        'ky': _ky_moi_nhat(), 'co_loc': co_loc, 'g': request.GET, 'mau': MAU_VAY, 'hom_nay': hom_nay,
        'loc_ngay': [
            {'ten': ten, 'nhan': nhan, 'ds': ds_chon, 'chon': request.GET.get(ten, ''),
             'tu_ten': tu, 'tu': request.GET.get(tu, ''), 'den_ten': den, 'den': request.GET.get(den, '')}
            for ten, nhan, ds_chon, tu, den in (
                ('giai_ngan', 'Ngày giải ngân', GIAI_NGAN_LOC, 'gn_tu', 'gn_den'),
                ('dao_han', 'Ngày đáo hạn', DAO_HAN_LOC, 'dh_tu', 'dh_den'),
                ('tra_tiep', 'Kỳ trả nợ tiếp theo', TRA_TIEP_LOC, 'tt_tu', 'tt_den'))],
        'thoi_han_loc': THOI_HAN_LOC,
        'nhom_no_loc': [(k, n, k in request.GET.getlist('nhom_no')) for k, n in NHOM_NO],
        'ds_loai_vay': ds('loai_vay'), 'ds_muc_dich': ds('muc_dich'), 'ds_can_bo': ds('can_bo'),
        'muc_tien': [(100000000, '100 tr'), (500000000, '500 tr'), (1000000000, '1 tỷ'), (5000000000, '5 tỷ')],
        **_ctx_chu(ds('pgd')),
    }
    if co_loc:
        tong = qs.aggregate(so_mon=Count('so_giai_ngan'), so_kh=Count('ma_kh', distinct=True), tong_no=Sum('du_no'),
                            lai_x_no=Sum(F('du_no') * F('lai_suat')),
                            no_xau=Sum('du_no', filter=Q(nhom_no__in=['03', '04', '05'])),
                            mon_nhom2=Count('so_giai_ngan', filter=Q(nhom_no__in=['02', '03', '04', '05'])))
        tong['ls_bq'] = tong['lai_x_no'] / tong['tong_no'] if tong['tong_no'] else None
        ctx['tong'] = tong
        nhan_nhom = dict(NHOM_NO)
        ctx['theo_nhom'] = [{**r, 'nhan': nhan_nhom.get(r['nhom_no'], r['nhom_no'] or '—')} for r in
                            qs.order_by().values('nhom_no').annotate(n=Count('so_giai_ngan'), t=Sum('du_no'))
                            .order_by('nhom_no')]
        ctx['theo_thoi_han'] = [
            {'nhan': nhan, **qs.filter(**dk).aggregate(n=Count('so_giai_ngan'), t=Sum('du_no'))}
            for nhan, dk in (('Ngắn hạn (≤ 12 tháng)', {'thoi_han_thang__lte': 12}),
                             ('Trung hạn (13–60 tháng)', {'thoi_han_thang__gte': 13, 'thoi_han_thang__lte': 60}),
                             ('Dài hạn (> 60 tháng)', {'thoi_han_thang__gt': 60}))]
        ctx['theo_can_bo'] = (qs.order_by().values('can_bo').annotate(n=Count('so_giai_ngan'), t=Sum('du_no'))
                              .order_by('-t')[:20])
        sort, page, qs_base = _trang(request, qs, SAP_XEP_VAY, '-du_no', 'so_giai_ngan')
        for v in page.object_list:
            _them_thong_tin_vay(v, hom_nay)
        ctx.update({'page': page, 'sort': sort, 'cot': COT_VAY, 'qs_base': qs_base})
    return render(request, 'kh360/thong_ke_vay.html', ctx)
