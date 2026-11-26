"""
Chứng từ → tab "Giao/Nhận chứng từ": theo dõi giao nhận từng tập chứng từ (bìa chứng từ).

Luồng (mỗi bước ghi BiaGiaoNhanLog: ai, chuyển cho ai, lúc nào, lý do):
  GDV đang giữ ─GDV giao KSV─▶ Chờ KSV nhận ─KSV nhận─▶ KSV đang ký ─KSV ký xong─▶ KSV trả chứng từ chờ GĐ ký
  ─GDV (GĐ đã ký) giao Hậu kiểm─▶ Chờ Hậu kiểm nhận ─HKV xác nhận─▶ Hậu kiểm đã nhận (đang kiểm tra)
  ─HKV─▶ Hoàn thành chứng từ  |  ─HKV─▶ HKV trả chứng từ để GDV sửa ─GDV sửa xong giao lại Hậu kiểm (hoặc KSV)─▶ …
  KSV trả lại (chưa ký) → GDV đang giữ; GDV thu hồi khi bên nhận chưa nhận (về trạng thái trước khi giao).

KSV = Trưởng/Phó phòng Kế toán & Ngân quỹ cùng đơn vị; Hậu kiểm = người dùng có nghiệp vụ Hậu kiểm viên.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .bia_chung_tu_views import MANAGER_POSITIONS, _gdv_branch, _manager_branch, _parse_date
from .models import GIAO_NHAN_CHOICES, BiaChungTu, BiaGiaoNhanLog, UserProfile

TRANG_THAI = dict(GIAO_NHAN_CHOICES)
DANG_XU_LY = ('cho_ksv_nhan', 'ksv_dang_ky', 'cho_hk_nhan', 'hk_da_nhan')  # đang chờ KSV / Hậu kiểm xử lý
GDV_CAN_LAM = ('cho_gd_ky', 'hk_tra_sua')  # GDV cần đem GĐ ký / sửa chứng từ

# hành động: (ai làm: 'gdv' = GDV của tập | 'xu_ly' = người đang giữ, từ trạng thái, đến trạng thái,
#             cần chọn người nhận: 'ksv' | 'hk' | None, bắt buộc lý do, nhãn)
HANH_DONG = {
    'giao_ksv': ('gdv', {'gdv_giu', 'hk_tra_sua'}, 'cho_ksv_nhan', 'ksv', False, 'GDV giao KSV'),
    'giao_hk': ('gdv', {'cho_gd_ky', 'hk_tra_sua'}, 'cho_hk_nhan', 'hk', False, 'GDV giao Hậu kiểm (GĐ đã ký / đã sửa)'),
    'thu_hoi': ('gdv', {'cho_ksv_nhan', 'cho_hk_nhan'}, None, None, False, 'GDV thu hồi (bên nhận chưa nhận)'),
    'ksv_nhan': ('xu_ly', {'cho_ksv_nhan'}, 'ksv_dang_ky', None, False, 'KSV đã nhận'),
    'ksv_ky': ('xu_ly', {'ksv_dang_ky'}, 'cho_gd_ky', None, False, 'KSV đã ký – trả GDV chờ GĐ ký'),
    'ksv_tra': ('xu_ly', {'cho_ksv_nhan', 'ksv_dang_ky'}, 'gdv_giu', None, True, 'KSV trả lại (chưa ký)'),
    'hk_nhan': ('xu_ly', {'cho_hk_nhan'}, 'hk_da_nhan', None, False, 'Hậu kiểm xác nhận đã nhận'),
    'hk_hoan_thanh': ('xu_ly', {'cho_hk_nhan', 'hk_da_nhan'}, 'hoan_thanh', None, False, 'Hoàn thành chứng từ'),
    'hk_tra': ('xu_ly', {'cho_hk_nhan', 'hk_da_nhan'}, 'hk_tra_sua', None, True, 'HKV trả chứng từ để GDV sửa'),
}
THU_HOI_VE = {'cho_ksv_nhan': 'gdv_giu', 'cho_hk_nhan': 'cho_gd_ky'}  # khi không có lịch sử
VE_GDV = ('gdv_giu', 'cho_gd_ky', 'hk_tra_sua')  # trạng thái tập đang ở GDV


def _ten(user):
    if not user:
        return ''
    p = getattr(user, 'profile', None)
    return (getattr(p, 'full_name', '') or user.get_full_name() or user.username).strip()


def ds_ksv(branch):
    return [(p.user_id, p.full_name or p.user.username) for p in UserProfile.objects.filter(
        branch=branch, department='KE_TOAN', position__in=MANAGER_POSITIONS, user__is_active=True,
    ).select_related('user').order_by('full_name')]


def ds_hau_kiem(branch):
    """Hậu kiểm viên (cùng đơn vị lên đầu)."""
    rows = UserProfile.objects.filter(job_function='HAU_KIEM_VIEN', user__is_active=True).select_related('user')
    return [(p.user_id, (p.full_name or p.user.username) + ('' if p.branch == branch else f' ({p.branch})'))
            for p in sorted(rows, key=lambda p: (p.branch != branch, p.full_name))]


def _la_hau_kiem(user):
    return getattr(getattr(user, 'profile', None), 'job_function', '') == 'HAU_KIEM_VIEN'


def so_cho_xu_ly(user):
    """Số tập đang chờ user (KSV/Hậu kiểm) xử lý + số tập GDV cần đem GĐ ký."""
    return (BiaChungTu.objects.filter(nguoi_xu_ly=user, trang_thai_gn__in=DANG_XU_LY).count()
            + BiaChungTu.objects.filter(gdv=user, trang_thai_gn__in=GDV_CAN_LAM).count())


def _pham_vi_tra_cuu(user):
    qs = BiaChungTu.objects.exclude(trang_thai_gn='')
    if user.is_superuser or _la_hau_kiem(user):
        return qs
    branch = _manager_branch(user)
    if branch:
        return qs.filter(branch=branch)
    return qs.filter(Q(gdv=user) | Q(nguoi_xu_ly=user) | Q(lich_su_gn__nguoi_nhan=user)).distinct()


def _gan_thong_tin(bias):
    """Gắn .dang_o (người đang giữ) và .lan_cuoi (log cuối) cho danh sách bìa."""
    bias = list(bias)
    last = {}
    for lg in BiaGiaoNhanLog.objects.filter(bia__in=bias).select_related('nguoi_thuc_hien__profile', 'nguoi_nhan__profile'):
        last[lg.bia_id] = lg
    for b in bias:
        b.dang_o = _ten(b.nguoi_xu_ly) if b.trang_thai_gn in DANG_XU_LY + ('hoan_thanh',) else _ten(b.gdv)
        b.lan_cuoi = last.get(b.pk)
    return bias


TABS = [('cho_toi', 'Chờ tôi xử lý'), ('cua_toi', 'Tập chứng từ của tôi'), ('tra_cuu', 'Tra cứu')]


@login_required
def bia_giao_nhan(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    branch = getattr(profile, 'branch', '')
    cho_toi = BiaChungTu.objects.filter(nguoi_xu_ly=user, trang_thai_gn__in=DANG_XU_LY)
    cua_toi = BiaChungTu.objects.filter(gdv=user).exclude(trang_thai_gn='')

    tab = request.GET.get('tab')
    if tab not in dict(TABS):
        tab = 'cho_toi' if cho_toi.exists() else ('cua_toi' if cua_toi.exclude(trang_thai_gn='hoan_thanh').exists() else 'tra_cuu')

    ctx = {
        'tab': tab, 'tabs': TABS, 'an_tao_bia': not (_manager_branch(user) or _gdv_branch(user)),
        'so_cho_toi': cho_toi.count(),
        'so_cho_gd_ky': cua_toi.filter(trang_thai_gn__in=GDV_CAN_LAM).count(),
        'trang_thai_choices': GIAO_NHAN_CHOICES[1:],
        'next': request.get_full_path(),
    }
    sel = ('gdv__profile', 'nguoi_xu_ly__profile')
    if tab == 'cho_toi':
        ctx['bias'] = _gan_thong_tin(cho_toi.select_related(*sel).order_by('trang_thai_gn', 'ngay_chung_tu', 'so_ho_so'))
    elif tab == 'cua_toi':
        an_xong = request.GET.get('xong') != '1'
        qs = cua_toi.exclude(trang_thai_gn='hoan_thanh') if an_xong else cua_toi
        ctx['bias'] = _gan_thong_tin(qs.select_related(*sel).order_by('-ngay_chung_tu', 'so_ho_so')[:300])
        ctx['an_xong'] = an_xong
        ctx['ksv_choices'] = ds_ksv(branch)
        ctx['hk_choices'] = ds_hau_kiem(branch)
    else:
        g = request.GET
        qs = _pham_vi_tra_cuu(user).select_related(*sel)
        f = {k: g.get(k, '').strip() for k in ('tu_ngay', 'den_ngay', 'trang_thai', 'q', 'gdv')}
        if _parse_date(f['tu_ngay']):
            qs = qs.filter(ngay_chung_tu__gte=_parse_date(f['tu_ngay']))
        if _parse_date(f['den_ngay']):
            qs = qs.filter(ngay_chung_tu__lte=_parse_date(f['den_ngay']))
        if f['trang_thai'] and f['trang_thai'] in TRANG_THAI:
            qs = qs.filter(trang_thai_gn=f['trang_thai'])
        if f['q']:
            qs = qs.filter(so_ho_so__icontains=f['q'])
        if f['gdv']:
            qs = qs.filter(Q(gdv__profile__full_name__icontains=f['gdv']) | Q(user_ipcas__icontains=f['gdv']))
        page = Paginator(qs.order_by('-ngay_chung_tu', 'so_ho_so'), 50).get_page(g.get('page'))
        bias = _gan_thong_tin(page)
        logs = {}
        for lg in (BiaGiaoNhanLog.objects.filter(bia__in=bias)
                   .select_related('nguoi_thuc_hien__profile', 'nguoi_nhan__profile')):
            lg.ten_thuc_hien, lg.ten_nhan = _ten(lg.nguoi_thuc_hien), _ten(lg.nguoi_nhan)
            logs.setdefault(lg.bia_id, []).append(lg)
        for b in bias:
            b.lich_su = logs.get(b.pk, [])
        query = g.copy()
        query.pop('page', None)
        ctx.update({'bias': bias, 'page': page, 'f': f, 'query': query.urlencode()})
    return render(request, 'templates_app/bia_chung_tu/giao_nhan.html', ctx)


@login_required
@require_POST
def bia_giao_nhan_xu_ly(request):
    """Thực hiện 1 hành động cho nhiều tập đã chọn; tập nào không hợp lệ thì bỏ qua và báo lại."""
    user = request.user
    hd = request.POST.get('hanh_dong')
    nxt = request.POST.get('next', '')
    back = redirect(nxt if nxt.startswith('/') and not nxt.startswith('//') else 'bia_chung_tu_giao_nhan')
    if hd not in HANH_DONG:
        messages.error(request, 'Hành động không hợp lệ.')
        return back
    vai_tro, tu, den, can_nguoi, can_ly_do, nhan = HANH_DONG[hd]
    ly_do = request.POST.get('ly_do', '').strip()[:300]
    if can_ly_do and not ly_do:
        messages.error(request, 'Vui lòng nhập lý do trả lại.')
        return back
    ids = [int(i) for i in request.POST.getlist('ids') if i.isdigit()]
    if not ids:
        messages.error(request, 'Chưa chọn tập chứng từ nào.')
        return back

    nguoi_nhan = None
    if can_nguoi:
        uid = request.POST.get(f'nguoi_nhan_{can_nguoi}', '')
        branch = getattr(getattr(user, 'profile', None), 'branch', '')
        hop_le = {u for u, _ in (ds_ksv(branch) if can_nguoi == 'ksv' else ds_hau_kiem(branch))}
        nguoi_nhan = User.objects.filter(pk=uid).first() if uid.isdigit() and int(uid) in hop_le else None
        if not nguoi_nhan:
            messages.error(request, 'Vui lòng chọn ' + ('KSV (Trưởng/Phó phòng)' if can_nguoi == 'ksv' else 'Hậu kiểm viên') + ' nhận chứng từ.')
            return back

    ok, bo_qua = [], []
    with transaction.atomic():
        for bia in BiaChungTu.objects.select_for_update().filter(pk__in=ids):
            dung_nguoi = bia.gdv_id == user.pk if vai_tro == 'gdv' else bia.nguoi_xu_ly_id == user.pk
            if not dung_nguoi or bia.trang_thai_gn not in tu:
                bo_qua.append(bia.so_ho_so)
                continue
            cu = bia.trang_thai_gn
            if hd == 'thu_hoi':  # về trạng thái trước lần giao gần nhất (vd HKV trả sửa → giao lại → thu hồi)
                lan_giao = bia.lich_su_gn.filter(den_trang_thai=cu).order_by('-thoi_diem', '-id').first()
                moi = lan_giao.tu_trang_thai if lan_giao and lan_giao.tu_trang_thai in VE_GDV else THU_HOI_VE[cu]
            else:
                moi = den
            if can_nguoi:
                bia.nguoi_xu_ly = nguoi_nhan
            elif moi in VE_GDV:
                bia.nguoi_xu_ly = None
            bia.trang_thai_gn = moi
            bia.save(update_fields=['trang_thai_gn', 'nguoi_xu_ly', 'updated_at'])
            BiaGiaoNhanLog.objects.create(
                bia=bia, tu_trang_thai=cu, den_trang_thai=moi, hanh_dong=nhan,
                nguoi_thuc_hien=user, nguoi_nhan=nguoi_nhan or (bia.gdv if moi in VE_GDV else None),
                ghi_chu=ly_do,
            )
            ok.append(bia.so_ho_so)
    if ok:
        messages.success(request, f'{nhan}: {len(ok)} tập ({", ".join(ok[:10])}{"…" if len(ok) > 10 else ""}).')
    if bo_qua:
        messages.warning(request, f'Bỏ qua {len(bo_qua)} tập không đúng trạng thái / không thuộc quyền của bạn: '
                                  f'{", ".join(bo_qua[:10])}{"…" if len(bo_qua) > 10 else ""}.')
    return back
