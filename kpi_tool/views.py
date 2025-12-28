"""
Views cho module quy đổi bút toán
"""
import os
import tempfile
from datetime import datetime
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count
from django.core.files.storage import default_storage
from django.views.decorators.http import require_http_methods

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

from .models import ConversionRule, TellerTransactionBatch, TellerTransactionDetail
from .services import DBFProcessor, RuleImporter


def index(request):
    """
    Trang chủ - Danh sách các lô đã xử lý
    """
    batches = TellerTransactionBatch.objects.all().order_by('-created_at')[:20]

    # Thống kê tổng quan
    stats = {
        'total_batches': TellerTransactionBatch.objects.filter(processing_status='completed').count(),
        'total_transactions': TellerTransactionDetail.objects.count(),
        'total_score': TellerTransactionDetail.objects.aggregate(Sum('score'))['score__sum'] or 0,
        'total_rules': ConversionRule.objects.filter(is_active=True).count(),
    }

    context = {
        'batches': batches,
        'stats': stats,
    }
    return render(request, 'kpi_tool/index.html', context)


def upload_view(request):
    """
    Trang upload file DBF
    """
    if request.method == 'POST':
        files = request.FILES.getlist('dbf_files')
        teller_name = request.POST.get('teller_name', '').strip()

        if not files:
            messages.error(request, 'Vui lòng chọn ít nhất một file để upload.')
            return redirect('kpi_tool:upload')

        # Lưu file tạm và xử lý
        processor = DBFProcessor()
        batches = []
        errors = []

        for uploaded_file in files:
            # Kiểm tra extension
            if not uploaded_file.name.upper().endswith('.DBF'):
                errors.append(f"{uploaded_file.name}: Không phải file DBF")
                continue

            # Lưu file tạm
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.dbf') as tmp_file:
                    for chunk in uploaded_file.chunks():
                        tmp_file.write(chunk)
                    tmp_file_path = tmp_file.name

                # Xử lý file
                batch = processor.process_dbf_file(tmp_file_path, teller_name)
                batches.append(batch)

                # Xóa file tạm
                os.unlink(tmp_file_path)

            except Exception as e:
                errors.append(f"{uploaded_file.name}: {str(e)}")
                continue

        # Hiển thị kết quả
        if batches:
            messages.success(request, f'Đã xử lý thành công {len(batches)} file.')
        if errors:
            for error in errors:
                messages.error(request, error)

        # Redirect đến trang kết quả nếu chỉ có 1 batch
        if len(batches) == 1:
            return redirect('kpi_tool:batch_detail', batch_id=batches[0].id)
        elif batches:
            return redirect('kpi_tool:index')

    return render(request, 'kpi_tool/upload.html')


def batch_detail(request, batch_id):
    """
    Trang chi tiết lô giao dịch
    """
    batch = get_object_or_404(TellerTransactionBatch, id=batch_id)

    # Lấy chi tiết giao dịch
    transactions = batch.transactions.all().select_related('matched_rule')

    # Thống kê theo ngày
    daily_stats = batch.transactions.values('transaction_date').annotate(
        count=Count('id'),
        total_score=Sum('score')
    ).order_by('transaction_date')

    context = {
        'batch': batch,
        'transactions': transactions,
        'daily_stats': daily_stats,
    }
    return render(request, 'kpi_tool/batch_detail.html', context)


def batch_list(request):
    """
    Danh sách tất cả các lô
    """
    # Lọc theo teller, month, year
    teller_id = request.GET.get('teller_id')
    month = request.GET.get('month')
    year = request.GET.get('year')

    batches = TellerTransactionBatch.objects.all()

    if teller_id:
        batches = batches.filter(teller_id__icontains=teller_id)
    if month:
        batches = batches.filter(month=month)
    if year:
        batches = batches.filter(year=year)

    batches = batches.order_by('-created_at')

    # Danh sách teller để lọc
    tellers = TellerTransactionBatch.objects.values('teller_id', 'teller_name').distinct()

    context = {
        'batches': batches,
        'tellers': tellers,
    }
    return render(request, 'kpi_tool/batch_list.html', context)


def export_excel(request, batch_id):
    """
    Xuất báo cáo Excel cho một lô
    """
    batch = get_object_or_404(TellerTransactionBatch, id=batch_id)
    transactions = batch.transactions.all().select_related('matched_rule')

    # Tạo workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Báo cáo KPI"

    # Header style
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")

    # Border style
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # Tiêu đề báo cáo
    ws.merge_cells('A1:H1')
    title_cell = ws['A1']
    title_cell.value = f"BÁO CÁO QUY ĐỔI BÚT TOÁN - {batch.teller_name}"
    title_cell.font = Font(bold=True, size=14)
    title_cell.alignment = header_alignment

    # Thông tin tổng quan
    ws.merge_cells('A2:B2')
    ws['A2'] = "Tháng/Năm:"
    ws['C2'] = f"{batch.month}/{batch.year}"

    ws.merge_cells('A3:B3')
    ws['A3'] = "Tổng số giao dịch:"
    ws['C3'] = batch.total_transactions

    ws.merge_cells('A4:B4')
    ws['A4'] = "Tổng điểm quy đổi:"
    ws['C4'] = float(batch.total_score)

    ws.merge_cells('A5:B5')
    ws['A5'] = "Số GD khớp:"
    ws['C5'] = batch.matched_transactions

    ws.merge_cells('A6:B6')
    ws['A6'] = "Số GD không khớp:"
    ws['C6'] = batch.unmatched_transactions

    # Bỏ qua 1 dòng
    current_row = 8

    # Header bảng chi tiết
    headers = ['STT', 'Ngày GD', 'Số tham chiếu', 'TK Nợ', 'TK Có', 'Số tiền', 'Nghiệp vụ', 'Điểm']
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(row=current_row, column=col)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border

    # Dữ liệu chi tiết
    current_row += 1
    for idx, trans in enumerate(transactions, start=1):
        ws.cell(row=current_row, column=1, value=idx).border = thin_border
        ws.cell(row=current_row, column=2, value=trans.transaction_date.strftime('%d/%m/%Y')).border = thin_border
        ws.cell(row=current_row, column=3, value=trans.reference_no).border = thin_border
        ws.cell(row=current_row, column=4, value=trans.debit_account).border = thin_border
        ws.cell(row=current_row, column=5, value=trans.credit_account).border = thin_border
        ws.cell(row=current_row, column=6, value=float(trans.amount)).border = thin_border
        ws.cell(row=current_row, column=7, value=trans.matched_rule.description if trans.matched_rule else 'Không khớp').border = thin_border
        ws.cell(row=current_row, column=8, value=float(trans.score)).border = thin_border
        current_row += 1

    # Điều chỉnh độ rộng cột
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 15
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 12
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 30
    ws.column_dimensions['H'].width = 12

    # Tạo response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f"BaoCaoKPI_{batch.teller_id}_{batch.file_date.strftime('%d%m%Y')}.xlsx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response


def import_rules_view(request):
    """
    Trang import quy tắc từ file hesoquydoi.BAK
    """
    if request.method == 'POST':
        file = request.FILES.get('rule_file')

        if not file:
            messages.error(request, 'Vui lòng chọn file để import.')
            return redirect('kpi_tool:import_rules')

        # Kiểm tra extension
        if not (file.name.upper().endswith('.BAK') or file.name.upper().endswith('.DBF')):
            messages.error(request, 'File phải có định dạng .BAK hoặc .DBF')
            return redirect('kpi_tool:import_rules')

        # Lưu file tạm và xử lý
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.dbf') as tmp_file:
                for chunk in file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            # Import rules
            importer = RuleImporter()
            count = importer.import_from_dbf(tmp_file_path)

            # Xóa file tạm
            os.unlink(tmp_file_path)

            messages.success(request, f'Đã import thành công {count} quy tắc.')
            return redirect('kpi_tool:rule_list')

        except Exception as e:
            messages.error(request, f'Lỗi khi import: {str(e)}')
            return redirect('kpi_tool:import_rules')

    # Thống kê quy tắc hiện có
    rules_count = ConversionRule.objects.count()
    active_rules_count = ConversionRule.objects.filter(is_active=True).count()

    context = {
        'rules_count': rules_count,
        'active_rules_count': active_rules_count,
    }
    return render(request, 'kpi_tool/import_rules.html', context)


def rule_list(request):
    """
    Danh sách quy tắc
    """
    rules = ConversionRule.objects.all().order_by('code')

    context = {
        'rules': rules,
    }
    return render(request, 'kpi_tool/rule_list.html', context)
