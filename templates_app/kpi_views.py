"""
KPI Dashboard Views
===================
Views cho tính năng Quyết Toán KPI tháng - Agribank
"""

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .kpi_utils.kpi_data_processor import DataProcessor
from .kpi_utils.kpi_report_generator import generate_kpi_report


# Danh sách GDV
GDV_LIST = [
    'GRATHIEU',
    'GRATNNHI',
    'GRACACHI',
    'GRANSINH',
    'GRALTHUC',
    'GRATTHAO',
    'GRANTHAO',
    'GRASHANH',
]


@login_required
def kpi_dashboard_view(request):
    current_month = datetime.now().month
    current_year  = datetime.now().year

    context = {
        'page_title': 'Quyết Toán KPI Tháng',
        'gdv_list':      GDV_LIST,
        'current_month': current_month,
        'current_year':  current_year,
        'year_range':    range(2020, 2031),
    }
    return render(request, 'templates_app/kpi/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def kpi_process_view(request):
    """
    Xử lý dữ liệu và trả về file Excel báo cáo KPI.
    """
    try:
        # ── Đọc & validate thông tin cơ bản ───────────────────────
        month_str = (request.POST.get('month') or '').replace('.', '').replace(',', '')
        year_str  = (request.POST.get('year')  or '').replace('.', '').replace(',', '')
        user_id   = request.POST.get('user_id', '').strip()

        try:
            month = int(month_str)
            year  = int(year_str)
        except (ValueError, TypeError):
            return JsonResponse(
                {'success': False, 'error': f'Tháng hoặc năm không hợp lệ: {month_str}, {year_str}'},
                status=400,
            )

        if not (1 <= month <= 12):
            return JsonResponse({'success': False, 'error': 'Tháng phải từ 1 đến 12.'}, status=400)

        if not (2020 <= year <= 2030):
            return JsonResponse({'success': False, 'error': 'Năm phải từ 2020 đến 2030.'}, status=400)

        if not user_id:
            return JsonResponse({'success': False, 'error': 'Vui lòng chọn Mã GDV.'}, status=400)

        # ── Lấy file upload ───────────────────────────────────────
        cif_file         = request.FILES.get('cif_file')
        card_file        = request.FILES.get('card_file')
        sms_file         = request.FILES.get('sms_file')
        emobile_file     = request.FILES.get('emobile_file')
        billpayment_file = request.FILES.get('billpayment_file')

        if not cif_file:
            return JsonResponse(
                {'success': False, 'error': 'Vui lòng upload file CIF (dữ liệu mở tài khoản)!'},
                status=400,
            )

        # ── Xử lý dữ liệu ────────────────────────────────────────
        processor = DataProcessor(user_id, month, year)

        # CIF: cá nhân + tổ chức theo ngày
        cif_personal_by_day, cif_corporate_by_day = processor.process_cif_file(cif_file)

        # Thẻ, SMS, E-Mobile, Billpayment: trả về dict {ngày: count} trực tiếp
        card_by_day        = processor.process_card_file(card_file)            if card_file        else {}
        sms_by_day         = processor.process_sms_file(sms_file)              if sms_file         else {}
        emobile_by_day     = processor.process_emobile_file(emobile_file)      if emobile_file     else {}
        billpayment_by_day = processor.process_billpayment_file(billpayment_file) if billpayment_file else {}

        # ── Tạo báo cáo Excel ─────────────────────────────────────
        output_buffer = generate_kpi_report(
            month=month,
            year=year,
            user_id=user_id,
            cif_personal_by_day=cif_personal_by_day,
            cif_corporate_by_day=cif_corporate_by_day,
            card_by_day=card_by_day,
            sms_by_day=sms_by_day,
            emobile_by_day=emobile_by_day,
            billpayment_by_day=billpayment_by_day,
        )

        filename = f"KPI_QuyetToan_{user_id}_{month:02d}_{year}.xlsx"
        response = HttpResponse(
            output_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except ValueError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Lỗi xảy ra: {str(e)}'}, status=500)
