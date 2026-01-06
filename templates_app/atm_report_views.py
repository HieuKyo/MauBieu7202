"""
Views cho tính năng Báo cáo Nộp/rút ATM
"""
import re
import pandas as pd
from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse
from django.db import transaction

from .models import ATMTransactionReport, ATMReportUpload
from .forms import ATMReportUploadForm


def parse_filename_date(filename):
    """
    Parse tên file để lấy tháng và năm
    Format: MMYYYY.xls hoặc MMYYYY.xlsx
    VD: 122025.xls -> tháng 12, năm 2025

    Returns:
        tuple: (month, year) hoặc (None, None) nếu không hợp lệ
    """
    # Loại bỏ extension
    name_without_ext = filename.rsplit('.', 1)[0]

    # Pattern: 1-2 chữ số tháng + 4 chữ số năm
    pattern = r'^(\d{1,2})(\d{4})$'
    match = re.match(pattern, name_without_ext)

    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        # Validate tháng (1-12)
        if 1 <= month <= 12:
            return month, year

    return None, None


def import_atm_excel(excel_file, user):
    """
    Import dữ liệu từ file Excel và lưu vào database

    Args:
        excel_file: File object từ form upload
        user: User object của người upload

    Returns:
        dict: {'success': bool, 'message': str, 'upload_id': int, 'record_count': int}
    """
    try:
        # Parse tên file để lấy tháng/năm
        filename = excel_file.name
        month, year = parse_filename_date(filename)

        if month is None or year is None:
            return {
                'success': False,
                'message': f'Tên file không hợp lệ: "{filename}". Vui lòng đặt theo mẫu MMYYYY.xls (VD: 122025.xls)',
                'upload_id': None,
                'record_count': 0
            }

        # Tạo report_period (ngày đầu tiên của tháng)
        report_period = datetime(year, month, 1).date()

        # Kiểm tra xem đã có dữ liệu của tháng này chưa
        existing_upload = ATMReportUpload.objects.filter(report_period=report_period).first()
        if existing_upload:
            return {
                'success': False,
                'message': f'Dữ liệu tháng {month}/{year} đã tồn tại. Vui lòng xóa dữ liệu cũ trước khi import lại.',
                'upload_id': existing_upload.id,
                'record_count': existing_upload.record_count,
                'existing': True
            }

        # Đọc file Excel
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            return {
                'success': False,
                'message': f'Không thể đọc file Excel: {str(e)}',
                'upload_id': None,
                'record_count': 0
            }

        # Kiểm tra các cột bắt buộc
        required_columns = ['Branch_Code', 'ATM_No', 'Tx_Code', 'Tx_Count', 'Tx_Amount', 'Tx_Fee', 'vatamt']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return {
                'success': False,
                'message': f'File thiếu các cột: {", ".join(missing_columns)}',
                'upload_id': None,
                'record_count': 0
            }

        # Bắt đầu transaction để đảm bảo tính toàn vẹn dữ liệu
        with transaction.atomic():
            # Tạo ATMReportUpload record
            upload = ATMReportUpload.objects.create(
                file_name=filename,
                report_period=report_period,
                uploaded_by=user,
                record_count=0
            )

            # Import từng dòng
            records_to_create = []
            for idx, row in df.iterrows():
                try:
                    # Chuyển đổi giá trị số, xử lý NaN
                    tx_count = int(row['Tx_Count']) if pd.notna(row['Tx_Count']) else 0
                    tx_amount = Decimal(str(row['Tx_Amount'])) if pd.notna(row['Tx_Amount']) else Decimal('0')
                    tx_fee = Decimal(str(row['Tx_Fee'])) if pd.notna(row['Tx_Fee']) else Decimal('0')
                    vatamt = Decimal(str(row['vatamt'])) if pd.notna(row['vatamt']) else Decimal('0')

                    record = ATMTransactionReport(
                        upload=upload,
                        branch_code=str(row['Branch_Code']),
                        atm_no=str(row['ATM_No']),
                        tx_code=str(row['Tx_Code']),
                        tx_count=tx_count,
                        tx_amount=tx_amount,
                        tx_fee=tx_fee,
                        vatamt=vatamt,
                        report_period=report_period
                    )
                    records_to_create.append(record)

                except Exception as e:
                    # Log lỗi nhưng tiếp tục
                    print(f"Lỗi tại dòng {idx + 2}: {str(e)}")
                    continue

            # Bulk create để tăng performance
            if records_to_create:
                ATMTransactionReport.objects.bulk_create(records_to_create)
                upload.record_count = len(records_to_create)
                upload.save()
            else:
                return {
                    'success': False,
                    'message': 'Không có dữ liệu hợp lệ để import',
                    'upload_id': None,
                    'record_count': 0
                }

        return {
            'success': True,
            'message': f'Import thành công {len(records_to_create)} bản ghi cho tháng {month}/{year}',
            'upload_id': upload.id,
            'record_count': len(records_to_create)
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Lỗi không xác định: {str(e)}',
            'upload_id': None,
            'record_count': 0
        }


@login_required
def atm_report_dashboard(request):
    """Dashboard hiển thị báo cáo ATM với bộ lọc"""

    # Lấy tham số filter từ request
    selected_period = request.GET.get('period', '')

    # Lấy danh sách các kỳ báo cáo có sẵn
    available_periods = ATMReportUpload.objects.all().order_by('-report_period')

    # Base queryset
    queryset = ATMTransactionReport.objects.all()

    # Filter theo period nếu có
    if selected_period:
        try:
            # Parse period format: YYYY-MM-DD
            period_date = datetime.strptime(selected_period, '%Y-%m-%d').date()
            queryset = queryset.filter(report_period=period_date)
        except ValueError:
            messages.error(request, 'Định dạng thời gian không hợp lệ')

    # Group by ATM_No và tính tổng
    report_data = queryset.values('atm_no', 'branch_code', 'report_period').annotate(
        total_tx_count=Sum('tx_count'),
        total_tx_amount=Sum('tx_amount'),
        total_tx_fee=Sum('tx_fee'),
        total_vatamt=Sum('vatamt'),
        transaction_types=Count('tx_code', distinct=True)
    ).order_by('branch_code', 'atm_no')

    # Tính tổng cộng
    totals = queryset.aggregate(
        grand_total_count=Sum('tx_count'),
        grand_total_amount=Sum('tx_amount'),
        grand_total_fee=Sum('tx_fee'),
        grand_total_vat=Sum('vatamt')
    )

    context = {
        'available_periods': available_periods,
        'selected_period': selected_period,
        'report_data': report_data,
        'totals': totals,
        'record_count': report_data.count()
    }

    return render(request, 'atm_report/dashboard.html', context)


@login_required
def atm_report_import(request):
    """View xử lý upload và import file Excel"""

    if request.method == 'POST':
        form = ATMReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            # Import dữ liệu
            result = import_atm_excel(excel_file, request.user)

            if result['success']:
                messages.success(request, result['message'])
                return redirect('atm_report_dashboard')
            else:
                # Kiểm tra nếu là trường hợp đã tồn tại
                if result.get('existing'):
                    messages.warning(request, result['message'])
                    # Có thể thêm nút xác nhận xóa và import lại
                else:
                    messages.error(request, result['message'])
    else:
        form = ATMReportUploadForm()

    context = {
        'form': form,
        'upload_history': ATMReportUpload.objects.all().order_by('-upload_date')[:10]
    }

    return render(request, 'atm_report/import.html', context)


@login_required
def atm_report_delete(request, upload_id):
    """Xóa dữ liệu báo cáo đã upload"""

    if request.method == 'POST':
        try:
            upload = ATMReportUpload.objects.get(id=upload_id)
            period_str = upload.report_period.strftime('%m/%Y')

            # Xóa upload sẽ cascade xóa tất cả transactions
            upload.delete()

            messages.success(request, f'Đã xóa dữ liệu tháng {period_str}')
        except ATMReportUpload.DoesNotExist:
            messages.error(request, 'Không tìm thấy dữ liệu')

    return redirect('atm_report_dashboard')


@login_required
def atm_report_detail(request, atm_no):
    """Xem chi tiết giao dịch của một máy ATM"""

    selected_period = request.GET.get('period', '')

    queryset = ATMTransactionReport.objects.filter(atm_no=atm_no)

    if selected_period:
        try:
            period_date = datetime.strptime(selected_period, '%Y-%m-%d').date()
            queryset = queryset.filter(report_period=period_date)
        except ValueError:
            messages.error(request, 'Định dạng thời gian không hợp lệ')

    transactions = queryset.order_by('tx_code')

    # Tính tổng cho máy ATM này
    totals = queryset.aggregate(
        total_count=Sum('tx_count'),
        total_amount=Sum('tx_amount'),
        total_fee=Sum('tx_fee'),
        total_vat=Sum('vatamt')
    )

    context = {
        'atm_no': atm_no,
        'selected_period': selected_period,
        'transactions': transactions,
        'totals': totals
    }

    return render(request, 'atm_report/detail.html', context)
