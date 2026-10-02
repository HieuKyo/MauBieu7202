"""
Đăng ký bảng QR (Kế toán & Ngân quỹ) — đăng ký tay, upload file Excel hàng loạt,
thống kê theo tháng. Cấu trúc phỏng theo module Đăng ký HĐV (hdv_reg_views.py).
"""
import io
import json
from datetime import date, timedelta

import openpyxl
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .models import BranchConfig, QRRegistration
from .report_views import _find_col, _hdv_clean_str

TEN_CUA_HANG_MAC_DINH = "Quét mã QR để chuyển khoản"


def _current_month_range(today):
    start = today.replace(day=1)
    next_month_first = date(today.year + 1, 1, 1) if today.month == 12 else date(today.year, today.month + 1, 1)
    return start, next_month_first - timedelta(days=1)


def _parse_thang(request):
    """Đọc tham số 'thang' dạng yyyy-mm (input type=month), mặc định tháng hiện tại."""
    thang_str = request.GET.get('thang', '').strip()
    try:
        year, month = (int(x) for x in thang_str.split('-'))
        return date(year, month, 1)
    except (ValueError, TypeError):
        return date.today().replace(day=1)


def _profile_defaults_qr(user):
    """Lấy tên cán bộ + phòng giao dịch mặc định từ hồ sơ nhân viên (nếu có)."""
    profile = getattr(user, 'profile', None)
    if not profile:
        return '', ''
    ten_can_bo = profile.full_name or ''
    phong_giao_dich = ''
    if profile.branch:
        bc = BranchConfig.objects.filter(branch_code=profile.branch).first()
        phong_giao_dich = bc.ten_chi_nhanh if bc else profile.branch
    return ten_can_bo, phong_giao_dich


# ---------------------------------------------------------------------------
# Dashboard / Thống kê theo tháng
# ---------------------------------------------------------------------------

@login_required
def qr_dashboard_view(request):
    thang = _parse_thang(request)
    thang_str = thang.strftime('%Y-%m')
    tu_ngay, den_ngay = _current_month_range(thang)

    qs = QRRegistration.objects.filter(ngay_dang_ky__date__gte=tu_ngay, ngay_dang_ky__date__lte=den_ngay)

    tong_qr = qs.count()

    theo_ngay = {}
    for r in qs.values_list('ngay_dang_ky', flat=True):
        d = r.date()
        theo_ngay[d] = theo_ngay.get(d, 0) + 1
    sorted_days = sorted(theo_ngay.keys())
    chart_labels = [d.strftime('%d/%m') for d in sorted_days]
    chart_values = [theo_ngay[d] for d in sorted_days]

    can_bo_agg = {}
    for r in qs.values('ten_can_bo', 'phong_giao_dich'):
        key = r['ten_can_bo'] or '(Chưa ghi tên)'
        e = can_bo_agg.setdefault(key, {'phong_giao_dich': r['phong_giao_dich'], 'so_luong': 0})
        e['so_luong'] += 1
    by_can_bo = sorted(
        [{'ten_can_bo': k, **v} for k, v in can_bo_agg.items()],
        key=lambda x: -x['so_luong'],
    )

    pgd_agg = {}
    for r in qs.exclude(phong_giao_dich='').values_list('phong_giao_dich', flat=True):
        pgd_agg[r] = pgd_agg.get(r, 0) + 1
    by_pgd = sorted(
        [{'phong_giao_dich': k, 'so_luong': v} for k, v in pgd_agg.items()],
        key=lambda x: -x['so_luong'],
    )

    context = {
        'thang': thang_str,
        'tu_ngay': tu_ngay.isoformat(),
        'den_ngay': den_ngay.isoformat(),
        'tong_qr': tong_qr,
        'so_can_bo': len(can_bo_agg),
        'so_pgd': len(pgd_agg),
        'chart_labels_json': json.dumps(chart_labels),
        'chart_values_json': json.dumps(chart_values),
        'by_can_bo': by_can_bo,
        'by_pgd': by_pgd,
    }
    return render(request, 'templates_app/qr/dashboard.html', context)


# ---------------------------------------------------------------------------
# Đăng ký (CRUD — mỗi user chỉ thấy bản ghi của mình)
# ---------------------------------------------------------------------------

@login_required
def qr_registration_list_view(request):
    qs = QRRegistration.objects.filter(user_dk=request.user)

    ten_kh = request.GET.get('ten_kh', '').strip()
    so_tai_khoan = request.GET.get('so_tai_khoan', '').strip()
    ten_cua_hang = request.GET.get('ten_cua_hang', '').strip()

    if ten_kh:
        qs = qs.filter(ten_kh__icontains=ten_kh)
    if so_tai_khoan:
        qs = qs.filter(so_tai_khoan__icontains=so_tai_khoan)
    if ten_cua_hang:
        qs = qs.filter(ten_cua_hang__icontains=ten_cua_hang)

    qs = qs.order_by('-ngay_dang_ky')

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    ten_cb_default, pgd_default = _profile_defaults_qr(request.user)

    context = {
        'page_obj': page_obj,
        'filters': {'ten_kh': ten_kh, 'so_tai_khoan': so_tai_khoan, 'ten_cua_hang': ten_cua_hang},
        'ten_cb_default': ten_cb_default,
        'pgd_default': pgd_default,
    }
    return render(request, 'templates_app/qr/registration_list.html', context)


def _qr_form_data(request, pgd_default):
    return {
        'ten_kh': request.POST.get('ten_kh', '').strip(),
        'so_tai_khoan': request.POST.get('so_tai_khoan', '').strip(),
        'ten_cua_hang': request.POST.get('ten_cua_hang', '').strip() or TEN_CUA_HANG_MAC_DINH,
        'ten_can_bo': request.POST.get('ten_can_bo', '').strip(),
        'phong_giao_dich': pgd_default,
    }


@login_required
@require_http_methods(["POST"])
def qr_registration_create_view(request):
    _, pgd_default = _profile_defaults_qr(request.user)
    data = _qr_form_data(request, pgd_default)

    if not data['ten_kh'] or not data['so_tai_khoan']:
        return JsonResponse({'success': False, 'error': 'Tên khách hàng và Số tài khoản là bắt buộc'}, status=400)

    reg = QRRegistration.objects.create(user_dk=request.user, **data)
    return JsonResponse({'success': True, 'message': f'Đã đăng ký QR cho {reg.ten_kh}', 'id': reg.id})


@login_required
@require_http_methods(["POST"])
def qr_registration_update_view(request, pk):
    reg = get_object_or_404(QRRegistration, pk=pk)
    if reg.user_dk_id != request.user.id and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền sửa bản ghi này'}, status=403)

    data = _qr_form_data(request, reg.phong_giao_dich)
    if not data['ten_kh'] or not data['so_tai_khoan']:
        return JsonResponse({'success': False, 'error': 'Tên khách hàng và Số tài khoản là bắt buộc'}, status=400)

    for k, v in data.items():
        setattr(reg, k, v)
    reg.save()
    return JsonResponse({'success': True, 'message': f'Đã cập nhật đăng ký của {reg.ten_kh}'})


@login_required
@require_http_methods(["POST"])
def qr_registration_delete_view(request, pk):
    reg = get_object_or_404(QRRegistration, pk=pk)
    if reg.user_dk_id != request.user.id and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền xóa bản ghi này'}, status=403)
    ten_kh = reg.ten_kh
    reg.delete()
    return JsonResponse({'success': True, 'message': f'Đã xóa đăng ký của {ten_kh}'})


# ---------------------------------------------------------------------------
# Upload file mẫu đăng ký QR hàng loạt
# ---------------------------------------------------------------------------

QR_UPLOAD_HEADERS = ['Tên khách hàng', 'Số tài khoản', 'Tên cửa hàng (nếu có)']


@login_required
def qr_registration_template_download_view(request):
    """Tải file mẫu (.xlsx) để đăng ký bảng QR hàng loạt."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Mau dang ky QR'

    header_fill = PatternFill('solid', fgColor='8B1E2D')
    bold_white = Font(bold=True, color='FFFFFF')
    ws.append(QR_UPLOAD_HEADERS)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = bold_white
        cell.alignment = Alignment(horizontal='center', vertical='center')

    ws.append(['Nguyễn Văn A', '1234567890', 'Tạp hóa Ánh Dương'])

    col_widths = [24, 20, 30]
    for col, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    resp = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    resp['Content-Disposition'] = 'attachment; filename="Mau_Dang_Ky_QR.xlsx"'
    return resp


@login_required
@require_http_methods(["POST"])
def qr_registration_import_view(request):
    """Upload file đăng ký QR hàng loạt — mỗi dòng tạo 1 bản ghi gán cho user
    đang đăng nhập (Tên cán bộ mặc định theo hồ sơ nếu file không có; Phòng giao
    dịch luôn lấy theo hồ sơ user, không đọc từ file)."""
    uploaded = request.FILES.get('import_file')
    if not uploaded:
        messages.error(request, "Vui lòng chọn file để upload.")
        return redirect('qr_registration_list')

    try:
        df = pd.read_excel(uploaded, sheet_name=0, dtype=str)
    except Exception as e:
        messages.error(request, f"Không đọc được file: {e}")
        return redirect('qr_registration_list')

    required = ['Tên khách hàng', 'Số tài khoản']
    missing = [c for c in required if _find_col(df.columns, [c]) is None]
    if missing:
        messages.error(request, f"File thiếu cột: {', '.join(missing)}")
        return redirect('qr_registration_list')

    col_ten_kh = _find_col(df.columns, ['Tên khách hàng'])
    col_so_tk = _find_col(df.columns, ['Số tài khoản'])
    col_ten_cua_hang = _find_col(df.columns, ['Tên cửa hàng (nếu có)', 'Tên cửa hàng'])

    ten_cb_default, pgd_default = _profile_defaults_qr(request.user)

    created, skipped = 0, 0
    to_create = []
    for _, row in df.iterrows():
        ten_kh = _hdv_clean_str(row[col_ten_kh])
        so_tk = _hdv_clean_str(row[col_so_tk])

        if not ten_kh or not so_tk:
            skipped += 1
            continue

        to_create.append(QRRegistration(
            user_dk=request.user,
            ten_kh=ten_kh,
            so_tai_khoan=so_tk,
            ten_cua_hang=(_hdv_clean_str(row[col_ten_cua_hang]) if col_ten_cua_hang else '') or TEN_CUA_HANG_MAC_DINH,
            ten_can_bo=ten_cb_default,
            phong_giao_dich=pgd_default,
        ))
        created += 1

    with transaction.atomic():
        QRRegistration.objects.bulk_create(to_create)

    messages.success(
        request,
        f"Đã upload xong: {created} đăng ký QR mới, {skipped} dòng bỏ qua "
        f"(thiếu Tên khách hàng hoặc Số tài khoản)."
    )
    return redirect('qr_registration_list')
