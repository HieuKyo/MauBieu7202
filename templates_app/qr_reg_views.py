"""
Đăng ký bảng QR / Loa Thần tài (Kế toán & Ngân quỹ) — đăng ký tay, upload file Excel hàng loạt (bảng QR),
thống kê theo tháng. Cấu trúc phỏng theo module Đăng ký HĐV (hdv_reg_views.py).
"""
import io
import json
from datetime import date, timedelta

import openpyxl
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from openpyxl.styles import Alignment, Font, PatternFill
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import BranchConfig, QRRegistration
from .report_views import _find_col
from .report_huy_dong_von_views import _hdv_clean_str

TEN_CUA_HANG_MAC_DINH = "Quét mã QR để chuyển khoản"

# Nội dung hướng dẫn — dùng chung cho modal "Hướng dẫn" và file Word tải về.
QR_HUONG_DAN = [
    ("1. Giới thiệu", [
        "Chức năng Đăng ký bảng QR / Loa Thần tài giúp cán bộ ghi nhận các bảng QR chuyển khoản và Loa Thần tài đã phát hành cho khách hàng/cửa hàng.",
        "Gồm 2 trang: Dashboard (thống kê và biểu đồ theo tháng, năm) và Đăng ký QR / Loa (nhập, sửa, xóa, upload hàng loạt).",
        "Mỗi cán bộ chỉ thấy và chỉnh sửa các bản ghi do mình đăng ký; Admin thấy toàn bộ đăng ký của tất cả các phòng.",
    ]),
    ("2. Đăng ký từng bảng QR", [
        "Vào menu Đăng ký QR / Loa, bấm nút \"Đăng ký bảng QR\".",
        "Nhập Tên khách hàng và Số tài khoản (bắt buộc).",
        "Tên cửa hàng có thể bỏ trống — hệ thống tự điền \"Quét mã QR để chuyển khoản\".",
        "Tên cán bộ đăng ký tự lấy theo hồ sơ, có thể sửa lại; Phòng giao dịch tự lấy theo hồ sơ và không sửa được.",
        "Bấm \"Đăng ký\" để lưu.",
    ]),
    ("3. Đăng ký hàng loạt bằng file Excel", [
        "Bấm \"Tải file mẫu\" để tải file Mau_Dang_Ky_QR.xlsx.",
        "Điền mỗi dòng một khách hàng với các cột: Tên khách hàng, Số tài khoản, Tên cửa hàng (nếu có). Xóa dòng ví dụ trước khi upload.",
        "Bấm \"Upload đăng ký QR\", chọn file và bấm \"Upload\".",
        "Dòng thiếu Tên khách hàng hoặc Số tài khoản sẽ bị bỏ qua; hệ thống báo số dòng đã tạo và số dòng bỏ qua.",
        "Tên cán bộ và Phòng giao dịch lấy theo hồ sơ người upload.",
    ]),
    ("4. Tìm kiếm, sửa, xóa", [
        "Dùng Bộ lọc tìm kiếm theo Tên khách hàng, Số tài khoản, Tên cửa hàng, Đã in, Loại rồi bấm \"Lọc\".",
        "Bấm biểu tượng bút chì để sửa, biểu tượng thùng rác để xóa bản ghi.",
        "Bản ghi đã in thì cán bộ không sửa, xóa được nữa; cần thay đổi hãy liên hệ Admin.",
    ]),
    ("5. Đánh dấu đã in", [
        "Đăng ký xong là Admin thấy ngay, không cần gửi duyệt.",
        "Admin in xong thì tích vào ô \"Đã in\". Cột Đã in hiện tên người đánh dấu và thời gian.",
        "Cán bộ đăng ký thấy ô \"Đã in\" của bản ghi của mình nhưng không tích được.",
        "Nếu tích nhầm, Admin bỏ tích để trả lại trạng thái chưa in.",
    ]),
    ("6. Bộ đếm và Dashboard", [
        "Bộ đếm tính số đã đăng ký trên toàn hệ thống, gồm cả bản ghi chưa in.",
        "Trang Đăng ký QR / Loa hiển thị số bảng QR và số Loa Thần tài đã đăng ký trong tháng và trong năm hiện tại.",
        "Trang Dashboard thống kê theo tháng được chọn: tổng trong tháng và trong năm của bảng QR, Loa Thần tài, số cán bộ, số phòng giao dịch, biểu đồ theo ngày, biểu đồ 12 tháng trong năm và bảng xếp hạng theo cán bộ/phòng giao dịch.",
    ]),
    ("7. Tải danh sách QR / Loa (chỉ Admin)", [
        "Tài khoản Admin có thêm nút \"Tải danh sách QR / Loa (Admin)\" để tải file Excel danh sách của tất cả cán bộ.",
        "File áp dụng theo bộ lọc đang chọn; để tải toàn bộ, hãy để trống bộ lọc.",
        "Tài khoản không phải Admin không thấy nút và không tải được file.",
    ]),
    ("8. Đăng ký Loa Thần tài", [
        "Bấm nút \"Đăng ký Loa Thần tài\", nhập Số tài khoản, Họ tên khách hàng, Địa chỉ, Số điện thoại (đều bắt buộc) rồi bấm \"Đăng ký\".",
        "Sửa, xóa, đánh dấu đã in và tải danh sách làm giống bảng QR.",
        "Upload file Excel hàng loạt chỉ dùng cho bảng QR.",
    ]),
]


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


def _filter_qr(qs, request):
    """Áp bộ lọc tìm kiếm từ query string, trả về (queryset đã sắp xếp, dict bộ lọc)."""
    filters = {
        k: request.GET.get(k, '').strip()
        for k in ('ten_kh', 'so_tai_khoan', 'ten_cua_hang', 'da_in', 'loai')
    }
    if filters['ten_kh']:
        qs = qs.filter(ten_kh__icontains=filters['ten_kh'])
    if filters['so_tai_khoan']:
        qs = qs.filter(so_tai_khoan__icontains=filters['so_tai_khoan'])
    if filters['ten_cua_hang']:
        qs = qs.filter(ten_cua_hang__icontains=filters['ten_cua_hang'])
    if filters['da_in'] in ('0', '1'):
        qs = qs.filter(da_in=filters['da_in'] == '1')
    if filters['loai']:
        qs = qs.filter(loai=filters['loai'])
    return qs.order_by('-ngay_dang_ky'), filters


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

    tong_qr = qs.filter(loai=QRRegistration.LOAI_QR).count()
    tong_loa = qs.filter(loai=QRRegistration.LOAI_LOA).count()

    trong_nam = QRRegistration.objects.filter(ngay_dang_ky__year=thang.year)
    tong_qr_nam = trong_nam.filter(loai=QRRegistration.LOAI_QR).count()
    tong_loa_nam = trong_nam.filter(loai=QRRegistration.LOAI_LOA).count()
    theo_thang = {
        (r['ngay_dang_ky__month'], r['loai']): r['so_luong']
        for r in trong_nam.values('ngay_dang_ky__month', 'loai').annotate(so_luong=Count('id')).order_by()
    }
    cac_thang = range(1, 13)

    theo_ngay = {}
    for ngay, loai in qs.values_list('ngay_dang_ky', 'loai'):
        e = theo_ngay.setdefault(timezone.localtime(ngay).date(), {'qr': 0, 'loa': 0})
        e[loai] += 1
    sorted_days = sorted(theo_ngay.keys())
    chart_labels = [d.strftime('%d/%m') for d in sorted_days]
    chart_qr = [theo_ngay[d]['qr'] for d in sorted_days]
    chart_loa = [theo_ngay[d]['loa'] for d in sorted_days]

    can_bo_agg = {}
    for r in qs.values('ten_can_bo', 'phong_giao_dich', 'loai'):
        key = r['ten_can_bo'] or '(Chưa ghi tên)'
        e = can_bo_agg.setdefault(key, {'phong_giao_dich': r['phong_giao_dich'], 'qr': 0, 'loa': 0})
        e[r['loai']] += 1
    by_can_bo = sorted(
        [{'ten_can_bo': k, **v, 'so_luong': v['qr'] + v['loa']} for k, v in can_bo_agg.items()],
        key=lambda x: -x['so_luong'],
    )

    pgd_agg = {}
    for pgd, loai in qs.exclude(phong_giao_dich='').values_list('phong_giao_dich', 'loai'):
        e = pgd_agg.setdefault(pgd, {'qr': 0, 'loa': 0})
        e[loai] += 1
    by_pgd = sorted(
        [{'phong_giao_dich': k, **v, 'so_luong': v['qr'] + v['loa']} for k, v in pgd_agg.items()],
        key=lambda x: -x['so_luong'],
    )

    context = {
        'thang': thang_str,
        'thang_hien_thi': thang.strftime('%m/%Y'),
        'nam': thang.strftime('%Y'),
        'tu_ngay': tu_ngay.isoformat(),
        'den_ngay': den_ngay.isoformat(),
        'tong_qr': tong_qr,
        'tong_loa': tong_loa,
        'tong_qr_nam': tong_qr_nam,
        'tong_loa_nam': tong_loa_nam,
        'so_can_bo': len(can_bo_agg),
        'so_pgd': len(pgd_agg),
        'chart_labels_json': json.dumps(chart_labels),
        'chart_qr_json': json.dumps(chart_qr),
        'chart_loa_json': json.dumps(chart_loa),
        'chart_thang_labels_json': json.dumps([f'T{m}' for m in cac_thang]),
        'chart_thang_qr_json': json.dumps([theo_thang.get((m, QRRegistration.LOAI_QR), 0) for m in cac_thang]),
        'chart_thang_loa_json': json.dumps([theo_thang.get((m, QRRegistration.LOAI_LOA), 0) for m in cac_thang]),
        'by_can_bo': by_can_bo,
        'by_pgd': by_pgd,
        'qr_huong_dan': QR_HUONG_DAN,
    }
    return render(request, 'templates_app/qr/dashboard.html', context)


# ---------------------------------------------------------------------------
# Đăng ký (CRUD — mỗi user chỉ thấy bản ghi của mình, admin thấy toàn bộ)
# ---------------------------------------------------------------------------

@login_required
def qr_registration_list_view(request):
    qs = QRRegistration.objects.all()
    if not request.user.is_superuser:
        qs = qs.filter(user_dk=request.user)
    qs, filters = _filter_qr(qs, request)

    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    ten_cb_default, pgd_default = _profile_defaults_qr(request.user)

    today = date.today()
    tu_ngay, den_ngay = _current_month_range(today)
    trong_thang = QRRegistration.objects.filter(ngay_dang_ky__date__gte=tu_ngay, ngay_dang_ky__date__lte=den_ngay)
    tong_qr_thang = trong_thang.filter(loai=QRRegistration.LOAI_QR).count()
    tong_loa_thang = trong_thang.filter(loai=QRRegistration.LOAI_LOA).count()
    trong_nam = QRRegistration.objects.filter(ngay_dang_ky__year=today.year)
    tong_qr_nam = trong_nam.filter(loai=QRRegistration.LOAI_QR).count()
    tong_loa_nam = trong_nam.filter(loai=QRRegistration.LOAI_LOA).count()

    context = {
        'page_obj': page_obj,
        'thang_hien_tai': today.strftime('%m/%Y'),
        'nam_hien_tai': today.strftime('%Y'),
        'tong_qr_thang': tong_qr_thang,
        'tong_qr_nam': tong_qr_nam,
        'tong_loa_thang': tong_loa_thang,
        'tong_loa_nam': tong_loa_nam,
        'qr_huong_dan': QR_HUONG_DAN,
        'filters': filters,
        'loai_choices': QRRegistration.LOAI_CHOICES,
        'ten_cb_default': ten_cb_default,
        'pgd_default': pgd_default,
    }
    return render(request, 'templates_app/qr/registration_list.html', context)


def _qr_form_data(request, pgd_default, loai):
    data = {
        'ten_kh': request.POST.get('ten_kh', '').strip(),
        'so_tai_khoan': request.POST.get('so_tai_khoan', '').strip(),
        'ten_can_bo': request.POST.get('ten_can_bo', '').strip(),
        'phong_giao_dich': pgd_default,
    }
    if loai == QRRegistration.LOAI_LOA:
        data['dia_chi'] = request.POST.get('dia_chi', '').strip()
        data['so_dien_thoai'] = request.POST.get('so_dien_thoai', '').strip()
    else:
        data['ten_cua_hang'] = request.POST.get('ten_cua_hang', '').strip() or TEN_CUA_HANG_MAC_DINH
    return data


def _qr_form_error(data, loai):
    if loai == QRRegistration.LOAI_LOA:
        if not all(data[k] for k in ('ten_kh', 'so_tai_khoan', 'dia_chi', 'so_dien_thoai')):
            return 'Số tài khoản, Họ tên khách hàng, Địa chỉ và Số điện thoại là bắt buộc'
    elif not data['ten_kh'] or not data['so_tai_khoan']:
        return 'Tên khách hàng và Số tài khoản là bắt buộc'
    return ''


@login_required
@require_http_methods(["POST"])
def qr_registration_create_view(request):
    _, pgd_default = _profile_defaults_qr(request.user)
    loai = QRRegistration.LOAI_LOA if request.POST.get('loai') == QRRegistration.LOAI_LOA else QRRegistration.LOAI_QR
    data = _qr_form_data(request, pgd_default, loai)

    error = _qr_form_error(data, loai)
    if error:
        return JsonResponse({'success': False, 'error': error}, status=400)

    reg = QRRegistration.objects.create(user_dk=request.user, loai=loai, **data)
    return JsonResponse({'success': True, 'message': f'Đã đăng ký {reg.get_loai_display()} cho {reg.ten_kh}', 'id': reg.id})


@login_required
@require_http_methods(["POST"])
def qr_registration_update_view(request, pk):
    reg = get_object_or_404(QRRegistration, pk=pk)
    if reg.user_dk_id != request.user.id and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền sửa bản ghi này'}, status=403)
    if reg.da_in and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bản ghi đã in, liên hệ Admin nếu cần sửa'}, status=403)

    data = _qr_form_data(request, reg.phong_giao_dich, reg.loai)
    error = _qr_form_error(data, reg.loai)
    if error:
        return JsonResponse({'success': False, 'error': error}, status=400)

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
    if reg.da_in and not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Bản ghi đã in, liên hệ Admin nếu cần xóa'}, status=403)
    ten_kh = reg.ten_kh
    reg.delete()
    return JsonResponse({'success': True, 'message': f'Đã xóa đăng ký của {ten_kh}'})


@login_required
@require_http_methods(["POST"])
def qr_registration_mark_printed_view(request, pk):
    """Admin tích/bỏ tích ô Đã in (da_in=1 là đã in)."""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Chỉ admin mới được đánh dấu đã in'}, status=403)

    reg = get_object_or_404(QRRegistration, pk=pk)

    reg.da_in = request.POST.get('da_in') == '1'
    if reg.da_in:
        reg.nguoi_in = _profile_defaults_qr(request.user)[0] or request.user.username
        reg.ngay_in = timezone.now()
        thong_tin_in = f"{reg.nguoi_in} — {timezone.localtime(reg.ngay_in):%d/%m/%Y %H:%M}"
    else:
        reg.nguoi_in = ''
        reg.ngay_in = None
        thong_tin_in = ''
    reg.save()
    return JsonResponse({'success': True, 'thong_tin_in': thong_tin_in})


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
def qr_registration_export_view(request):
    """Tải danh sách đăng ký QR / Loa Thần tài (toàn bộ cán bộ) ra file Excel — chỉ admin."""
    if not request.user.is_superuser:
        messages.error(request, 'Chỉ admin mới được tải danh sách QR / Loa')
        return redirect('qr_registration_list')

    qs, _ = _filter_qr(QRRegistration.objects.all(), request)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Danh sach QR'

    headers = ['STT', 'Tên khách hàng', 'Số tài khoản', 'Tên cửa hàng',
               'Tên cán bộ đăng ký', 'Phòng giao dịch', 'Ngày đăng ký', 'Trạng thái',
               'Loại', 'Địa chỉ', 'Số điện thoại']
    ws.append(headers)
    header_fill = PatternFill('solid', fgColor='8B1E2D')
    bold_white = Font(bold=True, color='FFFFFF')
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = bold_white
        cell.alignment = Alignment(horizontal='center', vertical='center')

    for i, reg in enumerate(qs, 1):
        ws.append([
            i, reg.ten_kh, reg.so_tai_khoan, reg.ten_cua_hang,
            reg.ten_can_bo, reg.phong_giao_dich,
            timezone.localtime(reg.ngay_dang_ky).strftime('%d/%m/%Y %H:%M'),
            'Đã in' if reg.da_in else 'Chưa in',
            reg.get_loai_display(), reg.dia_chi, reg.so_dien_thoai,
        ])
        # Giữ số tài khoản dạng text để Excel không làm mất số 0 đầu
        ws.cell(row=i + 1, column=3).number_format = '@'
        ws.cell(row=i + 1, column=11).number_format = '@'

    col_widths = [6, 28, 20, 32, 26, 26, 18, 16, 14, 36, 16]
    for col, w in enumerate(col_widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    resp = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    resp['Content-Disposition'] = f'attachment; filename="Danh_Sach_QR_{date.today():%Y%m%d}.xlsx"'
    return resp


@login_required
def qr_huong_dan_word_view(request):
    """Tải hướng dẫn sử dụng chức năng Đăng ký bảng QR / Loa Thần tài dạng Word (.docx)."""
    doc = Document()
    normal = doc.styles['Normal']
    normal.font.name = 'Times New Roman'
    normal.font.size = Pt(13)

    title = doc.add_heading('HƯỚNG DẪN SỬ DỤNG CHỨC NĂNG ĐĂNG KÝ BẢNG QR / LOA THẦN TÀI', level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for heading, items in QR_HUONG_DAN:
        doc.add_heading(heading, level=1)
        for item in items:
            doc.add_paragraph(item, style='List Bullet')

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    resp = HttpResponse(
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    resp['Content-Disposition'] = 'attachment; filename="Huong_dan_Dang_ky_QR.docx"'
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
