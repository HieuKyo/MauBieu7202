# Standard library imports
import io
import json
import os
import re
import tempfile
from datetime import date, datetime
from urllib.parse import urlparse

# Django imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

# Third-party imports
import mammoth

# Local application imports
from .forms import DynamicTemplateForm, CustomerForm, GlobalConfigForm
from .issueby_mapping import get_issueby_name
from .models import Category, Template, Variable, TemplateVariable, Customer, GlobalConfig, remove_vietnamese_diacritics
from .utils import render_word_template


# Security helper functions
def is_safe_redirect_url(url, allowed_host):
    """
    Validate redirect URL to prevent Open Redirect attacks.
    Returns True only if the URL is safe to redirect to.

    Args:
        url: The URL to validate
        allowed_host: The allowed host (from request.get_host())

    Returns:
        bool: True if URL is safe, False otherwise
    """
    if not url:
        return False

    # Parse the URL
    parsed = urlparse(url)

    # Allow only relative URLs (no scheme, no netloc) or same-host URLs
    if not parsed.netloc:
        # Relative URL - safe as long as it doesn't start with //
        return not url.startswith('//')

    # If netloc exists, it must match the allowed host
    return parsed.netloc == allowed_host


@login_required
def dashboard_view(request):
    """
    Trang chủ - Hiển thị danh sách khách hàng và mẫu biểu
    Layout: Customers (left) | Customer Detail + Templates (right)
    """
    user = request.user

    # Lấy danh sách khách hàng
    customers = Customer.objects.all().order_by('-created_at')

    # Lấy danh mục và templates mà user có quyền truy cập
    if user.is_superuser:
        categories = Category.objects.filter(
            templates__is_active=True
        ).distinct().prefetch_related('templates')
    else:
        user_groups = user.groups.all()
        categories = Category.objects.filter(
            templates__is_active=True
        ).filter(
            Q(templates__allowed_groups__isnull=True) |
            Q(templates__allowed_groups__in=user_groups)
        ).distinct().prefetch_related('templates')

    # Lọc templates theo quyền
    for category in categories:
        if user.is_superuser:
            category.accessible_templates = category.templates.filter(is_active=True)
        else:
            category.accessible_templates = category.templates.filter(
                is_active=True
            ).filter(
                Q(allowed_groups__isnull=True) |
                Q(allowed_groups__in=user_groups)
            ).distinct()

    context = {
        'customers': customers,
        'categories': categories,
        'user': user,
    }
    return render(request, 'templates_app/dashboard.html', context)


@login_required
def category_detail_view(request, category_id):
    """
    Hiển thị danh sách mẫu biểu trong một danh mục
    Chỉ hiển thị các template mà user có quyền truy cập
    """
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    # Lọc templates user có quyền truy cập
    if user.is_superuser:
        templates = category.templates.filter(is_active=True)
    else:
        user_groups = user.groups.all()
        templates = category.templates.filter(
            is_active=True
        ).filter(
            Q(allowed_groups__isnull=True) |
            Q(allowed_groups__in=user_groups)
        ).distinct()

    # Nếu không có template nào, raise 404
    if not templates.exists():
        raise Http404("Bạn không có quyền truy cập danh mục này")

    context = {
        'category': category,
        'templates': templates,
    }
    return render(request, 'templates_app/category_detail.html', context)


@login_required
def template_form_view(request, template_id):
    """
    Hiển thị form nhập liệu cho một template hoặc tự động lưu dữ liệu vào session
    Auto-fill từ customer nếu có customer parameter trong URL
    """
    template = get_object_or_404(Template, id=template_id, is_active=True)
    user = request.user

    # Kiểm tra quyền truy cập
    if not template.user_has_access(user):
        raise Http404("Bạn không có quyền truy cập mẫu biểu này")

    # Lấy danh sách biến của template (qua TemplateVariable để có thứ tự)
    template_variables = TemplateVariable.objects.filter(
        template=template
    ).select_related('variable').order_by('order', 'variable__name')

    # Check if customer ID is provided
    customer_id = request.GET.get('customer')
    customer = None
    initial_data = {}

    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
            initial_data = customer.get_data_dict()
        except Customer.DoesNotExist:
            messages.warning(request, 'Không tìm thấy thông tin khách hàng')

    # Tự động lưu dữ liệu vào session nếu có customer
    # (bỏ qua form nhập biến - tất cả biến đến từ customer + global config)
    if customer_id and customer:
        session_data = initial_data.copy()
        session_data['_customer_id'] = customer_id
        request.session[f'template_{template_id}_data'] = session_data

        # Nếu là AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Dữ liệu đã được lưu'})

    if request.method == 'POST':
        # Nếu không có variables, vẫn cho phép submit
        if template_variables.count() == 0:
            # Không có form fields, lưu session data từ customer hoặc rỗng
            session_data = initial_data.copy() if initial_data else {}
            if customer_id:
                session_data['_customer_id'] = customer_id
            request.session[f'template_{template_id}_data'] = session_data

            # Nếu là AJAX request (từ preview button), return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Dữ liệu đã được lưu'})

            return redirect('generate_document', template_id=template_id)

        # Có variables, validate form
        form = DynamicTemplateForm(request.POST, template=template)
        if form.is_valid():
            # Lưu dữ liệu vào session để generate document
            # Bao gồm cả customer_id để lấy date variables
            session_data = form.cleaned_data.copy()
            if customer_id:
                session_data['_customer_id'] = customer_id
            request.session[f'template_{template_id}_data'] = session_data

            # Nếu là AJAX request (từ preview button), return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Dữ liệu đã được lưu'})

            return redirect('generate_document', template_id=template_id)
        else:
            # Nếu form không hợp lệ và là AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        # Create form with initial data from customer if available
        form = DynamicTemplateForm(template=template, initial=initial_data)

    context = {
        'template': template,
        'form': form,
        'category': template.category,
        'customer': customer,
    }
    return render(request, 'templates_app/template_form.html', context)


@login_required
def generate_document_view(request, template_id):
    """
    Tạo file Word từ template và dữ liệu đã nhập
    Bao gồm các biến chi nhánh và date variables
    """
    template = get_object_or_404(Template, id=template_id, is_active=True)
    user = request.user

    # Kiểm tra quyền truy cập
    if not template.user_has_access(user):
        raise Http404("Bạn không có quyền truy cập mẫu biểu này")

    # Lấy dữ liệu từ session
    session_key = f'template_{template_id}_data'
    data = request.session.get(session_key)

    if not data:
        messages.error(request, "Không tìm thấy dữ liệu. Vui lòng điền form lại.")
        return redirect('template_form', template_id=template_id)

    try:
        # Lấy customer_id từ session data nếu có
        customer_id = data.pop('_customer_id', None)

        # Thêm TẤT CẢ biến chung (chi nhánh + custom variables) vào data
        global_config = GlobalConfig.get_instance()
        data.update(global_config.get_all_variables())

        # Thêm date variables nếu có customer
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                customer_data = customer.get_data_dict()
                # Thêm các biến d1, d2, m1, m2, y1, y2, y3, y4
                for key in ['d1', 'd2', 'm1', 'm2', 'y1', 'y2', 'y3', 'y4']:
                    if key in customer_data:
                        data[key] = customer_data[key]
            except Customer.DoesNotExist:
                pass

        # Render template Word với dữ liệu
        template_path = template.file.path
        output_stream = render_word_template(template_path, data)

        # Xóa dữ liệu khỏi session
        del request.session[session_key]

        # Trả về file Word
        response = HttpResponse(
            output_stream.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        filename = f"{template.name}_{user.username}.docx"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except Exception as e:
        messages.error(request, f"Lỗi khi tạo file Word: {str(e)}")
        return redirect('template_form', template_id=template_id)


# Authentication views
def login_view(request):
    """Trang đăng nhập - hỗ trợ username không phân biệt hoa/thường"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username_input = request.POST.get('username', '').strip()
        password = request.POST.get('password')

        # Tìm user với username không phân biệt hoa/thường
        # Ví dụ: kientranthihong = KIENTRANTHIHONG = KienTranThiHong
        try:
            user_obj = User.objects.get(username__iexact=username_input)
            actual_username = user_obj.username
        except User.DoesNotExist:
            actual_username = username_input

        # Authenticate với username thực tế trong database
        user = authenticate(request, username=actual_username, password=password)

        if user is not None:
            login(request, user)
            # Fix Open Redirect vulnerability: validate next_url before redirecting
            next_url = request.GET.get('next', '')
            if next_url and is_safe_redirect_url(next_url, request.get_host()):
                return redirect(next_url)
            return redirect('dashboard')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng')

    return render(request, 'templates_app/login.html')


@login_required
def logout_view(request):
    """Đăng xuất"""
    logout(request)
    messages.success(request, 'Đã đăng xuất thành công')
    return redirect('login')


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
            Q(email__icontains=search_query)
        )

    customers = customers.order_by('-created_at')

    context = {
        'customers': customers,
        'search_query': search_query,
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


# Branch Configuration views
@login_required
def branch_config_view(request):
    """Trang cấu hình toàn cục (chi nhánh + biến chung)"""
    if not request.user.is_superuser:
        messages.error(request, 'Bạn không có quyền truy cập trang này')
        return redirect('dashboard')

    config = GlobalConfig.get_instance()

    if request.method == 'POST':
        # Xử lý form cập nhật thông tin chi nhánh
        form = GlobalConfigForm(request.POST, instance=config)
        if form.is_valid():
            global_config = form.save(commit=False)
            global_config.updated_by = request.user
            global_config.save()
            messages.success(request, 'Đã cập nhật cấu hình thành công')
            return redirect('branch_config')
    else:
        form = GlobalConfigForm(instance=config)

    # Tạo danh sách biến mẫu từ Customer để hiển thị
    # (lấy tất cả field names từ Customer model)
    customer_fields = {}
    for field in Customer._meta.get_fields():
        if field.concrete and not field.many_to_many and not field.one_to_many:
            field_name = field.name
            if field_name not in ['id', 'created_at', 'updated_at', 'created_by']:
                # Lấy verbose_name nếu có
                verbose = getattr(field, 'verbose_name', field_name)
                customer_fields[field_name] = verbose

    # Thêm các biến ngày tháng
    date_variables = {
        'd1': 'Ngày - Chữ số thứ nhất',
        'd2': 'Ngày - Chữ số thứ hai',
        'm1': 'Tháng - Chữ số thứ nhất',
        'm2': 'Tháng - Chữ số thứ hai',
        'y1': 'Năm - Chữ số thứ nhất',
        'y2': 'Năm - Chữ số thứ hai',
        'y3': 'Năm - Chữ số thứ ba',
        'y4': 'Năm - Chữ số thứ tư',
    }

    # Biến chi nhánh
    branch_fields = {
        'ten_chi_nhanh': 'Tên chi nhánh',
        'ten_chi_nhanh_hoa': 'Tên chi nhánh (IN HOA)',
        'ma_chi_nhanh': 'Mã chi nhánh',
        'mst': 'Mã số thuế',
        'dia_chi_chi_nhanh': 'Địa chỉ chi nhánh',
        'dien_thoai_chi_nhanh': 'Điện thoại chi nhánh',
        'so_fax': 'Số Fax',
        'dia_danh': 'Địa danh (Bạc Liêu, Đồng Tháp...)',
        'giao_dich_vien': 'Giao dịch viên',
        'kiem_soat_vien': 'Kiểm soát viên',
        'giam_doc': 'Giám đốc',
        'ngay_hien_tai': 'Ngày hiện tại (dd/mm/yyyy) - Tự động',
        'ngay_thang_nam_text': 'Ngày tháng năm (văn bản) - Tự động',
    }

    context = {
        'form': form,
        'config': config,
        'custom_variables': config.custom_variables or {},
        'customer_fields': customer_fields,
        'date_variables': date_variables,
        'branch_fields': branch_fields,
    }
    return render(request, 'templates_app/branch_config.html', context)


@login_required
@require_http_methods(["POST"])
def add_custom_variable(request):
    """API: Thêm biến tùy chỉnh"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Không có quyền'}, status=403)

    variable_name = request.POST.get('name', '').strip()
    variable_value = request.POST.get('value', '').strip()

    if not variable_name:
        return JsonResponse({'success': False, 'error': 'Tên biến không được để trống'})

    config = GlobalConfig.get_instance()
    custom_vars = config.custom_variables or {}

    # Kiểm tra biến đã tồn tại
    if variable_name in custom_vars:
        return JsonResponse({'success': False, 'error': f'Biến "{variable_name}" đã tồn tại'})

    # Thêm biến mới
    custom_vars[variable_name] = variable_value
    config.custom_variables = custom_vars
    config.updated_by = request.user
    config.save()

    return JsonResponse({
        'success': True,
        'message': f'Đã thêm biến "{variable_name}"',
        'variable': {'name': variable_name, 'value': variable_value}
    })


@login_required
@require_http_methods(["POST"])
def update_custom_variable(request):
    """API: Cập nhật biến tùy chỉnh"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Không có quyền'}, status=403)

    variable_name = request.POST.get('name', '').strip()
    variable_value = request.POST.get('value', '').strip()

    if not variable_name:
        return JsonResponse({'success': False, 'error': 'Tên biến không được để trống'})

    config = GlobalConfig.get_instance()
    custom_vars = config.custom_variables or {}

    if variable_name not in custom_vars:
        return JsonResponse({'success': False, 'error': f'Biến "{variable_name}" không tồn tại'})

    # Cập nhật giá trị
    custom_vars[variable_name] = variable_value
    config.custom_variables = custom_vars
    config.updated_by = request.user
    config.save()

    return JsonResponse({
        'success': True,
        'message': f'Đã cập nhật biến "{variable_name}"'
    })


@login_required
@require_http_methods(["POST"])
def delete_custom_variable(request):
    """API: Xóa biến tùy chỉnh"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Không có quyền'}, status=403)

    variable_name = request.POST.get('name', '').strip()

    if not variable_name:
        return JsonResponse({'success': False, 'error': 'Tên biến không được để trống'})

    config = GlobalConfig.get_instance()
    custom_vars = config.custom_variables or {}

    if variable_name not in custom_vars:
        return JsonResponse({'success': False, 'error': f'Biến "{variable_name}" không tồn tại'})

    # Xóa biến
    del custom_vars[variable_name]
    config.custom_variables = custom_vars
    config.updated_by = request.user
    config.save()

    return JsonResponse({
        'success': True,
        'message': f'Đã xóa biến "{variable_name}"'
    })


@login_required
def variable_library_view(request):
    """
    Thư viện Biến - Hiển thị tất cả biến có sẵn với nút copy
    Solution 3: Advanced variable discovery page
    """
    # 1. Biến Khách hàng - Extract from Customer model
    customer_variables = []
    for field in Customer._meta.get_fields():
        if field.concrete and not field.many_to_many and not field.one_to_many:
            field_name = field.name
            if field_name not in ['id', 'created_at', 'updated_at', 'created_by']:
                verbose = getattr(field, 'verbose_name', field_name)
                customer_variables.append({
                    'name': field_name,
                    'description': verbose,
                    'example': ''  # Could add examples later
                })

    # Thêm biến tự động sinh (auto-generated)
    customer_variables.append({
        'name': 'ten_tieng_anh',
        'description': 'Tên tiếng Anh tự động (loại bỏ dấu tiếng Việt và UPPER CASE từ ho_ten)',
        'example': 'TRUONG TRUNG HIEU (từ Trương Trung Hiếu)'
    })

    # 2. Biến Ngày tháng - Derived from dates
    date_variables = [
        # Ngày sinh
        {'name': 'd1', 'description': 'Ngày sinh - Chữ số thứ nhất', 'example': 'Nếu ngày sinh là 05/03/1990 → d1 = 0'},
        {'name': 'd2', 'description': 'Ngày sinh - Chữ số thứ hai', 'example': 'Nếu ngày sinh là 05/03/1990 → d2 = 5'},
        {'name': 'm1', 'description': 'Tháng sinh - Chữ số thứ nhất', 'example': 'Nếu ngày sinh là 05/03/1990 → m1 = 0'},
        {'name': 'm2', 'description': 'Tháng sinh - Chữ số thứ hai', 'example': 'Nếu ngày sinh là 05/03/1990 → m2 = 3'},
        {'name': 'y1', 'description': 'Năm sinh - Chữ số thứ nhất', 'example': 'Nếu ngày sinh là 05/03/1990 → y1 = 1'},
        {'name': 'y2', 'description': 'Năm sinh - Chữ số thứ hai', 'example': 'Nếu ngày sinh là 05/03/1990 → y2 = 9'},
        {'name': 'y3', 'description': 'Năm sinh - Chữ số thứ ba', 'example': 'Nếu ngày sinh là 05/03/1990 → y3 = 9'},
        {'name': 'y4', 'description': 'Năm sinh - Chữ số thứ tư', 'example': 'Nếu ngày sinh là 05/03/1990 → y4 = 0'},
        # Ngày cấp CMND/CCCD
        {'name': 'dcc1', 'description': 'Ngày cấp CCCD - Chữ số thứ nhất', 'example': 'Nếu ngày cấp là 15/06/2020 → dcc1 = 1'},
        {'name': 'dcc2', 'description': 'Ngày cấp CCCD - Chữ số thứ hai', 'example': 'Nếu ngày cấp là 15/06/2020 → dcc2 = 5'},
        {'name': 'mcc1', 'description': 'Tháng cấp CCCD - Chữ số thứ nhất', 'example': 'Nếu ngày cấp là 15/06/2020 → mcc1 = 0'},
        {'name': 'mcc2', 'description': 'Tháng cấp CCCD - Chữ số thứ hai', 'example': 'Nếu ngày cấp là 15/06/2020 → mcc2 = 6'},
        {'name': 'ycc1', 'description': 'Năm cấp CCCD - Chữ số thứ nhất', 'example': 'Nếu ngày cấp là 15/06/2020 → ycc1 = 2'},
        {'name': 'ycc2', 'description': 'Năm cấp CCCD - Chữ số thứ hai', 'example': 'Nếu ngày cấp là 15/06/2020 → ycc2 = 0'},
        {'name': 'ycc3', 'description': 'Năm cấp CCCD - Chữ số thứ ba', 'example': 'Nếu ngày cấp là 15/06/2020 → ycc3 = 2'},
        {'name': 'ycc4', 'description': 'Năm cấp CCCD - Chữ số thứ tư', 'example': 'Nếu ngày cấp là 15/06/2020 → ycc4 = 0'},
        # Ngày hết hạn CMND/CCCD
        {'name': 'dhh1', 'description': 'Ngày hết hạn CCCD - Chữ số thứ nhất', 'example': 'Nếu ngày hết hạn là 15/06/2035 → dhh1 = 1'},
        {'name': 'dhh2', 'description': 'Ngày hết hạn CCCD - Chữ số thứ hai', 'example': 'Nếu ngày hết hạn là 15/06/2035 → dhh2 = 5'},
        {'name': 'mhh1', 'description': 'Tháng hết hạn CCCD - Chữ số thứ nhất', 'example': 'Nếu ngày hết hạn là 15/06/2035 → mhh1 = 0'},
        {'name': 'mhh2', 'description': 'Tháng hết hạn CCCD - Chữ số thứ hai', 'example': 'Nếu ngày hết hạn là 15/06/2035 → mhh2 = 6'},
        {'name': 'yhh1', 'description': 'Năm hết hạn CCCD - Chữ số thứ nhất', 'example': 'Nếu ngày hết hạn là 15/06/2035 → yhh1 = 2'},
        {'name': 'yhh2', 'description': 'Năm hết hạn CCCD - Chữ số thứ hai', 'example': 'Nếu ngày hết hạn là 15/06/2035 → yhh2 = 0'},
        {'name': 'yhh3', 'description': 'Năm hết hạn CCCD - Chữ số thứ ba', 'example': 'Nếu ngày hết hạn là 15/06/2035 → yhh3 = 3'},
        {'name': 'yhh4', 'description': 'Năm hết hạn CCCD - Chữ số thứ tư', 'example': 'Nếu ngày hết hạn là 15/06/2035 → yhh4 = 5'},
        # Ngày trả thẻ
        {'name': 'dtt1', 'description': 'Ngày trả thẻ - Chữ số thứ nhất', 'example': 'Nếu ngày trả thẻ là 20/12/2024 → dtt1 = 2'},
        {'name': 'dtt2', 'description': 'Ngày trả thẻ - Chữ số thứ hai', 'example': 'Nếu ngày trả thẻ là 20/12/2024 → dtt2 = 0'},
        {'name': 'mtt1', 'description': 'Tháng trả thẻ - Chữ số thứ nhất', 'example': 'Nếu ngày trả thẻ là 20/12/2024 → mtt1 = 1'},
        {'name': 'mtt2', 'description': 'Tháng trả thẻ - Chữ số thứ hai', 'example': 'Nếu ngày trả thẻ là 20/12/2024 → mtt2 = 2'},
        {'name': 'ytt1', 'description': 'Năm trả thẻ - Chữ số thứ nhất', 'example': 'Nếu ngày trả thẻ là 20/12/2024 → ytt1 = 2'},
        {'name': 'ytt2', 'description': 'Năm trả thẻ - Chữ số thứ hai', 'example': 'Nếu ngày trả thẻ là 20/12/2024 → ytt2 = 0'},
        {'name': 'ytt3', 'description': 'Năm trả thẻ - Chữ số thứ ba', 'example': 'Nếu ngày trả thẻ là 20/12/2024 → ytt3 = 2'},
        {'name': 'ytt4', 'description': 'Năm trả thẻ - Chữ số thứ tư', 'example': 'Nếu ngày trả thẻ là 20/12/2024 → ytt4 = 4'},
        # Ngày trả thẻ tính (tự động = ngày in + 7 ngày)
        {'name': 'dttt1', 'description': 'Ngày trả thẻ tính - Chữ số thứ nhất', 'example': 'Nếu ngày in là 13/12/2024 → ngày trả thẻ tính = 20/12/2024 → dttt1 = 2'},
        {'name': 'dttt2', 'description': 'Ngày trả thẻ tính - Chữ số thứ hai', 'example': 'dttt2 = 0'},
        {'name': 'mttt1', 'description': 'Tháng trả thẻ tính - Chữ số thứ nhất', 'example': 'mttt1 = 1'},
        {'name': 'mttt2', 'description': 'Tháng trả thẻ tính - Chữ số thứ hai', 'example': 'mttt2 = 2'},
        {'name': 'yttt1', 'description': 'Năm trả thẻ tính - Chữ số thứ nhất', 'example': 'yttt1 = 2'},
        {'name': 'yttt2', 'description': 'Năm trả thẻ tính - Chữ số thứ hai', 'example': 'yttt2 = 0'},
        {'name': 'yttt3', 'description': 'Năm trả thẻ tính - Chữ số thứ ba', 'example': 'yttt3 = 2'},
        {'name': 'yttt4', 'description': 'Năm trả thẻ tính - Chữ số thứ tư', 'example': 'yttt4 = 4'},
    ]

    # 2.5. Biến điều kiện dịch vụ & Checkbox
    service_variables = [
        # Dịch vụ điều kiện
        {'name': 'so_tai_khoan_AP', 'description': 'Số tài khoản (chỉ khi chọn Agribank Plus mà không chọn SMS Banking)', 'example': '1234567890'},
        {'name': 'so_dien_thoai_AP', 'description': 'Số điện thoại (chỉ khi chọn Agribank Plus mà không chọn SMS Banking)', 'example': '0987654321'},
        {'name': 'so_tai_khoan_SMS', 'description': 'Số tài khoản (chỉ khi chọn SMS Banking mà không chọn Agribank Plus)', 'example': '1234567890'},
        {'name': 'so_dien_thoai_SMS', 'description': 'Số điện thoại (chỉ khi chọn SMS Banking mà không chọn Agribank Plus)', 'example': '0987654321'},

        # Hạng thẻ
        {'name': 'the_hang_chuan', 'description': 'Checkbox ☑/☐ khi chọn Hạng chuẩn', 'example': '☑ hoặc ☐'},
        {'name': 'the_hang_vang', 'description': 'Checkbox ☑/☐ khi chọn Hạng vàng', 'example': '☑ hoặc ☐'},
        {'name': 'the_hang_bach_kim', 'description': 'Checkbox ☑/☐ khi chọn Hạng bạch kim', 'example': '☑ hoặc ☐'},

        # Loại thẻ
        {'name': 'the_ghi_no_noi_dia', 'description': 'Checkbox ☑/☐ khi chọn Thẻ Ghi nợ nội địa', 'example': '☑ hoặc ☐'},
        {'name': 'the_ghi_no_quoc_te', 'description': 'Checkbox ☑/☐ khi chọn Thẻ Ghi nợ quốc tế', 'example': '☑ hoặc ☐'},
        {'name': 'the_tin_dung', 'description': 'Checkbox ☑/☐ khi chọn Thẻ tín dụng', 'example': '☑ hoặc ☐'},
        {'name': 'loai_the_visa', 'description': 'Checkbox ☑/☐ khi chọn thẻ Visa', 'example': '☑ hoặc ☐'},
        {'name': 'loai_the_mastercard', 'description': 'Checkbox ☑/☐ khi chọn thẻ Mastercard', 'example': '☑ hoặc ☐'},
        {'name': 'loai_the_jcb', 'description': 'Checkbox ☑/☐ khi chọn thẻ JCB', 'example': '☑ hoặc ☐'},
        {'name': 'loai_the_khac', 'description': 'Checkbox ☑/☐ khi chọn loại thẻ khác', 'example': '☑ hoặc ☐'},

        # Loại tài khoản
        {'name': 'tk_ngau_nhien', 'description': 'Checkbox ☑/☐ khi chọn Tài khoản ngẫu nhiên', 'example': '☑ hoặc ☐'},
        {'name': 'tk_theo_yeu_cau', 'description': 'Checkbox ☑/☐ khi chọn Tài khoản số theo yêu cầu', 'example': '☑ hoặc ☐'},
        {'name': 'tk_chuyen_dung', 'description': 'Checkbox ☑/☐ khi chọn Tài khoản chuyên dụng', 'example': '☑ hoặc ☐'},

        # Kết quả phân loại KH
        {'name': 'pl_cao', 'description': 'Checkbox ☑/☐ khi chọn Kết quả phân loại KH là Cao', 'example': '☑ hoặc ☐'},
        {'name': 'pl_trungbinh', 'description': 'Checkbox ☑/☐ khi chọn Kết quả phân loại KH là Trung bình', 'example': '☑ hoặc ☐'},
        {'name': 'pl_thap', 'description': 'Checkbox ☑/☐ khi chọn Kết quả phân loại KH là Thấp', 'example': '☑ hoặc ☐'},

        # Loại tiền
        {'name': 'loai_tien_vnd', 'description': 'Checkbox ☑/☐ khi chọn loại tiền VND', 'example': '☑ hoặc ☐'},
        {'name': 'loai_tien_usd', 'description': 'Checkbox ☑/☐ khi chọn loại tiền USD', 'example': '☑ hoặc ☐'},
        {'name': 'loai_tien_eur', 'description': 'Checkbox ☑/☐ khi chọn loại tiền EUR', 'example': '☑ hoặc ☐'},

        # Giới tính
        {'name': 'gioi_tinh_nam', 'description': 'Checkbox ☑/☐ khi chọn giới tính Nam', 'example': '☑ hoặc ☐'},
        {'name': 'gioi_tinh_nu', 'description': 'Checkbox ☑/☐ khi chọn giới tính Nữ', 'example': '☑ hoặc ☐'},

        # Loại giấy tờ tùy thân (CMND vs CCCD vs Căn cước)
        {'name': 'cmnd', 'description': 'Checkbox ☑/☐ tự động cho CMND 9 số', 'example': '☑ hoặc ☐'},
        {'name': 'cccd', 'description': 'Checkbox ☑/☐ tự động cho CCCD 12 số có ngày cấp ≤ 01/07/2024', 'example': '☑ hoặc ☐'},
        {'name': 'cancuoc', 'description': 'Checkbox ☑/☐ tự động cho CCCD 12 số có ngày cấp > 01/07/2024', 'example': '☑ hoặc ☐'},

        # Nghề nghiệp
        {'name': 'nghe_nghiep_cong_chuc', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Công chức viên chức', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_nong_dan', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Nông dân', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_giao_vien_bac_si', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Giáo viên/Bác sĩ', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_giao_vien', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Giáo viên', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_bac_si', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Bác sĩ', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_cong_nhan', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Công nhân', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_kinh_doanh', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Kinh doanh tự do', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_hoc_sinh_sinh_vien', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Học sinh/Sinh viên', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_noi_tro', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Nội trợ', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_cong_an_bo_doi', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Công an/Bộ đội', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_ky_su', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Kỹ sư', 'example': '☑ hoặc ☐'},
        {'name': 'nghe_nghiep_khac', 'description': 'Checkbox ☑/☐ khi chọn nghề nghiệp Khác', 'example': '☑ hoặc ☐'},

        # Dịch vụ ngân hàng điện tử
        {'name': 'dv_sms_banking', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ SMS Banking', 'example': '☑ hoặc ☐'},
        {'name': 'dv_bankplus', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Agribank Plus', 'example': '☑ hoặc ☐'},  # FIX: Correct description
        {'name': 'dv_e_mobile', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Liên kết ví (E-Wallet)', 'example': '☑ hoặc ☐'},  # FIX: Correct description
        {'name': 'dv_e_commerce', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ E-Commerce', 'example': '☑ hoặc ☐'},
        {'name': 'dv_soft_otp', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Soft OTP', 'example': '☑ hoặc ☐'},
        {'name': 'dv_smart_otp', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Smart OTP', 'example': '☑ hoặc ☐'},
        {'name': 'dv_retail_ebanking', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Retail eBanking', 'example': '☑ hoặc ☐'},
        {'name': 'dv_abic', 'description': 'Checkbox ☑/☐ khi khách hàng đăng ký dịch vụ ABIC', 'example': '☑ hoặc ☐'},

        # Dịch vụ thu hộ
        {'name': 'dv_thu_ho_tien_nuoc', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Thu hộ tiền nước', 'example': '☑ hoặc ☐'},
        {'name': 'dv_thu_ho_tien_dien', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Thu hộ tiền điện', 'example': '☑ hoặc ☐'},
        {'name': 'dv_thu_ho_vien_thong', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Thu hộ viễn thông', 'example': '☑ hoặc ☐'},
        {'name': 'dv_thu_ho_hoc_phi', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Thu hộ học phí', 'example': '☑ hoặc ☐'},
        {'name': 'dv_thu_ho_bao_hiem', 'description': 'Checkbox ☑/☐ khi chọn dịch vụ Thu hộ bảo hiểm', 'example': '☑ hoặc ☐'},

        # Kênh giao dịch
        {'name': 'kenh_mobile', 'description': 'Checkbox ☑/☐ khi chọn kênh giao dịch Mobile', 'example': '☑ hoặc ☐'},
        {'name': 'kenh_internet', 'description': 'Checkbox ☑/☐ khi chọn kênh giao dịch Internet', 'example': '☑ hoặc ☐'},

        # Phát hành thẻ
        {'name': 'phat_hanh_lan_dau', 'description': 'Checkbox ☑/☐ khi chọn phát hành lần đầu', 'example': '☑ hoặc ☐'},
        {'name': 'phat_hanh_lai', 'description': 'Checkbox ☑/☐ khi chọn phát hành lại', 'example': '☑ hoặc ☐'},

        # Loại thẻ bổ sung
        {'name': 'the_lap_nghiep', 'description': 'Checkbox ☑/☐ khi chọn thẻ lập nghiệp', 'example': '☑ hoặc ☐'},
        {'name': 'the_lien_ket', 'description': 'Checkbox ☑/☐ khi chọn thẻ liên kết', 'example': '☑ hoặc ☐'},
        {'name': 'the_dong_thuong_hieu', 'description': 'Checkbox ☑/☐ khi chọn thẻ đồng thương hiệu', 'example': '☑ hoặc ☐'},

        # Thông tin thẻ
        {'name': 'ten_the_1', 'description': 'Tên in trên thẻ 1 (toàn bộ chuỗi)', 'example': 'NGUYEN VAN A'},
        {'name': 'ten_the_2', 'description': 'Tên in trên thẻ 2 (toàn bộ chuỗi)', 'example': 'NGUYEN VAN A'},

        # Biến ký tự riêng lẻ cho tên thẻ (dùng trong table Word)
        {'name': 'tt1_1 đến tt1_26', 'description': 'Từng ký tự của ten_the_1 (ô 1 đến ô 26). Dùng {{ tt1_1 }}, {{ tt1_2 }}, ..., {{ tt1_26 }} để chèn từng chữ vào từng ô table', 'example': 'tt1_1="N", tt1_2="G", tt1_3="U", ...'},
        {'name': 'tt2_1 đến tt2_26', 'description': 'Từng ký tự của ten_the_2 (ô 1 đến ô 26). Dùng {{ tt2_1 }}, {{ tt2_2 }}, ..., {{ tt2_26 }} để chèn từng chữ vào từng ô table', 'example': 'tt2_1="N", tt2_2="G", tt2_3="U", ...'},

        # Biến tài khoản điều kiện
        {'name': 'stk_theo_yeu_cau', 'description': 'Số tài khoản (chỉ hiển thị khi chọn "Tài khoản số theo yêu cầu")', 'example': '1234567890'},

        # Ngày tính toán
        {'name': 'ngay_tra_the_tinh', 'description': 'Ngày trả thẻ (tự động tính = ngày in + 7 ngày)', 'example': '15/12/2024'},
    ]

    # 3. Biến Chi nhánh - From GlobalConfig
    branch_variables = [
        {'name': 'ten_chi_nhanh', 'description': 'Tên chi nhánh', 'example': 'Chi nhánh Giá Rai Bạc Liêu'},
        {'name': 'ten_chi_nhanh_hoa', 'description': 'Tên chi nhánh (IN HOA)', 'example': 'CHI NHÁNH GIÁ RAI BẠC LIÊU'},
        {'name': 'mst', 'description': 'Mã số thuế', 'example': '0123456789'},
        {'name': 'giao_dich_vien', 'description': 'Họ tên giao dịch viên', 'example': 'Nguyễn Văn A'},
        {'name': 'kiem_soat_vien', 'description': 'Họ tên kiểm soát viên', 'example': 'Trần Thị B'},
        {'name': 'giam_doc', 'description': 'Họ tên giám đốc chi nhánh', 'example': 'Lê Văn C'},
        {'name': 'dia_chi_chi_nhanh', 'description': 'Địa chỉ chi nhánh', 'example': 'Số 123 Đường ABC, Phường XYZ'},
    ]

    # 3.5. Biến Auto-Calculation (Date objects & special variables)
    calc_variables = [
        {'name': 'ngay_hien_tai_obj', 'description': 'Ngày hiện tại (Date object) - Tự động thêm vào mọi template', 'example': 'Dùng cho tính toán: {% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai_obj) %}'},
        {'name': 'ngay_sinh_obj', 'description': 'Ngày sinh dạng Date object - Dùng cho tính toán tuổi', 'example': 'Tính tuổi: {{ ngay_sinh_obj|date_diff_years(ngay_hien_tai_obj) }}'},
        {'name': 'ngay_cap_cmnd_obj', 'description': 'Ngày cấp CCCD dạng Date object - Dùng cho tính toán', 'example': 'Tính số năm đã cấp: {{ ngay_cap_cmnd_obj|date_diff_years(ngay_hien_tai_obj) }}'},
        {'name': 'ngay_het_han_cmnd_obj', 'description': 'Ngày hết hạn CCCD dạng Date object - Dùng cho tính toán', 'example': 'Tính số ngày còn lại: {{ ngay_het_han_cmnd_obj|date_diff_days(ngay_hien_tai_obj) }}'},
        {'name': 'ngay_in_obj', 'description': 'Ngày in dạng Date object - Dùng cho tính toán', 'example': 'Dùng trong calculations'},
    ]

    # 3.6. Jinja2 Filters & Functions
    jinja_filters = [
        {'name': 'number_format', 'description': 'Format số tiền theo định dạng VN (thêm dấu phẩy)', 'example': '{{ 165000|number_format }} → 165,000'},
        {'name': 'date_diff_years', 'description': 'Tính số năm giữa 2 ngày', 'example': '{% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai_obj) %}'},
        {'name': 'date_diff_days', 'description': 'Tính số ngày giữa 2 ngày', 'example': '{% set ngay_con_lai = ngay_het_han_cmnd_obj|date_diff_days(ngay_hien_tai_obj) %}'},
        {'name': 'round', 'description': 'Làm tròn số (built-in Jinja2)', 'example': '{{ 2.567|round(2) }} → 2.57'},
        {'name': 'abs', 'description': 'Giá trị tuyệt đối (built-in Jinja2)', 'example': '{{ -5|abs }} → 5'},
        {'name': 'length', 'description': 'Độ dài danh sách/chuỗi (built-in Jinja2)', 'example': '{% if danh_sach|length > 0 %}'},
    ]

    # 3.7. Jinja2 Syntax Examples
    jinja_syntax = [
        {'name': 'if/else', 'description': 'Điều kiện if/else', 'example': '{% if tuoi >= 15 %}Đủ điều kiện{% else %}Chưa đủ{% endif %}'},
        {'name': 'set', 'description': 'Gán biến', 'example': '{% set tuoi = ngay_sinh_obj|date_diff_years(ngay_hien_tai) %}'},
        {'name': 'for loop', 'description': 'Vòng lặp', 'example': '{% for item in danh_sach %}{{ item }}{% endfor %}'},
        {'name': 'comment', 'description': 'Ghi chú (không hiển thị)', 'example': '{# Đây là comment #}'},
        {'name': 'toán tử', 'description': 'Các phép toán: +, -, *, /, %', 'example': '{% set tong = phi_1 + phi_2 %}'},
        {'name': 'so sánh', 'description': 'So sánh: ==, !=, <, >, <=, >=', 'example': '{% if tuoi >= 15 %}'},
        {'name': 'logic', 'description': 'Logic: and, or, not', 'example': '{% if tuoi >= 15 and cccd_con_han %}'},
    ]

    # 4. Biến Tùy chỉnh - From GlobalConfig.custom_variables
    config = GlobalConfig.get_instance()
    custom_variables = []
    if config.custom_variables:
        for var_name, var_value in config.custom_variables.items():
            custom_variables.append({
                'name': var_name,
                'description': 'Biến tùy chỉnh',
                'example': var_value[:100] if var_value else ''  # Limit example length
            })

    context = {
        'customer_variables': customer_variables,
        'date_variables': date_variables,
        'service_variables': service_variables,
        'calc_variables': calc_variables,
        'jinja_filters': jinja_filters,
        'jinja_syntax': jinja_syntax,
        'branch_variables': branch_variables,
        'custom_variables': custom_variables,
    }

    return render(request, 'templates_app/variable_library.html', context)


# New Dashboard API endpoints
@login_required
@require_http_methods(["GET"])
def category_templates_api(request, category_id):
    """
    API trả về danh sách templates và visible_field_groups của category
    """
    try:
        category = Category.objects.get(pk=category_id)

        # Get templates trong category (có quyền truy cập)
        user = request.user
        if user.is_superuser:
            templates = category.templates.filter(is_active=True)
        else:
            user_groups = user.groups.all()
            templates = category.templates.filter(
                is_active=True
            ).filter(
                Q(allowed_groups__isnull=True) |
                Q(allowed_groups__in=user_groups)
            ).distinct()

        templates_data = [{
            'id': t.id,
            'name': t.name,
            'description': t.description
        } for t in templates]

        return JsonResponse({
            'success': True,
            'templates': templates_data,
            'visible_field_groups': category.get_visible_field_groups()
        })
    except Category.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Category not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def generate_document_direct(request, template_id):
    """
    Generate document trực tiếp từ form data
    Nếu có customer_id trong POST data, sẽ cập nhật thông tin khách hàng trước khi tạo document
    """
    try:
        template = get_object_or_404(Template, pk=template_id)

        # Kiểm tra quyền
        if not template.user_has_access(request.user):
            return HttpResponse("Không có quyền truy cập", status=403)

        # Lấy GlobalConfig
        config = GlobalConfig.get_instance()

        # Build data dict from form
        data = {}

        # Personal info
        data['ma_khach_hang'] = request.POST.get('ma_khach_hang', '')
        data['cif'] = data['ma_khach_hang']  # CIF = Mã khách hàng (for backward compatibility)
        data['ho_ten'] = request.POST.get('ho_ten', '')
        data['ho_ten_tieng_anh'] = request.POST.get('ho_ten_tieng_anh', '')
        # Auto-generate ten_tieng_anh from ho_ten (remove diacritics and uppercase)
        data['ten_tieng_anh'] = remove_vietnamese_diacritics(data['ho_ten'])

        # FIX: Auto-fill card name source for ten_the_1 and ten_the_2
        # Priority: ho_ten_tieng_anh (manual) > ten_tieng_anh (auto-generated)
        card_name_source = data['ho_ten_tieng_anh'] if data['ho_ten_tieng_anh'] else data['ten_tieng_anh']

        data['ngay_sinh'] = request.POST.get('ngay_sinh', '')
        data['gioi_tinh'] = request.POST.get('gioi_tinh', '')

        # ID documents
        data['so_cmnd'] = request.POST.get('so_cmnd', '')
        data['ngay_cap_cmnd'] = request.POST.get('ngay_cap_cmnd', '')
        data['ngay_het_han_cmnd'] = request.POST.get('ngay_het_han_cmnd', '')
        data['noi_cap_cmnd'] = request.POST.get('noi_cap_cmnd', '')

        # Contact
        data['dia_chi'] = request.POST.get('dia_chi', '')
        data['so_dien_thoai'] = request.POST.get('so_dien_thoai', '')
        data['email'] = request.POST.get('email', '')

        # Employment
        data['nghe_nghiep'] = request.POST.get('nghe_nghiep', '')
        data['noi_lam_viec'] = request.POST.get('noi_lam_viec', '')

        # Customer Classification - FIX: Thêm phân loại khách hàng
        data['ket_qua_phan_loai_kh'] = request.POST.get('ket_qua_phan_loai_kh', '')

        # Banking
        data['so_tai_khoan'] = request.POST.get('so_tai_khoan', '')
        data['loai_tai_khoan'] = request.POST.get('loai_tai_khoan', '')
        data['so_tai_khoan_yc'] = request.POST.get('so_tai_khoan_yc', '')
        data['loai_tien_te'] = request.POST.get('loai_tien_te', 'VND')

        # Card
        data['loai_the'] = request.POST.get('loai_the', '')
        data['hang_the'] = request.POST.get('hang_the', '')
        # FIX: Auto-fill ten_the_1 and ten_the_2 from card_name_source (ten_tieng_anh)
        data['ten_the_1'] = card_name_source  # For first card name table
        data['ten_the_2'] = card_name_source  # For second card name table

        # FIX: Create individual character variables for ten_the_1 and ten_the_2
        # So users can use {{ tt1_1 }}, {{ tt1_2 }}, ... {{ tt1_26 }} in Word template
        # tt1 = ten_the_1, tt2 = ten_the_2, support up to 26 characters
        for i in range(26):
            if i < len(data['ten_the_1']):
                data[f'tt1_{i+1}'] = data['ten_the_1'][i]
            else:
                data[f'tt1_{i+1}'] = ''

            if i < len(data['ten_the_2']):
                data[f'tt2_{i+1}'] = data['ten_the_2'][i]
            else:
                data[f'tt2_{i+1}'] = ''

        data['ngay_tra_the'] = request.POST.get('ngay_tra_the', '')

        # Checkboxes - helper function
        def checkbox(value):
            return '☑' if value else '☐'

        data['phat_hanh_lan_dau'] = checkbox(request.POST.get('phat_hanh_lan_dau') == 'on')
        data['phat_hanh_lai'] = checkbox(request.POST.get('phat_hanh_lai') == 'on')

        # Service checkboxes - Dịch vụ ngân hàng điện tử
        data['dv_sms_banking'] = checkbox(request.POST.get('dv_sms_banking') == 'on')
        data['dv_bankplus'] = checkbox(request.POST.get('dv_bankplus') == 'on')
        data['dv_e_mobile'] = checkbox(request.POST.get('dv_e_mobile') == 'on')
        data['dv_e_commerce'] = checkbox(request.POST.get('dv_e_commerce') == 'on')
        data['dv_soft_otp'] = checkbox(request.POST.get('dv_soft_otp') == 'on')
        data['dv_smart_otp'] = checkbox(request.POST.get('dv_smart_otp') == 'on')
        data['dv_retail_ebanking'] = checkbox(request.POST.get('dv_retail_ebanking') == 'on')
        data['dv_abic'] = checkbox(request.POST.get('dv_abic') == 'on')  # FIX: Thêm dv_abic

        # Service checkboxes - Dịch vụ thu hộ
        data['dv_thu_ho_tien_nuoc'] = checkbox(request.POST.get('dv_thu_ho_tien_nuoc') == 'on')
        data['dv_thu_ho_tien_dien'] = checkbox(request.POST.get('dv_thu_ho_tien_dien') == 'on')
        data['dv_thu_ho_vien_thong'] = checkbox(request.POST.get('dv_thu_ho_vien_thong') == 'on')
        data['dv_thu_ho_hoc_phi'] = checkbox(request.POST.get('dv_thu_ho_hoc_phi') == 'on')
        data['dv_thu_ho_bao_hiem'] = checkbox(request.POST.get('dv_thu_ho_bao_hiem') == 'on')

        # Service checkboxes - Kênh giao dịch
        data['kenh_mobile'] = checkbox(request.POST.get('kenh_mobile') == 'on')
        data['kenh_internet'] = checkbox(request.POST.get('kenh_internet') == 'on')

        # Checkbox - Giới tính
        data['gioi_tinh_nam'] = checkbox(data['gioi_tinh'] == 'Nam')
        data['gioi_tinh_nu'] = checkbox(data['gioi_tinh'] == 'Nữ')

        # Checkbox - Nghề nghiệp
        nghe_nghiep = data.get('nghe_nghiep', '')

        data['nghe_nghiep_cong_chuc'] = checkbox(nghe_nghiep == 'Công chức viên chức')
        data['nghe_nghiep_nong_dan'] = checkbox(nghe_nghiep == 'Nông dân')
        data['nghe_nghiep_giao_vien_bac_si'] = checkbox(nghe_nghiep == 'Giáo viên/Bác Sĩ')
        data['nghe_nghiep_giao_vien'] = checkbox(nghe_nghiep == 'Giáo viên')  # FIX: Thêm riêng lẻ
        data['nghe_nghiep_bac_si'] = checkbox(nghe_nghiep == 'Bác sĩ')  # FIX: Thêm riêng lẻ
        data['nghe_nghiep_cong_nhan'] = checkbox(nghe_nghiep == 'Công nhân')
        data['nghe_nghiep_kinh_doanh'] = checkbox(nghe_nghiep == 'Kinh doanh tự do')
        data['nghe_nghiep_hoc_sinh_sinh_vien'] = checkbox(nghe_nghiep == 'Học sinh/Sinh viên')
        data['nghe_nghiep_noi_tro'] = checkbox(nghe_nghiep == 'Nội trợ')
        data['nghe_nghiep_cong_an_bo_doi'] = checkbox(nghe_nghiep == 'Công an/Bộ đội')  # FIX: Thêm nghề thiếu
        data['nghe_nghiep_ky_su'] = checkbox(nghe_nghiep == 'Kỹ sư')  # FIX: Thêm nghề thiếu
        data['nghe_nghiep_khac'] = checkbox(nghe_nghiep == 'Khác')

        # Checkbox - Hạng thẻ
        data['the_hang_chuan'] = checkbox(data['hang_the'] == 'Hạng chuẩn')
        data['the_hang_vang'] = checkbox(data['hang_the'] == 'Hạng vàng')
        data['the_hang_bach_kim'] = checkbox(data['hang_the'] == 'Hạng bạch kim')

        # Checkbox - Loại thẻ
        data['the_ghi_no_noi_dia'] = checkbox(data['loai_the'] == 'Thẻ Ghi nợ nội địa')
        data['the_ghi_no_quoc_te'] = checkbox(data['loai_the'] == 'Thẻ Ghi nợ quốc tế')
        data['the_tin_dung'] = checkbox(data['loai_the'] == 'Thẻ tín dụng')
        data['loai_the_jcb'] = checkbox(data['loai_the'] == 'Thẻ JCB')
        data['loai_the_visa'] = checkbox(data['loai_the'] == 'Thẻ Visa')
        data['loai_the_mastercard'] = checkbox(data['loai_the'] == 'Thẻ MasterCard')
        data['loai_the_khac'] = checkbox(data['loai_the'] not in ['Thẻ Ghi nợ nội địa', 'Thẻ Ghi nợ quốc tế', 'Thẻ tín dụng', 'Thẻ JCB', 'Thẻ Visa', 'Thẻ MasterCard', 'The Plus Success', 'Agribank Debit Card'])

        # Checkbox - Loại tiền
        data['loai_tien_vnd'] = checkbox(data['loai_tien_te'] == 'VND')
        data['loai_tien_usd'] = checkbox(data['loai_tien_te'] == 'USD')
        data['loai_tien_eur'] = checkbox(data['loai_tien_te'] == 'EUR')

        # Checkbox - Loại tài khoản
        data['tk_ngau_nhien'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản ngẫu nhiên')
        data['tk_theo_yeu_cau'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản số theo yêu cầu')
        data['tk_chuyen_dung'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản chuyên dụng')

        # FIX: If "Tài khoản ngẫu nhiên" selected, set so_tai_khoan_yc to dots
        if data.get('loai_tai_khoan') == 'Tài khoản ngẫu nhiên':
            data['so_tai_khoan_yc'] = '.................'

        # Checkbox - Kết quả phân loại KH
        ket_qua_phan_loai_kh = data.get('ket_qua_phan_loai_kh', '')
        data['pl_cao'] = checkbox(ket_qua_phan_loai_kh == 'Cao')
        data['pl_trungbinh'] = checkbox(ket_qua_phan_loai_kh == 'Trung bình')
        data['pl_thap'] = checkbox(ket_qua_phan_loai_kh == 'Thấp')

        # Tiền gửi tiết kiệm chung - Thông tin người gửi tiền thứ hai
        data['ho_ten_nguoi_gui_2'] = request.POST.get('ho_ten_nguoi_gui_2', '')
        data['so_cmnd_nguoi_gui_2'] = request.POST.get('so_cmnd_nguoi_gui_2', '')
        data['noi_cap_cmnd_nguoi_gui_2'] = request.POST.get('noi_cap_cmnd_nguoi_gui_2', '')
        data['dia_chi_nguoi_gui_2'] = request.POST.get('dia_chi_nguoi_gui_2', '')
        data['sdt_nguoi_gui_2'] = request.POST.get('sdt_nguoi_gui_2', '')

        # Ngày cấp CMND người gửi 2 - format date
        ngay_cap_cmnd_nguoi_gui_2_str = request.POST.get('ngay_cap_cmnd_nguoi_gui_2', '')
        if ngay_cap_cmnd_nguoi_gui_2_str:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(ngay_cap_cmnd_nguoi_gui_2_str, '%Y-%m-%d')
                data['ngay_cap_cmnd_nguoi_gui_2'] = date_obj.strftime('%d/%m/%Y')
            except ValueError:
                data['ngay_cap_cmnd_nguoi_gui_2'] = ngay_cap_cmnd_nguoi_gui_2_str
        else:
            data['ngay_cap_cmnd_nguoi_gui_2'] = ''

        # Tiền gửi tiết kiệm chung - Giao dịch thẻ tiết kiệm (Text: "Có" hoặc "Không")
        data['gd_rut_lai_tat_ca'] = 'Có' if request.POST.get('gd_rut_lai_tat_ca') == 'on' else 'Không'
        data['gd_rut_lai_mot_so'] = 'Có' if request.POST.get('gd_rut_lai_mot_so') == 'on' else 'Không'
        data['gd_tat_toan_tat_ca'] = 'Có' if request.POST.get('gd_tat_toan_tat_ca') == 'on' else 'Không'
        data['gd_tat_toan_mot_so'] = 'Có' if request.POST.get('gd_tat_toan_mot_so') == 'on' else 'Không'
        data['gd_bao_mat_tat_ca'] = 'Có' if request.POST.get('gd_bao_mat_tat_ca') == 'on' else 'Không'
        data['gd_bao_mat_mot_so'] = 'Có' if request.POST.get('gd_bao_mat_mot_so') == 'on' else 'Không'
        data['gd_bao_hong_tat_ca'] = 'Có' if request.POST.get('gd_bao_hong_tat_ca') == 'on' else 'Không'
        data['gd_bao_hong_mot_so'] = 'Có' if request.POST.get('gd_bao_hong_mot_so') == 'on' else 'Không'
        data['gd_phong_toa_tat_ca'] = 'Có' if request.POST.get('gd_phong_toa_tat_ca') == 'on' else 'Không'
        data['gd_phong_toa_mot_so'] = 'Có' if request.POST.get('gd_phong_toa_mot_so') == 'on' else 'Không'
        data['gd_xac_nhan_so_du_tat_ca'] = 'Có' if request.POST.get('gd_xac_nhan_so_du_tat_ca') == 'on' else 'Không'
        data['gd_xac_nhan_so_du_mot_so'] = 'Có' if request.POST.get('gd_xac_nhan_so_du_mot_so') == 'on' else 'Không'

        # Ngoại tệ - Nhận tiền nước ngoài
        data['quan_he_nguoi_gui_nhan'] = request.POST.get('quan_he_nguoi_gui_nhan', '')
        data['muc_dich_giao_dich'] = request.POST.get('muc_dich_giao_dich', '')
        data['ho_ten_nguoi_gui_tien'] = request.POST.get('ho_ten_nguoi_gui_tien', '')
        data['quoc_gia_gui_tien'] = request.POST.get('quoc_gia_gui_tien', '')
        data['ma_so_nhan_tien'] = request.POST.get('ma_so_nhan_tien', '')
        data['so_tien_ngoai_te'] = request.POST.get('so_tien_ngoai_te', '')
        data['loai_tien_ngoai_te'] = request.POST.get('loai_tien_ngoai_te', '')

        # FIX: Checkbox - CMND/CCCD/CĂN CƯỚC based on digit length and issue date
        # - 9 digits = CMND
        # - 12 digits + issue date ≤ 01/07/2024 = CCCD
        # - 12 digits + issue date > 01/07/2024 = CĂN CƯỚC
        so_cmnd = data.get('so_cmnd', '').strip()
        ngay_cap_cmnd_str = data.get('ngay_cap_cmnd', '')

        # Default all to unchecked
        data['cmnd'] = checkbox(False)
        data['cccd'] = checkbox(False)
        data['cancuoc'] = checkbox(False)

        if len(so_cmnd) == 9:
            # 9 digits = CMND (old ID card)
            data['cmnd'] = checkbox(True)
        elif len(so_cmnd) == 12 and ngay_cap_cmnd_str:
            # 12 digits = CCCD or CĂN CƯỚC, depends on issue date
            try:
                from datetime import datetime, date
                # Parse ngay_cap_cmnd (already in 'DD/MM/YYYY' format from earlier processing)
                if '/' in ngay_cap_cmnd_str:
                    ngay_cap_obj = datetime.strptime(ngay_cap_cmnd_str, '%d/%m/%Y').date()
                else:
                    # If still in YYYY-MM-DD format
                    ngay_cap_obj = datetime.strptime(ngay_cap_cmnd_str, '%Y-%m-%d').date()

                cutoff_date = date(2024, 7, 1)
                if ngay_cap_obj <= cutoff_date:
                    data['cccd'] = checkbox(True)  # Old CCCD
                else:
                    data['cancuoc'] = checkbox(True)  # New CĂN CƯỚC
            except (ValueError, TypeError):
                # If date parsing fails, default to CCCD for 12-digit numbers
                data['cccd'] = checkbox(True)

        # Note: Card name (tên trên thẻ) is auto-filled into tables
        # by _render_card_name_tables() in utils.py
        # No need to generate individual character variables

        # Print info
        ngay_in_str = request.POST.get('ngay_in', '')
        if ngay_in_str:
            try:
                from datetime import datetime, timedelta
                # 1. Parse chuỗi 'YYYY-MM-DD' từ form
                date_obj = datetime.strptime(ngay_in_str, '%Y-%m-%d')

                # 2. Định dạng lại thành 'DD/MM/YYYY'
                formatted_date = date_obj.strftime('%d/%m/%Y')

                # 3. Gán vào cả 'ngay_in' và 'ngay_lap' (vì template Mau_1a.docx dùng 'ngay_lap')
                data['ngay_in'] = formatted_date
                data['ngay_lap'] = formatted_date

                # 4. FIX: Tính ngay_tra_the_tinh = ngay_in + 7 ngày
                ngay_tra_the_calculated = date_obj + timedelta(days=7)
                data['ngay_tra_the_tinh'] = ngay_tra_the_calculated.strftime('%d/%m/%Y')
                data['ngay_tra_the_tinh_obj'] = ngay_tra_the_calculated.date()

                # Add individual digit variables for ngay_tra_the_tinh (dttt1, mttt1, yttt1, etc.)
                date_str = ngay_tra_the_calculated.strftime('%d%m%Y')
                if len(date_str) == 8:
                    data['dttt1'] = date_str[0]
                    data['dttt2'] = date_str[1]
                    data['mttt1'] = date_str[2]
                    data['mttt2'] = date_str[3]
                    data['yttt1'] = date_str[4]
                    data['yttt2'] = date_str[5]
                    data['yttt3'] = date_str[6]
                    data['yttt4'] = date_str[7]
            except ValueError:
                # Nếu có lỗi, dùng giá trị gốc
                data['ngay_in'] = ngay_in_str
                data['ngay_lap'] = ngay_in_str
                data['ngay_tra_the_tinh'] = ''
                data['ngay_tra_the_tinh_obj'] = None
        else:
            data['ngay_in'] = ''
            data['ngay_lap'] = ''
            data['ngay_tra_the_tinh'] = ''
            data['ngay_tra_the_tinh_obj'] = None

        # Date variables (from ngay_sinh)
        if data['ngay_sinh']:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['ngay_sinh'], '%Y-%m-%d')
                # Store both formatted string and date object
                data['ngay_sinh'] = date_obj.strftime('%d/%m/%Y')
                data['ngay_sinh_obj'] = date_obj.date()  # Date object for Jinja2 calculations
                date_str = date_obj.strftime('%d%m%Y')
                data['d1'], data['d2'] = date_str[0], date_str[1]
                data['m1'], data['m2'] = date_str[2], date_str[3]
                data['y1'], data['y2'], data['y3'], data['y4'] = date_str[4], date_str[5], date_str[6], date_str[7]
            except (ValueError, TypeError) as e:
                # Invalid date format or type - set to None to avoid errors
                data['ngay_sinh_obj'] = None

        # Date variables (from ngay_cap_cmnd)
        if data['ngay_cap_cmnd']:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['ngay_cap_cmnd'], '%Y-%m-%d')
                # Store both formatted string and date object
                data['ngay_cap_cmnd'] = date_obj.strftime('%d/%m/%Y')
                data['ngay_cap_cmnd_obj'] = date_obj.date()  # Date object for Jinja2 calculations
                date_str = date_obj.strftime('%d%m%Y')
                data['dcc1'], data['dcc2'] = date_str[0], date_str[1]
                data['mcc1'], data['mcc2'] = date_str[2], date_str[3]
                data['ycc1'], data['ycc2'], data['ycc3'], data['ycc4'] = date_str[4], date_str[5], date_str[6], date_str[7]
            except (ValueError, TypeError) as e:
                # Invalid date format or type - set to None to avoid errors
                data['ngay_cap_cmnd_obj'] = None

        # Date variables (from ngay_het_han_cmnd)
        if data['ngay_het_han_cmnd']:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['ngay_het_han_cmnd'], '%Y-%m-%d')
                # Store both formatted string and date object
                data['ngay_het_han_cmnd'] = date_obj.strftime('%d/%m/%Y')
                data['ngay_het_han_cmnd_obj'] = date_obj.date()  # Date object for Jinja2 calculations
                date_str = date_obj.strftime('%d%m%Y')
                data['dhh1'], data['dhh2'] = date_str[0], date_str[1]
                data['mhh1'], data['mhh2'] = date_str[2], date_str[3]
                data['yhh1'], data['yhh2'], data['yhh3'], data['yhh4'] = date_str[4], date_str[5], date_str[6], date_str[7]
            except (ValueError, TypeError) as e:
                # Invalid date format or type - set to None to avoid errors
                data['ngay_het_han_cmnd_obj'] = None

        # Ngày hiện tại cho tính toán (Date object)
        from datetime import datetime
        data['ngay_hien_tai_obj'] = datetime.now().date()  # Date object for calculations

        # Service-specific account and phone logic
        # If Agribank Plus is selected but NOT SMS Banking
        if data['dv_bankplus'] == '☑' and data['dv_sms_banking'] == '☐':
            data['so_tai_khoan_AP'] = data['so_tai_khoan']
            data['so_dien_thoai_AP'] = data['so_dien_thoai']
        else:
            data['so_tai_khoan_AP'] = ''
            data['so_dien_thoai_AP'] = ''

        # If SMS Banking is selected but NOT Agribank Plus
        if data['dv_sms_banking'] == '☑' and data['dv_bankplus'] == '☐':
            data['so_tai_khoan_SMS'] = data['so_tai_khoan']
            data['so_dien_thoai_SMS'] = data['so_dien_thoai']
        else:
            data['so_tai_khoan_SMS'] = ''
            data['so_dien_thoai_SMS'] = ''

        # Check if this is updating an existing customer
        customer_id = request.POST.get('customer_id', '').strip()
        if customer_id:
            try:
                customer = Customer.objects.get(pk=int(customer_id))

                # Update customer fields from form data
                customer.ma_khach_hang = data.get('ma_khach_hang', '')
                customer.ho_ten = data.get('ho_ten', '')
                customer.ho_ten_tieng_anh = data.get('ho_ten_tieng_anh', '')

                # Parse and update dates
                if data.get('ngay_sinh'):
                    try:
                        from datetime import datetime
                        customer.ngay_sinh = datetime.strptime(data['ngay_sinh'], '%d/%m/%Y').date()
                    except (ValueError, TypeError):
                        # Invalid date format - skip update
                        pass

                if data.get('ngay_cap_cmnd'):
                    try:
                        from datetime import datetime
                        customer.ngay_cap_cmnd = datetime.strptime(data['ngay_cap_cmnd'], '%d/%m/%Y').date()
                    except (ValueError, TypeError):
                        # Invalid date format - skip update
                        pass

                if data.get('ngay_het_han_cmnd'):
                    try:
                        from datetime import datetime
                        customer.ngay_het_han_cmnd = datetime.strptime(data['ngay_het_han_cmnd'], '%d/%m/%Y').date()
                    except (ValueError, TypeError):
                        # Invalid date format - skip update
                        pass

                customer.gioi_tinh = data.get('gioi_tinh', '')
                customer.dan_toc = data.get('dan_toc', '')
                customer.so_cmnd = data.get('so_cmnd', '')
                customer.noi_cap_cmnd = data.get('noi_cap_cmnd', '')
                customer.dia_chi = data.get('dia_chi', '')
                customer.ho_khau = data.get('ho_khau', '')
                customer.so_dien_thoai = data.get('so_dien_thoai', '')
                customer.email = data.get('email', '')
                customer.nghe_nghiep = data.get('nghe_nghiep', '')
                customer.noi_lam_viec = data.get('noi_lam_viec', '')
                customer.so_tai_khoan = data.get('so_tai_khoan', '')
                customer.loai_tai_khoan = data.get('loai_tai_khoan', '')
                customer.so_tai_khoan_yc = data.get('so_tai_khoan_yc', '')
                customer.loai_tien_te = data.get('loai_tien_te', 'VND')
                customer.loai_the = data.get('loai_the', '')
                customer.hang_the = data.get('hang_the', '')
                customer.so_the_atm = data.get('so_the_atm', '')
                customer.ten_the_1 = (data.get('ten_the_1', '') or '').strip()

                # Update service checkboxes (convert from ☑/☐ back to boolean)
                customer.phat_hanh_lan_dau = (request.POST.get('phat_hanh_lan_dau') == 'on')
                customer.phat_hanh_lai = (request.POST.get('phat_hanh_lai') == 'on')
                customer.dv_sms_banking = (request.POST.get('dv_sms_banking') == 'on')
                customer.dv_bankplus = (request.POST.get('dv_bankplus') == 'on')
                customer.dv_e_mobile = (request.POST.get('dv_e_mobile') == 'on')
                customer.dv_e_commerce = (request.POST.get('dv_e_commerce') == 'on')
                customer.dv_soft_otp = (request.POST.get('dv_soft_otp') == 'on')
                customer.dv_smart_otp = (request.POST.get('dv_smart_otp') == 'on')
                customer.dv_retail_ebanking = (request.POST.get('dv_retail_ebanking') == 'on')
                customer.dv_thu_ho_tien_nuoc = (request.POST.get('dv_thu_ho_tien_nuoc') == 'on')
                customer.dv_thu_ho_tien_dien = (request.POST.get('dv_thu_ho_tien_dien') == 'on')
                customer.dv_thu_ho_vien_thong = (request.POST.get('dv_thu_ho_vien_thong') == 'on')
                customer.dv_thu_ho_hoc_phi = (request.POST.get('dv_thu_ho_hoc_phi') == 'on')
                customer.dv_thu_ho_bao_hiem = (request.POST.get('dv_thu_ho_bao_hiem') == 'on')
                customer.dv_abic = (request.POST.get('dv_abic') == 'on')
                customer.kenh_mobile = (request.POST.get('kenh_mobile') == 'on')
                customer.kenh_internet = (request.POST.get('kenh_internet') == 'on')
                customer.the_lap_nghiep = (request.POST.get('the_lap_nghiep') == 'on')
                customer.the_lien_ket = (request.POST.get('the_lien_ket') == 'on')
                customer.the_dong_thuong_hieu = (request.POST.get('the_dong_thuong_hieu') == 'on')

                # Update kết quả phân loại KH
                customer.ket_qua_phan_loai_kh = data.get('ket_qua_phan_loai_kh', '')

                # Save updated customer
                customer.save()

            except Customer.DoesNotExist:
                pass  # Customer not found, generate document without saving
            except Exception as e:
                pass  # Failed to update customer, continue with document generation
        else:
            # No customer_id provided - this is a new customer
            # Create new customer from form data
            try:
                from datetime import datetime

                # Prepare customer data
                customer_data = {
                    'ma_khach_hang': data.get('ma_khach_hang', ''),
                    'ho_ten': data.get('ho_ten', ''),
                    'ho_ten_tieng_anh': data.get('ho_ten_tieng_anh', ''),
                    'gioi_tinh': data.get('gioi_tinh', 'Nam'),
                    'dan_toc': data.get('dan_toc', 'Kinh'),
                    'so_cmnd': data.get('so_cmnd', ''),
                    'noi_cap_cmnd': data.get('noi_cap_cmnd', 'Cục CSQLHC về TTXH'),
                    'dia_chi': data.get('dia_chi', ''),
                    'ho_khau': data.get('ho_khau', ''),
                    'so_dien_thoai': data.get('so_dien_thoai', ''),
                    'email': data.get('email', ''),
                    'nghe_nghiep': data.get('nghe_nghiep', ''),
                    'noi_lam_viec': data.get('noi_lam_viec', ''),
                    'so_tai_khoan': data.get('so_tai_khoan', ''),
                    'loai_tai_khoan': data.get('loai_tai_khoan', ''),
                    'so_tai_khoan_yc': data.get('so_tai_khoan_yc', ''),
                    'loai_tien_te': data.get('loai_tien_te', 'VND'),
                    'loai_the': data.get('loai_the', ''),
                    'hang_the': data.get('hang_the', ''),
                    'so_the_atm': data.get('so_the_atm', ''),
                    'ten_the_1': (data.get('ten_the_1', '') or '').strip(),
                    'ket_qua_phan_loai_kh': data.get('ket_qua_phan_loai_kh', ''),
                    'created_by': request.user,

                    # Service checkboxes (convert from ☑/☐ to boolean)
                    'phat_hanh_lan_dau': (request.POST.get('phat_hanh_lan_dau') == 'on'),
                    'phat_hanh_lai': (request.POST.get('phat_hanh_lai') == 'on'),
                    'dv_sms_banking': (request.POST.get('dv_sms_banking') == 'on'),
                    'dv_bankplus': (request.POST.get('dv_bankplus') == 'on'),
                    'dv_e_mobile': (request.POST.get('dv_e_mobile') == 'on'),
                    'dv_e_commerce': (request.POST.get('dv_e_commerce') == 'on'),
                    'dv_soft_otp': (request.POST.get('dv_soft_otp') == 'on'),
                    'dv_smart_otp': (request.POST.get('dv_smart_otp') == 'on'),
                    'dv_retail_ebanking': (request.POST.get('dv_retail_ebanking') == 'on'),
                    'dv_thu_ho_tien_nuoc': (request.POST.get('dv_thu_ho_tien_nuoc') == 'on'),
                    'dv_thu_ho_tien_dien': (request.POST.get('dv_thu_ho_tien_dien') == 'on'),
                    'dv_thu_ho_vien_thong': (request.POST.get('dv_thu_ho_vien_thong') == 'on'),
                    'dv_thu_ho_hoc_phi': (request.POST.get('dv_thu_ho_hoc_phi') == 'on'),
                    'dv_thu_ho_bao_hiem': (request.POST.get('dv_thu_ho_bao_hiem') == 'on'),
                    'dv_abic': (request.POST.get('dv_abic') == 'on'),
                    'kenh_mobile': (request.POST.get('kenh_mobile') == 'on'),
                    'kenh_internet': (request.POST.get('kenh_internet') == 'on'),
                    'the_lap_nghiep': (request.POST.get('the_lap_nghiep') == 'on'),
                    'the_lien_ket': (request.POST.get('the_lien_ket') == 'on'),
                    'the_dong_thuong_hieu': (request.POST.get('the_dong_thuong_hieu') == 'on'),
                }

                # Parse and add dates
                if data.get('ngay_sinh'):
                    try:
                        customer_data['ngay_sinh'] = datetime.strptime(data['ngay_sinh'], '%d/%m/%Y').date()
                    except (ValueError, TypeError):
                        pass  # Invalid date format - skip

                if data.get('ngay_cap_cmnd'):
                    try:
                        customer_data['ngay_cap_cmnd'] = datetime.strptime(data['ngay_cap_cmnd'], '%d/%m/%Y').date()
                    except (ValueError, TypeError):
                        pass  # Invalid date format - skip

                if data.get('ngay_het_han_cmnd'):
                    try:
                        customer_data['ngay_het_han_cmnd'] = datetime.strptime(data['ngay_het_han_cmnd'], '%d/%m/%Y').date()
                    except (ValueError, TypeError):
                        pass  # Invalid date format - skip

                # Only create customer if required fields are present
                if customer_data['ho_ten'] and customer_data['so_cmnd']:
                    customer = Customer.objects.create(**customer_data)

            except Exception as e:
                # Failed to create customer, continue with document generation
                pass

        # Add ALL GlobalConfig variables (branch info + custom variables + auto-generated date variables)
        data.update(config.get_all_variables())

        # Generate document
        output_file = render_word_template(template.file.path, data)

        # Return as download
        from datetime import datetime
        response = HttpResponse(
            output_file.read(),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{template.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx"'
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Lỗi: {str(e)}", status=500)

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


@login_required
def print_preview_view(request, template_id):
    """
    Xem trước tài liệu (giống Google Print Preview)
    """
    template = get_object_or_404(Template, id=template_id, is_active=True)
    user = request.user

    # Kiểm tra quyền truy cập
    if not template.user_has_access(user):
        raise Http404("Bạn không có quyền truy cập mẫu biểu này")

    # Lấy dữ liệu từ session
    session_key = f'template_{template_id}_data'
    data = request.session.get(session_key)

    # Nếu không có data trong session, tạo mới từ customer hoặc rỗng
    if not data:
        customer_id = request.GET.get('customer')
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                data = customer.get_data_dict()
                data['_customer_id'] = customer_id
                # Lưu vào session cho lần sau
                request.session[session_key] = data
            except Customer.DoesNotExist:
                data = {}
        else:
            # Không có customer, tạo dict rỗng
            data = {}
            # Vẫn lưu vào session để không lỗi
            request.session[session_key] = data

    try:
        # Lấy customer_id từ session data nếu có
        customer_id = data.get('_customer_id', None)

        # Tạo bản sao của data để không ảnh hưởng đến session
        preview_data = data.copy()

        # Thêm TẤT CẢ biến chung (chi nhánh + custom variables) vào data
        global_config = GlobalConfig.get_instance()
        preview_data.update(global_config.get_all_variables())

        # Thêm date variables nếu có customer
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                customer_data = customer.get_data_dict()
                # Thêm các biến d1, d2, m1, m2, y1, y2, y3, y4
                for key in ['d1', 'd2', 'm1', 'm2', 'y1', 'y2', 'y3', 'y4']:
                    if key in customer_data:
                        preview_data[key] = customer_data[key]
            except Customer.DoesNotExist:
                pass

        # Render template Word với dữ liệu
        template_path = template.file.path
        output_stream = render_word_template(template_path, preview_data)

        # Tạo file tạm để convert sang HTML
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
            temp_docx.write(output_stream.getvalue())
            temp_docx_path = temp_docx.name

        try:
            # Convert Word sang HTML
            with open(temp_docx_path, 'rb') as docx_file:
                result = mammoth.convert_to_html(docx_file)
                html_content = result.value

        finally:
            # Xóa file tạm
            os.unlink(temp_docx_path)

        context = {
            'template': template,
            'html_content': html_content,
            'template_id': template_id,
        }

        return render(request, 'templates_app/print_preview.html', context)

    except Exception as e:
        messages.error(request, f"Lỗi khi tạo preview: {str(e)}")
        return redirect('template_form', template_id=template_id)


@login_required
@require_http_methods(["POST"])
def update_preview_data(request, template_id):
    """
    Cập nhật dữ liệu từ preview sau khi edit
    """
    try:
        # Lấy dữ liệu từ request
        updated_data = json.loads(request.body)

        # Cập nhật session
        session_key = f'template_{template_id}_data'
        session_data = request.session.get(session_key, {})

        # Merge updated data vào session
        session_data.update(updated_data)
        request.session[session_key] = session_data
        request.session.modified = True

        return JsonResponse({'success': True, 'message': 'Dữ liệu đã được cập nhật'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ====================
# Beautiful Number Fee Lookup Views
# ====================

@login_required
def beautiful_number_lookup(request):
    """
    Trang tra cứu phí số đẹp.
    Cho phép nhập số tài khoản hoặc số lượng số đẹp để tra cứu phí.
    """
    result = None
    error = None
    lookup_type = 'detailed'  # Default: Bảng 1 (chi tiết)

    if request.method == 'POST':
        lookup_type = request.POST.get('lookup_type', 'detailed')

        if lookup_type == 'detailed':
            # Tra cứu theo biểu phí chi tiết (Bảng 1)
            account_number = request.POST.get('account_number', '').strip()

            if not account_number:
                error = 'Vui lòng nhập số tài khoản'
            else:
                from .beautiful_number_services import get_detailed_fee
                result = get_detailed_fee(account_number)

        elif lookup_type == 'on_request':
            # Tra cứu theo biểu phí chọn số (Bảng 2)
            try:
                quantity = int(request.POST.get('quantity', 0))
                if quantity < 2:
                    error = 'Số lượng số đẹp phải từ 2 trở lên'
                else:
                    from .beautiful_number_services import get_on_request_fee
                    result = get_on_request_fee(quantity)
            except (ValueError, TypeError):
                error = 'Vui lòng nhập số lượng hợp lệ'

    # Lấy danh sách biểu phí để hiển thị
    from .models import DetailedFeeTier, OnRequestFeeTier

    detailed_tiers = DetailedFeeTier.objects.all().order_by('quantity', 'fee_type')
    on_request_tiers = OnRequestFeeTier.objects.all().order_by('min_quantity')

    context = {
        'result': result,
        'error': error,
        'lookup_type': lookup_type,
        'detailed_tiers': detailed_tiers,
        'on_request_tiers': on_request_tiers,
    }

    return render(request, 'templates_app/beautiful_number_lookup.html', context)


# ========== BEAUTIFUL NUMBER GENERATOR FUNCTIONS ==========

def get_price_tier_from_fee(fee_vat):
    """
    Map phí (có VAT) vào price_tier tương ứng

    Args:
        fee_vat: Phí đã bao gồm VAT

    Returns:
        Price tier code (PRICE_500K_1M, PRICE_1M_3M, etc.)
    """
    from .models import BeautifulNumber

    if fee_vat <= 1_100_000:
        return BeautifulNumber.PRICE_500K_1M
    elif fee_vat <= 3_300_000:
        return BeautifulNumber.PRICE_1M_3M
    elif fee_vat <= 5_500_000:
        return BeautifulNumber.PRICE_3M_5M
    elif fee_vat <= 11_000_000:
        return BeautifulNumber.PRICE_5M_10M
    elif fee_vat <= 22_000_000:
        return BeautifulNumber.PRICE_10M_20M
    else:
        return BeautifulNumber.PRICE_20M_PLUS


def get_category_from_generator_type(gen_type, analysis):
    """
    Map loại generator và analysis sang category trong model

    Args:
        gen_type: 'lap', 'tien', 'ganh', 'lap_kep', 'ngau_nhien', 'loc_phat', 'phong_thuy', 'hop_tuoi', 'cao_cap'
        analysis: Kết quả từ analyze_account_number

    Returns:
        Category code
    """
    from .models import BeautifulNumber

    # Ưu tiên dựa vào analysis nếu là số đặc biệt
    if analysis.get('is_special'):
        return BeautifulNumber.CATEGORY_DAC_BIET

    # Map theo loại generator
    category_map = {
        'lap': BeautifulNumber.CATEGORY_SO_LAP,
        'tien': BeautifulNumber.CATEGORY_SO_TIEN,
        'ganh': BeautifulNumber.CATEGORY_SO_DOI_XUNG,
        'lap_kep': BeautifulNumber.CATEGORY_SO_LAP,
        'loc_phat': BeautifulNumber.CATEGORY_LOC_PHAT,
        'phong_thuy': BeautifulNumber.CATEGORY_PHONG_THUY,
        'hop_tuoi': BeautifulNumber.CATEGORY_HOP_TUOI,
        'cao_cap': BeautifulNumber.CATEGORY_DAC_BIET,  # Số cao cấp -> Đặc biệt
        'ngau_nhien': BeautifulNumber.CATEGORY_TAI_LOC,  # Số thường -> Tài lộc
    }

    return category_map.get(gen_type, BeautifulNumber.CATEGORY_TAI_LOC)


def generate_and_save_beautiful_numbers(count_per_type=50, clear_existing=False):
    """
    Tạo số đẹp tự động và lưu vào database

    Args:
        count_per_type: Số lượng mỗi loại (mặc định 50)
        clear_existing: Xóa các số hiện có trước khi tạo mới (mặc định False)

    Returns:
        Dict với thống kê kết quả
    """
    from .models import BeautifulNumber
    from . import beautiful_number_generator as bng
    from .beautiful_number_services import analyze_account_number

    stats = {
        'created': 0,
        'skipped': 0,
        'errors': 0,
        'by_type': {}
    }

    # Xóa số cũ nếu được yêu cầu
    if clear_existing:
        deleted_count = BeautifulNumber.objects.all().delete()[0]
        stats['deleted'] = deleted_count

    # Định nghĩa các loại generator
    generator_types = {
        'lap': (bng.gen_so_lap, 20),  # Chỉ có 20 số lặp tối đa
        'tien': (bng.gen_so_tien, 15),  # Chỉ có 15 số tiến
        'ganh': (bng.gen_so_ganh, count_per_type),
        'lap_kep': (bng.gen_so_lap_kep, count_per_type),
        'loc_phat': (bng.gen_so_loc_phat, count_per_type),  # Số Lộc Phát (6,8)
        'phong_thuy': (bng.gen_so_phong_thuy, count_per_type),  # Số Phong Thủy
        'hop_tuoi': (bng.gen_so_hop_tuoi, count_per_type),  # Số Hợp Tuổi
        'cao_cap': (bng.gen_so_cao_cap, min(count_per_type, 50)),  # Số cao cấp (giá cao)
        'ngau_nhien': (bng.gen_so_ngau_nhien, count_per_type),
    }

    # Tạo số cho từng loại
    for gen_type, (generator_func, count) in generator_types.items():
        type_stats = {
            'created': 0,
            'skipped': 0,
            'errors': 0
        }

        try:
            # Tạo số
            numbers = bng.generate_numbers(generator_func, count)

            for num in numbers:
                try:
                    # Phân tích số
                    analysis = analyze_account_number(num)

                    # Bỏ qua nếu có lỗi
                    if analysis.get('error'):
                        type_stats['errors'] += 1
                        continue

                    # Xác định category và price_tier
                    category = get_category_from_generator_type(gen_type, analysis)
                    price_tier = get_price_tier_from_fee(analysis['fee_min_vat'])

                    # Tạo hoặc cập nhật số trong database
                    beautiful_num, created = BeautifulNumber.objects.get_or_create(
                        account_number=num,
                        defaults={
                            'category': category,
                            'price_tier': price_tier,
                            'fee': analysis['fee_min_vat'],
                            'description': analysis['description'],
                            'is_available': True,
                        }
                    )

                    if created:
                        type_stats['created'] += 1
                        stats['created'] += 1
                    else:
                        type_stats['skipped'] += 1
                        stats['skipped'] += 1

                except Exception as e:
                    type_stats['errors'] += 1
                    stats['errors'] += 1
                    print(f"Error processing number {num}: {e}")

            stats['by_type'][gen_type] = type_stats

        except Exception as e:
            stats['by_type'][gen_type] = {
                'created': 0,
                'skipped': 0,
                'errors': count,
                'error_message': str(e)
            }
            stats['errors'] += count

    return stats


@login_required
@require_http_methods(["POST"])
def generate_beautiful_numbers_ajax(request):
    """
    AJAX endpoint để tạo số đẹp tự động
    """
    try:
        # Lấy tham số từ request
        count_per_type = int(request.POST.get('count_per_type', 50))
        clear_existing = request.POST.get('clear_existing', 'false').lower() == 'true'

        # Giới hạn số lượng để tránh quá tải
        count_per_type = min(count_per_type, 200)

        # Tạo số đẹp
        stats = generate_and_save_beautiful_numbers(count_per_type, clear_existing)

        return JsonResponse({
            'success': True,
            'message': f'Đã tạo {stats["created"]} số mới, bỏ qua {stats["skipped"]} số trùng',
            'stats': stats
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)


@login_required
def beautiful_number_list(request):
    """
    Trang danh sách số đẹp có sẵn để khách hàng chọn.
    Có filter theo giá và loại số đẹp. Có thể in ra.
    """
    from .models import BeautifulNumber
    from .beautiful_number_services import analyze_account_number

    # Lấy tham số filter từ request
    category_filter = request.GET.get('category', '')
    price_filter = request.GET.get('price', '')
    available_only = request.GET.get('available', 'true') == 'true'
    pattern_filter = request.GET.get('pattern', '').strip()

    # Query base
    numbers_queryset = BeautifulNumber.objects.all()

    # Apply filters
    if available_only:
        numbers_queryset = numbers_queryset.filter(is_available=True)

    if category_filter:
        numbers_queryset = numbers_queryset.filter(category=category_filter)

    if price_filter:
        numbers_queryset = numbers_queryset.filter(price_tier=price_filter)

    # Pattern search - convert * to regex wildcard
    # Example: "7202***777***" -> matches numbers with 777 in the middle
    if pattern_filter:
        import re
        # Convert pattern to regex: * matches any single digit
        regex_pattern = ''
        for char in pattern_filter:
            if char == '*':
                regex_pattern += r'\d'  # Match any single digit
            elif char.isdigit():
                regex_pattern += char
            # Ignore other characters

        if regex_pattern:
            # Use regex filter on account_number
            numbers_queryset = numbers_queryset.filter(account_number__regex=f'^{regex_pattern}$')

    # Order by price and category
    numbers_queryset = numbers_queryset.order_by('price_tier', 'category', 'account_number')

    # IMPORTANT: Convert to list to allow attribute assignment
    numbers = list(numbers_queryset)

    # Get choices for filters
    category_choices = BeautifulNumber.CATEGORY_CHOICES
    price_choices = BeautifulNumber.PRICE_TIER_CHOICES

    # Enrich numbers with fee range from analysis
    from collections import defaultdict
    numbers_by_price = defaultdict(list)

    for number in numbers:
        # Phân tích để lấy fee_min và fee_max
        analysis = analyze_account_number(number.account_number)

        # Attach fee range to number object (works because numbers is a list)
        number.fee_min = int(analysis.get('fee_min_vat', number.fee))
        number.fee_max = int(analysis.get('fee_max_vat', number.fee))

        numbers_by_price[number.price_tier].append(number)

    context = {
        'numbers': numbers,
        'numbers_by_price': dict(numbers_by_price),
        'category_choices': category_choices,
        'price_choices': price_choices,
        'selected_category': category_filter,
        'selected_price': price_filter,
        'available_only': available_only,
        'pattern_filter': pattern_filter,
    }

    return render(request, 'templates_app/beautiful_number_list.html', context)


@login_required
def test_address_selector(request):
    """
    Test page for Address Selector Component
    """
    return render(request, 'templates_app/test_address_selector.html')


def area_lookup(request):
    """
    Trang tra cứu thông tin địa bàn hành chính.
    Sử dụng AddressSelector component và dữ liệu từ dia_danh.json và chuyen_doi.json
    """
    return render(request, 'templates_app/area_lookup.html')


# ====================
# Bank Statement Analyzer Views
# ====================

@login_required
def bank_statement_upload(request):
    """
    Trang upload file sao kê ngân hàng
    """
    from .models import BankStatement

    if request.method == 'POST' and request.FILES.get('statement_file'):
        try:
            from .bank_statement_parser import BankStatementParser
            import os
            from django.conf import settings

            # Lưu file upload
            uploaded_file = request.FILES['statement_file']
            file_name = uploaded_file.name

            # Tạo thư mục upload nếu chưa có
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'bank_statements')
            os.makedirs(upload_dir, exist_ok=True)

            # Lưu file tạm
            file_path = os.path.join(upload_dir, file_name)
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Parse file
            parser = BankStatementParser(file_path)

            # Validate file
            is_valid, error_msg = parser.validate_file()
            if not is_valid:
                messages.error(request, f'File không hợp lệ: {error_msg}')
                return redirect('bank_statement_upload')

            # Process file
            transactions_data = parser.process()
            summary = parser.get_summary()

            # Tạo BankStatement
            statement = BankStatement.objects.create(
                file_name=file_name,
                total_transactions=summary['total_transactions'],
                total_debit=summary['total_debit'],
                total_credit=summary['total_credit'],
                final_balance=summary['final_balance'],
                processed=True,
                uploaded_by=request.user
            )

            # Lưu các transactions
            from .models import Transaction
            for trans_data in transactions_data:
                Transaction.objects.create(
                    statement=statement,
                    stt=trans_data['stt'],
                    transaction_date=trans_data['ngay_giao_dich'],
                    debit_amount=trans_data['so_tien_ghi_no'],
                    credit_amount=trans_data['so_tien_ghi_co'],
                    balance=trans_data['so_du_sau_gd'],
                    bank_name=trans_data['ngan_hang'],
                    account_number=trans_data['so_tai_khoan'],
                    beneficiary_name=trans_data['ten_nguoi'],
                    description=trans_data['noi_dung'],
                    transaction_type=trans_data['ghi_chu'],
                    raw_trcdnm=trans_data['raw_trcdnm'],
                    raw_tomgntno=trans_data['raw_tomgntno']
                )

            messages.success(request, f'Đã phân tích thành công {summary["total_transactions"]} giao dịch!')
            return redirect('bank_statement_result', statement_id=statement.id)

        except Exception as e:
            messages.error(request, f'Lỗi khi xử lý file: {str(e)}')
            return redirect('bank_statement_upload')

    # Lấy danh sách các statement đã upload
    statements = BankStatement.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')[:10]

    context = {
        'statements': statements,
    }
    return render(request, 'templates_app/bank_statement_upload.html', context)


@login_required
def bank_statement_result(request, statement_id):
    """
    Hiển thị kết quả phân tích sao kê
    """
    from .models import BankStatement, Transaction
    from django.core.paginator import Paginator

    statement = get_object_or_404(BankStatement, id=statement_id, uploaded_by=request.user)

    # Lấy tham số filter
    transaction_type_filter = request.GET.get('type', '')

    # Query transactions
    transactions = statement.transactions.all()

    # Apply filter
    if transaction_type_filter:
        transactions = transactions.filter(transaction_type=transaction_type_filter)

    # Pagination
    paginator = Paginator(transactions, 50)  # 50 giao dịch mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Thống kê theo loại giao dịch
    transaction_types = statement.transactions.exclude(transaction_type='').values('transaction_type').annotate(
        count=models.Count('id'),
        total_debit=models.Sum('debit_amount'),
        total_credit=models.Sum('credit_amount')
    ).order_by('transaction_type')

    # Danh sách các loại giao dịch để filter
    filter_options = [
        "Chuyển khoản nội bộ Agribank",
        "Nhận chuyển khoản nội bộ Agribank",
        "Chuyển khoản liên ngân hàng",
        "Nhận chuyển khoản liên ngân hàng",
        "Rút tiền ATM",
        "Rút tiền mặt",
        "Nộp tiền ATM",
        "Nộp tiền mặt",
        "Thanh toán thẻ",
        "Thanh toán POS",
        "Nạp tiền điện thoại",
        "Thanh toán tiền điện",
        "Thanh toán dịch vụ (VNPT)",
        "Phí dịch vụ",
        "Trả lãi tiền gửi"
    ]

    context = {
        'statement': statement,
        'page_obj': page_obj,
        'transaction_types': transaction_types,
        'filter_options': filter_options,
        'selected_type': transaction_type_filter,
    }

    return render(request, 'templates_app/bank_statement_result.html', context)


@login_required
def bank_statement_export(request, statement_id):
    """
    Export báo cáo sao kê ra file Excel
    """
    from .models import BankStatement
    from io import BytesIO
    import xlsxwriter
    from django.http import HttpResponse

    statement = get_object_or_404(BankStatement, id=statement_id, uploaded_by=request.user)

    # Tạo file Excel trong memory
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    # Format cho số tiền
    money_format = workbook.add_format({
        'num_format': '#,##0',
        'align': 'right'
    })

    # Format cho header
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#4472C4',
        'font_color': 'white',
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })

    # Format cho ngày
    date_format = workbook.add_format({
        'num_format': 'dd/mm/yyyy',
        'align': 'center'
    })

    # Sheet 1: Chi tiết giao dịch
    worksheet1 = workbook.add_worksheet('Chi tiết')

    # Header
    headers = [
        'STT', 'Ngày GD', 'Số tiền ghi nợ', 'Số tiền ghi có',
        'Số dư sau GD', 'Ngân hàng', 'Số TK', 'Tên người',
        'Nội dung', 'Loại giao dịch'
    ]

    for col_num, header in enumerate(headers):
        worksheet1.write(0, col_num, header, header_format)

    # Set column widths
    worksheet1.set_column('A:A', 8)   # STT
    worksheet1.set_column('B:B', 12)  # Ngày
    worksheet1.set_column('C:E', 15)  # Các cột tiền
    worksheet1.set_column('F:F', 15)  # Ngân hàng
    worksheet1.set_column('G:G', 18)  # Số TK
    worksheet1.set_column('H:H', 25)  # Tên người
    worksheet1.set_column('I:I', 40)  # Nội dung
    worksheet1.set_column('J:J', 30)  # Loại GD

    # Data
    transactions = statement.transactions.all()
    for row_num, trans in enumerate(transactions, start=1):
        worksheet1.write(row_num, 0, trans.stt)
        worksheet1.write(row_num, 1, trans.transaction_date, date_format)
        worksheet1.write(row_num, 2, float(trans.debit_amount), money_format)
        worksheet1.write(row_num, 3, float(trans.credit_amount), money_format)
        worksheet1.write(row_num, 4, float(trans.balance), money_format)
        worksheet1.write(row_num, 5, trans.bank_name)
        worksheet1.write(row_num, 6, trans.account_number)
        worksheet1.write(row_num, 7, trans.beneficiary_name)
        worksheet1.write(row_num, 8, trans.description)
        worksheet1.write(row_num, 9, trans.transaction_type)

    # Sheet 2: Thống kê
    worksheet2 = workbook.add_worksheet('Thống kê')

    # Thống kê tổng quan
    worksheet2.write(0, 0, 'THỐNG KÊ TỔNG QUAN', header_format)
    worksheet2.write(1, 0, 'Tên file:')
    worksheet2.write(1, 1, statement.file_name)
    worksheet2.write(2, 0, 'Ngày upload:')
    worksheet2.write(2, 1, statement.uploaded_at.strftime('%d/%m/%Y %H:%M'))
    worksheet2.write(3, 0, 'Tổng số giao dịch:')
    worksheet2.write(3, 1, statement.total_transactions)
    worksheet2.write(4, 0, 'Tổng tiền ghi nợ:')
    worksheet2.write(4, 1, float(statement.total_debit), money_format)
    worksheet2.write(5, 0, 'Tổng tiền ghi có:')
    worksheet2.write(5, 1, float(statement.total_credit), money_format)
    worksheet2.write(6, 0, 'Số dư cuối kỳ:')
    worksheet2.write(6, 1, float(statement.final_balance), money_format)

    # Thống kê theo loại giao dịch
    worksheet2.write(8, 0, 'THỐNG KÊ THEO LOẠI GIAO DỊCH', header_format)
    worksheet2.write(9, 0, 'Loại giao dịch', header_format)
    worksheet2.write(9, 1, 'Số lượng', header_format)
    worksheet2.write(9, 2, 'Tổng ghi nợ', header_format)
    worksheet2.write(9, 3, 'Tổng ghi có', header_format)

    transaction_types = statement.transactions.exclude(transaction_type='').values('transaction_type').annotate(
        count=models.Count('id'),
        total_debit=models.Sum('debit_amount'),
        total_credit=models.Sum('credit_amount')
    ).order_by('transaction_type')

    for row_num, item in enumerate(transaction_types, start=10):
        worksheet2.write(row_num, 0, item['transaction_type'])
        worksheet2.write(row_num, 1, item['count'])
        worksheet2.write(row_num, 2, float(item['total_debit'] or 0), money_format)
        worksheet2.write(row_num, 3, float(item['total_credit'] or 0), money_format)

    worksheet2.set_column('A:A', 40)
    worksheet2.set_column('B:D', 15)

    workbook.close()

    # Chuẩn bị response
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="BaoCao_SaoKe_{statement.id}.xlsx"'

    return response


# ====================
# Employee Management Views
# ====================

def check_employee_import_permission(user):
    """
    Kiểm tra quyền import nhân viên
    Chỉ Superuser có quyền
    """
    return user.is_superuser


@login_required
def download_employee_template(request):
    """
    Tải về file Excel mẫu để import nhân viên
    """
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from django.http import HttpResponse

    # Create workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Danh sách nhân viên"

    # Define headers (Vietnamese names that the import function looks for)
    headers = [
        'Username',
        'Họ và tên',
        'Mã nhân viên',
        'Ngày sinh',
        'Giới tính',
        'Điện thoại',
        'Địa chỉ',
        'Số CCCD',
        'Ngày cấp CCCD',
        'Nơi cấp CCCD',
        'Chi nhánh',
        'Phòng ban',
        'Chức vụ',
        'Nghiệp vụ',
        'Mã chứng thư số',
        'CTS từ ngày',
        'CTS đến ngày'
    ]

    # Write headers with styling
    header_fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=11)

    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Add sample data rows
    sample_data = [
        [
            'nguyenvana',
            'Nguyễn Văn A',
            'NV001',
            '15/01/1990',
            'Nam',
            '0912345678',
            '123 Đường ABC, Phường 1, TP. Bạc Liêu',
            '001234567890',
            '01/01/2020',
            'Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư',
            'HOI_SO',
            'KE_TOAN',
            'TRUONG_PHONG',
            'KIEM_SOAT_VIEN',
            'CTS-NV001-2024',
            '01/01/2024',
            '31/12/2025'
        ],
        [
            'tranthib',
            'Trần Thị B',
            'NV002',
            '20/05/1995',
            'Nữ',
            '0987654321',
            '456 Đường XYZ, Phường 2, TP. Bạc Liêu',
            '002345678901',
            '15/03/2021',
            'Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư',
            'PGD_P1',
            'KHACH_HANG',
            'NHAN_VIEN',
            'GIAO_DICH_VIEN',
            'CTS-NV002-2024',
            '15/06/2024',
            '14/06/2025'
        ],
        [
            'levanc',
            'Lê Văn C',
            'NV003',
            '10/12/1988',
            'Nam',
            '0901234567',
            '789 Đường DEF, Láng Tròn, TP. Bạc Liêu',
            '003456789012',
            '20/07/2019',
            'Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư',
            'PGD_LANG_TRON',
            'TONG_HOP',
            'PHO_PHONG',
            'TONG_HOP_VIEN',
            'CTS-NV003-2023',
            '01/07/2023',
            '30/06/2024'
        ],
    ]

    for row_idx, row_data in enumerate(sample_data, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.alignment = Alignment(horizontal='left', vertical='center')

    # Adjust column widths
    column_widths = [15, 25, 15, 15, 12, 15, 35, 18, 15, 45, 20, 25, 25, 20, 20, 15, 15]
    for col_idx, width in enumerate(column_widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = width

    # Add instruction sheet
    ws_instructions = wb.create_sheet(title="Hướng dẫn")
    instructions = [
        ['HƯỚNG DẪN IMPORT NHÂN VIÊN'],
        [''],
        ['1. Các cột bắt buộc:'],
        ['   - Username: Tên đăng nhập (không trùng)'],
        ['   - Họ và tên: Họ tên đầy đủ'],
        ['   - Mã nhân viên: Mã nhân viên (không trùng)'],
        [''],
        ['2. Thông tin cá nhân (tùy chọn):'],
        ['   - Ngày sinh: Định dạng dd/mm/yyyy (ví dụ: 15/01/1990)'],
        ['   - Giới tính: Nam, Nữ, hoặc Khác'],
        ['   - Điện thoại: Số điện thoại liên hệ'],
        ['   - Địa chỉ: Địa chỉ nơi ở hiện tại'],
        [''],
        ['3. Thông tin CCCD (tùy chọn):'],
        ['   - Số CCCD: Số căn cước công dân (12 chữ số)'],
        ['   - Ngày cấp CCCD: Định dạng dd/mm/yyyy (ví dụ: 01/01/2020)'],
        ['   - Nơi cấp CCCD: Nơi cấp CCCD (ví dụ: Cục Cảnh sát ĐKQL cư trú và DLQG về dân cư)'],
        [''],
        ['4. Thông tin công việc (tùy chọn):'],
        ['   - Chi nhánh: HOI_SO, PGD_P1, PGD_LANG_TRON'],
        ['   - Phòng ban: KE_TOAN, KHACH_HANG, BAN_GIAM_DOC, TONG_HOP'],
        ['   - Chức vụ: GIAM_DOC, PHO_GIAM_DOC, TRUONG_PHONG, PHO_PHONG, GD_PGD, PGD_PGD, NHAN_VIEN'],
        ['   - Nghiệp vụ: GIAO_DICH_VIEN, KIEM_SOAT_VIEN, HAU_KIEM_VIEN, TONG_HOP_VIEN'],
        [''],
        ['5. Thông tin chứng thư số (tùy chọn):'],
        ['   - Mã chứng thư số: Mã số chứng thư (ví dụ: CTS-NV001-2024)'],
        ['   - CTS từ ngày: Ngày bắt đầu hiệu lực, định dạng dd/mm/yyyy'],
        ['   - CTS đến ngày: Ngày hết hạn hiệu lực, định dạng dd/mm/yyyy'],
        [''],
        ['6. Lưu ý quan trọng:'],
        ['   - Không xóa dòng tiêu đề (dòng đầu tiên)'],
        ['   - Mật khẩu mặc định cho user mới: Csi@123'],
        ['   - Nếu Username đã tồn tại, hệ thống sẽ cập nhật thông tin nhân viên'],
        ['   - Các cột Chi nhánh, Phòng ban, Chức vụ, Nghiệp vụ phải sử dụng đúng mã như trên'],
        ['   - Ngày tháng phải đúng định dạng dd/mm/yyyy'],
        ['   - Hệ thống sẽ cảnh báo khi chứng thư số hết hạn trong vòng 20 ngày'],
    ]

    title_font = Font(bold=True, size=14, color='366092')
    for row_idx, instruction in enumerate(instructions, start=1):
        cell = ws_instructions.cell(row=row_idx, column=1, value=instruction[0])
        if row_idx == 1:
            cell.font = title_font
        cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

    ws_instructions.column_dimensions['A'].width = 80

    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Mau_Import_Nhan_Vien.xlsx"'
    wb.save(response)

    return response


@login_required
@require_http_methods(["GET", "POST"])
def employee_import_excel(request):
    """
    View để import nhân viên từ file Excel
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        messages.error(request, 'Bạn không có quyền import nhân viên')
        return redirect('dashboard')
    if request.method == 'POST' and request.FILES.get('excel_file'):
        try:
            import openpyxl
            from datetime import datetime
            from .models import UserProfile

            excel_file = request.FILES['excel_file']

            # Validate file extension
            if not excel_file.name.endswith(('.xlsx', '.xls')):
                messages.error(request, 'File phải có định dạng .xlsx hoặc .xls')
                return redirect('employee_import_excel')

            wb = openpyxl.load_workbook(excel_file, data_only=True)
            ws = wb.active

            # Dòng đầu tiên là header
            headers = [cell.value for cell in ws[1]]

            success_count = 0
            error_count = 0
            errors = []

            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    data = {}
                    for col_idx, value in enumerate(row):
                        if col_idx < len(headers) and headers[col_idx]:
                            data[headers[col_idx]] = value if value else ''

                    # Extract required fields
                    username = str(data.get('Username', '')).strip()
                    full_name = str(data.get('Full Name', '') or data.get('Họ và tên', '')).strip()
                    employee_code = str(data.get('Employee Code', '') or data.get('Mã nhân viên', '')).strip()

                    # Validate required fields
                    if not username or not employee_code:
                        errors.append(f"Dòng {row_idx}: Thiếu Username hoặc Mã nhân viên")
                        error_count += 1
                        continue

                    # Check if user exists
                    user = User.objects.filter(username=username).first()
                    if not user:
                        # Create new user with default password Csi@123
                        user = User.objects.create_user(
                            username=username,
                            password='Csi@123',
                            first_name=full_name.split()[0] if full_name else '',
                            last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
                        )

                    # Get or create UserProfile
                    profile, created = UserProfile.objects.get_or_create(user=user)

                    # Update profile fields
                    if employee_code:
                        profile.employee_code = employee_code
                    if full_name:
                        profile.full_name = full_name

                    # Optional fields
                    if data.get('Branch') or data.get('Chi nhánh'):
                        branch_value = str(data.get('Branch') or data.get('Chi nhánh', '')).strip()
                        # Map value to choice
                        profile.branch = branch_value

                    if data.get('Department') or data.get('Phòng ban'):
                        dept_value = str(data.get('Department') or data.get('Phòng ban', '')).strip()
                        profile.department = dept_value

                    if data.get('Position') or data.get('Chức vụ'):
                        pos_value = str(data.get('Position') or data.get('Chức vụ', '')).strip()
                        profile.position = pos_value

                    if data.get('Job Function') or data.get('Nghiệp vụ'):
                        job_value = str(data.get('Job Function') or data.get('Nghiệp vụ', '')).strip()
                        profile.job_function = job_value

                    if data.get('Phone') or data.get('Điện thoại'):
                        profile.phone = str(data.get('Phone') or data.get('Điện thoại', '')).strip()

                    # Gender
                    if data.get('Gender') or data.get('Giới tính'):
                        gender_value = str(data.get('Gender') or data.get('Giới tính', '')).strip()
                        if gender_value:
                            profile.gender = gender_value

                    # Address
                    if data.get('Address') or data.get('Địa chỉ'):
                        address_value = str(data.get('Address') or data.get('Địa chỉ', '')).strip()
                        if address_value:
                            profile.address = address_value

                    # ID Card (CCCD) fields
                    if data.get('ID Card Number') or data.get('Số CCCD'):
                        id_card_num = str(data.get('ID Card Number') or data.get('Số CCCD', '')).strip()
                        if id_card_num:
                            profile.id_card_number = id_card_num

                    if data.get('ID Card Place') or data.get('Nơi cấp CCCD'):
                        id_card_place = str(data.get('ID Card Place') or data.get('Nơi cấp CCCD', '')).strip()
                        if id_card_place:
                            profile.id_card_place = id_card_place

                    # Parse date fields
                    dob_value = data.get('DOB') or data.get('Ngày sinh')
                    if dob_value:
                        if isinstance(dob_value, datetime):
                            profile.dob = dob_value.date()
                        elif isinstance(dob_value, str):
                            try:
                                profile.dob = datetime.strptime(dob_value, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                try:
                                    profile.dob = datetime.strptime(dob_value, '%Y-%m-%d').date()
                                except (ValueError, TypeError):
                                    pass

                    # ID Card Date
                    id_card_date_value = data.get('ID Card Date') or data.get('Ngày cấp CCCD')
                    if id_card_date_value:
                        if isinstance(id_card_date_value, datetime):
                            profile.id_card_date = id_card_date_value.date()
                        elif isinstance(id_card_date_value, str):
                            try:
                                profile.id_card_date = datetime.strptime(id_card_date_value, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                try:
                                    profile.id_card_date = datetime.strptime(id_card_date_value, '%Y-%m-%d').date()
                                except (ValueError, TypeError):
                                    pass

                    # Digital Certificate fields
                    if data.get('Certificate Code') or data.get('Mã chứng thư số'):
                        cert_code = str(data.get('Certificate Code') or data.get('Mã chứng thư số', '')).strip()
                        if cert_code:
                            profile.certificate_code = cert_code

                    # Certificate Start Date
                    cert_start_value = data.get('Certificate Start Date') or data.get('CTS từ ngày')
                    if cert_start_value:
                        if isinstance(cert_start_value, datetime):
                            profile.certificate_start_date = cert_start_value.date()
                        elif isinstance(cert_start_value, str):
                            try:
                                profile.certificate_start_date = datetime.strptime(cert_start_value, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                try:
                                    profile.certificate_start_date = datetime.strptime(cert_start_value, '%Y-%m-%d').date()
                                except (ValueError, TypeError):
                                    pass

                    # Certificate End Date
                    cert_end_value = data.get('Certificate End Date') or data.get('CTS đến ngày')
                    if cert_end_value:
                        if isinstance(cert_end_value, datetime):
                            profile.certificate_end_date = cert_end_value.date()
                        elif isinstance(cert_end_value, str):
                            try:
                                profile.certificate_end_date = datetime.strptime(cert_end_value, '%d/%m/%Y').date()
                            except (ValueError, TypeError):
                                try:
                                    profile.certificate_end_date = datetime.strptime(cert_end_value, '%Y-%m-%d').date()
                                except (ValueError, TypeError):
                                    pass

                    profile.save()
                    success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append(f"Dòng {row_idx}: {str(e)}")

            # Show results
            if success_count > 0:
                messages.success(request, f'Đã import thành công {success_count} nhân viên')
            if error_count > 0:
                for error in errors[:10]:
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f'... và {len(errors) - 10} lỗi khác')

            return redirect('employee_import_excel')

        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Lỗi khi xử lý file: {str(e)}')
            return redirect('employee_import_excel')

    # GET request - show form
    context = {
        'title': 'Import nhân viên từ Excel',
    }
    return render(request, 'templates_app/employee_import.html', context)


@login_required
def employee_list(request):
    """
    Hiển thị danh sách nhân viên và form thêm/sửa
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        messages.error(request, 'Bạn không có quyền quản lý nhân viên')
        return redirect('dashboard')

    from .models import UserProfile
    from datetime import date, timedelta

    employees = UserProfile.objects.select_related('user').all()

    # Get filter parameters
    filter_department = request.GET.get('department', '')
    filter_position = request.GET.get('position', '')
    filter_branch = request.GET.get('branch', '')
    filter_cert_status = request.GET.get('cert_status', '')

    # Apply filters
    if filter_department:
        employees = employees.filter(department=filter_department)
    if filter_position:
        employees = employees.filter(position=filter_position)
    if filter_branch:
        employees = employees.filter(branch=filter_branch)

    # Filter by certificate status
    today = date.today()
    warning_date = today + timedelta(days=20)

    if filter_cert_status == 'expiring':
        # Certificates expiring within 20 days
        employees = employees.filter(
            certificate_end_date__lte=warning_date,
            certificate_end_date__gte=today
        )
    elif filter_cert_status == 'expired':
        # Already expired certificates
        employees = employees.filter(certificate_end_date__lt=today)
    elif filter_cert_status == 'valid':
        # Valid certificates (not expiring soon)
        employees = employees.filter(certificate_end_date__gt=warning_date)
    elif filter_cert_status == 'no_cert':
        # No certificate
        employees = employees.filter(certificate_code='')

    employees = employees.order_by('employee_code')

    # Count warnings for display
    expiring_count = UserProfile.objects.filter(
        certificate_end_date__lte=warning_date,
        certificate_end_date__gte=today
    ).count()
    expired_count = UserProfile.objects.filter(certificate_end_date__lt=today).count()

    # Get unique values for filter dropdowns
    departments = UserProfile.DEPARTMENT_CHOICES
    positions = UserProfile.POSITION_CHOICES
    branches = UserProfile.BRANCH_CHOICES

    context = {
        'title': 'Quản lý nhân viên',
        'employees': employees,
        'filter_department': filter_department,
        'filter_position': filter_position,
        'filter_branch': filter_branch,
        'filter_cert_status': filter_cert_status,
        'departments': departments,
        'positions': positions,
        'branches': branches,
        'expiring_count': expiring_count,
        'expired_count': expired_count,
    }
    return render(request, 'templates_app/employee_list.html', context)


@login_required
@require_http_methods(["POST"])
def employee_create_manual(request):
    """
    Tạo nhân viên mới thủ công
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền'}, status=403)

    from .models import UserProfile
    from datetime import datetime

    try:
        # Required fields
        username = request.POST.get('username', '').strip()
        employee_code = request.POST.get('employee_code', '').strip()
        full_name = request.POST.get('full_name', '').strip()

        if not username or not employee_code or not full_name:
            return JsonResponse({'success': False, 'error': 'Thiếu thông tin bắt buộc'}, status=400)

        # Check if username exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': f'Username "{username}" đã tồn tại'}, status=400)

        # Check if employee_code exists
        if UserProfile.objects.filter(employee_code=employee_code).exists():
            return JsonResponse({'success': False, 'error': f'Mã nhân viên "{employee_code}" đã tồn tại'}, status=400)

        # Create user
        user = User.objects.create_user(
            username=username,
            password=request.POST.get('password', 'Csi@123'),
            first_name=full_name.split()[0] if full_name else '',
            last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
        )

        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            employee_code=employee_code,
            full_name=full_name
        )

        # Optional fields
        if request.POST.get('dob'):
            try:
                profile.dob = datetime.strptime(request.POST.get('dob'), '%Y-%m-%d').date()
            except:
                pass

        profile.gender = request.POST.get('gender', 'Nam')
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.id_card_number = request.POST.get('id_card_number', '')

        if request.POST.get('id_card_date'):
            try:
                profile.id_card_date = datetime.strptime(request.POST.get('id_card_date'), '%Y-%m-%d').date()
            except:
                pass

        profile.id_card_place = request.POST.get('id_card_place', '')
        profile.branch = request.POST.get('branch', '')
        profile.department = request.POST.get('department', '')
        profile.position = request.POST.get('position', '')
        profile.job_function = request.POST.get('job_function', '')

        # Digital certificate fields
        profile.certificate_code = request.POST.get('certificate_code', '')

        if request.POST.get('certificate_start_date'):
            try:
                profile.certificate_start_date = datetime.strptime(request.POST.get('certificate_start_date'), '%Y-%m-%d').date()
            except:
                pass

        if request.POST.get('certificate_end_date'):
            try:
                profile.certificate_end_date = datetime.strptime(request.POST.get('certificate_end_date'), '%Y-%m-%d').date()
            except:
                pass

        profile.save()

        return JsonResponse({
            'success': True,
            'message': f'Đã thêm nhân viên {full_name} thành công'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def employee_update_manual(request, employee_id):
    """
    Cập nhật thông tin nhân viên
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền'}, status=403)

    from .models import UserProfile
    from datetime import datetime

    try:
        profile = UserProfile.objects.get(id=employee_id)

        # Update fields
        full_name = request.POST.get('full_name', '').strip()
        if full_name:
            profile.full_name = full_name

        if request.POST.get('dob'):
            try:
                profile.dob = datetime.strptime(request.POST.get('dob'), '%Y-%m-%d').date()
            except:
                pass

        profile.gender = request.POST.get('gender', profile.gender)
        profile.phone = request.POST.get('phone', profile.phone)
        profile.address = request.POST.get('address', profile.address)
        profile.id_card_number = request.POST.get('id_card_number', profile.id_card_number)

        if request.POST.get('id_card_date'):
            try:
                profile.id_card_date = datetime.strptime(request.POST.get('id_card_date'), '%Y-%m-%d').date()
            except:
                pass

        profile.id_card_place = request.POST.get('id_card_place', profile.id_card_place)
        profile.branch = request.POST.get('branch', profile.branch)
        profile.department = request.POST.get('department', profile.department)
        profile.position = request.POST.get('position', profile.position)
        profile.job_function = request.POST.get('job_function', profile.job_function)

        # Digital certificate fields
        profile.certificate_code = request.POST.get('certificate_code', profile.certificate_code)

        if request.POST.get('certificate_start_date'):
            try:
                profile.certificate_start_date = datetime.strptime(request.POST.get('certificate_start_date'), '%Y-%m-%d').date()
            except:
                pass

        if request.POST.get('certificate_end_date'):
            try:
                profile.certificate_end_date = datetime.strptime(request.POST.get('certificate_end_date'), '%Y-%m-%d').date()
            except:
                pass

        profile.save()

        return JsonResponse({
            'success': True,
            'message': f'Đã cập nhật thông tin nhân viên {profile.full_name}'
        })

    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy nhân viên'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def employee_delete_manual(request, employee_id):
    """
    Xóa nhân viên
    Chỉ Superuser có quyền
    """
    if not check_employee_import_permission(request.user):
        return JsonResponse({'success': False, 'error': 'Bạn không có quyền'}, status=403)

    from .models import UserProfile

    try:
        profile = UserProfile.objects.get(id=employee_id)
        full_name = profile.full_name
        user = profile.user

        # Delete profile and user
        profile.delete()
        user.delete()

        return JsonResponse({
            'success': True,
            'message': f'Đã xóa nhân viên {full_name}'
        })

    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Không tìm thấy nhân viên'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ====================
# E-Learning Views
# ====================

def check_elearning_manage_permission(user):
    """
    Kiểm tra quyền quản lý e-learning (tạo/sửa/xóa khóa học)
    Chỉ Superuser và nhóm "Phòng Tổng hợp" có quyền
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name='Phòng Tổng hợp').exists()


@login_required
def course_dashboard(request):
    """
    Dashboard hiển thị danh sách khóa học (accordion style)
    - Quản lý (Superuser, Phòng Tổng hợp): Xem tất cả khóa học và tất cả học viên
    - Nhân viên: Chỉ xem khóa học được giao và chỉ thấy bản thân
    """
    from .models import Course, CourseEnrollment, UserProfile

    # Check if user has permission to manage courses (create/edit/delete)
    has_permission = check_elearning_manage_permission(request.user)

    if has_permission:
        # Managers see all courses with all enrollments
        courses = Course.objects.all().prefetch_related('enrollments__user__profile')

        # Enrich courses with completion stats
        for course in courses:
            stats = course.get_completion_stats()
            course.completed_count = stats['completed']
            course.total_count = stats['total']

            # Get all enrollments with profile info
            enrollments = course.enrollments.select_related('user__profile').order_by('user__username')
            course.enrollment_list = enrollments
    else:
        # Regular employees only see courses they are enrolled in
        # Get courses where current user is enrolled
        enrolled_course_ids = CourseEnrollment.objects.filter(
            user=request.user
        ).values_list('course_id', flat=True)

        courses = Course.objects.filter(
            id__in=enrolled_course_ids
        ).prefetch_related('enrollments__user__profile')

        # Enrich courses - only show current user's enrollment
        for course in courses:
            # For regular users, show their own enrollment only
            user_enrollment = course.enrollments.filter(user=request.user).select_related('user__profile')
            course.enrollment_list = user_enrollment

            # Stats for this user only
            course.completed_count = user_enrollment.filter(is_completed=True).count()
            course.total_count = user_enrollment.count()

    context = {
        'courses': courses,
        'has_permission': has_permission,
    }
    return render(request, 'templates_app/course_dashboard.html', context)


@login_required
def course_create(request):
    """
    Tạo khóa học mới
    Chỉ Superuser và Phòng Tổng hợp có quyền
    """
    if not check_elearning_manage_permission(request.user):
        messages.error(request, 'Bạn không có quyền tạo khóa học')
        return redirect('course_dashboard')

    if request.method == 'POST':
        try:
            from .models import Course
            from datetime import datetime

            name = request.POST.get('name', '').strip()
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            description = request.POST.get('description', '').strip()

            # Validate
            if not name or not start_date or not end_date:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin')
                return redirect('course_create')

            # Parse dates
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

            if end_date_obj < start_date_obj:
                messages.error(request, 'Ngày kết thúc phải sau ngày bắt đầu')
                return redirect('course_create')

            # Create course
            course = Course.objects.create(
                name=name,
                start_date=start_date_obj,
                end_date=end_date_obj,
                description=description
            )

            messages.success(request, f'Đã tạo khóa học "{course.name}"')
            return redirect('course_dashboard')

        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('course_create')

    return render(request, 'templates_app/course_create.html')


@login_required
def course_add_students(request, course_id):
    """
    Thêm học viên vào khóa học
    Chỉ Superuser và Phòng Tổng hợp có quyền
    """
    from .models import Course, CourseEnrollment, UserProfile

    if not check_elearning_manage_permission(request.user):
        messages.error(request, 'Bạn không có quyền thêm học viên')
        return redirect('course_dashboard')

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        try:
            # Get filter criteria
            filter_type = request.POST.get('filter_type', 'individual')

            if filter_type == 'individual':
                # Add individual users
                user_ids = request.POST.getlist('user_ids')
                added_count = 0

                for user_id in user_ids:
                    user = User.objects.get(id=user_id)
                    enrollment, created = CourseEnrollment.objects.get_or_create(
                        course=course,
                        user=user
                    )
                    if created:
                        added_count += 1

                messages.success(request, f'Đã thêm {added_count} học viên vào khóa học')

            elif filter_type == 'bulk':
                # Bulk add by criteria
                job_function = request.POST.get('job_function', '')
                department = request.POST.get('department', '')
                position = request.POST.get('position', '')

                # Build query
                profiles = UserProfile.objects.all()

                if job_function:
                    profiles = profiles.filter(job_function=job_function)
                if department:
                    profiles = profiles.filter(department=department)
                if position:
                    profiles = profiles.filter(position=position)

                added_count = 0
                for profile in profiles:
                    enrollment, created = CourseEnrollment.objects.get_or_create(
                        course=course,
                        user=profile.user
                    )
                    if created:
                        added_count += 1

                messages.success(request, f'Đã thêm {added_count} học viên vào khóa học')

            return redirect('course_dashboard')

        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('course_add_students', course_id=course_id)

    # GET - show form
    # Get all users with profiles
    users_with_profiles = User.objects.filter(profile__isnull=False).select_related('profile').order_by('username')

    # Get already enrolled users
    enrolled_user_ids = course.enrollments.values_list('user_id', flat=True)

    context = {
        'course': course,
        'users': users_with_profiles,
        'enrolled_user_ids': list(enrolled_user_ids),
        'job_function_choices': UserProfile.JOB_FUNCTION_CHOICES,
        'department_choices': UserProfile.DEPARTMENT_CHOICES,
        'position_choices': UserProfile.POSITION_CHOICES,
    }

    return render(request, 'templates_app/course_add_students.html', context)


@login_required
def course_edit(request, course_id):
    """
    Chỉnh sửa khóa học
    Chỉ Superuser và Phòng Tổng hợp có quyền
    """
    from .models import Course

    if not check_elearning_manage_permission(request.user):
        messages.error(request, 'Bạn không có quyền chỉnh sửa khóa học')
        return redirect('course_dashboard')

    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        try:
            from datetime import datetime

            name = request.POST.get('name', '').strip()
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            description = request.POST.get('description', '').strip()

            # Validate
            if not name or not start_date or not end_date:
                messages.error(request, 'Vui lòng điền đầy đủ thông tin')
                return redirect('course_edit', course_id=course_id)

            # Parse dates
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()

            if end_date_obj < start_date_obj:
                messages.error(request, 'Ngày kết thúc phải sau ngày bắt đầu')
                return redirect('course_edit', course_id=course_id)

            # Update course
            course.name = name
            course.start_date = start_date_obj
            course.end_date = end_date_obj
            course.description = description
            course.save()

            messages.success(request, f'Đã cập nhật khóa học "{course.name}"')
            return redirect('course_dashboard')

        except Exception as e:
            messages.error(request, f'Lỗi: {str(e)}')
            return redirect('course_edit', course_id=course_id)

    context = {
        'course': course,
        'is_edit': True,
    }
    return render(request, 'templates_app/course_create.html', context)


@login_required
@require_http_methods(["POST"])
def course_delete(request, course_id):
    """
    Xóa khóa học
    Chỉ Superuser và Phòng Tổng hợp có quyền
    """
    from .models import Course

    if not check_elearning_manage_permission(request.user):
        return JsonResponse({
            'success': False,
            'error': 'Bạn không có quyền xóa khóa học'
        }, status=403)

    try:
        course = get_object_or_404(Course, id=course_id)
        course_name = course.name
        course.delete()

        return JsonResponse({
            'success': True,
            'message': f'Đã xóa khóa học "{course_name}"'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def course_remove_student(request, course_id, user_id):
    """
    Xóa học viên khỏi khóa học
    Chỉ Superuser và Phòng Tổng hợp có quyền
    """
    from .models import CourseEnrollment

    if not check_elearning_manage_permission(request.user):
        return JsonResponse({
            'success': False,
            'error': 'Bạn không có quyền xóa học viên'
        }, status=403)

    try:
        enrollment = get_object_or_404(
            CourseEnrollment,
            course_id=course_id,
            user_id=user_id
        )
        enrollment.delete()

        # Get updated stats
        from .models import Course
        course = get_object_or_404(Course, id=course_id)
        stats = course.get_completion_stats()

        return JsonResponse({
            'success': True,
            'message': 'Đã xóa học viên khỏi khóa học',
            'course_stats': {
                'completed': stats['completed'],
                'total': stats['total']
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def course_toggle_completion(request, enrollment_id):
    """
    AJAX endpoint để toggle trạng thái hoàn thành khóa học
    Chỉ Superuser và Phòng Tổng hợp có quyền
    """
    from .models import CourseEnrollment
    from django.utils import timezone

    if not check_elearning_manage_permission(request.user):
        return JsonResponse({
            'success': False,
            'error': 'Bạn không có quyền cập nhật'
        }, status=403)

    try:
        enrollment = get_object_or_404(CourseEnrollment, id=enrollment_id)

        # Toggle completion
        enrollment.is_completed = not enrollment.is_completed

        if enrollment.is_completed:
            enrollment.completion_date = timezone.now()
        else:
            enrollment.completion_date = None

        enrollment.save()

        # Get updated course stats
        course = enrollment.course
        stats = course.get_completion_stats()

        return JsonResponse({
            'success': True,
            'is_completed': enrollment.is_completed,
            'completion_date': enrollment.completion_date.strftime('%d/%m/%Y %H:%M') if enrollment.completion_date else None,
            'course_stats': {
                'completed': stats['completed'],
                'total': stats['total']
            }
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
