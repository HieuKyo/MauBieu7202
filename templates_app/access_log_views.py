"""
Thống kê lượt truy cập menu theo ngày / tuần / tháng — chỉ Superuser.
Dữ liệu do MenuAccessLogMiddleware ghi (templates_app/middleware.py).
"""
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Max
from django.db.models.functions import TruncDate, TruncMonth, TruncWeek
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from .models import MenuAccessLog

# Lượt truy cập là dữ liệu cá nhân của nhân viên → chỉ giữ trong thời hạn cần cho thống kê
LUU_TOI_DA_NGAY = 400

# kiểu kỳ: (tên hiển thị, số kỳ mặc định, hàm gom nhóm)
KIEU_KY = {
    'ngay': ('Ngày', 14, TruncDate),
    'tuan': ('Tuần', 12, TruncWeek),
    'thang': ('Tháng', 12, TruncMonth),
}


def _cac_ky(kieu, so_ky, hom_nay):
    """Danh sách ngày đầu của từng kỳ, cũ → mới (tuần bắt đầu thứ Hai)."""
    if kieu == 'ngay':
        return [hom_nay - timedelta(days=i) for i in range(so_ky - 1, -1, -1)]
    if kieu == 'tuan':
        dau_tuan = hom_nay - timedelta(days=hom_nay.weekday())
        return [dau_tuan - timedelta(weeks=i) for i in range(so_ky - 1, -1, -1)]
    ky = []
    nam, thang = hom_nay.year, hom_nay.month
    for _ in range(so_ky):
        ky.append(date(nam, thang, 1))
        nam, thang = (nam, thang - 1) if thang > 1 else (nam - 1, 12)
    return ky[::-1]


def _nhan_ky(kieu, d):
    if kieu == 'ngay':
        return d.strftime('%d/%m')
    if kieu == 'tuan':
        return f"{d:%d/%m}–{d + timedelta(days=6):%d/%m}"
    return d.strftime('%m/%Y')


def _duong_dan(view_name, path_gan_nhat):
    """URL của trang (để khớp tên menu); trang có tham số thì dùng đường dẫn đã ghi."""
    try:
        return reverse(view_name)
    except NoReverseMatch:
        return path_gan_nhat


@login_required
def access_stats_view(request):
    if not request.user.is_superuser:
        messages.error(request, 'Bạn không có quyền truy cập trang này!')
        return redirect('dashboard')

    MenuAccessLog.objects.filter(accessed_at__lt=timezone.now() - timedelta(days=LUU_TOI_DA_NGAY)).delete()

    kieu = request.GET.get('ky') if request.GET.get('ky') in KIEU_KY else 'ngay'
    ten_kieu, so_ky_mac_dinh, trunc = KIEU_KY[kieu]
    try:
        so_ky = min(max(int(request.GET.get('so_ky', so_ky_mac_dinh)), 1), 60)
    except ValueError:
        so_ky = so_ky_mac_dinh
    user_id = request.GET.get('user', '')

    cac_ky = _cac_ky(kieu, so_ky, timezone.localdate())
    tu_luc = timezone.make_aware(datetime.combine(cac_ky[0], time.min))
    qs = MenuAccessLog.objects.filter(accessed_at__gte=tu_luc)
    if user_id.isdigit():
        qs = qs.filter(user_id=int(user_id))

    # Số lượt theo (trang, kỳ)
    theo_ky = {}
    for r in qs.annotate(ky=trunc('accessed_at')).values('view_name', 'ky').annotate(c=Count('id')):
        ky = r['ky'].date() if isinstance(r['ky'], datetime) else r['ky']
        theo_ky[(r['view_name'], ky)] = r['c']

    trang = []
    for r in (qs.values('view_name')
              .annotate(tong=Count('id'), so_nguoi=Count('user', distinct=True),
                        path=Max('path'), lan_cuoi=Max('accessed_at'))
              .order_by('-tong')):
        trang.append({
            'view_name': r['view_name'],
            'url': _duong_dan(r['view_name'], r['path']),
            'tong': r['tong'],
            'so_nguoi': r['so_nguoi'],
            'lan_cuoi': r['lan_cuoi'],
            'luot': [theo_ky.get((r['view_name'], k), 0) for k in cac_ky],
        })

    nguoi_dung = (qs.values('user_id', 'user__username', 'user__profile__full_name')
                  .annotate(tong=Count('id'), so_trang=Count('view_name', distinct=True), lan_cuoi=Max('accessed_at'))
                  .order_by('-tong'))

    return render(request, 'templates_app/access_stats.html', {
        'kieu': kieu,
        'ten_kieu': ten_kieu,
        'so_ky': so_ky,
        'kieu_ky': [(k, v[0]) for k, v in KIEU_KY.items()],
        'nhan_ky': [_nhan_ky(kieu, k) for k in cac_ky],
        'tong_ky': [sum(t['luot'][i] for t in trang) for i in range(len(cac_ky))],
        'tong': sum(t['tong'] for t in trang),
        'trang': trang,
        'nguoi_dung': nguoi_dung,
        'users': User.objects.filter(is_active=True).order_by('username'),
        'user_id': user_id,
        'luu_toi_da_ngay': LUU_TOI_DA_NGAY,
    })
