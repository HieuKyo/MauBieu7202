"""
Báo cáo ATM: tồn quỹ ATM, nộp/rút ATM (import file giao dịch, xem chi tiết).
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
import re
from datetime import datetime


@login_required
def atm_fund_balance_view(request):
    """Giao diện báo cáo Tồn quỹ ATM - xử lý client-side"""
    return render(request, 'templates_app/reports/atm_fund_balance.html')


# ===== ATM TRANSACTION REPORT VIEWS =====

def parse_atm_filename_date(filename):
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
    from .models import ATMTransactionReport, ATMReportUpload
    from decimal import Decimal

    try:
        # Parse tên file để lấy tháng/năm
        filename = excel_file.name
        month, year = parse_atm_filename_date(filename)

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
        from django.db import transaction
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
def atm_transaction_report(request):
    """Dashboard hiển thị báo cáo ATM với bộ lọc nâng cao"""
    from .models import ATMTransactionReport, ATMReportUpload
    from django.db.models import Sum, Count, Q, Case, When, IntegerField, DecimalField
    from dateutil.relativedelta import relativedelta

    # Định nghĩa mã giao dịch cho từng loại
    DEPOSIT_CODES = ['0210']  # Nộp tiền
    WITHDRAWAL_CODES = ['ATM Withdrawal']  # Rút tiền
    TRANSFER_CODES = ['ATM Transfer Debit', 'ATM IBFT Debit']  # Chuyển khoản
    # GD khác: Tất cả các mã còn lại

    # Lấy tham số filter từ request
    selected_period = request.GET.get('period', '')
    selected_atm = request.GET.get('atm', '')
    selected_branch = request.GET.get('branch', '')
    period_type = request.GET.get('period_type', 'month')  # month, 6months, quarter, year
    tx_type_filter = request.GET.get('tx_type', '')  # deposit, withdrawal, transfer, other

    # Lấy danh sách các kỳ báo cáo có sẵn
    available_periods = ATMReportUpload.objects.all().order_by('-report_period')

    # Tổng hợp danh sách năm và quý từ dữ liệu có sẵn
    from django.db.models.functions import TruncYear, TruncQuarter
    available_years = (
        ATMReportUpload.objects.annotate(nam=TruncYear('report_period'))
        .values('nam').distinct().order_by('-nam')
    )
    available_quarters = (
        ATMReportUpload.objects.annotate(quy=TruncQuarter('report_period'))
        .values('quy').distinct().order_by('-quy')
    )
    available_quarters_list = []
    for row in available_quarters:
        m = row['quy'].month
        available_quarters_list.append({
            'value': row['quy'].strftime('%Y-%m-%d'),
            'label': f"Q{(m-1)//3+1}/{row['quy'].year}",
        })

    # Lấy danh sách ATM và chi nhánh để làm filter
    all_atms = ATMTransactionReport.objects.values('atm_no').distinct().order_by('atm_no')
    all_branches = ATMTransactionReport.objects.values('branch_code').distinct().order_by('branch_code')

    # Base queryset
    queryset = ATMTransactionReport.objects.all()

    # Filter theo period
    if selected_period:
        try:
            period_date = datetime.strptime(selected_period, '%Y-%m-%d').date()

            if period_type == '6months':
                start_date = period_date - relativedelta(months=5)
                queryset = queryset.filter(
                    report_period__gte=start_date,
                    report_period__lte=period_date
                )
            elif period_type == 'quarter':
                # Lấy toàn bộ quý chứa tháng được chọn
                q_month = ((period_date.month - 1) // 3) * 3 + 1
                import datetime as dt
                q_start = period_date.replace(month=q_month, day=1)
                q_end_month = q_month + 2
                q_end_year = period_date.year + (1 if q_end_month > 12 else 0)
                q_end_month = q_end_month if q_end_month <= 12 else q_end_month - 12
                import calendar
                q_end = dt.date(q_end_year, q_end_month, calendar.monthrange(q_end_year, q_end_month)[1])
                queryset = queryset.filter(
                    report_period__gte=q_start,
                    report_period__lte=q_end
                )
            elif period_type == 'year':
                # Lấy toàn bộ năm của tháng được chọn
                queryset = queryset.filter(report_period__year=period_date.year)
            else:
                # Chỉ lấy tháng được chọn
                queryset = queryset.filter(report_period=period_date)
        except ValueError:
            messages.error(request, 'Định dạng thời gian không hợp lệ')

    # Filter theo ATM
    if selected_atm:
        queryset = queryset.filter(atm_no=selected_atm)

    # Filter theo chi nhánh
    if selected_branch:
        queryset = queryset.filter(branch_code=selected_branch)

    # Filter theo loại giao dịch
    if tx_type_filter == 'deposit':
        queryset = queryset.filter(tx_code__in=DEPOSIT_CODES)
    elif tx_type_filter == 'transfer':
        queryset = queryset.filter(tx_code__in=TRANSFER_CODES)
    elif tx_type_filter == 'withdrawal':
        queryset = queryset.filter(tx_code__in=WITHDRAWAL_CODES)
    elif tx_type_filter == 'other':
        # GD khác: không phải deposit, transfer, withdrawal
        all_known_codes = DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES
        queryset = queryset.exclude(tx_code__in=all_known_codes)

    # Group by ATM_No và tính tổng riêng cho từng loại giao dịch
    report_data = queryset.values('atm_no', 'branch_code').annotate(
        # Giao dịch nộp tiền
        deposit_count=Sum(
            Case(
                When(tx_code__in=DEPOSIT_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        deposit_amount=Sum(
            Case(
                When(tx_code__in=DEPOSIT_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        # Giao dịch rút tiền
        withdrawal_count=Sum(
            Case(
                When(tx_code__in=WITHDRAWAL_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        withdrawal_amount=Sum(
            Case(
                When(tx_code__in=WITHDRAWAL_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        # Giao dịch chuyển khoản
        transfer_count=Sum(
            Case(
                When(tx_code__in=TRANSFER_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        transfer_amount=Sum(
            Case(
                When(tx_code__in=TRANSFER_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        # Giao dịch khác
        other_count=Sum(
            Case(
                When(
                    ~Q(tx_code__in=DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES),
                    then='tx_count'
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        other_amount=Sum(
            Case(
                When(
                    ~Q(tx_code__in=DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES),
                    then='tx_amount'
                ),
                default=0,
                output_field=DecimalField()
            )
        ),
        # Tổng cộng
        total_tx_count=Sum('tx_count'),
        total_tx_amount=Sum('tx_amount'),
        total_tx_fee=Sum('tx_fee'),
        total_vatamt=Sum('vatamt'),
        transaction_types=Count('tx_code', distinct=True)
    ).order_by('branch_code', 'atm_no')

    # Tính tổng cộng toàn bộ
    totals = queryset.aggregate(
        grand_deposit_count=Sum(
            Case(
                When(tx_code__in=DEPOSIT_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        grand_deposit_amount=Sum(
            Case(
                When(tx_code__in=DEPOSIT_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        grand_withdrawal_count=Sum(
            Case(
                When(tx_code__in=WITHDRAWAL_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        grand_withdrawal_amount=Sum(
            Case(
                When(tx_code__in=WITHDRAWAL_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        grand_transfer_count=Sum(
            Case(
                When(tx_code__in=TRANSFER_CODES, then='tx_count'),
                default=0,
                output_field=IntegerField()
            )
        ),
        grand_transfer_amount=Sum(
            Case(
                When(tx_code__in=TRANSFER_CODES, then='tx_amount'),
                default=0,
                output_field=DecimalField()
            )
        ),
        grand_other_count=Sum(
            Case(
                When(
                    ~Q(tx_code__in=DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES),
                    then='tx_count'
                ),
                default=0,
                output_field=IntegerField()
            )
        ),
        grand_other_amount=Sum(
            Case(
                When(
                    ~Q(tx_code__in=DEPOSIT_CODES + TRANSFER_CODES + WITHDRAWAL_CODES),
                    then='tx_amount'
                ),
                default=0,
                output_field=DecimalField()
            )
        ),
        grand_total_count=Sum('tx_count'),
        grand_total_amount=Sum('tx_amount'),
        grand_total_fee=Sum('tx_fee'),
        grand_total_vat=Sum('vatamt')
    )

    context = {
        'available_periods': available_periods,
        'available_years': available_years,
        'available_quarters': available_quarters_list,
        'all_atms': all_atms,
        'all_branches': all_branches,
        'selected_period': selected_period,
        'selected_atm': selected_atm,
        'selected_branch': selected_branch,
        'period_type': period_type,
        'tx_type_filter': tx_type_filter,
        'report_data': report_data,
        'totals': totals,
        'record_count': report_data.count()
    }

    return render(request, 'templates_app/reports/atm_transaction_report.html', context)


@login_required
def atm_transaction_import(request):
    """View xử lý upload và import file Excel"""
    from .models import ATMReportUpload
    from .forms import ATMReportUploadForm

    if request.method == 'POST':
        form = ATMReportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            # Import dữ liệu
            result = import_atm_excel(excel_file, request.user)

            if result['success']:
                messages.success(request, result['message'])
                return redirect('atm_transaction_report')
            else:
                # Kiểm tra nếu là trường hợp đã tồn tại
                if result.get('existing'):
                    messages.warning(request, result['message'])
                else:
                    messages.error(request, result['message'])
    else:
        form = ATMReportUploadForm()

    context = {
        'form': form,
        'upload_history': ATMReportUpload.objects.all().order_by('-upload_date')[:10]
    }

    return render(request, 'templates_app/reports/atm_transaction_import.html', context)


@login_required
def atm_transaction_delete(request, upload_id):
    """Xóa dữ liệu báo cáo đã upload"""
    from .models import ATMReportUpload

    if request.method == 'POST':
        try:
            upload = ATMReportUpload.objects.get(id=upload_id)
            period_str = upload.report_period.strftime('%m/%Y')

            # Xóa upload sẽ cascade xóa tất cả transactions
            upload.delete()

            messages.success(request, f'Đã xóa dữ liệu tháng {period_str}')
        except ATMReportUpload.DoesNotExist:
            messages.error(request, 'Không tìm thấy dữ liệu')

    return redirect('atm_transaction_report')


@login_required
def atm_transaction_detail(request, atm_no):
    """Xem chi tiết giao dịch của một máy ATM"""
    from .models import ATMTransactionReport
    from django.db.models import Sum

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

    return render(request, 'templates_app/reports/atm_transaction_detail.html', context)
