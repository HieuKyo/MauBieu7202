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
    'so_du': 'tong_so_du', 'du_no': 'tong_du_no', 'pgd': 'pgd',
}


COT_BANG = [  # (khoá sắp xếp, nhãn, lớp ẩn trên màn hẹp — xem _bang_kh.html)
    ('ma_kh', 'Mã KH', 'an-md'), ('ten', 'Tên KH', ''), ('loai', 'Loại', 'an-lg'), ('hang', 'Hạng', ''),
    ('so_du', 'Số dư TG', ''), ('du_no', 'Dư nợ', 'an-sm'), ('pgd', 'Điểm GD', 'an-xxl'),
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


def _bang_kh(request, qs):
    """Ngữ cảnh cho bảng KH dùng chung (_bang_kh.html): sắp xếp + 10 dòng/trang."""
    sort, qs = _sap_xep(request, qs)
    page = Paginator(qs, 10).get_page(request.GET.get('page'))
    for kh in page.object_list:
        kh.nhan_hang = XepHangKH.nhan(kh.nhom_hang or '', kh.ten_hang or '')
        kh.css_hang = lop_hang(kh.nhom_hang, kh.ten_hang) if kh.nhom_hang else ''
    tham_so = request.GET.copy()
    for k in ('page', 'sort', 'xuat'):
        tham_so.pop(k, None)
    return {'page': page, 'sort': sort, 'cot': COT_BANG, 'qs_base': tham_so.urlencode()}


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
    so_du_tu, so_du_den = _so_tien(g.get('so_du_tu')), _so_tien(g.get('so_du_den'))
    if so_du_tu is not None:
        qs, co_loc = qs.filter(tong_so_du__gte=so_du_tu), True
    if so_du_den is not None:
        qs, co_loc = qs.filter(tong_so_du__lte=so_du_den), True
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
        tong = qs.aggregate(so_kh=Count('ma_kh'), so_du=Sum('tong_so_du'), du_no=Sum('tong_du_no'),
                            to_chuc=Count('ma_kh', filter=Q(la_to_chuc=True)))
        ctx['tong'] = tong
        ctx.update(_bang_kh(request, qs))
    return render(request, 'kh360/thong_ke.html', ctx)


def _xuat_excel_thong_ke(qs):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet('Thống kê KH 360')
    ws.append(['STT', 'Mã KH', 'Tên KH', 'Loại', 'Hạng (BC06)', 'CCCD/Giấy tờ', 'Ngày sinh', 'SĐT', 'Địa chỉ',
               'Điểm GD', 'Số dư TG (VND)', 'Dư nợ', 'Dịch vụ đã có'])
    nhan_dv = parsers.NHAN_DICH_VU
    for i, kh in enumerate(qs.iterator(chunk_size=2000), 1):
        ws.append([
            i, kh.ma_kh, kh.ten, 'Tổ chức' if kh.la_to_chuc else 'Cá nhân',
            XepHangKH.nhan(kh.nhom_hang or '', kh.ten_hang or ''), kh.cccd,
            kh.ngay_sinh.strftime('%d/%m/%Y') if kh.ngay_sinh else '', kh.sdt, kh.dia_chi, kh.pgd,
            float(kh.tong_so_du), float(kh.tong_du_no),
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


def _loc_so(g):
    """Bộ lọc sổ tiết kiệm (TK đang hoạt động, kỳ hạn > 0) → (queryset, có lọc gì không)."""
    hom_nay = date.today()
    xh = XepHangKH.objects.filter(ma_kh=OuterRef('ma_kh'))
    kh = KhachHang.objects.filter(ma_kh=OuterRef('ma_kh'))
    qs = TaiKhoanTG.objects.filter(con_hoat_dong=True, ky_han__gt=0).annotate(
        nhom_hang=Subquery(xh.values('nhom_cn')[:1]), ten_hang=Subquery(xh.values('hang_cn')[:1]),
        la_to_chuc=Subquery(kh.values('la_to_chuc')[:1]),
    )
    co_loc = False

    den_han = g.get('den_han')
    if den_han:
        co_loc = True
        dau_thang = hom_nay.replace(day=1)
        if den_han in ('7', '30'):
            qs = qs.filter(ngay_den_han__gte=hom_nay, ngay_den_han__lte=hom_nay + relativedelta(days=int(den_han)))
        elif den_han == 'thang_nay':
            qs = qs.filter(ngay_den_han__gte=dau_thang, ngay_den_han__lt=dau_thang + relativedelta(months=1))
        elif den_han == 'thang_sau':
            qs = qs.filter(ngay_den_han__gte=dau_thang + relativedelta(months=1),
                           ngay_den_han__lt=dau_thang + relativedelta(months=2))
        elif den_han == 'qua_han':
            qs = qs.filter(ngay_den_han__lt=hom_nay)
        elif den_han == 'khoang':
            tu, den = _ngay_iso(g.get('dh_tu')), _ngay_iso(g.get('dh_den'))
            if tu:
                qs = qs.filter(ngay_den_han__gte=tu)
            if den:
                qs = qs.filter(ngay_den_han__lte=den)

    ky_han = [int(k) for k in g.getlist('ky_han') if k.isdigit()]
    if ky_han:
        qs, co_loc = qs.filter(ky_han__in=ky_han), True
    ky_han_tu = _so_nguyen(g.get('ky_han_tu'))
    if ky_han_tu is not None:
        qs, co_loc = qs.filter(ky_han__gte=ky_han_tu), True

    gui_tu, gui_den = _so_nguyen(g.get('gui_tu')), _so_nguyen(g.get('gui_den'))   # số tháng đã gửi
    if gui_tu is not None:
        qs, co_loc = qs.filter(ngay_mo__lte=hom_nay - relativedelta(months=gui_tu)), True
    if gui_den is not None:
        qs, co_loc = qs.filter(ngay_mo__gt=hom_nay - relativedelta(months=gui_den + 1)), True

    so_du_tu, so_du_den = _so_tien(g.get('so_du_tu')), _so_tien(g.get('so_du_den'))
    if so_du_tu is not None:
        qs, co_loc = qs.filter(so_du__gte=so_du_tu), True
    if so_du_den is not None:
        qs, co_loc = qs.filter(so_du__lte=so_du_den), True
    ls_tu, ls_den = _so_thap_phan(g.get('ls_tu')), _so_thap_phan(g.get('ls_den'))
    if ls_tu is not None:
        qs, co_loc = qs.filter(lai_suat__gte=ls_tu), True
    if ls_den is not None:
        qs, co_loc = qs.filter(lai_suat__lte=ls_den), True

    hinh_thuc = g.get('hinh_thuc')
    if hinh_thuc == 'gui_gop':          # mẫu nhanh: mọi hình thức gửi góp
        qs, co_loc = qs.filter(hinh_thuc__icontains='góp'), True
    elif hinh_thuc:
        qs, co_loc = qs.filter(hinh_thuc=hinh_thuc), True
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


def _sap_xep_so(request, qs):
    sort = request.GET.get('sort', 'den_han')
    if sort.lstrip('-') not in SAP_XEP_SO:
        sort = 'den_han'
    truong = SAP_XEP_SO[sort.lstrip('-')]
    return sort, qs.order_by(f'-{truong}' if sort.startswith('-') else truong, 'so_tk')


def _them_thong_tin_so(tk, hom_nay):
    tk.con_ngay = (tk.ngay_den_han - hom_nay).days if tk.ngay_den_han else None
    da_gui = relativedelta(hom_nay, tk.ngay_mo) if tk.ngay_mo else None
    tk.da_gui_thang = da_gui.years * 12 + da_gui.months if da_gui else None
    tk.nhan_hang = XepHangKH.nhan(tk.nhom_hang or '', tk.ten_hang or '')
    tk.css_hang = lop_hang(tk.nhom_hang, tk.ten_hang) if tk.nhom_hang else ''


@_yeu_cau_quyen(QUYEN_QUAN_LY)
def thong_ke_so(request):
    qs, co_loc = _loc_so(request.GET)
    if request.GET.get('xuat') == 'excel':
        return _xuat_excel_so(_sap_xep_so(request, qs)[1])
    tat_ca = TaiKhoanTG.objects.filter(con_hoat_dong=True, ky_han__gt=0)
    ky_han_chon = request.GET.getlist('ky_han')
    ctx = {
        'ky': _ky_moi_nhat(), 'co_loc': co_loc, 'g': request.GET, 'mau': MAU_SO, 'hom_nay': date.today(),
        'den_han_loc': DEN_HAN_LOC, 'hang_loc': HANG_LOC,
        'ds_ky_han': [(k, str(k) in ky_han_chon) for k in
                      tat_ca.order_by('ky_han').values_list('ky_han', flat=True).distinct()],
        'ds_hinh_thuc': tat_ca.exclude(hinh_thuc='').order_by('hinh_thuc').values_list('hinh_thuc', flat=True).distinct(),
        'ds_pgd': tat_ca.exclude(pgd='').order_by('pgd').values_list('pgd', flat=True).distinct(),
        'dich_vu': [(k, nhan) for _, k, nhan in parsers.CN05_DICH_VU],
        'muc_tien': [(100000000, '100 tr'), (500000000, '500 tr'), (1000000000, '1 tỷ')],
    }
    if co_loc:
        tong = qs.aggregate(so_so=Count('so_tk'), so_kh=Count('ma_kh', distinct=True), tong_du=Sum('so_du'),
                            lai_x_du=Sum(F('so_du') * F('lai_suat')))
        tong['ls_bq'] = tong['lai_x_du'] / tong['tong_du'] if tong['tong_du'] else None
        ctx['tong'] = tong
        ctx['theo_ky_han'] = (qs.order_by().values('ky_han').annotate(n=Count('so_tk'), t=Sum('so_du'))
                              .order_by('ky_han'))
        dau_thang = date.today().replace(day=1)   # sổ đến hạn trước tháng này gộp 1 dòng, còn lại theo từng tháng
        ctx['truoc_thang'] = qs.filter(ngay_den_han__lt=dau_thang).aggregate(n=Count('so_tk'), t=Sum('so_du'))
        ctx['theo_thang'] = (qs.filter(ngay_den_han__gte=dau_thang).order_by()
                             .annotate(thang=TruncMonth('ngay_den_han'))
                             .values('thang').annotate(n=Count('so_tk'), t=Sum('so_du')).order_by('thang')[:24])
        sort, qs = _sap_xep_so(request, qs)
        page = Paginator(qs, 10).get_page(request.GET.get('page'))
        hom_nay = date.today()
        for tk in page.object_list:
            _them_thong_tin_so(tk, hom_nay)
        tham_so = request.GET.copy()
        for k in ('page', 'sort', 'xuat'):
            tham_so.pop(k, None)
        ctx.update({'page': page, 'sort': sort, 'cot': COT_SO, 'qs_base': tham_so.urlencode()})
    return render(request, 'kh360/thong_ke_so.html', ctx)


def _xuat_excel_so(qs):
    wb = openpyxl.Workbook(write_only=True)
    ws = wb.create_sheet('Sổ tiết kiệm')
    ws.append(['STT', 'Số TK', 'Số sổ', 'Mã KH', 'Tên KH', 'Hạng KH (BC06)', 'Loại tiền gửi', 'Hình thức',
               'Kỳ hạn (tháng)', 'Số dư', 'Loại tiền', 'Lãi suất (%)', 'Ngày gửi', 'Ngày đến hạn',
               'Còn (ngày)', 'Đã gửi (tháng)', 'Điểm GD', 'Cán bộ'])
    hom_nay = date.today()
    for i, tk in enumerate(qs.iterator(chunk_size=2000), 1):
        _them_thong_tin_so(tk, hom_nay)
        ws.append([
            i, tk.so_tk, tk.so_so, tk.ma_kh, tk.ten_kh, tk.nhan_hang, tk.loai_tg, tk.hinh_thuc, tk.ky_han,
            float(tk.so_du), tk.ccy, float(tk.lai_suat),
            tk.ngay_mo.strftime('%d/%m/%Y') if tk.ngay_mo else '',
            tk.ngay_den_han.strftime('%d/%m/%Y') if tk.ngay_den_han else '',
            tk.con_ngay, tk.da_gui_thang, tk.pgd, tk.can_bo,
        ])
    resp = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    resp['Content-Disposition'] = f'attachment; filename="SoTietKiem_KH360_{date.today():%Y%m%d}.xlsx"'
    wb.save(resp)
    return resp
