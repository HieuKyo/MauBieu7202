"""
Views cho app Salary - Quản lý chi lương và thu hộ
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
import os
from datetime import datetime

from .models import Bank, CompanyAccount, Beneficiary, ProcessingHistory
from .forms import BeneficiaryForm, CompanyAccountForm, FileUploadForm
from .decorators import admins_only, giaodichvien_or_admin
from .services import SalaryFileProcessor, SalaryStatisticsService


@login_required
def dashboard(request):
    """Dashboard chính - Thống kê tổng quan"""
    # Kiểm tra quyền và redirect
    user_groups = request.user.groups.values_list('name', flat=True)
    is_admin = request.user.is_superuser or 'Admins' in user_groups
    is_giaodichvien = 'GiaoDichViens' in user_groups

    # GiaoDichViens redirect sang upload
    if is_giaodichvien and not is_admin:
        return redirect('salary:upload')

    # Lấy thống kê
    period = request.GET.get('period', 'month')
    stats = SalaryStatisticsService.get_statistics(period=period)

    # Lịch sử xử lý gần đây
    recent_histories = ProcessingHistory.objects.all()[:10]

    context = {
        'stats': stats,
        'period': period,
        'recent_histories': recent_histories,
        'is_admin': is_admin,
    }
    return render(request, 'salary/dashboard.html', context)


@giaodichvien_or_admin
def upload_file(request):
    """Upload và xử lý file Excel/CSV"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            transaction_type = form.cleaned_data['transaction_type']

            # Get company account from hidden field
            company_account_id = request.POST.get('company_account_id')
            company_account = None
            if company_account_id:
                try:
                    company_account = CompanyAccount.objects.get(id=int(company_account_id))
                except (ValueError, CompanyAccount.DoesNotExist):
                    pass

            # Lưu file tạm
            from django.core.files.storage import default_storage
            from django.conf import settings

            media_root = getattr(settings, 'MEDIA_ROOT', 'media')
            upload_dir = os.path.join(media_root, 'salary_uploads')
            os.makedirs(upload_dir, exist_ok=True)

            file_path = os.path.join(upload_dir, file.name)
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            # Xử lý file
            processor = SalaryFileProcessor()
            result = processor.process_excel_file(
                file_path,
                transaction_type,
                company_account
            )

            # Lưu lịch sử
            history = ProcessingHistory.objects.create(
                filename=file.name,
                transaction_type=transaction_type,
                company_account=company_account,
                total_records=result.get('total_records', 0),
                successful_records=result.get('total_records', 0) if result['success'] else 0,
                failed_records=0 if result['success'] else result.get('total_records', 0),
                total_amount=result.get('total_amount', 0),
                duplicate_accounts=','.join(map(str, result.get('duplicate_accounts', []))),
                status='SUCCESS' if result['success'] else 'ERROR',
                error_message='\n'.join(result.get('errors', [])),
                output_file=result.get('output_file', ''),
                processed_by=request.user
            )

            if result['success']:
                messages.success(request, f'Xử lý file thành công! Đã tạo file: {result["output_file"]}')

                # Hiển thị warnings nếu có
                for warning in result.get('warnings', []):
                    messages.warning(request, warning)

                return redirect('salary:processing_detail', pk=history.id)
            else:
                for error in result.get('errors', []):
                    messages.error(request, error)
    else:
        form = FileUploadForm()

    return render(request, 'salary/upload.html', {'form': form})


@admins_only
def processing_history(request):
    """Lịch sử xử lý file"""
    histories = ProcessingHistory.objects.all()

    # Filter
    transaction_type = request.GET.get('transaction_type')
    status = request.GET.get('status')
    search = request.GET.get('search')

    if transaction_type:
        histories = histories.filter(transaction_type=transaction_type)
    if status:
        histories = histories.filter(status=status)
    if search:
        histories = histories.filter(
            Q(filename__icontains=search) |
            Q(company_account__account_name__icontains=search)
        )

    # Pagination
    paginator = Paginator(histories, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'transaction_type': transaction_type,
        'status': status,
        'search': search,
    }
    return render(request, 'salary/history.html', context)


@giaodichvien_or_admin
def processing_detail(request, pk):
    """Chi tiết xử lý file"""
    history = get_object_or_404(ProcessingHistory, pk=pk)
    context = {'history': history}
    return render(request, 'salary/detail.html', context)


@giaodichvien_or_admin
def download_output_file(request, pk):
    """Download file CSV đã xử lý"""
    history = get_object_or_404(ProcessingHistory, pk=pk)

    if not history.output_file:
        messages.error(request, 'File không tồn tại')
        return redirect('salary:processing_detail', pk=pk)

    from django.conf import settings
    media_root = getattr(settings, 'MEDIA_ROOT', 'media')
    upload_dir = os.path.join(media_root, 'salary_uploads')
    file_path = os.path.join(upload_dir, history.output_file)

    if not os.path.exists(file_path):
        messages.error(request, 'File không tồn tại trên server')
        return redirect('salary:processing_detail', pk=pk)

    response = FileResponse(open(file_path, 'rb'), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{history.output_file}"'
    return response


@admins_only
def beneficiary_list(request):
    """Danh sách người thụ hưởng"""
    beneficiaries = Beneficiary.objects.all()

    # Filter
    search = request.GET.get('search')
    bank_code = request.GET.get('bank')

    if search:
        beneficiaries = beneficiaries.filter(
            Q(full_name__icontains=search) |
            Q(account_number__icontains=search)
        )
    if bank_code:
        beneficiaries = beneficiaries.filter(bank__code=bank_code)

    # Pagination
    paginator = Paginator(beneficiaries, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    banks = Bank.objects.all()

    context = {
        'page_obj': page_obj,
        'banks': banks,
        'search': search,
        'bank_code': bank_code,
    }
    return render(request, 'salary/beneficiary_list.html', context)


@admins_only
def company_account_list(request):
    """Danh sách tài khoản công ty"""
    accounts = CompanyAccount.objects.all()

    # Filter
    search = request.GET.get('search')
    is_active = request.GET.get('is_active')

    if search:
        accounts = accounts.filter(
            Q(account_number__icontains=search) |
            Q(account_name__icontains=search)
        )
    if is_active:
        accounts = accounts.filter(is_active=(is_active == '1'))

    context = {
        'accounts': accounts,
        'search': search,
        'is_active': is_active,
    }
    return render(request, 'salary/company_account_list.html', context)


@login_required
def company_account_search(request):
    """API search company accounts for autocomplete"""
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'results': []})

    accounts = CompanyAccount.objects.filter(
        Q(account_number__icontains=query) |
        Q(account_name__icontains=query),
        is_active=True
    )[:10]

    results = [{
        'id': account.id,
        'account_number': account.account_number,
        'account_name': account.account_name,
        'bank': str(account.bank)
    } for account in accounts]

    return JsonResponse({'results': results})


@login_required
def access_denied(request):
    """Trang báo lỗi không có quyền"""
    return render(request, 'salary/access_denied.html', status=403)
