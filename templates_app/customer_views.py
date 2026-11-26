"""
Views khách hàng: danh sách, tìm kiếm, API dữ liệu, kiểm tra hợp lệ, thêm/sửa/xóa, nhập Excel/TSV.
"""
# Standard library imports
import re
from datetime import date, datetime

# Django imports
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods

# Local application imports
from .issueby_mapping import get_issueby_name
from .models import Template, Customer


def _customer_error_text(e):
    """Lỗi lưu khách hàng → câu tiếng Việt ngắn, kèm tên trường (vd. "Giới tính: Trường này không được để trắng.")."""
    by_field = getattr(e, 'message_dict', None)
    if by_field:
        def label(f):
            try:
                return str(Customer._meta.get_field(f).verbose_name)
            except Exception:
                return f
        return '; '.join(f'{label(f)}: {" ".join(m)}' for f, m in by_field.items())
    messages_ = getattr(e, 'messages', None)
    return '; '.join(messages_) if messages_ else str(e)


# Customer views
@login_required
def customer_list_view(request):
    """Danh sách khách hàng với tìm kiếm"""
    search_query = request.GET.get('q', '')

    customers = Customer.objects.all()

    if search_query:
        customers = customers.filter(
            Q(ho_ten__icontains=search_query) |
            Q(so_cmnd__icontains=search_query) |
            Q(so_dien_thoai__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(ghi_chu__icontains=search_query)
        )

    customers = customers.order_by('-created_at')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(customers, 20)  # 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Số ảnh chữ ký đã chụp + ảnh 2 mặt thẻ (học sinh gửi online) của từng khách trên trang
    from .customer_cccd_images import cccd_image_sides
    from .customer_signature import signature_files
    for customer in page_obj:
        customer.signature_count = len(signature_files(customer.pk))
        customer.cccd_sides = cccd_image_sides(customer.pk)

    # Mẫu biểu cho "In theo lô" (mẫu học sinh đứng đầu)
    from .student_registration import STUDENT_TEMPLATE_NAME
    batch_templates = [t for t in Template.objects.filter(is_active=True).select_related('category').order_by('category__name', 'order', 'name')
                       if t.user_has_access(request.user)]
    batch_templates.sort(key=lambda t: t.name != STUDENT_TEMPLATE_NAME)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'batch_templates': batch_templates,
    }
    return render(request, 'templates_app/customer_list.html', context)


@login_required
def customer_search_api(request):
    """API endpoint để tìm kiếm khách hàng (cho AJAX)"""
    search_query = request.GET.get('q', '')

    if len(search_query) < 2:
        return JsonResponse({'customers': []})

    customers = Customer.objects.filter(
        Q(ho_ten__icontains=search_query) |
        Q(so_cmnd__icontains=search_query) |
        Q(so_dien_thoai__icontains=search_query)
    ).order_by('ho_ten')[:20]  # Giới hạn 20 kết quả

    customer_list = [{
        'id': c.id,
        'ho_ten': c.ho_ten,
        'so_cmnd': c.so_cmnd,
        'so_dien_thoai': c.so_dien_thoai,
        'display': f"{c.ho_ten} - {c.so_cmnd}"
    } for c in customers]

    return JsonResponse({'customers': customer_list})


@login_required
def customer_data_api(request, customer_id):
    """API endpoint để lấy dữ liệu khách hàng theo ID (cho auto-fill)"""
    try:
        customer = Customer.objects.get(id=customer_id)
        return JsonResponse({
            'success': True,
            'data': customer.get_data_dict()
        })
    except Customer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Không tìm thấy khách hàng'
        }, status=404)


@login_required
def customer_detail_api(request, customer_id):
    """API endpoint để lấy thông tin chi tiết khách hàng (cho display)"""
    try:
        customer = Customer.objects.get(id=customer_id)
        return JsonResponse({
            'success': True,
            'customer': {
                'id': customer.id,
                'ma_khach_hang': customer.ma_khach_hang,
                'cif': customer.cif,
                'ho_ten': customer.ho_ten,
                'ngay_sinh': customer.ngay_sinh.strftime('%d/%m/%Y') if customer.ngay_sinh else '',
                'gioi_tinh': customer.gioi_tinh,
                'so_cmnd': customer.so_cmnd,
                'ngay_cap_cmnd': customer.ngay_cap_cmnd.strftime('%d/%m/%Y') if customer.ngay_cap_cmnd else '',
                'ngay_het_han_cmnd': customer.ngay_het_han_cmnd.strftime('%d/%m/%Y') if customer.ngay_het_han_cmnd else '',
                'noi_cap_cmnd': customer.noi_cap_cmnd,  # Raw value for form
                'noi_cap_cmnd_custom': customer.noi_cap_cmnd_custom,  # Custom value for form
                'noi_cap_cmnd_display': customer.get_noi_cap_display_value(),  # Display value
                'dia_chi': customer.dia_chi,
                'so_dien_thoai': customer.so_dien_thoai,
                'email': customer.email,
                'nghe_nghiep': customer.nghe_nghiep,
                'noi_lam_viec': customer.noi_lam_viec,
                'so_tai_khoan': customer.so_tai_khoan,
                'loai_tai_khoan': customer.loai_tai_khoan,
                'loai_tien_te': customer.loai_tien_te,
                'loai_the': customer.loai_the,
                'hang_the': customer.hang_the,
                'ghi_chu': customer.ghi_chu,
            }
        })
    except Customer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Không tìm thấy khách hàng'
        }, status=404)


# ============================================
# Customer Validation Functions
# ============================================

def validate_phone_number(phone):
    """
    Validate Vietnamese phone number format
    Returns: (is_valid, error_message)
    """
    if not phone or phone.strip() == '':
        return True, None  # Optional field

    # Remove spaces and dashes
    phone = phone.replace(' ', '').replace('-', '')

    # Must be 10 digits and start with 0
    if not re.match(r'^0\d{9}$', phone):
        return False, 'Số điện thoại phải có 10 số và bắt đầu bằng 0'

    return True, None


def validate_birth_date(date_str):
    """
    Validate birth date
    Returns: (is_valid, error_message)
    """
    if not date_str or date_str.strip() == '':
        return True, None  # Optional field

    try:
        birth_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return False, 'Ngày sinh không hợp lệ'

    today = date.today()

    # Cannot be in the future
    if birth_date > today:
        return False, 'Ngày sinh không thể là ngày trong tương lai'

    # Cannot be more than 150 years old
    max_age = today.year - 150
    if birth_date.year < max_age:
        return False, 'Ngày sinh không hợp lệ'

    return True, None


def validate_issuance_date(date_str):
    """
    Validate CCCD issuance date
    Returns: (is_valid, error_message)
    """
    if not date_str or date_str.strip() == '':
        return True, None  # Optional field

    try:
        issue_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return False, 'Ngày cấp CCCD không hợp lệ'

    today = date.today()

    # Cannot be in the future
    if issue_date > today:
        return False, 'Ngày cấp CCCD không thể là ngày trong tương lai'

    return True, None


def validate_expiry_date(issue_date_str, expiry_date_str):
    """
    Validate CCCD expiry date (must be after issuance date)
    Returns: (is_valid, error_message)
    """
    if not expiry_date_str or expiry_date_str.strip() == '':
        return True, None  # Optional field

    if not issue_date_str or issue_date_str.strip() == '':
        return True, None  # Can't validate if no issue date

    try:
        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
    except ValueError:
        return True, None  # Skip if dates are invalid (will be caught by other validators)

    # Expiry date must be after issue date
    if expiry_date <= issue_date:
        return False, 'Ngày hết hạn CCCD phải lớn hơn ngày cấp'

    return True, None


def validate_customer_data(request_data):
    """
    Validate all customer data fields
    Returns: (is_valid, error_messages_list)
    """
    errors = []

    # Validate phone number
    phone = request_data.get('so_dien_thoai', '')
    is_valid, error_msg = validate_phone_number(phone)
    if not is_valid:
        errors.append(error_msg)

    # Validate birth date
    birth_date = request_data.get('ngay_sinh', '')
    is_valid, error_msg = validate_birth_date(birth_date)
    if not is_valid:
        errors.append(error_msg)

    # Validate issuance date
    issue_date = request_data.get('ngay_cap_cmnd', '')
    is_valid, error_msg = validate_issuance_date(issue_date)
    if not is_valid:
        errors.append(error_msg)

    # Validate expiry date
    expiry_date = request_data.get('ngay_het_han_cmnd', '')
    is_valid, error_msg = validate_expiry_date(issue_date, expiry_date)
    if not is_valid:
        errors.append(error_msg)

    return len(errors) == 0, errors


# ============================================
# Customer CRUD Views
# ============================================

@login_required
@require_http_methods(["POST"])
def customer_create_view(request):
    """Tạo khách hàng mới"""
    try:
        # Get form data
        ho_ten = request.POST.get('ho_ten', '').strip()
        so_cmnd = request.POST.get('so_cmnd', '').strip()

        # Validate required fields
        if not ho_ten or not so_cmnd:
            return JsonResponse({
                'success': False,
                'error': 'Họ tên và Số CMND/CCCD là bắt buộc'
            }, status=400)

        # Check if CMND already exists
        if Customer.objects.filter(so_cmnd=so_cmnd).exists():
            return JsonResponse({
                'success': False,
                'error': f'Số CMND/CCCD {so_cmnd} đã tồn tại trong hệ thống'
            }, status=400)

        # Create customer
        customer = Customer(
            ma_khach_hang=request.POST.get('ma_khach_hang', ''),
            ho_ten=ho_ten,
            so_cmnd=so_cmnd,
            ngay_cap_cmnd=request.POST.get('ngay_cap_cmnd') or None,
            ngay_het_han_cmnd=request.POST.get('ngay_het_han_cmnd') or None,
            noi_cap_cmnd=request.POST.get('noi_cap_cmnd', 'Cục CSQLHC về TTXH'),
            ngay_sinh=request.POST.get('ngay_sinh') or None,
            gioi_tinh=request.POST.get('gioi_tinh', 'Nam'),
            so_dien_thoai=request.POST.get('so_dien_thoai', ''),
            email=request.POST.get('email', ''),
            dia_chi=request.POST.get('dia_chi', ''),
            nghe_nghiep=request.POST.get('nghe_nghiep', ''),
            noi_lam_viec=request.POST.get('noi_lam_viec', ''),
            so_tai_khoan=request.POST.get('so_tai_khoan', ''),
            ghi_chu=request.POST.get('ghi_chu', ''),
            # Service checkboxes
            dv_sms_banking=(request.POST.get('dv_sms_banking') == 'on'),
            dv_bankplus=(request.POST.get('dv_bankplus') == 'on'),
            dv_e_mobile=(request.POST.get('dv_e_mobile') == 'on'),
            dv_abic=(request.POST.get('dv_abic') == 'on'),
            # Tiền gửi tiết kiệm chung - Thông tin người gửi tiền thứ hai
            ho_ten_nguoi_gui_2=request.POST.get('ho_ten_nguoi_gui_2', ''),
            so_cmnd_nguoi_gui_2=request.POST.get('so_cmnd_nguoi_gui_2', ''),
            ngay_cap_cmnd_nguoi_gui_2=request.POST.get('ngay_cap_cmnd_nguoi_gui_2') or None,
            noi_cap_cmnd_nguoi_gui_2=request.POST.get('noi_cap_cmnd_nguoi_gui_2', ''),
            dia_chi_nguoi_gui_2=request.POST.get('dia_chi_nguoi_gui_2', ''),
            sdt_nguoi_gui_2=request.POST.get('sdt_nguoi_gui_2', ''),
            # Tiền gửi tiết kiệm chung - Giao dịch
            gd_rut_lai_tat_ca=(request.POST.get('gd_rut_lai_tat_ca') == 'on'),
            gd_rut_lai_mot_so=(request.POST.get('gd_rut_lai_mot_so') == 'on'),
            gd_tat_toan_tat_ca=(request.POST.get('gd_tat_toan_tat_ca') == 'on'),
            gd_tat_toan_mot_so=(request.POST.get('gd_tat_toan_mot_so') == 'on'),
            gd_bao_mat_tat_ca=(request.POST.get('gd_bao_mat_tat_ca') == 'on'),
            gd_bao_mat_mot_so=(request.POST.get('gd_bao_mat_mot_so') == 'on'),
            gd_bao_hong_tat_ca=(request.POST.get('gd_bao_hong_tat_ca') == 'on'),
            gd_bao_hong_mot_so=(request.POST.get('gd_bao_hong_mot_so') == 'on'),
            gd_phong_toa_tat_ca=(request.POST.get('gd_phong_toa_tat_ca') == 'on'),
            gd_phong_toa_mot_so=(request.POST.get('gd_phong_toa_mot_so') == 'on'),
            gd_xac_nhan_so_du_tat_ca=(request.POST.get('gd_xac_nhan_so_du_tat_ca') == 'on'),
            gd_xac_nhan_so_du_mot_so=(request.POST.get('gd_xac_nhan_so_du_mot_so') == 'on'),
            # Ngoại tệ - Nhận tiền nước ngoài
            quan_he_nguoi_gui_nhan=request.POST.get('quan_he_nguoi_gui_nhan', ''),
            muc_dich_giao_dich=request.POST.get('muc_dich_giao_dich', ''),
            ho_ten_nguoi_gui_tien=request.POST.get('ho_ten_nguoi_gui_tien', ''),
            quoc_gia_gui_tien=request.POST.get('quoc_gia_gui_tien', ''),
            ma_so_nhan_tien=request.POST.get('ma_so_nhan_tien', ''),
            so_tien_ngoai_te=request.POST.get('so_tien_ngoai_te', ''),
            loai_tien_ngoai_te=request.POST.get('loai_tien_ngoai_te', ''),
            created_by=request.user
        )
        customer.save()

        return JsonResponse({
            'success': True,
            'message': 'Đã thêm khách hàng thành công',
            'customer_id': customer.id,
            'customer_name': customer.ho_ten
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi tạo khách hàng: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def customer_update_view(request, customer_id):
    """Cập nhật thông tin khách hàng"""
    try:
        customer = get_object_or_404(Customer, id=customer_id)

        # Get form data
        ho_ten = request.POST.get('ho_ten', '').strip()
        so_cmnd = request.POST.get('so_cmnd', '').strip()

        # Validate required fields
        if not ho_ten or not so_cmnd:
            return JsonResponse({
                'success': False,
                'error': 'Họ tên và Số CMND/CCCD là bắt buộc'
            }, status=400)

        # Check if CMND already exists (excluding current customer)
        if Customer.objects.filter(so_cmnd=so_cmnd).exclude(id=customer_id).exists():
            return JsonResponse({
                'success': False,
                'error': f'Số CMND/CCCD {so_cmnd} đã tồn tại trong hệ thống'
            }, status=400)

        # Update customer fields
        customer.ma_khach_hang = request.POST.get('ma_khach_hang', '')
        customer.ho_ten = ho_ten
        customer.so_cmnd = so_cmnd
        customer.ngay_cap_cmnd = request.POST.get('ngay_cap_cmnd') or None
        customer.ngay_het_han_cmnd = request.POST.get('ngay_het_han_cmnd') or None
        customer.noi_cap_cmnd = request.POST.get('noi_cap_cmnd', 'Cục CSQLHC về TTXH')
        customer.ngay_sinh = request.POST.get('ngay_sinh') or None
        customer.gioi_tinh = request.POST.get('gioi_tinh', 'Nam')
        customer.so_dien_thoai = request.POST.get('so_dien_thoai', '')
        customer.email = request.POST.get('email', '')
        customer.dia_chi = request.POST.get('dia_chi', '')
        customer.nghe_nghiep = request.POST.get('nghe_nghiep', '')
        customer.noi_lam_viec = request.POST.get('noi_lam_viec', '')
        customer.so_tai_khoan = request.POST.get('so_tai_khoan', '')
        customer.ghi_chu = request.POST.get('ghi_chu', '')
        # Tiền gửi tiết kiệm chung - Thông tin người gửi tiền thứ hai
        customer.ho_ten_nguoi_gui_2 = request.POST.get('ho_ten_nguoi_gui_2', '')
        customer.so_cmnd_nguoi_gui_2 = request.POST.get('so_cmnd_nguoi_gui_2', '')
        customer.ngay_cap_cmnd_nguoi_gui_2 = request.POST.get('ngay_cap_cmnd_nguoi_gui_2') or None
        customer.noi_cap_cmnd_nguoi_gui_2 = request.POST.get('noi_cap_cmnd_nguoi_gui_2', '')
        customer.dia_chi_nguoi_gui_2 = request.POST.get('dia_chi_nguoi_gui_2', '')
        customer.sdt_nguoi_gui_2 = request.POST.get('sdt_nguoi_gui_2', '')
        # Tiền gửi tiết kiệm chung - Giao dịch
        customer.gd_rut_lai_tat_ca = (request.POST.get('gd_rut_lai_tat_ca') == 'on')
        customer.gd_rut_lai_mot_so = (request.POST.get('gd_rut_lai_mot_so') == 'on')
        customer.gd_tat_toan_tat_ca = (request.POST.get('gd_tat_toan_tat_ca') == 'on')
        customer.gd_tat_toan_mot_so = (request.POST.get('gd_tat_toan_mot_so') == 'on')
        customer.gd_bao_mat_tat_ca = (request.POST.get('gd_bao_mat_tat_ca') == 'on')
        customer.gd_bao_mat_mot_so = (request.POST.get('gd_bao_mat_mot_so') == 'on')
        customer.gd_bao_hong_tat_ca = (request.POST.get('gd_bao_hong_tat_ca') == 'on')
        customer.gd_bao_hong_mot_so = (request.POST.get('gd_bao_hong_mot_so') == 'on')
        customer.gd_phong_toa_tat_ca = (request.POST.get('gd_phong_toa_tat_ca') == 'on')
        customer.gd_phong_toa_mot_so = (request.POST.get('gd_phong_toa_mot_so') == 'on')
        customer.gd_xac_nhan_so_du_tat_ca = (request.POST.get('gd_xac_nhan_so_du_tat_ca') == 'on')
        customer.gd_xac_nhan_so_du_mot_so = (request.POST.get('gd_xac_nhan_so_du_mot_so') == 'on')
        # Ngoại tệ - Nhận tiền nước ngoài
        customer.quan_he_nguoi_gui_nhan = request.POST.get('quan_he_nguoi_gui_nhan', '')
        customer.muc_dich_giao_dich = request.POST.get('muc_dich_giao_dich', '')
        customer.ho_ten_nguoi_gui_tien = request.POST.get('ho_ten_nguoi_gui_tien', '')
        customer.quoc_gia_gui_tien = request.POST.get('quoc_gia_gui_tien', '')
        customer.ma_so_nhan_tien = request.POST.get('ma_so_nhan_tien', '')
        customer.so_tien_ngoai_te = request.POST.get('so_tien_ngoai_te', '')
        customer.loai_tien_ngoai_te = request.POST.get('loai_tien_ngoai_te', '')
        customer.save()

        return JsonResponse({
            'success': True,
            'message': 'Đã cập nhật thông tin khách hàng'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi cập nhật khách hàng: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def customer_delete_view(request, customer_id):
    """Xóa khách hàng"""
    customer = get_object_or_404(Customer, id=customer_id)
    customer_name = customer.ho_ten
    customer.delete()
    return JsonResponse({
        'success': True,
        'message': f'Đã xóa khách hàng: {customer_name}'
    })


@login_required
@require_http_methods(["POST"])
def customer_import_excel(request):
    """Import khách hàng từ file Excel"""
    if 'excel_file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'Vui lòng chọn file Excel'
        }, status=400)

    excel_file = request.FILES['excel_file']

    # Kiểm tra file extension
    if not excel_file.name.endswith(('.xlsx', '.xls')):
        return JsonResponse({
            'success': False,
            'error': 'File phải có định dạng .xlsx hoặc .xls'
        }, status=400)

    try:
        import openpyxl
        from datetime import datetime

        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb.active

        # Giả sử dòng đầu tiên là header
        headers = [cell.value for cell in ws[1]]

        # Mapping column names to model fields
        # Có thể customize mapping này
        field_mapping = {
            'Mã KH': 'ma_khach_hang',
            'CIF': 'cif',
            'Họ tên': 'ho_ten',
            'Họ và tên': 'ho_ten',
            'Ngày sinh': 'ngay_sinh',
            'Giới tính': 'gioi_tinh',
            'CMND/CCCD': 'so_cmnd',
            'Số CMND': 'so_cmnd',
            'Ngày cấp': 'ngay_cap_cmnd',
            'Ngày cấp CMND': 'ngay_cap_cmnd',
            'Nơi cấp': 'noi_cap_cmnd',
            'Nơi cấp CMND': 'noi_cap_cmnd',
            'Địa chỉ': 'dia_chi',
            'Điện thoại': 'so_dien_thoai',
            'Số điện thoại': 'so_dien_thoai',
            'Email': 'email',
            'Nghề nghiệp': 'nghe_nghiep',
            'Nơi làm việc': 'noi_lam_viec',
            'Số tài khoản': 'so_tai_khoan',
            'Loại tài khoản': 'loai_tai_khoan',
            'Loại tiền tệ': 'loai_tien_te',
            'Loại thẻ': 'loai_the',
            'Hạng thẻ': 'hang_the',
        }

        imported_count = 0
        skipped_count = 0
        errors = []

        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # Build data dict from row
                data = {}
                for col_idx, value in enumerate(row):
                    if col_idx < len(headers):
                        header = headers[col_idx]
                        if header and header in field_mapping:
                            field_name = field_mapping[header]

                            # Handle date fields
                            if field_name in ['ngay_sinh', 'ngay_cap_cmnd', 'ngay_het_han_cmnd', 'ngay_in']:
                                if value:
                                    if isinstance(value, datetime):
                                        data[field_name] = value.date()
                                    else:
                                        # Try parsing string date
                                        try:
                                            parsed_date = datetime.strptime(str(value), '%d/%m/%Y')
                                            data[field_name] = parsed_date.date()
                                        except (ValueError, TypeError):
                                            try:
                                                parsed_date = datetime.strptime(str(value), '%Y-%m-%d')
                                                data[field_name] = parsed_date.date()
                                            except (ValueError, TypeError):
                                                # Invalid date format - skip this field
                                                pass
                            else:
                                data[field_name] = value if value else ''

                # Validate required fields
                if not data.get('ho_ten') or not data.get('so_cmnd'):
                    skipped_count += 1
                    errors.append(f"Dòng {row_idx}: Thiếu họ tên hoặc CMND")
                    continue

                # Check if customer already exists
                existing_customer = Customer.objects.filter(so_cmnd=data['so_cmnd']).first()
                if existing_customer:
                    # Update existing customer
                    for field, value in data.items():
                        setattr(existing_customer, field, value)
                    existing_customer.save()
                else:
                    # Create new customer
                    customer = Customer(**data)
                    customer.created_by = request.user
                    customer.save()

                imported_count += 1

            except Exception as e:
                skipped_count += 1
                errors.append(f"Dòng {row_idx}: {str(e)}")
                continue

        return JsonResponse({
            'success': True,
            'imported': imported_count,
            'skipped': skipped_count,
            'errors': errors[:10]  # Limit errors to 10
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi xử lý file Excel: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def customer_get(request, customer_id):
    """Lấy thông tin khách hàng theo ID để hiển thị trong form edit"""
    try:
        customer = get_object_or_404(Customer, id=customer_id)

        return JsonResponse({
            'success': True,
            'customer': {
                'id': customer.id,
                'ma_khach_hang': customer.ma_khach_hang,
                'ho_ten': customer.ho_ten,
                'so_cmnd': customer.so_cmnd,
                'ngay_cap_cmnd': customer.ngay_cap_cmnd.isoformat() if customer.ngay_cap_cmnd else '',
                'ngay_het_han_cmnd': customer.ngay_het_han_cmnd.isoformat() if customer.ngay_het_han_cmnd else '',
                'noi_cap_cmnd': customer.noi_cap_cmnd,
                'ngay_sinh': customer.ngay_sinh.isoformat() if customer.ngay_sinh else '',
                'gioi_tinh': customer.gioi_tinh,
                'so_dien_thoai': customer.so_dien_thoai,
                'email': customer.email,
                'dia_chi': customer.dia_chi,
                'nghe_nghiep': customer.nghe_nghiep,
                'noi_lam_viec': customer.noi_lam_viec,
                'so_tai_khoan': customer.so_tai_khoan,
                'ghi_chu': customer.ghi_chu,
                # Address fields
                'province': customer.province or '',
                'district': customer.district or '',
                'ward': customer.ward or '',
                'hamlet': customer.hamlet or '',
                'full_address': customer.full_address or '',
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Không tìm thấy khách hàng: {str(e)}'
        }, status=404)


# ============================================
# TSV Import for AGRIBANK clipboard data
# ============================================

def parse_tsv_date(date_str):
    """
    Convert date from YYYYMMDD to date object
    Args:
        date_str: Date string in YYYYMMDD format
    Returns:
        date object or None
    """
    if not date_str or not date_str.strip() or len(date_str) < 8:
        return None

    try:
        date_str = date_str.strip()
        if len(date_str) == 8:
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            return date(year, month, day)
    except (ValueError, IndexError):
        pass

    return None


@login_required
@require_http_methods(["POST"])
def customer_import_tsv(request):
    """
    Import khách hàng từ file TSV (clipboard AGRIBANK)
    """
    if 'tsv_file' not in request.FILES:
        return JsonResponse({
            'success': False,
            'error': 'Vui lòng chọn file TSV'
        }, status=400)

    tsv_file = request.FILES['tsv_file']

    # Kiểm tra file extension
    if not (tsv_file.name.endswith('.tsv') or tsv_file.name.endswith('.txt')):
        return JsonResponse({
            'success': False,
            'error': 'File phải có định dạng .tsv hoặc .txt'
        }, status=400)

    try:
        # Read file content
        content = tsv_file.read().decode('utf-8')
        lines = content.strip().split('\n')

        if len(lines) < 2:
            return JsonResponse({
                'success': False,
                'error': 'File không có dữ liệu'
            }, status=400)

        # Parse header
        header = lines[0].strip().split('\t')

        success_count = 0
        error_count = 0
        errors = []
        updated_count = 0

        # Process each data line
        for line_num, line in enumerate(lines[1:], start=2):
            try:
                values = line.strip().split('\t')

                # Create dict from header and values
                data = {}
                for i, field in enumerate(header):
                    data[field] = values[i] if i < len(values) else ''

                # Clean values
                def clean(val):
                    return str(val).strip() if val else ''

                # Extract required fields
                custno = clean(data.get('custno', ''))
                nmloc = clean(data.get('nmloc', ''))
                regno = clean(data.get('regno', ''))

                # Validate required fields
                if not nmloc:
                    errors.append(f'Dòng {line_num}: Thiếu họ tên')
                    error_count += 1
                    continue

                if not regno:
                    errors.append(f'Dòng {line_num}: Thiếu số CMND/CCCD')
                    error_count += 1
                    continue

                # Check if customer already exists
                if Customer.objects.filter(so_cmnd=regno).exists():
                    customer = Customer.objects.get(so_cmnd=regno)
                    update_mode = True
                else:
                    customer = Customer(created_by=request.user)
                    update_mode = False

                # Map basic fields
                customer.ma_khach_hang = custno
                if custno:
                    customer.cif = custno
                customer.ho_ten = nmloc
                customer.so_cmnd = regno

                # Parse dates
                ngay_sinh_str = clean(data.get('name_1', ''))
                if ngay_sinh_str:
                    ngay_sinh = parse_tsv_date(ngay_sinh_str)
                    if ngay_sinh:
                        customer.ngay_sinh = ngay_sinh

                ngay_cap_str = clean(data.get('issuedt1', ''))
                if ngay_cap_str:
                    ngay_cap = parse_tsv_date(ngay_cap_str)
                    if ngay_cap:
                        customer.ngay_cap_cmnd = ngay_cap

                # Gender
                gioi_tinh = clean(data.get('name_3', ''))
                if gioi_tinh:
                    customer.gioi_tinh = gioi_tinh

                # Phone
                so_dien_thoai = clean(data.get('name_4', ''))
                if so_dien_thoai:
                    customer.so_dien_thoai = so_dien_thoai

                # Address
                dia_chi = clean(data.get('addr1loc', ''))
                if dia_chi:
                    customer.dia_chi = dia_chi

                # Issueby - map code to name
                issueby_code = clean(data.get('issueby1', ''))
                if issueby_code:
                    customer.ma_noi_cap_cmnd = issueby_code
                    issueby_name = get_issueby_name(issueby_code)
                    # Try to match with existing choices
                    if 'Cục' in issueby_name or 'CSQLHC' in issueby_name:
                        customer.noi_cap_cmnd = 'Cục CSQLHC về TTXH'
                    elif 'Bộ Công An' in issueby_name:
                        customer.noi_cap_cmnd = 'Bộ Công An'
                    else:
                        customer.noi_cap_cmnd = 'Khác'
                    customer.noi_cap_cmnd_custom = issueby_name

                # Profession
                profnm = clean(data.get('profnm', ''))
                if profnm and profnm != 'Khác':
                    customer.nghe_nghiep = profnm

                # Email
                email = clean(data.get('emailaddr', ''))
                if email:
                    customer.email = email

                # Administrative codes
                ma_tinh = clean(data.get('province', ''))
                if ma_tinh:
                    customer.ma_tinh = ma_tinh

                ma_quan_huyen = clean(data.get('district', ''))
                if ma_quan_huyen:
                    customer.ma_quan_huyen = ma_quan_huyen

                ma_phuong_xa = clean(data.get('commune_ward', ''))
                if ma_phuong_xa:
                    customer.ma_phuong_xa = ma_phuong_xa

                # Nationality
                quoc_tich = clean(data.get('ctrycdnatl', ''))
                if quoc_tich:
                    customer.quoc_tich = quoc_tich

                # Tax code
                ma_so_thue = clean(data.get('taxno', ''))
                if ma_so_thue:
                    customer.ma_so_thue = ma_so_thue

                # Passport
                so_ho_chieu = clean(data.get('passno', ''))
                if so_ho_chieu:
                    customer.so_ho_chieu = so_ho_chieu

                # Save customer
                customer.save()

                if update_mode:
                    updated_count += 1
                else:
                    success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f'Dòng {line_num}: {str(e)}')
                continue

        return JsonResponse({
            'success': True,
            'message': f'Import thành công: {success_count} khách hàng mới, {updated_count} cập nhật',
            'imported': success_count,
            'updated': updated_count,
            'errors': error_count,
            'error_details': errors[:10]  # Chỉ trả về 10 lỗi đầu tiên
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi xử lý file TSV: {str(e)}'
        }, status=500)
