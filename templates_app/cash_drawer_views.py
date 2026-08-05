"""
Bảng kê tiền mặt (Kế toán Ngân quỹ) — theo dõi tồn quỹ theo mệnh giá của từng
GDV và in bảng kê thu/chi đè lên giấy nộp/rút tiền in sẵn (chỉ in số, không vẽ
khung/bảng — giấy đã có kẻ ô sẵn).
"""
import io
import os
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from reportlab.lib.pagesizes import A5, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from .models import (
    CASH_DENOMINATIONS, CashDrawerBalance, CashDrawerStatement,
    CashPrintConfig, CashPrintConfigNopTien, GlobalConfig,
    CashPrintConfigBangKeThu, CashPrintConfigBangKeChi, CashPrintConfigDeNghi,
)

# Helvetica (font PDF chuẩn) không có dấu tiếng Việt — đăng ký font hệ thống Windows
# (Arial/Tahoma) để in đúng dấu. Hệ thống chạy trên LAN Windows nội bộ nên font này
# luôn có sẵn; nếu không tìm thấy (vd chạy thử trên máy khác), rơi về Helvetica.
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'
FONT_OBLIQUE = 'Helvetica-Oblique'

for _regular, _bold in [
    (r'C:\Windows\Fonts\arial.ttf', r'C:\Windows\Fonts\arialbd.ttf'),
    (r'C:\Windows\Fonts\tahoma.ttf', r'C:\Windows\Fonts\tahomabd.ttf'),
]:
    if os.path.exists(_regular):
        try:
            pdfmetrics.registerFont(TTFont('VNRegular', _regular))
            FONT_REGULAR = FONT_OBLIQUE = 'VNRegular'
            if os.path.exists(_bold):
                pdfmetrics.registerFont(TTFont('VNBold', _bold))
                FONT_BOLD = 'VNBold'
            else:
                FONT_BOLD = 'VNRegular'
            break
        except Exception:
            continue


# ---------------------------------------------------------------------------
# Chuyển số tiền sang chữ tiếng Việt
# ---------------------------------------------------------------------------

_ONES  = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
_TEENS = ['mười', 'mười một', 'mười hai', 'mười ba', 'mười bốn', 'mười lăm',
          'mười sáu', 'mười bảy', 'mười tám', 'mười chín']
_TENS  = ['', '', 'hai mươi', 'ba mươi', 'bốn mươi', 'năm mươi',
          'sáu mươi', 'bảy mươi', 'tám mươi', 'chín mươi']
_UNIT_NAMES = ['', 'ngàn', 'triệu', 'tỷ']


def _group3(n, has_higher=False):
    if n == 0:
        return ''
    h, r = divmod(n, 100)
    t, u = divmod(r, 10)
    parts = []
    if h:
        parts.append(_ONES[h] + ' trăm')
    if r == 0:
        pass
    elif r < 10:
        parts.append(('lẻ ' if h or has_higher else '') + _ONES[r])
    elif r < 20:
        parts.append(_TEENS[r - 10])
    else:
        unit = '' if u == 0 else (' mốt' if u == 1 else (' lăm' if u == 5 else ' ' + _ONES[u]))
        parts.append(_TENS[t] + unit)
    return ' '.join(parts)


def _so_tien_bang_chu(so_tien):
    """VD: 7400000 -> 'Bảy triệu, bốn trăm ngàn đồng.' (giọng miền Nam, dùng 'ngàn')."""
    n = abs(int(so_tien))
    if n == 0:
        return 'Không đồng.'

    groups = []
    while n > 0:
        groups.append(n % 1000)
        n //= 1000

    parts = []
    has_higher = False
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g == 0:
            continue
        text = _group3(g, has_higher=has_higher)
        unit = _UNIT_NAMES[i] if i < len(_UNIT_NAMES) else ''
        parts.append(f"{text} {unit}".strip())
        has_higher = True

    result = ', '.join(parts)
    return result[0].upper() + result[1:] + ' đồng.'


def _current_balances(user):
    """Trả về dict {menh_gia: so_to} đầy đủ 9 mệnh giá (mặc định 0 nếu chưa có)."""
    existing = {b.menh_gia: b.so_to for b in CashDrawerBalance.objects.filter(user=user)}
    return {mg: existing.get(mg, 0) for mg in CASH_DENOMINATIONS}


def _parse_chi_tiet(request):
    """Đọc số tờ từng mệnh giá từ POST (name="so_to_<menh_gia>"), cộng thêm dòng
    "Khác" (name="khac_thanh_tien") — nhập trực tiếp số tiền, không phải số tờ,
    dùng cho khoản không thuộc mệnh giá chuẩn (không tính vào tồn quỹ theo tờ).
    Số âm bị chặn (không cho nhập số tờ/số tiền âm)."""
    chi_tiet = {}
    for mg in CASH_DENOMINATIONS:
        raw = request.POST.get(f'so_to_{mg}', '0').strip()
        try:
            so_to = int(raw) if raw else 0
        except ValueError:
            so_to = 0
        if so_to > 0:
            chi_tiet[str(mg)] = so_to

    raw_khac = request.POST.get('khac_thanh_tien', '0').strip()
    try:
        khac = int(float(raw_khac)) if raw_khac else 0
    except ValueError:
        khac = 0
    if khac > 0:
        chi_tiet['khac'] = khac

    return chi_tiet


def _apply_chi_tiet_to_balance(user, loai, chi_tiet, reverse=False):
    """Cộng/trừ tồn quỹ theo chi_tiet. THU/NHAP_QUY cộng, CHI trừ; reverse=True để
    hoàn tác (dùng khi xóa/sửa 1 bút toán đã lưu)."""
    dau = -1 if loai == 'CHI' else 1
    if reverse:
        dau = -dau
    for mg_str, so_to in chi_tiet.items():
        if mg_str == 'khac':
            continue
        mg = int(mg_str)
        balance, _ = CashDrawerBalance.objects.get_or_create(user=user, menh_gia=mg)
        balance.so_to += dau * so_to
        balance.save()


def _chi_tiet_tong_tien(chi_tiet):
    """Tính tổng tiền từ chi_tiet — 'khac' là số tiền trực tiếp, còn lại là mệnh_giá*so_to."""
    tong = 0
    for key, val in chi_tiet.items():
        tong += val if key == 'khac' else int(key) * val
    return tong


@login_required
def cash_statement_view(request):
    balances = _current_balances(request.user)
    balance_rows = [
        {'menh_gia': mg, 'so_to': so_to, 'thanh_tien': mg * so_to}
        for mg, so_to in balances.items()
    ]
    tong_ton_quy = sum(row['thanh_tien'] for row in balance_rows)

    history = CashDrawerStatement.objects.filter(user=request.user)[:20]

    print_id = request.GET.get('print_id')
    print_pdf_url_name = None
    print_statement_loai = None
    if print_id:
        stmt = CashDrawerStatement.objects.filter(pk=print_id, user=request.user).first()
        if stmt:
            print_statement_loai = stmt.loai
            if stmt.loai == 'DE_NGHI':
                print_pdf_url_name = 'cash_de_nghi_pdf'
            else:
                kieu_in = request.GET.get('kieu', 'trang')
                print_pdf_url_name = 'cash_statement_full_pdf' if kieu_in == 'day_du' else 'cash_statement_print_pdf'
        else:
            print_id = None

    context = {
        'denominations': CASH_DENOMINATIONS,
        'balance_rows': balance_rows,
        'tong_ton_quy': tong_ton_quy,
        'history': history,
        'print_id': print_id,
        'print_pdf_url_name': print_pdf_url_name,
        'print_statement_loai': print_statement_loai,
    }
    return render(request, 'templates_app/cash/statement.html', context)


@login_required
@require_http_methods(["POST"])
def cash_statement_submit_view(request):
    loai = request.POST.get('loai', '').strip()
    if loai not in ('THU', 'CHI', 'NHAP_QUY'):
        messages.error(request, "Loại bảng kê không hợp lệ.")
        return redirect('cash_statement')

    chi_tiet = _parse_chi_tiet(request)
    if not chi_tiet:
        messages.error(request, "Vui lòng nhập số tờ cho ít nhất 1 mệnh giá.")
        return redirect('cash_statement')

    ghi_chu = request.POST.get('ghi_chu', '').strip()
    tong_tien = _chi_tiet_tong_tien(chi_tiet)

    # CHI: kiểm tra đủ tồn quỹ mới cho xuất (bỏ qua dòng "Khác", không theo dõi tồn quỹ)
    if loai == 'CHI':
        balances = _current_balances(request.user)
        thieu = [
            mg for mg, so_to in chi_tiet.items()
            if mg != 'khac' and so_to > balances.get(int(mg), 0)
        ]
        if thieu:
            messages.error(
                request,
                f"Không đủ tồn quỹ mệnh giá: {', '.join(f'{int(mg):,}đ' for mg in thieu)}."
            )
            return redirect('cash_statement')

    statement = CashDrawerStatement.objects.create(
        user=request.user, loai=loai, ghi_chu=ghi_chu,
        chi_tiet=chi_tiet, tong_tien=tong_tien,
    )

    _apply_chi_tiet_to_balance(request.user, loai, chi_tiet)

    if loai in ('THU', 'CHI'):
        kieu_in = request.POST.get('kieu_in', 'trang').strip()
        messages.success(request, f"Đã lưu {statement.get_loai_display().lower()} {tong_tien:,}đ. Đang tải file PDF...")
        return redirect(f"{reverse('cash_statement')}?print_id={statement.id}&kieu={kieu_in}")

    messages.success(request, f"Đã ghi nhận nhập quỹ {tong_tien:,}đ.")
    return redirect('cash_statement')


@login_required
@require_http_methods(["POST"])
def cash_de_nghi_submit_view(request):
    """Đề nghị tiếp quỹ — chỉ cần tổng số tiền muốn nhận, KHÔNG rõ mệnh giá trước
    (do thủ quỹ chính quyết định khi xuất), nên không cập nhật tồn quỹ ở bước này."""
    raw = request.POST.get('tong_tien_de_nghi', '').strip()
    try:
        tong_tien = int(float(raw)) if raw else 0
    except ValueError:
        tong_tien = 0

    if tong_tien <= 0:
        messages.error(request, "Vui lòng nhập số tiền đề nghị tiếp quỹ lớn hơn 0.")
        return redirect('cash_statement')

    statement = CashDrawerStatement.objects.create(
        user=request.user, loai='DE_NGHI',
        ghi_chu=request.POST.get('ghi_chu', '').strip(),
        chi_tiet={}, tong_tien=tong_tien,
    )
    messages.success(request, f"Đã lập đề nghị tiếp quỹ {tong_tien:,}đ. Đang tải file PDF...")
    return redirect(f"{reverse('cash_statement')}?print_id={statement.id}")


def _check_statement_edit_permission(request, statement):
    """Trả về (None) nếu được phép sửa/xóa, hoặc thông báo lỗi nếu không."""
    if statement.user_id != request.user.id and not request.user.is_superuser:
        return "Bạn không có quyền sửa/xóa bút toán này."
    if statement.loai == 'RESET':
        return "Không thể sửa/xóa bút toán reset counter (đã chốt số dư out quỹ)."
    return None


@login_required
def cash_statement_edit_view(request, pk):
    """Form sửa 1 bút toán đã lưu — cho phép nhập lại đúng số tờ khi lỡ gõ nhầm."""
    statement = get_object_or_404(CashDrawerStatement, pk=pk)
    err = _check_statement_edit_permission(request, statement)
    if err:
        messages.error(request, err)
        return redirect('cash_drawer_history')

    context = {
        'statement': statement,
        'denomination_rows': [
            {'mg': mg, 'so_to': statement.chi_tiet.get(str(mg), 0)}
            for mg in CASH_DENOMINATIONS
        ],
        'khac_tien': statement.chi_tiet.get('khac', 0),
    }
    return render(request, 'templates_app/cash/edit_statement.html', context)


@login_required
@require_http_methods(["POST"])
def cash_statement_edit_submit_view(request, pk):
    statement = get_object_or_404(CashDrawerStatement, pk=pk)
    err = _check_statement_edit_permission(request, statement)
    if err:
        messages.error(request, err)
        return redirect('cash_drawer_history')

    ghi_chu = request.POST.get('ghi_chu', '').strip()

    if statement.loai == 'DE_NGHI':
        raw = request.POST.get('tong_tien_de_nghi', '').strip()
        try:
            tong_tien = int(float(raw)) if raw else 0
        except ValueError:
            tong_tien = 0
        if tong_tien <= 0:
            messages.error(request, "Vui lòng nhập số tiền đề nghị lớn hơn 0.")
            return redirect('cash_statement_edit', pk=pk)
        statement.tong_tien = tong_tien
        statement.ghi_chu = ghi_chu
        statement.save()
        messages.success(request, "Đã cập nhật đề nghị tiếp quỹ.")
        return redirect('cash_drawer_history')

    # THU / CHI / NHAP_QUY: hoàn tác tồn quỹ theo số liệu cũ, áp lại theo số liệu mới
    new_chi_tiet = _parse_chi_tiet(request)
    if not new_chi_tiet:
        messages.error(request, "Vui lòng nhập số tờ cho ít nhất 1 mệnh giá.")
        return redirect('cash_statement_edit', pk=pk)

    _apply_chi_tiet_to_balance(statement.user, statement.loai, statement.chi_tiet, reverse=True)

    if statement.loai == 'CHI':
        balances = _current_balances(statement.user)
        thieu = [
            mg for mg, so_to in new_chi_tiet.items()
            if mg != 'khac' and so_to > balances.get(int(mg), 0)
        ]
        if thieu:
            # Chưa đủ tồn quỹ cho số liệu mới — hoàn tác lại bước reverse ở trên
            _apply_chi_tiet_to_balance(statement.user, statement.loai, statement.chi_tiet)
            messages.error(
                request,
                f"Không đủ tồn quỹ mệnh giá: {', '.join(f'{int(mg):,}đ' for mg in thieu)}."
            )
            return redirect('cash_statement_edit', pk=pk)

    _apply_chi_tiet_to_balance(statement.user, statement.loai, new_chi_tiet)

    statement.chi_tiet = new_chi_tiet
    statement.tong_tien = _chi_tiet_tong_tien(new_chi_tiet)
    statement.ghi_chu = ghi_chu
    statement.save()
    messages.success(request, "Đã cập nhật bút toán và tồn quỹ.")
    return redirect('cash_drawer_history')


@login_required
@require_http_methods(["POST"])
def cash_statement_delete_view(request, pk):
    statement = get_object_or_404(CashDrawerStatement, pk=pk)
    err = _check_statement_edit_permission(request, statement)
    if err:
        messages.error(request, err)
        return redirect('cash_drawer_history')

    if statement.loai in ('THU', 'CHI', 'NHAP_QUY'):
        _apply_chi_tiet_to_balance(statement.user, statement.loai, statement.chi_tiet, reverse=True)

    statement.delete()
    messages.success(request, "Đã xóa bút toán và cập nhật lại tồn quỹ.")
    return redirect('cash_drawer_history')


@login_required
@require_http_methods(["POST"])
def cash_drawer_reset_view(request):
    """Reset counter về 0 (out quỹ giữa ngày hoặc cuối ngày) — lưu snapshot trước khi xóa."""
    balances = _current_balances(request.user)
    non_zero = {str(mg): so_to for mg, so_to in balances.items() if so_to}
    tong_tien = sum(int(mg) * so_to for mg, so_to in non_zero.items())

    if non_zero:
        CashDrawerStatement.objects.create(
            user=request.user, loai='RESET',
            ghi_chu=request.POST.get('ghi_chu', '').strip(),
            chi_tiet=non_zero, tong_tien=tong_tien,
        )
        CashDrawerBalance.objects.filter(user=request.user).update(so_to=0)
        messages.success(request, f"Đã reset tồn quỹ ({tong_tien:,}đ đã out về quỹ chính).")
    else:
        messages.info(request, "Tồn quỹ hiện đang trống, không có gì để reset.")

    return redirect('cash_statement')


@login_required
def cash_drawer_history_view(request):
    ngay_str = request.GET.get('ngay', '').strip()
    try:
        ngay = date.fromisoformat(ngay_str) if ngay_str else date.today()
    except ValueError:
        ngay = date.today()

    qs = CashDrawerStatement.objects.filter(
        user=request.user,
        created_at__date=ngay,
    ).order_by('-created_at')

    tong_thu = sum(s.tong_tien for s in qs if s.loai == 'THU')
    tong_chi = sum(s.tong_tien for s in qs if s.loai == 'CHI')

    context = {
        'ngay': ngay.isoformat(),
        'statements': qs,
        'tong_thu': tong_thu,
        'tong_chi': tong_chi,
    }
    return render(request, 'templates_app/cash/history.html', context)


# ---------------------------------------------------------------------------
# Cấu hình in — trang gộp chung, chọn tab theo từng mẫu (5 mẫu)
# ---------------------------------------------------------------------------

def _config_field_list(config):
    """Sinh danh sách field số (bỏ id/updated_at) để template lặp render generic."""
    return [
        {'name': f.name, 'label': f.verbose_name, 'value': getattr(config, f.name)}
        for f in config._meta.fields
        if f.name not in ('id', 'updated_at')
    ]


# (key, tiêu đề tab, model, url submit, url preview)
CASH_PRINT_CONFIG_TABS = [
    ('trang', 'Bảng kê trắng (Thu/Chi)', CashPrintConfig,
     'cash_print_config_trang_submit', 'cash_print_config_preview'),
    ('trang_nop', 'Bảng kê trắng (giấy nộp tiền)', CashPrintConfigNopTien,
     'cash_print_config_nop_tien_submit', 'cash_print_config_nop_tien_preview'),
    ('thu', 'Bảng kê Thu (có khung)', CashPrintConfigBangKeThu,
     'cash_print_config_thu_submit', 'cash_print_config_thu_preview'),
    ('chi', 'Bảng kê Chi (có khung)', CashPrintConfigBangKeChi,
     'cash_print_config_chi_submit', 'cash_print_config_chi_preview'),
    ('de_nghi', 'Đề nghị tiếp quỹ', CashPrintConfigDeNghi,
     'cash_print_config_de_nghi_submit', 'cash_print_config_de_nghi_preview'),
]


@login_required
def cash_print_config_view(request):
    """Trang cấu hình in gộp chung — chọn tab để chỉnh từng mẫu, mỗi tab tự POST
    về endpoint riêng rồi quay lại đúng trang này."""
    tabs = []
    for key, label, model_cls, submit_url, preview_url in CASH_PRINT_CONFIG_TABS:
        config = model_cls.get_instance(request.user)
        tabs.append({
            'key': key,
            'label': label,
            'fields': _config_field_list(config),
            'submit_url': submit_url,
            'preview_url': preview_url,
        })
    return render(request, 'templates_app/cash/print_config.html', {'tabs': tabs})


def _generic_config_submit(request, config_model):
    config = config_model.get_instance(request.user)

    if 'cancel' in request.POST:
        messages.info(request, "Đã hủy, không lưu thay đổi.")
        return redirect('cash_print_config')

    fields = [f.name for f in config._meta.fields if f.name not in ('id', 'updated_at')]
    try:
        for f in fields:
            setattr(config, f, float(request.POST.get(f, getattr(config, f))))
    except ValueError:
        messages.error(request, "Giá trị nhập không hợp lệ (phải là số).")
        return redirect('cash_print_config')

    config.save()
    messages.success(request, "Đã lưu cấu hình in.")
    return redirect('cash_print_config')


@login_required
@require_http_methods(["POST"])
def cash_print_config_trang_submit_view(request):
    return _generic_config_submit(request, CashPrintConfig)


@login_required
@require_http_methods(["POST"])
def cash_print_config_nop_tien_submit_view(request):
    return _generic_config_submit(request, CashPrintConfigNopTien)


@login_required
@require_http_methods(["POST"])
def cash_print_config_thu_submit_view(request):
    return _generic_config_submit(request, CashPrintConfigBangKeThu)


@login_required
@require_http_methods(["POST"])
def cash_print_config_chi_submit_view(request):
    return _generic_config_submit(request, CashPrintConfigBangKeChi)


@login_required
@require_http_methods(["POST"])
def cash_print_config_de_nghi_submit_view(request):
    return _generic_config_submit(request, CashPrintConfigDeNghi)


def _sample_statement(user, loai='THU'):
    return CashDrawerStatement(
        user=user, loai=loai, created_at=datetime.now(),
        chi_tiet={str(mg): 1 for mg in CASH_DENOMINATIONS},
        tong_tien=sum(CASH_DENOMINATIONS),
    )


def _draw_statement_pdf(buf, statement, config):
    page_size = landscape(A5)
    c = canvas.Canvas(buf, pagesize=page_size)
    page_w, page_h = page_size
    c.setFont(FONT_REGULAR, config.font_size)

    def xy(x_mm, y_mm):
        """Chuyển tọa độ (mm từ trái, mm từ trên) + offset config sang điểm reportlab (gốc dưới-trái)."""
        x = (x_mm + config.offset_x) * mm
        y = page_h - (y_mm + config.offset_y) * mm
        return x, y

    # Từng dòng mệnh giá
    for i, mg in enumerate(CASH_DENOMINATIONS):
        so_to = statement.chi_tiet.get(str(mg), 0)
        if not so_to:
            continue
        row_y = config.start_y + i * config.row_spacing
        x1, y1 = xy(config.col_so_to_x, row_y)
        c.drawString(x1, y1, str(so_to))
        x2, y2 = xy(config.col_thanh_tien_x, row_y)
        c.drawRightString(x2, y2, f"{mg * so_to:,}")

    # Dòng "Khác" (nếu có) — ngay dưới dòng mệnh giá cuối cùng
    khac_tien = statement.chi_tiet.get('khac', 0)
    if khac_tien:
        row_y = config.start_y + len(CASH_DENOMINATIONS) * config.row_spacing
        x2, y2 = xy(config.col_thanh_tien_x, row_y)
        c.drawRightString(x2, y2, f"{khac_tien:,}")

    # Tổng cộng
    x, y = xy(config.total_x, config.total_y)
    c.drawRightString(x, y, f"{statement.tong_tien:,}")

    # Số tiền bằng chữ
    x, y = xy(config.so_tien_chu_x, config.so_tien_chu_y)
    c.drawString(x, y, _so_tien_bang_chu(statement.tong_tien))

    c.showPage()
    c.save()


def _ngay_thang_nam(d):
    return f"Ngày {d.day:02d} tháng {d.month:02d} năm {d.year}"


def _draw_full_statement_pdf(buf, statement, config):
    """Bảng kê Thu/Chi tiền — chứng từ đầy đủ có khung/bảng + tiêu đề."""
    page_size = landscape(A5)
    c = canvas.Canvas(buf, pagesize=page_size)
    page_w, page_h = page_size
    margin = config.margin * mm
    title_fs = config.title_font_size
    body_fs = config.body_font_size
    row_h = config.row_height * mm
    ox, oy = config.offset_x * mm, -config.offset_y * mm

    def X(x):
        return x + ox

    def Y(y):
        return y + oy

    tieu_de = 'BẢNG KÊ THU TIỀN' if statement.loai == 'THU' else 'BẢNG KÊ CHI TIỀN'

    c.setFont(FONT_BOLD, title_fs)
    c.drawCentredString(X(page_w / 2), Y(page_h - margin - 5 * mm), tieu_de)
    c.setFont(FONT_OBLIQUE, body_fs)
    c.drawCentredString(X(page_w / 2), Y(page_h - margin - 11 * mm), _ngay_thang_nam(statement.created_at))

    # Bảng: (trống) | Mệnh giá | Số Tờ | Thành Tiền
    col_widths = [12 * mm, 40 * mm, 25 * mm, 40 * mm]
    table_w = sum(col_widths)
    table_x = (page_w - table_w) / 2
    header_y = page_h - margin - 18 * mm

    rows = [(mg, statement.chi_tiet.get(str(mg), 0)) for mg in CASH_DENOMINATIONS]
    khac_tien = statement.chi_tiet.get('khac', 0)
    n_rows = len(rows) + 1 + 2  # + dòng Khác + header + Tổng cộng
    table_h = row_h * n_rows

    col_x = [table_x]
    for w in col_widths:
        col_x.append(col_x[-1] + w)

    # Khung ngoài + các đường kẻ ngang/dọc
    c.setLineWidth(0.6)
    c.rect(X(table_x), Y(header_y - table_h), table_w, table_h)
    for i in range(1, n_rows):
        y = header_y - i * row_h
        c.line(X(table_x), Y(y), X(table_x + table_w), Y(y))
    for x in col_x[1:-1]:
        c.line(X(x), Y(header_y - table_h), X(x), Y(header_y))

    c.setFont(FONT_BOLD, body_fs)
    for i, htext in enumerate(['', 'Mệnh giá', 'Số Tờ', 'Thành Tiền']):
        c.drawCentredString(X((col_x[i] + col_x[i + 1]) / 2), Y(header_y - row_h + 2 * mm), htext)

    c.setFont(FONT_REGULAR, body_fs)
    for i, (mg, so_to) in enumerate(rows, start=1):
        y = header_y - (i + 1) * row_h + 2 * mm
        c.drawCentredString(X((col_x[0] + col_x[1]) / 2), Y(y), str(i))
        c.drawCentredString(X((col_x[1] + col_x[2]) / 2), Y(y), f"{mg:,}")
        c.drawCentredString(X((col_x[2] + col_x[3]) / 2), Y(y), str(so_to) if so_to else '')
        c.drawRightString(X(col_x[4] - 2 * mm), Y(y), f"{mg * so_to:,}")

    # Dòng "Khác"
    khac_row_idx = len(rows) + 1
    y = header_y - (khac_row_idx + 1) * row_h + 2 * mm
    c.drawCentredString(X((col_x[0] + col_x[1]) / 2), Y(y), str(khac_row_idx))
    c.drawCentredString(X((col_x[1] + col_x[2]) / 2), Y(y), 'Khác')
    c.drawRightString(X(col_x[4] - 2 * mm), Y(y), f"{khac_tien:,}")

    # Dòng Tổng cộng (đỏ, đậm)
    tong_y = header_y - n_rows * row_h + 2 * mm
    c.setFont(FONT_BOLD, body_fs)
    c.drawCentredString(X((col_x[0] + col_x[2]) / 2), Y(tong_y), 'Tổng cộng')
    c.setFillColorRGB(0.8, 0, 0)
    c.drawRightString(X(col_x[4] - 2 * mm), Y(tong_y), f"{statement.tong_tien:,}")
    c.setFillColorRGB(0, 0, 0)

    # Số tiền bằng chữ — ngay dưới bảng, canh cùng lề trái với bảng
    table_bottom_y = header_y - table_h
    c.setFont(FONT_OBLIQUE, body_fs)
    chu_y = table_bottom_y - 8 * mm
    c.drawString(X(table_x), Y(chu_y), f"Bằng chữ: {_so_tien_bang_chu(statement.tong_tien)}")

    # Khách hàng / Giao dịch viên — canh theo dòng bằng chữ để không đè lên bảng
    footer_label_y = chu_y - 10 * mm
    c.setFont(FONT_BOLD, body_fs)
    c.drawCentredString(X(page_w * 0.25), Y(footer_label_y), 'Khách hàng')
    c.drawCentredString(X(page_w * 0.75), Y(footer_label_y), 'Giao dịch viên')

    c.showPage()
    c.save()


def _draw_de_nghi_tiep_quy_pdf(buf, statement, config):
    """GIẤY ĐỀ NGHỊ TIẾP QUỸ (Mẫu 13/TTKQ) — chỉ có tổng số tiền, không có mệnh giá
    (do thủ quỹ chính quyết định loại tiền khi xuất quỹ)."""
    page_size = landscape(A5)
    c = canvas.Canvas(buf, pagesize=page_size)
    page_w, page_h = page_size
    margin = config.margin * mm
    title_fs = config.title_font_size
    body_fs = config.body_font_size
    ox, oy = config.offset_x * mm, -config.offset_y * mm

    def X(x):
        return x + ox

    def Y(y):
        return y + oy

    ten_chi_nhanh = GlobalConfig.get_instance().ten_chi_nhanh

    c.setFont(FONT_REGULAR, body_fs - 1)
    c.drawRightString(X(page_w - margin), Y(page_h - margin), 'Mẫu 13/TTKQ')

    y = page_h - margin - 6 * mm
    c.setFont(FONT_BOLD, body_fs)
    c.drawString(X(margin), Y(y), 'NGÂN HÀNG NÔNG NGHIỆP')
    c.drawCentredString(X(page_w * 0.72), Y(y), 'CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM')
    y -= 4.5 * mm
    c.drawString(X(margin), Y(y), 'VÀ PHÁT TRIỂN NÔNG THÔN VIỆT NAM')
    c.setFont(FONT_OBLIQUE, body_fs)
    c.drawCentredString(X(page_w * 0.72), Y(y), 'Độc lập - Tự do - Hạnh phúc')
    y -= 4.5 * mm
    c.setFont(FONT_REGULAR, body_fs)
    c.drawString(X(margin), Y(y), f"Chi nhánh: {ten_chi_nhanh}")

    y -= 8 * mm
    c.drawString(X(margin), Y(y), 'Số: ........................')
    c.setFont(FONT_OBLIQUE, body_fs)
    c.drawCentredString(X(page_w * 0.72), Y(y), _ngay_thang_nam(statement.created_at))

    y -= 10 * mm
    c.setFont(FONT_BOLD, title_fs)
    c.drawCentredString(X(page_w / 2), Y(y), 'GIẤY ĐỀ NGHỊ TIẾP QUỸ')

    y -= 9 * mm
    c.setFont(FONT_REGULAR, body_fs)
    c.drawString(X(margin), Y(y), f"Kính gửi: Ban giám đốc Agribank Chi nhánh {ten_chi_nhanh}")
    y -= 6 * mm
    c.drawString(X(margin), Y(y), 'Căn cứ nhu cầu tiền mặt giao dịch trong ngày;')
    y -= 6 * mm
    c.drawString(X(margin), Y(y), 'Đề nghị tiếp quỹ tiền mặt như sau:')

    ten_gdv = statement.user.get_full_name() or statement.user.username
    y -= 6 * mm
    c.drawString(X(margin), Y(y), f"- Người đề nghị: {ten_gdv}      User ID: {statement.user.username.upper()}")
    y -= 6 * mm
    c.drawString(X(margin), Y(y), f"- Người nhận: {ten_gdv}      Phòng/Tổ: KTNQ")
    y -= 6 * mm
    c.drawString(X(margin), Y(y), '- Loại tiền tệ: VND')
    y -= 6 * mm
    c.drawString(X(margin), Y(y), '- Số tiền bằng số: ')
    c.setFont(FONT_OBLIQUE, body_fs)
    c.drawString(X(margin + 38 * mm), Y(y), f"{statement.tong_tien:,} VND")
    y -= 6 * mm
    c.setFont(FONT_REGULAR, body_fs)
    c.drawString(X(margin), Y(y), '- Số tiền bằng chữ: ')
    c.setFont(FONT_OBLIQUE, body_fs)
    c.drawString(X(margin + 38 * mm), Y(y), _so_tien_bang_chu(statement.tong_tien))

    y -= 10 * mm
    c.setFont(FONT_BOLD, body_fs)
    c.drawCentredString(X(page_w * 0.18), Y(y), 'NGƯỜI ĐỀ NGHỊ')
    c.drawCentredString(X(page_w * 0.5), Y(y), 'NGƯỜI KIỂM SOÁT')
    c.drawCentredString(X(page_w * 0.82), Y(y), 'NGƯỜI PHÊ DUYỆT')
    y -= 5 * mm
    c.setFont(FONT_OBLIQUE, body_fs - 1)
    c.drawCentredString(X(page_w * 0.18), Y(y), '(Ký, ghi rõ họ tên)')
    c.drawCentredString(X(page_w * 0.5), Y(y), '(Ký, ghi rõ họ tên)')
    c.drawCentredString(X(page_w * 0.82), Y(y), '(Ký, ghi rõ họ tên)')

    y -= 14 * mm
    c.setFont(FONT_REGULAR, body_fs)
    c.drawCentredString(X(page_w * 0.18), Y(y), ten_gdv)

    c.showPage()
    c.save()


@login_required
def cash_statement_print_pdf_view(request, pk):
    statement = get_object_or_404(CashDrawerStatement, pk=pk)
    if statement.user_id != request.user.id and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền in bảng kê này.")
        return redirect('cash_statement')

    config = CashPrintConfig.get_instance(request.user)
    buf = io.BytesIO()
    _draw_statement_pdf(buf, statement, config)
    buf.seek(0)

    loai_label = 'Thu' if statement.loai == 'THU' else 'Chi'
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = (
        f'attachment; filename="BangKe{loai_label}_{statement.created_at.strftime("%Y%m%d_%H%M%S")}.pdf"'
    )
    return resp


@login_required
def cash_statement_full_pdf_view(request, pk):
    """Bảng kê đầy đủ (có khung/tiêu đề) — dùng khi in lên giấy trắng thường,
    không phải giấy nộp/rút tiền in sẵn."""
    statement = get_object_or_404(CashDrawerStatement, pk=pk)
    if statement.user_id != request.user.id and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền in bảng kê này.")
        return redirect('cash_statement')
    if statement.loai not in ('THU', 'CHI'):
        messages.error(request, "Chỉ in được bảng kê đầy đủ cho Thu/Chi.")
        return redirect('cash_statement')

    config = (
        CashPrintConfigBangKeThu.get_instance(request.user) if statement.loai == 'THU'
        else CashPrintConfigBangKeChi.get_instance(request.user)
    )
    buf = io.BytesIO()
    _draw_full_statement_pdf(buf, statement, config)
    buf.seek(0)

    loai_label = 'Thu' if statement.loai == 'THU' else 'Chi'
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = (
        f'attachment; filename="BangKe{loai_label}DayDu_{statement.created_at.strftime("%Y%m%d_%H%M%S")}.pdf"'
    )
    return resp


@login_required
def cash_statement_nop_tien_pdf_view(request, pk):
    """Bảng kê trắng (giấy nộp tiền) — chỉ in số, layout tọa độ riêng cho tờ
    giấy nộp tiền in sẵn (khác giấy rút tiền)."""
    statement = get_object_or_404(CashDrawerStatement, pk=pk)
    if statement.user_id != request.user.id and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền in bảng kê này.")
        return redirect('cash_statement')

    config = CashPrintConfigNopTien.get_instance(request.user)
    buf = io.BytesIO()
    _draw_statement_pdf(buf, statement, config)
    buf.seek(0)

    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = (
        f'attachment; filename="BangKeTrangNopTien_{statement.created_at.strftime("%Y%m%d_%H%M%S")}.pdf"'
    )
    return resp


@login_required
def cash_de_nghi_pdf_view(request, pk):
    """Giấy đề nghị tiếp quỹ (Mẫu 13/TTKQ)."""
    statement = get_object_or_404(CashDrawerStatement, pk=pk)
    if statement.user_id != request.user.id and not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền in đề nghị này.")
        return redirect('cash_statement')
    if statement.loai != 'DE_NGHI':
        messages.error(request, "Bản ghi này không phải đề nghị tiếp quỹ.")
        return redirect('cash_statement')

    config = CashPrintConfigDeNghi.get_instance(request.user)
    buf = io.BytesIO()
    _draw_de_nghi_tiep_quy_pdf(buf, statement, config)
    buf.seek(0)

    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = (
        f'attachment; filename="DeNghiTiepQuy_{statement.created_at.strftime("%Y%m%d_%H%M%S")}.pdf"'
    )
    return resp


@login_required
def cash_print_config_preview_view(request):
    """In thử với dữ liệu mẫu để canh chỉnh tọa độ X/Y, không lưu vào lịch sử."""
    config = CashPrintConfig.get_instance(request.user)
    sample = CashDrawerStatement(
        user=request.user, loai='THU', created_at=datetime.now(),
        chi_tiet={str(mg): 1 for mg in CASH_DENOMINATIONS},
        tong_tien=sum(CASH_DENOMINATIONS),
    )
    buf = io.BytesIO()
    _draw_statement_pdf(buf, sample, config)
    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = 'inline; filename="in_thu_can_chinh.pdf"'
    return resp


@login_required
def cash_print_config_nop_tien_preview_view(request):
    """In thử bảng kê trắng (giấy nộp tiền) với dữ liệu mẫu để canh chỉnh tọa độ X/Y."""
    config = CashPrintConfigNopTien.get_instance(request.user)
    sample = CashDrawerStatement(
        user=request.user, loai='THU', created_at=datetime.now(),
        chi_tiet={str(mg): 1 for mg in CASH_DENOMINATIONS},
        tong_tien=sum(CASH_DENOMINATIONS),
    )
    buf = io.BytesIO()
    _draw_statement_pdf(buf, sample, config)
    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = 'inline; filename="in_nop_tien_can_chinh.pdf"'
    return resp


@login_required
def cash_print_config_thu_preview_view(request):
    """In thử Bảng kê Thu với dữ liệu mẫu để canh chỉnh cấu hình."""
    config = CashPrintConfigBangKeThu.get_instance(request.user)
    buf = io.BytesIO()
    _draw_full_statement_pdf(buf, _sample_statement(request.user, 'THU'), config)
    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = 'inline; filename="in_bang_ke_thu_can_chinh.pdf"'
    return resp


@login_required
def cash_print_config_chi_preview_view(request):
    """In thử Bảng kê Chi với dữ liệu mẫu để canh chỉnh cấu hình."""
    config = CashPrintConfigBangKeChi.get_instance(request.user)
    buf = io.BytesIO()
    _draw_full_statement_pdf(buf, _sample_statement(request.user, 'CHI'), config)
    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = 'inline; filename="in_bang_ke_chi_can_chinh.pdf"'
    return resp


@login_required
def cash_print_config_de_nghi_preview_view(request):
    """In thử Giấy đề nghị tiếp quỹ với dữ liệu mẫu để canh chỉnh cấu hình."""
    config = CashPrintConfigDeNghi.get_instance(request.user)
    sample = _sample_statement(request.user, 'DE_NGHI')
    sample.chi_tiet = {}
    buf = io.BytesIO()
    _draw_de_nghi_tiep_quy_pdf(buf, sample, config)
    buf.seek(0)
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = 'inline; filename="in_de_nghi_tiep_quy_can_chinh.pdf"'
    return resp
