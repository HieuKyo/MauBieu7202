import io
from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q
from docxtpl import DocxTemplate
from .utils import doc_so_thanh_chu
from .models import TaxLocation, TaxSubEntry, TaxPaymentStatement, TaxPaymentItem
from .utils import number_to_vietnamese_words, format_currency_vnd, date_to_vietnamese_text


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
        'today': date.today(),
    }
    return render(request, 'tax_payment/create_statement.html', context)


def save_tax_payment(request, statement_id=None):
    """
    Hàm dùng chung cho cả Tạo mới và Cập nhật
    """
    try:
        # Lấy dữ liệu từ POST
        ten_nguoi_nop = request.POST.get('ten_nguoi_nop', '').strip()
        ma_so_thue = request.POST.get('ma_so_thue', '').strip()
        dia_chi = request.POST.get('dia_chi', '').strip()
        nguoi_nop_thay = request.POST.get('nguoi_nop_thay', '').strip()
        dia_chi_nguoi_nop_thay = request.POST.get('dia_chi_nguoi_nop_thay', '').strip()
        ngay_lap = request.POST.get('ngay_lap', date.today())
        ma_co_quan_thu = request.POST.get('ma_co_quan_thu', '').strip()

        if not ten_nguoi_nop or not ma_co_quan_thu:
            messages.error(request, 'Thiếu thông tin bắt buộc!')
            return redirect('tax_payment:create')

        # Lấy TaxLocation
        try:
            tax_location = TaxLocation.objects.get(ma_co_quan_thu=ma_co_quan_thu)
        except TaxLocation.DoesNotExist:
            messages.error(request, 'Không tìm thấy cơ quan thu!')
            return redirect('tax_payment:create')

        # === XỬ LÝ TẠO MỚI HOẶC UPDATE ===
        if statement_id:
            # Update
            statement = get_object_or_404(TaxPaymentStatement, pk=statement_id)
            statement.ten_nguoi_nop = ten_nguoi_nop
            statement.ma_so_thue = ma_so_thue
            statement.dia_chi = dia_chi
            statement.nguoi_nop_thay = nguoi_nop_thay
            statement.dia_chi_nguoi_nop_thay = dia_chi_nguoi_nop_thay
            statement.ngay_lap = ngay_lap
            statement.tax_location = tax_location
            statement.save()

            # Xóa hết item cũ để lưu lại từ đầu (đơn giản hóa logic update list)
            statement.items.all().delete()
            msg = 'Cập nhật bảng kê thành công!'
        else:
            # Create
            statement = TaxPaymentStatement.objects.create(
                ten_nguoi_nop=ten_nguoi_nop,
                ma_so_thue=ma_so_thue,
                dia_chi=dia_chi,
                nguoi_nop_thay=nguoi_nop_thay,
                dia_chi_nguoi_nop_thay=dia_chi_nguoi_nop_thay,
                tax_location=tax_location,
                ngay_lap=ngay_lap,
                tong_so_tien=0
            )
            msg = 'Tạo bảng kê thành công!'

        # === LƯU DANH SÁCH TIỂU MỤC ===
        ma_tieu_muc_list = request.POST.getlist('ma_tieu_muc[]')
        noi_dung_list = request.POST.getlist('noi_dung[]')
        so_tien_list = request.POST.getlist('so_tien[]')

        tong_tien = Decimal('0')

        for i, (ma_tm, noi_dung, so_tien) in enumerate(zip(ma_tieu_muc_list, noi_dung_list, so_tien_list), start=1):
            if ma_tm and so_tien:
                try:
                    so_tien_clean = so_tien.replace(',', '').replace('.', '') # Fix lỗi format
                    so_tien_decimal = Decimal(so_tien_clean)
                    
                    # Tìm TaxSubEntry (Optional)
                    tax_sub_entry = TaxSubEntry.objects.filter(ma_tieu_muc=ma_tm).first()

                    TaxPaymentItem.objects.create(
                        statement=statement,
                        tax_sub_entry=tax_sub_entry,
                        ma_tieu_muc=ma_tm,
                        noi_dung=noi_dung,
                        so_tien=so_tien_decimal,
                        stt=i
                    )
                    tong_tien += so_tien_decimal
                except (ValueError, TypeError):
                    continue

        statement.tong_so_tien = tong_tien
        statement.save()

        messages.success(request, f'{msg} Tổng tiền: {tong_tien:,.0f} VNĐ')
        # Quay về trang danh sách sau khi lưu xong
        return redirect('tax_payment:list')

    except Exception as e:
        messages.error(request, f'Lỗi hệ thống: {str(e)}')
        return redirect('tax_payment:create')


# --- THÊM VIEW EDIT ---
def tax_payment_edit(request, pk):
    statement = get_object_or_404(TaxPaymentStatement, pk=pk)
    
    if request.method == 'POST':
        return save_tax_payment(request, statement_id=pk)

    # Chuẩn bị dữ liệu để đổ vào form
    # 1. List Tỉnh (luôn có)
    tinh_list = TaxLocation.objects.values_list('tinh', flat=True).distinct().order_by('tinh')
    
    # 2. List Cơ quan thuế (của tỉnh đã chọn)
    co_quan_thue_list = []
    if statement.tax_location:
        co_quan_thue_list = TaxLocation.objects.filter(tinh=statement.tax_location.tinh)\
            .values_list('co_quan_thue_group', flat=True).distinct().order_by('co_quan_thue_group')

    # 3. List Xã phường (của cơ quan thuế đã chọn)
    xa_phuong_list = []
    if statement.tax_location:
        xa_phuong_list = TaxLocation.objects.filter(
            tinh=statement.tax_location.tinh, 
            co_quan_thue_group=statement.tax_location.co_quan_thue_group
        ).exclude(xa_phuong__isnull=True).values_list('xa_phuong', flat=True).distinct().order_by('xa_phuong')

    context = {
        'statement': statement,
        'tinh_list': tinh_list,
        'co_quan_thue_list': co_quan_thue_list, # Để pre-fill dropdown 2
        'xa_phuong_list': xa_phuong_list,       # Để pre-fill dropdown 3
        'items': statement.items.all().order_by('stt'),
        'is_edit': True, # Cờ đánh dấu đang edit
        'today': date.today(),
        'tax_sub_entries': TaxSubEntry.objects.all().order_by('ma_tieu_muc'),
    }
    return render(request, 'tax_payment/create_statement.html', context)


# --- THÊM VIEW DELETE ---
def tax_payment_delete(request, pk):
    statement = get_object_or_404(TaxPaymentStatement, pk=pk)
    if request.method == 'POST':
        statement.delete()
        messages.success(request, 'Đã xóa bảng kê thành công.')
    return redirect('tax_payment:list')


# ===== AJAX Views cho Cascading Dropdown =====

@require_http_methods(["GET"])
def get_co_quan_thue(request):
    """
    HTMX: Trả về HTML danh sách options cơ quan thuế
    """
    tinh = request.GET.get('tinh', '').strip()
    
    if not tinh:
        options = []
    else:
        options = TaxLocation.objects.filter(tinh=tinh)\
            .order_by('co_quan_thue_group')\
            .values_list('co_quan_thue_group', flat=True)\
            .distinct()
            
    # Trả về template con chứa các thẻ <option>
    return render(request, 'tax_payment/dropdown_options.html', {'options': options})


@require_http_methods(["GET"])
def get_xa_phuong(request):
    """
    HTMX: Trả về HTML danh sách options xã phường
    """
    tinh = request.GET.get('tinh', '').strip()
    co_quan_thue = request.GET.get('co_quan_thue', '').strip()
    
    if not tinh or not co_quan_thue:
        return JsonResponse({'xa_phuong': []})

    # Use order_by before distinct to ensure proper deduplication
    xa_phuong_list = TaxLocation.objects.filter(
        tinh=tinh,
        co_quan_thue_group=co_quan_thue
    ).order_by('xa_phuong').values_list('xa_phuong', flat=True).distinct()

    return render(request, 'tax_payment/dropdown_options.html', {'options': xa_phuong_list})


@require_http_methods(["GET"])
def get_location_details(request):
    """
    Lấy thông tin chi tiết (Mã CQT, Mã ĐB, KBNN) để điền tự động
    """
    tinh = request.GET.get('tinh', '').strip()
    co_quan_thue = request.GET.get('co_quan_thue', '').strip()
    xa_phuong = request.GET.get('xa_phuong', '').strip()

    if not tinh or not co_quan_thue or not xa_phuong:
        return JsonResponse({'error': 'Thiếu thông tin'}, status=400)

    # Tìm chính xác địa điểm
    location = TaxLocation.objects.filter(
        tinh=tinh,
        co_quan_thue_group=co_quan_thue,
        xa_phuong=xa_phuong
    ).first()

    if location:
        # Xử lý cắt đuôi .0 cho mã địa bàn nếu có
        ma_dia_ban = str(location.ma_dia_ban).replace('.0', '') if location.ma_dia_ban else ''
        
        return JsonResponse({
            'ma_co_quan_thu': location.ma_co_quan_thu,
            'ten_co_quan_thu': location.ten_co_quan_thu,
            'ma_dia_ban': ma_dia_ban,
            'kho_bac': location.kho_bac
        })
    else:
        return JsonResponse({'error': 'Không tìm thấy dữ liệu'}, status=404)


@require_http_methods(["GET"])
def search_sub_entry(request):
    """Tìm tiểu mục theo mã chính xác"""
    ma_tieu_muc = request.GET.get('ma_tieu_muc', '').strip()
    if not ma_tieu_muc:
        return JsonResponse({'error': 'Rỗng'}, status=400)
    sub_entry = TaxSubEntry.objects.filter(ma_tieu_muc=ma_tieu_muc).first()

    if sub_entry:
        return JsonResponse({
            'ma_tieu_muc': sub_entry.ma_tieu_muc,
            'ten_tieu_muc': sub_entry.ten_tieu_muc
        })
    return JsonResponse({'error': 'Không tìm thấy'}, status=404)


@require_http_methods(["GET"])
def search_sub_entries(request):
    """
    API tìm kiếm tiểu mục theo keyword (mã hoặc nội dung)
    Dùng cho modal search
    """
    keyword = request.GET.get('q', '').strip()

    if not keyword:
        return JsonResponse({'results': []})

    # Tìm kiếm theo cả mã và tên tiểu mục
    results = TaxSubEntry.objects.filter(
        Q(ma_tieu_muc__icontains=keyword) |
        Q(ten_tieu_muc__icontains=keyword)
    ).order_by('ma_tieu_muc')[:20]  # Giới hạn 20 kết quả

    data = {
        'results': [
            {
                'ma_tieu_muc': item.ma_tieu_muc,
                'ten_tieu_muc': item.ten_tieu_muc
            }
            for item in results
        ]
    }

    return JsonResponse(data)


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

    # Chuyển số tiền sang chữ
    so_tien_bang_chu = number_to_vietnamese_words(statement.tong_so_tien)

    # Xử lý Mã địa bàn: Xóa đuôi .0 nếu có
    ma_dia_ban = ''
    if statement.tax_location and statement.tax_location.ma_dia_ban:
        ma_dia_ban = str(statement.tax_location.ma_dia_ban).replace('.0', '')
    so_tien_bang_chu = doc_so_thanh_chu(statement.tong_so_tien)
    
    context = {
        # Thông tin người nộp
        'ten_nguoi_nop': statement.ten_nguoi_nop,
        'ma_so_thue': statement.ma_so_thue,
        'dia_chi': statement.dia_chi,
        'nguoi_nop_thay': statement.nguoi_nop_thay,
        'dia_chi_nguoi_nop_thay': statement.dia_chi_nguoi_nop_thay,
        'ngay_lap': statement.ngay_lap.strftime('%d/%m/%Y'),
        'ngay_thang_nam_text': date_to_vietnamese_text(statement.ngay_lap),

        # Thông tin cơ quan thu
        'tinh': statement.tax_location.tinh if statement.tax_location else '',
        'co_quan_thue': statement.tax_location.co_quan_thue_group if statement.tax_location else '',
        'xa_phuong': statement.tax_location.xa_phuong if statement.tax_location else '',
        'ma_co_quan_thu': statement.tax_location.ma_co_quan_thu if statement.tax_location else '',
        'ten_co_quan_thu': statement.tax_location.ten_co_quan_thu if statement.tax_location else '',
        
        # SỬA DÒNG NÀY: Dùng biến ma_dia_ban đã xử lý ở trên
        'ma_dia_ban': ma_dia_ban, 
        
        'kho_bac': statement.tax_location.kho_bac if statement.tax_location else '',

        # Thông tin bảng kê
        'tong_so_tien': f"{statement.tong_so_tien:,}".replace(',', '.'),
        'so_tien_bang_chu': so_tien_bang_chu,
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
