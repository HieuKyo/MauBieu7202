import io
from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q
from docxtpl import DocxTemplate

from .models import TaxLocation, TaxSubEntry, TaxPaymentStatement, TaxPaymentItem


def tax_payment_create(request):
    """
    View chính để tạo Bảng kê nộp thuế
    """
    if request.method == 'POST':
        return save_tax_payment(request)

    # GET request - hiển thị form
    context = {
        'tinh_list': TaxLocation.objects.values_list('tinh', flat=True).distinct().order_by('tinh'),
        'tax_sub_entries': TaxSubEntry.objects.all().order_by('ma_tieu_muc'),
    }
    return render(request, 'tax_payment/create_statement.html', context)


def save_tax_payment(request):
    """
    Xử lý lưu dữ liệu bảng kê nộp thuế
    """
    try:
        # Lấy thông tin cơ bản
        ten_nguoi_nop = request.POST.get('ten_nguoi_nop', '').strip()
        ma_so_thue = request.POST.get('ma_so_thue', '').strip()
        dia_chi = request.POST.get('dia_chi', '').strip()
        ngay_lap = request.POST.get('ngay_lap', date.today())

        # Lấy thông tin cơ quan thu
        ma_co_quan_thu = request.POST.get('ma_co_quan_thu', '').strip()

        if not ten_nguoi_nop or not ma_co_quan_thu:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin bắt buộc!')
            return redirect('tax_payment:create')

        # Lấy TaxLocation
        try:
            tax_location = TaxLocation.objects.get(ma_co_quan_thu=ma_co_quan_thu)
        except TaxLocation.DoesNotExist:
            messages.error(request, 'Không tìm thấy thông tin cơ quan thu!')
            return redirect('tax_payment:create')

        # Tạo Statement
        statement = TaxPaymentStatement.objects.create(
            ten_nguoi_nop=ten_nguoi_nop,
            ma_so_thue=ma_so_thue,
            dia_chi=dia_chi,
            tax_location=tax_location,
            ngay_lap=ngay_lap,
            tong_so_tien=0
        )

        # Lấy các dòng tiểu mục
        ma_tieu_muc_list = request.POST.getlist('ma_tieu_muc[]')
        noi_dung_list = request.POST.getlist('noi_dung[]')
        so_tien_list = request.POST.getlist('so_tien[]')

        tong_tien = Decimal('0')

        # Tạo các TaxPaymentItem
        for i, (ma_tm, noi_dung, so_tien) in enumerate(zip(ma_tieu_muc_list, noi_dung_list, so_tien_list), start=1):
            if ma_tm and so_tien:
                try:
                    so_tien_decimal = Decimal(str(so_tien).replace(',', ''))

                    # Tìm TaxSubEntry nếu có
                    tax_sub_entry = None
                    try:
                        tax_sub_entry = TaxSubEntry.objects.get(ma_tieu_muc=ma_tm)
                    except TaxSubEntry.DoesNotExist:
                        pass

                    TaxPaymentItem.objects.create(
                        statement=statement,
                        tax_sub_entry=tax_sub_entry,
                        ma_tieu_muc=ma_tm,
                        noi_dung=noi_dung,
                        so_tien=so_tien_decimal,
                        stt=i
                    )

                    tong_tien += so_tien_decimal
                except (ValueError, TypeError) as e:
                    continue

        # Cập nhật tổng tiền
        statement.tong_so_tien = tong_tien
        statement.save()

        messages.success(request, f'Đã tạo bảng kê thành công! Tổng tiền: {tong_tien:,} VNĐ')
        return redirect('tax_payment:export', statement_id=statement.id)

    except Exception as e:
        messages.error(request, f'Có lỗi xảy ra: {str(e)}')
        return redirect('tax_payment:create')


# ===== AJAX Views cho Cascading Dropdown =====

@require_http_methods(["GET"])
def get_co_quan_thue(request):
    """
    AJAX endpoint: Lấy danh sách Cơ quan thuế theo Tỉnh
    """
    tinh = request.GET.get('tinh', '').strip()

    if not tinh:
        return JsonResponse({'co_quan_thue': []})

    co_quan_thue_list = TaxLocation.objects.filter(
        tinh=tinh
    ).values_list('co_quan_thue_group', flat=True).distinct().order_by('co_quan_thue_group')

    return JsonResponse({
        'co_quan_thue': list(co_quan_thue_list)
    })


@require_http_methods(["GET"])
def get_xa_phuong(request):
    """
    AJAX endpoint: Lấy danh sách Xã/Phường theo Tỉnh và Cơ quan thuế
    """
    tinh = request.GET.get('tinh', '').strip()
    co_quan_thue = request.GET.get('co_quan_thue', '').strip()

    if not tinh or not co_quan_thue:
        return JsonResponse({'xa_phuong': []})

    xa_phuong_list = TaxLocation.objects.filter(
        tinh=tinh,
        co_quan_thue_group=co_quan_thue
    ).values_list('xa_phuong', flat=True).distinct().order_by('xa_phuong')

    return JsonResponse({
        'xa_phuong': list(xa_phuong_list)
    })


@require_http_methods(["GET"])
def get_location_details(request):
    """
    AJAX endpoint: Lấy chi tiết thông tin cơ quan thu (auto-fill)
    """
    tinh = request.GET.get('tinh', '').strip()
    co_quan_thue = request.GET.get('co_quan_thue', '').strip()
    xa_phuong = request.GET.get('xa_phuong', '').strip()

    if not tinh or not co_quan_thue or not xa_phuong:
        return JsonResponse({'error': 'Thiếu thông tin'}, status=400)

    try:
        location = TaxLocation.objects.get(
            tinh=tinh,
            co_quan_thue_group=co_quan_thue,
            xa_phuong=xa_phuong
        )

        return JsonResponse({
            'ma_co_quan_thu': str(location.ma_co_quan_thu),
            'ten_co_quan_thu': str(location.ten_co_quan_thu),
            'ma_dia_ban': str(location.ma_dia_ban).replace('.0', ''),  # Remove .0 if exists
            'kho_bac': str(location.kho_bac)
        })
    except TaxLocation.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy thông tin'}, status=404)
    except TaxLocation.MultipleObjectsReturned:
        # Trường hợp có nhiều kết quả, lấy kết quả đầu tiên
        location = TaxLocation.objects.filter(
            tinh=tinh,
            co_quan_thue_group=co_quan_thue,
            xa_phuong=xa_phuong
        ).first()

        return JsonResponse({
            'ma_co_quan_thu': str(location.ma_co_quan_thu),
            'ten_co_quan_thu': str(location.ten_co_quan_thu),
            'ma_dia_ban': str(location.ma_dia_ban).replace('.0', ''),  # Remove .0 if exists
            'kho_bac': str(location.kho_bac)
        })


@require_http_methods(["GET"])
def search_sub_entry(request):
    """
    AJAX endpoint: Tìm kiếm Tiểu mục theo mã
    """
    ma_tieu_muc = request.GET.get('ma_tieu_muc', '').strip()

    if not ma_tieu_muc:
        return JsonResponse({'error': 'Thiếu mã tiểu mục'}, status=400)

    try:
        sub_entry = TaxSubEntry.objects.get(ma_tieu_muc=ma_tieu_muc)
        return JsonResponse({
            'ma_tieu_muc': sub_entry.ma_tieu_muc,
            'ten_tieu_muc': sub_entry.ten_tieu_muc
        })
    except TaxSubEntry.DoesNotExist:
        return JsonResponse({'error': 'Không tìm thấy tiểu mục'}, status=404)


# ===== Export Word View =====

def export_tax_statement(request, statement_id):
    """
    View xuất file Word bảng kê nộp thuế
    """
    statement = get_object_or_404(TaxPaymentStatement, id=statement_id)

    # Đường dẫn đến file template Word
    # Bạn cần tạo file mẫu tax_statement_template.docx trong thư mục templates
    template_path = 'tax_payment/templates/tax_statement_template.docx'

    try:
        doc = DocxTemplate(template_path)
    except Exception as e:
        messages.error(request, f'Không tìm thấy file mẫu Word: {str(e)}')
        return redirect('tax_payment:create')

    # Chuẩn bị dữ liệu cho template
    items_data = []
    for item in statement.items.all():
        items_data.append({
            'stt': item.stt,
            'ma_tieu_muc': item.ma_tieu_muc,
            'noi_dung': item.noi_dung,
            'so_tien': f"{item.so_tien:,}".replace(',', '.'),  # Format số tiền
        })

    context = {
        # Thông tin người nộp
        'ten_nguoi_nop': statement.ten_nguoi_nop,
        'ma_so_thue': statement.ma_so_thue,
        'dia_chi': statement.dia_chi,
        'ngay_lap': statement.ngay_lap.strftime('%d/%m/%Y'),

        # Thông tin cơ quan thu
        'tinh': statement.tax_location.tinh if statement.tax_location else '',
        'co_quan_thue': statement.tax_location.co_quan_thue_group if statement.tax_location else '',
        'xa_phuong': statement.tax_location.xa_phuong if statement.tax_location else '',
        'ma_co_quan_thu': statement.tax_location.ma_co_quan_thu if statement.tax_location else '',
        'ten_co_quan_thu': statement.tax_location.ten_co_quan_thu if statement.tax_location else '',
        'ma_dia_ban': statement.tax_location.ma_dia_ban if statement.tax_location else '',
        'kho_bac': statement.tax_location.kho_bac if statement.tax_location else '',

        # Thông tin bảng kê
        'tong_so_tien': f"{statement.tong_so_tien:,}".replace(',', '.'),
        'items': items_data,
    }

    # Render template
    doc.render(context)

    # Tạo response để download
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )

    filename = f"Bang_ke_nop_thue_{statement.ten_nguoi_nop}_{statement.ngay_lap.strftime('%d%m%Y')}.docx"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


def tax_statement_list(request):
    """
    View danh sách các bảng kê đã tạo
    """
    statements = TaxPaymentStatement.objects.all().order_by('-created_at')
    return render(request, 'tax_payment/statement_list.html', {'statements': statements})
