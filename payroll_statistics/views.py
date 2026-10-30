"""
Views cho app Payroll Statistics
"""
import pandas as pd
from datetime import datetime
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from .models import PayingUnit, BeneficiaryAccount, Transaction
from .forms import PayrollUploadForm


def is_unit_account(account_number):
    """
    Kiểm tra xem tài khoản có phải là tài khoản đơn vị không

    Args:
        account_number: Số tài khoản

    Returns:
        bool: True nếu là tài khoản đơn vị
    """
    acc_str = str(account_number).strip()
    # CHI LƯƠNG CHỈ CÓ 2 LOẠI TK:
    # - 7202201xxx: Tài khoản đơn vị chính
    # - 7202000xxx: Tài khoản đơn vị phụ
    return acc_str.startswith('7202201') or acc_str.startswith('7202000')


def is_employee_account(account_number):
    """
    Kiểm tra xem tài khoản có phải là tài khoản nhân viên không

    Args:
        account_number: Số tài khoản

    Returns:
        bool: True nếu là tài khoản nhân viên
    """
    acc_str = str(account_number).strip()
    # Tài khoản nhân viên thường bắt đầu với 7202215 hoặc 7202205
    return acc_str.startswith('7202215') or acc_str.startswith('7202205')


def determine_transaction_type(facno, tacno, remark, rsltremark):
    """
    Xác định loại giao dịch và mapping đúng đơn vị - nhân viên

    Logic mới (FIXED):
    1. Kiểm tra pattern tài khoản TRƯỚC để xác định đâu là unit, đâu là employee
    2. Chỉ chấp nhận giao dịch nếu có ít nhất 1 tài khoản là unit (7202201xxx hoặc 7202000xxx)
    3. Sau đó dùng dấu âm, từ khóa, hoặc direction để xác định loại giao dịch

    Args:
        facno: Số tài khoản người chuyển
        tacno: Số tài khoản người nhận
        remark: Nội dung giao dịch
        rsltremark: Số tiền kết quả

    Returns:
        tuple: (is_collection, unit_account, employee_account) hoặc None nếu không hợp lệ
    """
    remark_str = str(remark).strip().upper()
    rsltremark_str = str(rsltremark).strip()

    # BƯỚC 1: Kiểm tra pattern tài khoản TRƯỚC
    facno_is_unit = is_unit_account(facno)
    tacno_is_unit = is_unit_account(tacno)
    facno_is_employee = is_employee_account(facno)
    tacno_is_employee = is_employee_account(tacno)

    # Xác định unit_account và employee_account dựa trên pattern
    unit_account = None
    employee_account = None

    # Case 1: facno là đơn vị, tacno là nhân viên
    if facno_is_unit and tacno_is_employee:
        unit_account = facno
        employee_account = tacno
    # Case 2: tacno là đơn vị, facno là nhân viên
    elif tacno_is_unit and facno_is_employee:
        unit_account = tacno
        employee_account = facno
    # Case 3: Chỉ facno là đơn vị (tacno không rõ pattern)
    elif facno_is_unit and not tacno_is_unit:
        unit_account = facno
        employee_account = tacno
    # Case 4: Chỉ tacno là đơn vị (facno không rõ pattern)
    elif tacno_is_unit and not facno_is_unit:
        unit_account = tacno
        employee_account = facno
    # Case 5: Không có tài khoản nào là đơn vị hợp lệ → SKIP
    else:
        return None

    # BƯỚC 2: Xác định loại giao dịch (payroll hay collection)

    # 2.1: Check dấu âm ở rsltremark (ưu tiên cao nhất)
    if rsltremark_str.startswith('-'):
        return True, unit_account, employee_account  # Thu hộ

    # 2.2: Check từ khóa thu hộ
    thu_ho_keywords = [
        'THU NO', 'THU HO',
        'KHOAN THU', 'KHOAN TRU',
        'TRU LUONG', 'TRU 1 NGAY', 'TRU NGAY',  # Trừ lương
        'GIAM TRU', 'GIAM LUONG',  # Giảm trừ
    ]
    for keyword in thu_ho_keywords:
        if keyword in remark_str:
            return True, unit_account, employee_account  # Thu hộ

    # 2.3: Check direction dựa trên pattern
    # Nếu facno là đơn vị → Chi lương (đơn vị chuyển tiền cho nhân viên)
    # Nếu tacno là đơn vị → Thu hộ (nhân viên chuyển tiền cho đơn vị)
    if facno_is_unit:
        return False, unit_account, employee_account  # Chi lương
    else:
        return True, unit_account, employee_account  # Thu hộ


def parse_amount(rsltremark):
    """Parse số tiền từ rsltremark"""
    try:
        rsltremark_str = str(rsltremark).strip()
        # Remove commas and convert to Decimal
        amount_str = rsltremark_str.replace(',', '').replace('-', '')
        if amount_str and amount_str != 'nan':
            return abs(Decimal(amount_str))
    except Exception:
        pass
    return Decimal('0')


def parse_date(date_value):
    """Parse ngày từ nhiều định dạng"""
    if pd.isna(date_value):
        return None

    if isinstance(date_value, datetime):
        return date_value.date()

    if isinstance(date_value, str):
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_value, fmt).date()
            except Exception:
                continue
    return None


def process_import_file(file_obj):
    """
    Xử lý file import và lưu vào database

    Args:
        file_obj: File object từ upload

    Returns:
        dict: Kết quả import {success: bool, message: str, stats: dict}
    """
    try:
        # Đọc file
        file_name = file_obj.name.lower()

        if file_name.endswith('.csv'):
            df = pd.read_csv(file_obj)
        elif file_name.endswith('.xls'):
            df = pd.read_excel(file_obj, engine='xlrd')
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(file_obj, engine='openpyxl')
        else:
            return {
                'success': False,
                'message': 'File không đúng định dạng',
                'stats': {}
            }

        # Kiểm tra các cột bắt buộc
        required_columns = ['facno', 'tacno', 'remark']
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            return {
                'success': False,
                'message': f'File thiếu các cột: {", ".join(missing_cols)}',
                'stats': {}
            }

        # Thống kê
        total_rows = 0
        chi_luong_count = 0
        thu_ho_count = 0
        units_created = 0
        beneficiaries_created = 0
        transactions_created = 0
        errors = []

        # Duyệt qua từng dòng
        for idx, row in df.iterrows():
            try:
                facno = str(row.get('facno', '')).strip()
                tacno = str(row.get('tacno', '')).strip()
                remark = str(row.get('remark', '')).strip()
                rsltremark = str(row.get('rsltremark', '')).strip() if 'rsltremark' in df.columns else ''

                # Parse ngày giao dịch (nếu có)
                transaction_date = None
                if 'transaction_date' in df.columns:
                    transaction_date = parse_date(row.get('transaction_date'))
                elif 'trdt' in df.columns:
                    transaction_date = parse_date(row.get('trdt'))

                # Parse số tiền
                amount = parse_amount(rsltremark)

                # Bỏ qua dòng trống
                if not facno or not tacno or facno == 'nan' or tacno == 'nan':
                    continue

                total_rows += 1

                # Bước 1: Xác định loại giao dịch và mapping đúng
                # Sử dụng logic mới với ưu tiên: pattern → rsltremark âm → remark từ khóa → direction
                result = determine_transaction_type(facno, tacno, remark, rsltremark)

                # Nếu không xác định được (không có unit account hợp lệ) → SKIP
                if result is None:
                    continue

                is_collection, unit_account, beneficiary_account = result

                # Bước 2: Set transaction type và đếm
                if is_collection:
                    transaction_type = 'collection'
                    thu_ho_count += 1
                else:
                    transaction_type = 'payroll'
                    chi_luong_count += 1

                # Bước 3: Lưu vào database
                # Lưu/Lấy PayingUnit
                unit, unit_created = PayingUnit.objects.get_or_create(
                    account_number=unit_account
                )
                if unit_created:
                    units_created += 1

                # Lưu/Lấy BeneficiaryAccount
                beneficiary, ben_created = BeneficiaryAccount.objects.get_or_create(
                    unit=unit,
                    account_number=beneficiary_account,
                    defaults={'remark_ref': remark}
                )
                if ben_created:
                    beneficiaries_created += 1
                elif remark and not beneficiary.remark_ref:
                    # Update remark nếu chưa có
                    beneficiary.remark_ref = remark
                    beneficiary.save()

                # Bước 4: Lưu Transaction
                Transaction.objects.create(
                    unit=unit,
                    beneficiary=beneficiary,
                    transaction_type=transaction_type,
                    amount=amount,
                    transaction_date=transaction_date,
                    remark=remark,
                    facno=facno,
                    tacno=tacno,
                    rsltremark=rsltremark
                )
                transactions_created += 1

            except Exception as e:
                errors.append(f"Dòng {idx + 2}: {str(e)}")
                continue

        # Tạo message kết quả
        if total_rows == 0:
            return {
                'success': False,
                'message': 'File không có dữ liệu hợp lệ',
                'stats': {}
            }

        stats = {
            'total_rows': total_rows,
            'chi_luong': chi_luong_count,
            'thu_ho': thu_ho_count,
            'units_created': units_created,
            'beneficiaries_created': beneficiaries_created,
            'transactions_created': transactions_created,
            'errors': errors
        }

        message = f"""Import thành công {total_rows} giao dịch:
        - Chi lương: {chi_luong_count}
        - Thu hộ: {thu_ho_count}
        - Đơn vị mới: {units_created}
        - Nhân viên mới: {beneficiaries_created}
        - Giao dịch đã lưu: {transactions_created}"""

        if errors:
            message += f"\n- Có {len(errors)} lỗi"

        return {
            'success': True,
            'message': message,
            'stats': stats
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Lỗi khi xử lý file: {str(e)}',
            'stats': {}
        }


def upload_view(request):
    """View upload file"""
    if request.method == 'POST':
        form = PayrollUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = request.FILES['file']
            result = process_import_file(file_obj)

            if result['success']:
                messages.success(request, result['message'])
                return redirect('payroll_statistics:statistics')
            else:
                messages.error(request, result['message'])
    else:
        form = PayrollUploadForm()

    return render(request, 'payroll_statistics/upload.html', {
        'form': form,
        'title': 'Upload File Lương/Thu Hộ'
    })


def statistics_view(request):
    """View hiển thị thống kê với filters"""
    # Lấy filters từ request
    unit_filter = request.GET.get('unit', '')
    month_filter = request.GET.get('month', '')
    year_filter = request.GET.get('year', '')
    transaction_type_filter = request.GET.get('type', '')

    # Base queryset
    transactions = Transaction.objects.select_related('unit', 'beneficiary').all()

    # Apply filters
    if unit_filter:
        transactions = transactions.filter(unit__account_number=unit_filter)

    if month_filter and year_filter:
        transactions = transactions.filter(
            transaction_date__month=month_filter,
            transaction_date__year=year_filter
        )
    elif year_filter:
        transactions = transactions.filter(transaction_date__year=year_filter)

    if transaction_type_filter:
        transactions = transactions.filter(transaction_type=transaction_type_filter)

    # Tính tổng tiền
    total_payroll = transactions.filter(transaction_type='payroll').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    total_collection = transactions.filter(transaction_type='collection').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    # Thống kê theo đơn vị
    units_stats = PayingUnit.objects.annotate(
        beneficiary_count=Count('beneficiaries', distinct=True),
        transaction_count=Count('transactions'),
        total_amount=Sum('transactions__amount')
    ).order_by('-beneficiary_count')

    # Thống kê chi tiết theo đơn vị với phân loại payroll/collection
    units_with_stats = PayingUnit.objects.annotate(
        beneficiary_count=Count('beneficiaries', distinct=True),
        payroll_count=Count('transactions', filter=Q(transactions__transaction_type='payroll')),
        payroll_amount=Sum('transactions__amount', filter=Q(transactions__transaction_type='payroll')),
        collection_count=Count('transactions', filter=Q(transactions__transaction_type='collection')),
        collection_amount=Sum('transactions__amount', filter=Q(transactions__transaction_type='collection'))
    ).order_by('-beneficiary_count')

    # Kiểm tra nhân viên trùng lặp (1 nhân viên thuộc nhiều đơn vị)
    duplicate_employees = BeneficiaryAccount.objects.values('account_number').annotate(
        unit_count=Count('unit', distinct=True)
    ).filter(unit_count__gt=1).order_by('-unit_count')

    # Lấy danh sách đơn vị cho mỗi nhân viên trùng lặp
    duplicate_employees_list = []
    for dup in duplicate_employees:
        units_list = BeneficiaryAccount.objects.filter(
            account_number=dup['account_number']
        ).values_list('unit__account_number', flat=True)
        duplicate_employees_list.append({
            'account_number': dup['account_number'],
            'unit_count': dup['unit_count'],
            'units': list(units_list)
        })

    # Thống kê tổng quan
    total_units = PayingUnit.objects.count()
    total_beneficiaries = BeneficiaryAccount.objects.count()
    total_transactions = Transaction.objects.count()

    # Lấy danh sách năm và tháng có dữ liệu
    years = Transaction.objects.dates('transaction_date', 'year', order='DESC')
    months = range(1, 13)

    context = {
        'title': 'Thống Kê Lương/Thu Hộ',
        'total_units': total_units,
        'total_beneficiaries': total_beneficiaries,
        'total_transactions': total_transactions,
        'total_payroll': total_payroll,
        'total_collection': total_collection,
        'transactions': transactions,
        'units_stats': units_stats,
        'units_with_stats': units_with_stats,
        'duplicate_employees': duplicate_employees_list,
        'years': years,
        'months': months,
        # Filters
        'unit_filter': unit_filter,
        'month_filter': month_filter,
        'year_filter': year_filter,
        'transaction_type_filter': transaction_type_filter,
    }

    return render(request, 'payroll_statistics/statistics.html', context)


def statistics_data_api(request):
    """API trả về dữ liệu cho DataTables (Ajax)"""
    # Lấy filters
    unit_filter = request.GET.get('unit', '')
    month_filter = request.GET.get('month', '')
    year_filter = request.GET.get('year', '')
    transaction_type_filter = request.GET.get('type', '')

    # Base queryset
    transactions = Transaction.objects.select_related('unit', 'beneficiary').all()

    # Apply filters
    if unit_filter:
        transactions = transactions.filter(unit__account_number=unit_filter)

    if month_filter and year_filter:
        transactions = transactions.filter(
            transaction_date__month=month_filter,
            transaction_date__year=year_filter
        )
    elif year_filter:
        transactions = transactions.filter(transaction_date__year=year_filter)

    if transaction_type_filter:
        transactions = transactions.filter(transaction_type=transaction_type_filter)

    data = []
    for trans in transactions:
        data.append({
            'transaction_date': trans.transaction_date.strftime('%d/%m/%Y') if trans.transaction_date else '',
            'transaction_type': trans.get_transaction_type_display(),
            'unit_account': trans.unit.account_number,
            'unit_name': trans.unit.name if trans.unit.name else '',
            'beneficiary_account': trans.beneficiary.account_number,
            'amount': str(trans.amount),
            'remark': trans.remark,
        })

    return JsonResponse({
        'data': data
    })
