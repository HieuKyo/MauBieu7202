"""
KPI Dashboard Views - Django Integration
=========================================
Views for Bank KPI Dashboard integrated directly into Django
No Streamlit required - pure Django implementation
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
import calendar
from datetime import datetime
from io import BytesIO

from .kpi_utils.kpi_data_processor import DataProcessor
from .kpi_utils.kpi_calculator import KPICalculator


# Danh sách GDV
GDV_LIST = [
    'GRATHIEU',
    'GRATNNHI',
    'GRACACHI',
    'GRANSINH',
    'GRALTHUC',
    'GRATTHAO',
    'GRANTHAO',
    'GRASHANH'
]

# Hệ số KPI mặc định
DEFAULT_COEFFICIENTS = {
    'card': 3.0,
    'signature': 3.0,
    'sms': 4.0,
    'archive': 0.5,
    'cif': 3.0
}


@login_required
def kpi_dashboard_view(request):
    """
    Main KPI Dashboard page - Django implementation
    """
    current_month = datetime.now().month
    current_year = datetime.now().year

    context = {
        'page_title': 'Dashboard Tính KPI Ngân hàng',
        'gdv_list': GDV_LIST,
        'current_month': current_month,
        'current_year': current_year,
        'year_range': range(2020, 2031),  # 2020 to 2030
        'coefficients': DEFAULT_COEFFICIENTS,
    }
    return render(request, 'templates_app/kpi/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def kpi_process_view(request):
    """
    Process KPI calculation and return Excel file
    """
    try:
        # Get form data with validation
        month_str = request.POST.get('month')
        year_str = request.POST.get('year')
        user_id = request.POST.get('user_id')

        # Validate and convert month/year
        try:
            # Remove any locale-specific thousand separators (. or ,)
            # Handle cases like "2.025" or "2,025" which should be "2025"
            if month_str:
                month_str = month_str.replace('.', '').replace(',', '')
            if year_str:
                year_str = year_str.replace('.', '').replace(',', '')

            month = int(month_str)
            year = int(year_str)
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'success': False,
                'error': f'Tháng hoặc năm không hợp lệ: {month_str}, {year_str}'
            }, status=400)

        # Validate ranges
        if not (1 <= month <= 12):
            return JsonResponse({
                'success': False,
                'error': 'Tháng phải từ 1 đến 12.'
            }, status=400)

        if not (2020 <= year <= 2030):
            return JsonResponse({
                'success': False,
                'error': 'Năm phải từ 2020 đến 2030.'
            }, status=400)

        # Get coefficients (with defaults)
        coefficients = {
            'card': float(request.POST.get('coef_card', DEFAULT_COEFFICIENTS['card'])),
            'signature': float(request.POST.get('coef_signature', DEFAULT_COEFFICIENTS['signature'])),
            'sms': float(request.POST.get('coef_sms', DEFAULT_COEFFICIENTS['sms'])),
            'archive': float(request.POST.get('coef_archive', DEFAULT_COEFFICIENTS['archive'])),
            'cif': float(request.POST.get('coef_cif', DEFAULT_COEFFICIENTS['cif'])),
        }

        # Get uploaded files
        template_file = request.FILES.get('template_file')
        card_file = request.FILES.get('card_file')
        sms_file = request.FILES.get('sms_file')
        emobile_file = request.FILES.get('emobile_file')

        # Validate
        if not template_file:
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng upload file KPI mẫu!'
            }, status=400)

        if not (card_file or sms_file or emobile_file):
            return JsonResponse({
                'success': False,
                'error': 'Vui lòng upload ít nhất một file dữ liệu (Thẻ, SMS hoặc E-Mobile)!'
            }, status=400)

        # Initialize processors
        days_in_month = calendar.monthrange(year, month)[1]
        data_processor = DataProcessor(user_id, month, year)
        kpi_calculator = KPICalculator(coefficients)

        # Process data files
        card_data = None
        sms_data = None
        emobile_data = None
        summary = {}

        if card_file:
            card_data = data_processor.process_card_file(card_file)
            summary['card'] = {
                'total': int(card_data['count'].sum()) if not card_data.empty else 0,
                'new_issue': int(card_data['new_issue_count'].sum()) if not card_data.empty else 0
            }

        if sms_file:
            sms_data = data_processor.process_sms_file(sms_file)
            summary['sms'] = {
                'total': int(sms_data['count'].sum()) if not sms_data.empty else 0
            }

        if emobile_file:
            emobile_data = data_processor.process_emobile_file(emobile_file)
            summary['emobile'] = {
                'total': int(emobile_data['count'].sum()) if not emobile_data.empty else 0
            }

        # Calculate KPI and update template
        output_buffer = kpi_calculator.calculate_and_update_template(
            template_file=template_file,
            card_data=card_data,
            sms_data=sms_data,
            emobile_data=emobile_data,
            days_in_month=days_in_month
        )

        # Return Excel file
        filename = f"KPI_{user_id}_{month:02d}_{year}.xlsx"
        response = HttpResponse(
            output_buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Lỗi xảy ra: {str(e)}'
        }, status=500)
