"""
Đăng ký chỉ tiêu Huy động vốn — Dashboard, Báo cáo, Đăng ký khách hàng.

Module độc lập: mỗi cán bộ tự đăng ký chỉ tiêu HĐV cho khách hàng của mình,
Dashboard/Báo cáo tổng hợp theo toàn chi nhánh. Không tích hợp với công cụ
đối chiếu HĐV/IPCAS (huy_dong_von_report).
"""
import io
import json
from datetime import date, datetime, timedelta

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Max, Min, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import BranchConfig, HDVImportRecord, HDVRegistration, UserProfile
from .report_views import _find_col, _hdv_clean_str, _hdv_remove_leading_zeros, _hdv_to_float


def _current_month_range(today):
    """Trả về (ngày đầu tháng, ngày cuối tháng) chứa `today`."""
    start = today.replace(day=1)
    next_month_first = date(today.year + 1, 1, 1) if today.month == 12 else date(today.year, today.month + 1, 1)
    return start, next_month_first - timedelta(days=1)


def _default_date_range():
    """Mặc định: khoảng ngày bao trùm toàn bộ dữ liệu hiện có (cả đăng ký thủ công
    lẫn import IPCAS) — dữ liệu import thường thuộc tháng trước (kỳ báo cáo đã
    đóng), còn đăng ký thủ công có thể ở tháng hiện tại/tương lai gần, nên không
    thể cố định theo "tháng hiện tại". Nếu chưa có dữ liệu nào, dùng tháng hiện tại."""
    reg_agg = HDVRegistration.objects.aggregate(mn=Min('ngay_dk_huy_dong'), mx=Max('ngay_dk_huy_dong'))
    imp_agg = HDVImportRecord.objects.aggregate(mn=Min('opening_date'), mx=Max('opening_date'))
    dates = [d for d in (reg_agg['mn'], reg_agg['mx'], imp_agg['mn'], imp_agg['mx']) if d]
    if not dates:
        return _current_month_range(date.today())
    return min(dates), max(dates)


def _parse_date_range(request):
    """Đọc tu_ngay/den_ngay từ GET, mặc định bao trùm toàn bộ dữ liệu hiện có."""
    default_tu, default_den = _default_date_range()
    try:
        tu_ngay = date.fromisoformat(request.GET.get('tu_ngay', '')) if request.GET.get('tu_ngay') else default_tu
    except ValueError:
        tu_ngay = default_tu
    try:
        den_ngay = date.fromisoformat(request.GET.get('den_ngay', '')) if request.GET.get('den_ngay') else default_den
    except ValueError:
        den_ngay = default_den
    return tu_ngay, den_ngay


def _branch_choices():
    return list(
        BranchConfig.objects.filter(is_active=True)
        .exclude(ma_chi_nhanh='')
        .order_by('ma_chi_nhanh')
        .values_list('ma_chi_nhanh', 'ten_chi_nhanh')
    )


def _profile_defaults(user):
    """Lấy mã/tên cán bộ + chi nhánh mặc định từ hồ sơ nhân viên (nếu có)."""
    profile = getattr(user, 'profile', None)
    if not profile:
        return '', '', ''
    return profile.employee_code or '', profile.full_name or '', profile.branch or ''


def _parse_ipcas_date(val):
    """Parse ngày dạng YYYYMMDD (hoặc YYYY-MM-DD) từ file IPCAS thành date object."""
    s = _hdv_clean_str(val)
    if not s:
        return None
    date_part = s.split(' ')[0]
    for fmt in ('%Y%m%d', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_part, fmt).date()
        except ValueError:
            continue
    return None


def _combined_hdv_data(tu_ngay, den_ngay):
    """Gộp dữ liệu từ 2 nguồn trong khoảng ngày:
    - HDVRegistration (đăng ký thủ công, theo ngay_dk_huy_dong)
    - HDVImportRecord (import từ file IPCAS, theo opening_date — ngày KH thực gửi)
    Trả về: tong_hdv, tong_kh, nhan_vien, theo_ngay (dict date->tong), theo_nhan_vien (list),
    theo_chi_nhanh (list).
    """
    reg_qs = HDVRegistration.objects.filter(ngay_dk_huy_dong__gte=tu_ngay, ngay_dk_huy_dong__lte=den_ngay)
    imp_qs = HDVImportRecord.objects.filter(opening_date__gte=tu_ngay, opening_date__lte=den_ngay)

    theo_ngay = {}
    kh_theo_ngay = {}
    for r in reg_qs.values('ngay_dk_huy_dong').annotate(tong=Sum('so_tien')):
        d = r['ngay_dk_huy_dong']
        theo_ngay[d] = theo_ngay.get(d, 0) + (r['tong'] or 0)
    for r in imp_qs.values('opening_date').annotate(tong=Sum('current_balance')):
        d = r['opening_date']
        if d:
            theo_ngay[d] = theo_ngay.get(d, 0) + (r['tong'] or 0)

    # Đếm KH theo MA_KH (mã khách hàng nội bộ IPCAS) chứ không phải ID_NUMBER (CCCD),
    # vì khách hàng tổ chức thường không có CCCD nên đếm theo CCCD sẽ bị sót.
    for r in reg_qs.values('ngay_dk_huy_dong', 'cccd'):
        if r['cccd']:
            kh_theo_ngay.setdefault(r['ngay_dk_huy_dong'], set()).add(r['cccd'])
    for r in imp_qs.values('opening_date', 'ma_kh', 'id_number'):
        kh_key = r['ma_kh'] or r['id_number']
        if r['opening_date'] and kh_key:
            kh_theo_ngay.setdefault(r['opening_date'], set()).add(kh_key)

    kh_set = {c for c in reg_qs.values_list('cccd', flat=True) if c}
    kh_set |= {(r['ma_kh'] or r['id_number']) for r in imp_qs.values('ma_kh', 'id_number') if r['ma_kh'] or r['id_number']}

    nv_set = {c for c in reg_qs.values_list('ma_can_bo', flat=True) if c}
    nv_set |= {c for c in imp_qs.values_list('employee_number', flat=True) if c}

    cn_set = {c for c in reg_qs.exclude(chi_nhanh='').values_list('chi_nhanh', flat=True) if c}
    cn_set |= {c for c in imp_qs.exclude(ma_cn='').values_list('ma_cn', flat=True) if c}

    tong_hdv = (reg_qs.aggregate(t=Sum('so_tien'))['t'] or 0) + (imp_qs.aggregate(t=Sum('current_balance'))['t'] or 0)

    # Gộp theo nhân viên
    nv_agg = {}
    for r in reg_qs.values('ma_can_bo', 'ten_can_bo', 'chi_nhanh', 'cccd', 'so_tien'):
        key = r['ma_can_bo']
        if not key:
            continue
        e = nv_agg.setdefault(key, {'ten': '', 'chi_nhanh': '', 'kh': set(), 'tong': 0})
        e['ten'] = e['ten'] or r['ten_can_bo'] or ''
        e['chi_nhanh'] = e['chi_nhanh'] or r['chi_nhanh'] or ''
        if r['cccd']:
            e['kh'].add(r['cccd'])
        e['tong'] += r['so_tien'] or 0
    for r in imp_qs.values('employee_number', 'employee_name', 'ma_cn', 'ma_kh', 'id_number', 'current_balance'):
        key = r['employee_number']
        if not key:
            continue
        e = nv_agg.setdefault(key, {'ten': '', 'chi_nhanh': '', 'kh': set(), 'tong': 0})
        e['ten'] = e['ten'] or r['employee_name'] or ''
        e['chi_nhanh'] = e['chi_nhanh'] or r['ma_cn'] or ''
        kh_key = r['ma_kh'] or r['id_number']
        if kh_key:
            e['kh'].add(kh_key)
        e['tong'] += r['current_balance'] or 0

    theo_nhan_vien = sorted(
        [
            {'ma_can_bo': k, 'ten_can_bo': v['ten'], 'chi_nhanh': v['chi_nhanh'], 'so_kh': len(v['kh']), 'tong': v['tong']}
            for k, v in nv_agg.items()
        ],
        key=lambda x: -x['tong'],
    )

    # Gộp theo chi nhánh
    cn_agg = {}
    for r in reg_qs.exclude(chi_nhanh='').values('chi_nhanh', 'cccd', 'so_tien'):
        e = cn_agg.setdefault(r['chi_nhanh'], {'kh': set(), 'tong': 0})
        if r['cccd']:
            e['kh'].add(r['cccd'])
        e['tong'] += r['so_tien'] or 0
    for r in imp_qs.exclude(ma_cn='').values('ma_cn', 'ma_kh', 'id_number', 'current_balance'):
        e = cn_agg.setdefault(r['ma_cn'], {'kh': set(), 'tong': 0})
        kh_key = r['ma_kh'] or r['id_number']
        if kh_key:
            e['kh'].add(kh_key)
        e['tong'] += r['current_balance'] or 0

    theo_chi_nhanh = sorted(
        [{'chi_nhanh': k, 'so_kh': len(v['kh']), 'tong': v['tong']} for k, v in cn_agg.items()],
        key=lambda x: -x['tong'],
    )

    return {
        'tong_hdv': tong_hdv,
        'tong_kh': len(kh_set),
        'so_nhan_vien': len(nv_set),
        'so_chi_nhanh': len(cn_set),
        'theo_ngay': theo_ngay,
        'kh_theo_ngay': kh_theo_ngay,
        'theo_nhan_vien': theo_nhan_vien,
        'theo_chi_nhanh': theo_chi_nhanh,
    }


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def hdv_dashboard_view(request):
    tu_ngay, den_ngay = _parse_date_range(request)
    data = _combined_hdv_data(tu_ngay, den_ngay)

    sorted_days = sorted(data['theo_ngay'].keys())
    chart_labels = [d.strftime('%d/%m') for d in sorted_days]
    chart_values = [round(data['theo_ngay'][d] / 1e9, 3) for d in sorted_days]

    context = {
        'tu_ngay': tu_ngay.isoformat(),
        'den_ngay': den_ngay.isoformat(),
        'tong_hdv': data['tong_hdv'],
        'tong_kh': data['tong_kh'],
        'nhan_vien_phat_sinh': data['so_nhan_vien'],
        'chart_labels_json': json.dumps(chart_labels),
        'chart_values_json': json.dumps(chart_values),
        'by_employee': data['theo_nhan_vien'],
    }
    return render(request, 'templates_app/hdv/dashboard.html', context)


# ---------------------------------------------------------------------------
# Báo cáo
# ---------------------------------------------------------------------------

@login_required
def hdv_reports_view(request):
    tu_ngay, den_ngay = _parse_date_range(request)
    data = _combined_hdv_data(tu_ngay, den_ngay)

    sorted_days = sorted(data['theo_ngay'].keys())
    chart_labels = [d.strftime('%d/%m') for d in sorted_days]
    chart_so_kh = [len(data['kh_theo_ngay'].get(d, set())) for d in sorted_days]
    chart_tong_ty = [round(data['theo_ngay'][d] / 1e9, 3) for d in sorted_days]

    context = {
        'tu_ngay': tu_ngay.isoformat(),
        'den_ngay': den_ngay.isoformat(),
        'tong_hdv': data['tong_hdv'],
        'tong_kh': data['tong_kh'],
        'nhan_vien_co_hdv': data['so_nhan_vien'],
        'chi_nhanh_co_hdv': data['so_chi_nhanh'],
        'chart_labels_json': json.dumps(chart_labels),
        'chart_so_kh_json': json.dumps(chart_so_kh),
        'chart_tong_ty_json': json.dumps(chart_tong_ty),
        'top_nhan_vien': data['theo_nhan_vien'][:10],
        'top_chi_nhanh': data['theo_chi_nhanh'][:10],
    }
    return render(request, 'templates_app/hdv/reports.html', context)


@login_required
def hdv_reports_export_view(request):
    """Xuất Excel báo cáo HĐV theo khoảng ngày đang lọc — gộp cả 2 nguồn
    (đăng ký thủ công + import từ IPCAS), có cột "Nguồn" để phân biệt."""
    tu_ngay, den_ngay = _parse_date_range(request)
    reg_qs = HDVRegistration.objects.filter(
        ngay_dk_huy_dong__gte=tu_ngay, ngay_dk_huy_dong__lte=den_ngay
    ).order_by('ma_can_bo', 'ngay_dk_huy_dong')
    imp_qs = HDVImportRecord.objects.filter(
        opening_date__gte=tu_ngay, opening_date__lte=den_ngay
    ).order_by('employee_number', 'opening_date')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Bao cao HDV'

    header_fill = PatternFill('solid', fgColor='8B1E2D')
    bold_white = Font(bold=True, color='FFFFFF')
    headers = [
        'Nguồn', 'Tên KH/Tên KHPN', 'CCCD/GPĐKKD/GCNĐT/Mã số DN/MST',
        'Ngày ĐK/mở sổ', 'Số tiền', 'Loại tiền', 'Mã cán bộ', 'Tên cán bộ',
        'Chi nhánh', 'Ghi chú',
    ]
    ws.append(headers)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = bold_white
        cell.alignment = Alignment(horizontal='center', vertical='center')

    for r in reg_qs:
        ws.append([
            'Đăng ký thủ công', r.ten_kh, r.cccd,
            r.ngay_dk_huy_dong.strftime('%d/%m/%Y'), r.so_tien, r.loai_tien,
            r.ma_can_bo, r.ten_can_bo, r.chi_nhanh,
            f"Người ĐK: {r.user_dk.get_full_name() or r.user_dk.username}",
        ])
    for r in imp_qs:
        ws.append([
            'Import IPCAS', r.ten_kh, r.id_number,
            r.opening_date.strftime('%d/%m/%Y') if r.opening_date else '',
            r.current_balance, r.ccy,
            r.employee_number, r.employee_name, r.ma_cn,
            f"Số TK: {r.so_tai_khoan} ({r.account_status})",
        ])

    col_widths = [16, 24, 22, 14, 16, 8, 12, 20, 10, 26]
    for col, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    resp = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    resp['Content-Disposition'] = (
        f'attachment; filename="BaoCao_HDV_{tu_ngay.isoformat()}_{den_ngay.isoformat()}.xlsx"'
    )
    return resp


# ---------------------------------------------------------------------------
# Đăng ký khách hàng (CRUD — mỗi user chỉ thấy bản ghi của mình)
# ---------------------------------------------------------------------------

@login_required
def hdv_registration_list_view(request):
    qs = HDVRegistration.objects.filter(user_dk=request.user)

    ten_kh = request.GET.get('ten_kh', '').strip()
    sdt = request.GET.get('sdt', '').strip()
    cccd = request.GET.get('cccd', '').strip()
    ma_can_bo = request.GET.get('ma_can_bo', '').strip()
    ngay_dk = request.GET.get('ngay_dk', '').strip()

    if ten_kh:
        qs = qs.filter(ten_kh__icontains=ten_kh)
    if sdt:
        qs = qs.filter(sdt__icontains=sdt)
    if cccd:
        qs = qs.filter(cccd__icontains=cccd)
    if ma_can_bo:
        qs = qs.filter(ma_can_bo__icontains=ma_can_bo)
    if ngay_dk:
        try:
            qs = qs.filter(ngay_dk_huy_dong=datetime.strptime(ngay_dk, '%d/%m/%Y').date())
        except ValueError:
            pass

    qs = qs.order_by('-ngay_gui_dk')

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    ma_cb_default, ten_cb_default, chi_nhanh_default = _profile_defaults(request.user)

    context = {
        'page_obj': page_obj,
        'filters': {
            'ten_kh': ten_kh, 'sdt': sdt, 'cccd': cccd,
            'ma_can_bo': ma_can_bo, 'ngay_dk': ngay_dk,
        },
        'branch_choices': _branch_choices(),
        'ky_han_choices': HDVRegistration.KY_HAN_CHOICES,
        'ma_cb_default': ma_cb_default,
        'ten_cb_default': ten_cb_default,
        'chi_nhanh_default': chi_nhanh_default,
    }
    return render(request, 'templates_app/hdv/registration_list.html', context)


def _hdv_form_data(request):
    ngay_str = request.POST.get('ngay_dk_huy_dong', '').strip()
    try:
        ngay = datetime.strptime(ngay_str, '%Y-%m-%d').date()
    except ValueError:
        ngay = None
    try:
        so_tien = int(float(request.POST.get('so_tien', '0') or 0))
    except ValueError:
        so_tien = 0
    return {
        'ten_kh': request.POST.get('ten_kh', '').strip(),
        'sdt': request.POST.get('sdt', '').strip(),
        'cccd': request.POST.get('cccd', '').strip(),
        'dia_chi': request.POST.get('dia_chi', '').strip(),
        'ngay_dk_huy_dong': ngay,
        'ky_han': request.POST.get('ky_han', '').strip(),
        'so_tien': so_tien,
        'loai_tien': request.POST.get('loai_tien', 'VND').strip() or 'VND',
        'ma_can_bo': request.POST.get('ma_can_bo', '').strip(),
        'ten_can_bo': request.POST.get('ten_can_bo', '').strip(),
        'chi_nhanh': request.POST.get('chi_nhanh', '').strip(),
    }


@login_required
@require_http_methods(["POST"])
def hdv_registration_create_view(request):
    data = _hdv_form_data(request)

    if not data['ten_kh'] or not data['cccd']:
        return JsonResponse({'success': False, 'error': 'Tên KH và CCCD/GPĐKKD/GCNĐT/Mã số DN/MST là bắt buộc'}, status=400)
    if not data['ngay_dk_huy_dong']:
        return JsonResponse({'success': False, 'error': 'Ngày ĐK huy động không hợp lệ'}, status=400)
    if data['so_tien'] <= 0:
        return JsonResponse({'success': False, 'error': 'Số tiền phải lớn hơn 0'}, status=400)
    if not data['ma_can_bo']:
        return JsonResponse({'success': False, 'error': 'Mã cán bộ là bắt buộc'}, status=400)

    reg = HDVRegistration.objects.create(user_dk=request.user, **data)
    return JsonResponse({'success': True, 'message': f'Đã đăng ký HĐV cho {reg.ten_kh}', 'id': reg.id})


@login_required
@require_http_methods(["POST"])
def hdv_registration_update_view(request, pk):
    reg = get_object_or_404(HDVRegistration, pk=pk)
    if reg.user_dk_id != request.user.id and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền sửa bản ghi này'}, status=403)

    data = _hdv_form_data(request)
    if not data['ten_kh'] or not data['cccd']:
        return JsonResponse({'success': False, 'error': 'Tên KH và CCCD/GPĐKKD/GCNĐT/Mã số DN/MST là bắt buộc'}, status=400)
    if not data['ngay_dk_huy_dong']:
        return JsonResponse({'success': False, 'error': 'Ngày ĐK huy động không hợp lệ'}, status=400)
    if data['so_tien'] <= 0:
        return JsonResponse({'success': False, 'error': 'Số tiền phải lớn hơn 0'}, status=400)

    for k, v in data.items():
        setattr(reg, k, v)
    reg.save()
    return JsonResponse({'success': True, 'message': f'Đã cập nhật đăng ký của {reg.ten_kh}'})


@login_required
def hdv_employee_lookup_view(request):
    """Tra cứu tên cán bộ theo mã nhân viên (UserProfile.employee_code) để tự động
    điền Tên cán bộ khi nhập Mã cán bộ."""
    ma = request.GET.get('ma', '').strip()
    if not ma:
        return JsonResponse({'found': False})
    profile = UserProfile.objects.filter(employee_code__iexact=ma).first()
    if profile:
        return JsonResponse({'found': True, 'ten_can_bo': profile.full_name})
    return JsonResponse({'found': False})


@login_required
@require_http_methods(["POST"])
def hdv_registration_delete_view(request, pk):
    reg = get_object_or_404(HDVRegistration, pk=pk)
    if reg.user_dk_id != request.user.id and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền xóa bản ghi này'}, status=403)
    ten_kh = reg.ten_kh
    reg.delete()
    return JsonResponse({'success': True, 'message': f'Đã xóa đăng ký của {ten_kh}'})


# ---------------------------------------------------------------------------
# Upload file mẫu đăng ký HĐV hàng loạt
# ---------------------------------------------------------------------------

HDV_UPLOAD_HEADERS = [
    'Họ tên', 'CCCD/GPĐKKD/GCNĐT/Mã số DN/MST', 'Địa chỉ',
    'Số tiền', 'Kỳ hạn', 'Ngày dự kiến gửi tiền',
]

_KY_HAN_LABEL_TO_CODE = {label.strip().lower(): code for code, label in HDVRegistration.KY_HAN_CHOICES}
_KY_HAN_CODE_SET = {code for code, _label in HDVRegistration.KY_HAN_CHOICES}


def _parse_ky_han(raw):
    """Nhận cả mã (VD '12T') lẫn nhãn tiếng Việt (VD '12 tháng') từ file upload."""
    s = _hdv_clean_str(raw).strip()
    if not s:
        return ''
    if s.upper() in _KY_HAN_CODE_SET:
        return s.upper()
    return _KY_HAN_LABEL_TO_CODE.get(s.lower(), '')


def _parse_upload_date(raw):
    """Nhận ngày dạng dd/mm/yyyy (chuẩn file mẫu) hoặc ô ngày Excel thực (đã bị
    pandas ép thành chuỗi 'yyyy-mm-dd hh:mm:ss')."""
    s = _hdv_clean_str(raw)
    if not s:
        return None
    date_part = s.split(' ')[0]
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_part, fmt).date()
        except ValueError:
            continue
    return None


@login_required
def hdv_registration_template_download_view(request):
    """Tải file mẫu (.xlsx) để đăng ký HĐV hàng loạt."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Mau dang ky HDV'

    header_fill = PatternFill('solid', fgColor='8B1E2D')
    bold_white = Font(bold=True, color='FFFFFF')
    ws.append(HDV_UPLOAD_HEADERS)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = bold_white
        cell.alignment = Alignment(horizontal='center', vertical='center')

    ws.append(['Nguyễn Văn A', '079123456789', '123 Đường ABC, Phường X, TP Cần Thơ',
                '100000000', '12 tháng', '25/07/2026'])

    col_widths = [24, 26, 36, 16, 14, 20]
    for col, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    resp = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    resp['Content-Disposition'] = 'attachment; filename="Mau_Dang_Ky_HDV.xlsx"'
    return resp


@login_required
@require_http_methods(["POST"])
def hdv_registration_import_view(request):
    """Upload file đăng ký HĐV hàng loạt — mỗi dòng tạo 1 bản ghi HDVRegistration
    gán cho user đang đăng nhập (Mã/Tên cán bộ, Chi nhánh lấy theo hồ sơ user đó)."""
    uploaded = request.FILES.get('import_file')
    if not uploaded:
        messages.error(request, "Vui lòng chọn file để upload.")
        return redirect('hdv_registration_list')

    try:
        df = pd.read_excel(uploaded, sheet_name=0, dtype=str)
    except Exception as e:
        messages.error(request, f"Không đọc được file: {e}")
        return redirect('hdv_registration_list')

    required = ['Họ tên', 'CCCD/GPĐKKD/GCNĐT/Mã số DN/MST', 'Số tiền', 'Ngày dự kiến gửi tiền']
    missing = [c for c in required if _find_col(df.columns, [c]) is None]
    if missing:
        messages.error(request, f"File thiếu cột: {', '.join(missing)}")
        return redirect('hdv_registration_list')

    col_ten_kh = _find_col(df.columns, ['Họ tên'])
    col_cccd = _find_col(df.columns, ['CCCD/GPĐKKD/GCNĐT/Mã số DN/MST'])
    col_dia_chi = _find_col(df.columns, ['Địa chỉ'])
    col_so_tien = _find_col(df.columns, ['Số tiền'])
    col_ky_han = _find_col(df.columns, ['Kỳ hạn'])
    col_ngay = _find_col(df.columns, ['Ngày dự kiến gửi tiền'])

    ma_cb_default, ten_cb_default, chi_nhanh_default = _profile_defaults(request.user)

    created, skipped = 0, 0
    to_create = []
    for _, row in df.iterrows():
        ten_kh = _hdv_clean_str(row[col_ten_kh])
        cccd = _hdv_clean_str(row[col_cccd])
        ngay = _parse_upload_date(row[col_ngay])
        so_tien = int(_hdv_to_float(row[col_so_tien]))

        if not ten_kh or not cccd or not ngay or so_tien <= 0:
            skipped += 1
            continue

        to_create.append(HDVRegistration(
            user_dk=request.user,
            ten_kh=ten_kh,
            cccd=cccd,
            dia_chi=_hdv_clean_str(row[col_dia_chi]) if col_dia_chi else '',
            ngay_dk_huy_dong=ngay,
            ky_han=_parse_ky_han(row[col_ky_han]) if col_ky_han else '',
            so_tien=so_tien,
            ma_can_bo=ma_cb_default,
            ten_can_bo=ten_cb_default,
            chi_nhanh=chi_nhanh_default,
        ))
        created += 1

    with transaction.atomic():
        HDVRegistration.objects.bulk_create(to_create)

    messages.success(
        request,
        f"Đã upload xong: {created} đăng ký mới, {skipped} dòng bỏ qua "
        f"(thiếu Họ tên/CCCD/Ngày dự kiến gửi tiền hoặc Số tiền không hợp lệ)."
    )
    return redirect('hdv_registration_list')


# ---------------------------------------------------------------------------
# Import file xuất từ hệ thống IPCAS (bổ sung dữ liệu thực gửi vào Dashboard/Báo cáo)
# ---------------------------------------------------------------------------

REQUIRED_IPCAS_COLS = [
    'MA_CN', 'MA_KH', 'TEN_KH', 'CCY', 'CURRENT_BALANCE', 'SO_TAI_KHOAN',
    'OPENING_DATE', 'MATURITY_DATE', 'MONTH_TERM', 'ACCOUNT_STATUS',
    'ID_NUMBER', 'EMPLOYEE_NUMBER', 'EMPLOYEE_NAME',
]


@login_required
@require_http_methods(["POST"])
def hdv_import_upload_view(request):
    """Upload file xuất từ hệ thống IPCAS — chỉ lấy các sổ VND, kỳ hạn >= 1 tháng.
    Mỗi lần upload cập nhật theo Số tài khoản (SO_TAI_KHOAN) để tránh cộng trùng
    khi upload lại file mới/cập nhật cho cùng kỳ."""
    uploaded = request.FILES.get('import_file')
    if not uploaded:
        messages.error(request, "Vui lòng chọn file để upload.")
        return redirect('hdv_dashboard')

    try:
        df = pd.read_excel(uploaded, sheet_name=0, dtype=str)
    except Exception as e:
        messages.error(request, f"Không đọc được file: {e}")
        return redirect('hdv_dashboard')

    missing = [c for c in REQUIRED_IPCAS_COLS if _find_col(df.columns, [c]) is None]
    if missing:
        messages.error(request, f"File thiếu cột: {', '.join(missing)}")
        return redirect('hdv_dashboard')

    cols = {name: _find_col(df.columns, [name]) for name in REQUIRED_IPCAS_COLS}

    created, updated, skipped = 0, 0, 0
    with transaction.atomic():
        for _, row in df.iterrows():
            if _hdv_clean_str(row[cols['CCY']]).upper() != 'VND':
                skipped += 1
                continue
            month_term = int(_hdv_to_float(row[cols['MONTH_TERM']]))
            if month_term < 1:
                skipped += 1
                continue
            so_tk = _hdv_clean_str(row[cols['SO_TAI_KHOAN']])
            if not so_tk:
                skipped += 1
                continue

            _, is_created = HDVImportRecord.objects.update_or_create(
                so_tai_khoan=so_tk,
                defaults={
                    'ma_cn': _hdv_clean_str(row[cols['MA_CN']]),
                    'ma_kh': _hdv_clean_str(row[cols['MA_KH']]),
                    'ten_kh': _hdv_clean_str(row[cols['TEN_KH']]),
                    'id_number': _hdv_remove_leading_zeros(row[cols['ID_NUMBER']]),
                    'ccy': 'VND',
                    'current_balance': int(_hdv_to_float(row[cols['CURRENT_BALANCE']])),
                    'opening_date': _parse_ipcas_date(row[cols['OPENING_DATE']]),
                    'maturity_date': _parse_ipcas_date(row[cols['MATURITY_DATE']]),
                    'month_term': month_term,
                    'account_status': _hdv_clean_str(row[cols['ACCOUNT_STATUS']]),
                    'employee_number': _hdv_clean_str(row[cols['EMPLOYEE_NUMBER']]),
                    'employee_name': _hdv_clean_str(row[cols['EMPLOYEE_NAME']]),
                    'uploaded_by': request.user,
                },
            )
            if is_created:
                created += 1
            else:
                updated += 1

    messages.success(
        request,
        f"Import xong: {created} sổ mới, {updated} sổ cập nhật, {skipped} dòng bỏ qua "
        f"(không phải VND hoặc kỳ hạn < 1 tháng)."
    )
    return redirect('hdv_dashboard')
