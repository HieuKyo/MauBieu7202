# Standard library imports
import json
import os
import re
import tempfile
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

# Django imports
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

# Third-party imports
import mammoth

# Local application imports
from .forms import DynamicTemplateForm, GlobalConfigForm
from .issueby_mapping import get_issueby_name
from .models import Category, Template, Variable, TemplateVariable, Customer, Business, GlobalConfig, BranchConfig, remove_vietnamese_diacritics
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
    Trang chủ - News Feed hiển thị chương trình khuyến mãi/tin tức
    """
    from .models import Promotion
    today = date.today()
    promotions = Promotion.objects.filter(
        is_active=True,
        end_date__gte=today,
    ).order_by('-created_at')

    context = {
        'promotions': promotions,
        'user': user if (user := request.user) else None,
        **_dashboard_alerts(request.user, today),
    }
    return render(request, 'templates_app/news_feed.html', context)


def _dashboard_alerts(user, today):
    """Số liệu cho khối 'Cần chú ý' ở trang chủ."""
    from tasks.models import Task
    from tasks.views import REMINDER_DAYS_AHEAD
    from .hdv_reg_views import _is_kiem_soat_vien, _pgd_status_counts

    hdv_cho_duyet, hdv_cho_add = _pgd_status_counts(user)

    my_tasks = Task.objects.filter(
        Q(created_by=user) | Q(assigned_to=user),
        is_completed=False,
        due_date__isnull=False,
    )
    task_qua_han = my_tasks.filter(due_date__lt=today).count()
    task_sap_den_han = my_tasks.filter(
        due_date__gte=today, due_date__lte=today + timedelta(days=REMINDER_DAYS_AHEAD),
    ).count()

    return {
        # Chỉ KSV mới duyệt được nên chỉ nhắc KSV
        'hdv_cho_duyet': hdv_cho_duyet if _is_kiem_soat_vien(user) else 0,
        'hdv_cho_add': hdv_cho_add,
        'task_qua_han': task_qua_han,
        'task_sap_den_han': task_sap_den_han,
        'task_reminder_days': REMINDER_DAYS_AHEAD,
    }


@login_required
def print_templates_view(request):
    """
    In mẫu biểu - Hiển thị danh sách khách hàng và mẫu biểu
    (Chức năng Dashboard cũ được di chuyển sang đây)
    """
    user = request.user

    # Lấy danh sách khách hàng
    customers = Customer.objects.all().order_by('-created_at')

    # Lấy danh sách doanh nghiệp
    businesses = Business.objects.all().order_by('-created_at')

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
        'businesses': businesses,
        'categories': categories,
        'user': user,
        # Địa danh in trên trang ảnh CCCD 2 mặt
        'dia_danh': BranchConfig.get_for_user(user).dia_danh,
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


# Trường để trống khi in → in dấu chấm để ghi tay (Mã khách hàng / CIF, Số tài khoản)
PRINT_EMPTY_DOTS = '.........................'
PRINT_DOTS_FIELDS = ('ma_khach_hang', 'cif', 'so_tai_khoan')


def fill_empty_print_fields(data):
    """Chỉ dùng cho dữ liệu đưa vào file Word, KHÔNG dùng cho dữ liệu lưu khách hàng."""
    for field in PRINT_DOTS_FIELDS:
        if not str(data.get(field) or '').strip():
            data[field] = PRINT_EMPTY_DOTS
    return data


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
        branch_config = BranchConfig.get_for_user(request.user)
        data.update(branch_config.get_all_variables())

        # Merge toàn bộ customer data nếu có customer
        # Customer data có priority thấp hơn - không overwrite form data
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                customer_data = customer.get_data_dict()
                # Merge: customer data first, then overlay with session data
                # This ensures form inputs take precedence over customer defaults
                for key, value in customer_data.items():
                    if key not in data or data[key] in ('', None):
                        data[key] = value
            except Customer.DoesNotExist:
                pass

        fill_empty_print_fields(data)

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
        {'name': 'gcndkdn', 'description': 'Giấy chứng nhận đăng ký kinh doanh', 'example': '0123456789'},
        {'name': 'mst_chi_nhanh', 'description': 'Mã số thuế chi nhánh', 'example': '0123456789-001'},
        {'name': 'nguoi_dai_dien', 'description': 'Người đại diện', 'example': 'Nguyễn Văn A'},
        {'name': 'chuc_vu', 'description': 'Chức vụ', 'example': 'Giám đốc'},
        {'name': 'so_uy_quyen', 'description': 'Số uỷ quyền', 'example': '123/UQ-HĐQT'},
        {'name': 'ngay_uy_quyen', 'description': 'Ngày uỷ quyền', 'example': '15/12/2024'},
        {'name': 'dien_thoai_chi_nhanh', 'description': 'Điện thoại chi nhánh', 'example': '0291.3822468'},
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

    # 4. Biến ATM - From ATM replenishment
    atm_variables = [
        # Thông tin máy ATM
        {'name': 'atm_machine_id', 'description': 'ID máy ATM', 'example': 'ATM-001'},
        {'name': 'atm_serial_number', 'description': 'Số Serial máy ATM', 'example': 'SN123456789'},
        {'name': 'atm_address', 'description': 'Địa chỉ lắp đặt máy ATM', 'example': '123 Đường ABC, Phường XYZ'},
        {'name': 'atm_machine_type', 'description': 'Loại máy ATM', 'example': 'NCR'},
        {'name': 'atm_machine_line', 'description': 'Dòng máy ATM', 'example': 'SelfServ'},
        {'name': 'atm_installation_date', 'description': 'Ngày lắp đặt máy ATM (dd/mm/yyyy)', 'example': '15/01/2023'},

        # Date variables - Ngày lắp đặt
        {'name': 'atm_ld_d1', 'description': 'Ngày lắp đặt - Chữ số thứ nhất', 'example': '1'},
        {'name': 'atm_ld_d2', 'description': 'Ngày lắp đặt - Chữ số thứ hai', 'example': '5'},
        {'name': 'atm_ld_m1', 'description': 'Tháng lắp đặt - Chữ số thứ nhất', 'example': '0'},
        {'name': 'atm_ld_m2', 'description': 'Tháng lắp đặt - Chữ số thứ hai', 'example': '1'},
        {'name': 'atm_ld_y1', 'description': 'Năm lắp đặt - Chữ số thứ nhất', 'example': '2'},
        {'name': 'atm_ld_y2', 'description': 'Năm lắp đặt - Chữ số thứ hai', 'example': '0'},
        {'name': 'atm_ld_y3', 'description': 'Năm lắp đặt - Chữ số thứ ba', 'example': '2'},
        {'name': 'atm_ld_y4', 'description': 'Năm lắp đặt - Chữ số thứ tư', 'example': '3'},

        # Thông tin tiếp quỹ
        {'name': 'replenishment_date', 'description': 'Ngày tiếp quỹ (dd/mm/yyyy)', 'example': '20/12/2024'},

        # Date variables - Ngày tiếp quỹ
        {'name': 'tq_d1', 'description': 'Ngày tiếp quỹ - Chữ số thứ nhất', 'example': '2'},
        {'name': 'tq_d2', 'description': 'Ngày tiếp quỹ - Chữ số thứ hai', 'example': '0'},
        {'name': 'tq_m1', 'description': 'Tháng tiếp quỹ - Chữ số thứ nhất', 'example': '1'},
        {'name': 'tq_m2', 'description': 'Tháng tiếp quỹ - Chữ số thứ hai', 'example': '2'},
        {'name': 'tq_y1', 'description': 'Năm tiếp quỹ - Chữ số thứ nhất', 'example': '2'},
        {'name': 'tq_y2', 'description': 'Năm tiếp quỹ - Chữ số thứ hai', 'example': '0'},
        {'name': 'tq_y3', 'description': 'Năm tiếp quỹ - Chữ số thứ ba', 'example': '2'},
        {'name': 'tq_y4', 'description': 'Năm tiếp quỹ - Chữ số thứ tư', 'example': '4'},

        # Số lượng tờ tiền
        {'name': 'bills_50k', 'description': 'Số tờ 50.000đ', 'example': '100'},
        {'name': 'bills_100k', 'description': 'Số tờ 100.000đ', 'example': '200'},
        {'name': 'bills_200k', 'description': 'Số tờ 200.000đ', 'example': '150'},
        {'name': 'bills_500k', 'description': 'Số tờ 500.000đ', 'example': '300'},

        # Thành tiền
        {'name': 'amount_50k', 'description': 'Thành tiền mệnh giá 50k (có dấu phẩy)', 'example': '5,000,000'},
        {'name': 'amount_100k', 'description': 'Thành tiền mệnh giá 100k (có dấu phẩy)', 'example': '20,000,000'},
        {'name': 'amount_200k', 'description': 'Thành tiền mệnh giá 200k (có dấu phẩy)', 'example': '30,000,000'},
        {'name': 'amount_500k', 'description': 'Thành tiền mệnh giá 500k (có dấu phẩy)', 'example': '150,000,000'},
        {'name': 'total_amount', 'description': 'Tổng số tiền tiếp quỹ (có dấu phẩy)', 'example': '205,000,000'},
        {'name': 'total_amount_words', 'description': 'Số tiền bằng chữ', 'example': 'Hai trăm lẻ năm triệu đồng'},

        # Thông tin phương tiện
        {'name': 'vehicle_license_plate', 'description': 'Biển số xe vận chuyển', 'example': '94A - 021.46'},
        {'name': 'vehicle_type', 'description': 'Loại xe', 'example': 'Xe tải'},

        # Thông tin tài xế
        {'name': 'driver_full_name', 'description': 'Họ tên tài xế', 'example': 'Nguyễn Văn A'},
        {'name': 'driver_id_number', 'description': 'Số CCCD tài xế', 'example': '001234567890'},
        {'name': 'driver_id_issue_date', 'description': 'Ngày cấp CCCD tài xế (dd/mm/yyyy)', 'example': '01/01/2020'},
        {'name': 'driver_id_issue_place', 'description': 'Nơi cấp CCCD tài xế', 'example': 'CA Bạc Liêu'},

        # Date variables - CCCD tài xế
        {'name': 'tx_d1', 'description': 'Ngày cấp CCCD tài xế - Chữ số thứ nhất', 'example': '0'},
        {'name': 'tx_d2', 'description': 'Ngày cấp CCCD tài xế - Chữ số thứ hai', 'example': '1'},
        {'name': 'tx_m1', 'description': 'Tháng cấp CCCD tài xế - Chữ số thứ nhất', 'example': '0'},
        {'name': 'tx_m2', 'description': 'Tháng cấp CCCD tài xế - Chữ số thứ hai', 'example': '1'},
        {'name': 'tx_y1', 'description': 'Năm cấp CCCD tài xế - Chữ số thứ nhất', 'example': '2'},
        {'name': 'tx_y2', 'description': 'Năm cấp CCCD tài xế - Chữ số thứ hai', 'example': '0'},
        {'name': 'tx_y3', 'description': 'Năm cấp CCCD tài xế - Chữ số thứ ba', 'example': '2'},
        {'name': 'tx_y4', 'description': 'Năm cấp CCCD tài xế - Chữ số thứ tư', 'example': '0'},

        # Thông tin bảo vệ
        {'name': 'guard_full_name', 'description': 'Họ tên bảo vệ', 'example': 'Trần Văn B'},
        {'name': 'guard_id_number', 'description': 'Số CCCD bảo vệ', 'example': '001234567891'},
        {'name': 'guard_id_issue_date', 'description': 'Ngày cấp CCCD bảo vệ (dd/mm/yyyy)', 'example': '01/01/2020'},
        {'name': 'guard_id_issue_place', 'description': 'Nơi cấp CCCD bảo vệ', 'example': 'CA Bạc Liêu'},

        # Date variables - CCCD bảo vệ
        {'name': 'bv_d1', 'description': 'Ngày cấp CCCD bảo vệ - Chữ số thứ nhất', 'example': '0'},
        {'name': 'bv_d2', 'description': 'Ngày cấp CCCD bảo vệ - Chữ số thứ hai', 'example': '1'},
        {'name': 'bv_m1', 'description': 'Tháng cấp CCCD bảo vệ - Chữ số thứ nhất', 'example': '0'},
        {'name': 'bv_m2', 'description': 'Tháng cấp CCCD bảo vệ - Chữ số thứ hai', 'example': '1'},
        {'name': 'bv_y1', 'description': 'Năm cấp CCCD bảo vệ - Chữ số thứ nhất', 'example': '2'},
        {'name': 'bv_y2', 'description': 'Năm cấp CCCD bảo vệ - Chữ số thứ hai', 'example': '0'},
        {'name': 'bv_y3', 'description': 'Năm cấp CCCD bảo vệ - Chữ số thứ ba', 'example': '2'},
        {'name': 'bv_y4', 'description': 'Năm cấp CCCD bảo vệ - Chữ số thứ tư', 'example': '0'},

        # Ban quản lý ATM
        {'name': 'team_leader_name', 'description': 'Họ tên Trưởng Ban quản lý ATM', 'example': 'Nguyễn Văn C'},
        {'name': 'team_leader_title', 'description': 'Chức danh Trưởng Ban', 'example': 'Trưởng Ban'},
        {'name': 'treasury_head_name', 'description': 'Họ tên Trưởng phòng KTNQ', 'example': 'Trần Văn D'},
        {'name': 'treasury_head_title', 'description': 'Chức danh Trưởng phòng KTNQ', 'example': 'Trưởng phòng'},
        {'name': 'atm_officer_name', 'description': 'Họ tên Cán bộ phụ trách ATM', 'example': 'Lê Văn E'},
        {'name': 'atm_officer_title', 'description': 'Chức danh Cán bộ phụ trách ATM', 'example': 'Cán bộ'},
        {'name': 'board_decision_number', 'description': 'Số quyết định thành lập Ban quản lý ATM', 'example': '123/QĐ-NHNo-GR'},
        {'name': 'board_decision_date', 'description': 'Ngày quyết định thành lập Ban quản lý ATM', 'example': 'ngày 01 tháng 01 năm 2024'},
        {'name': 'travel_order_number', 'description': 'Số văn bản giấy đi đường — tự động tăng dần theo năm (sang năm mới reset về 1), gán 1 lần duy nhất khi tạo phiếu tiếp quỹ', 'example': '15'},

        # Metadata
        {'name': 'created_by', 'description': 'Username người tạo phiếu tiếp quỹ', 'example': 'admin'},
        {'name': 'created_at', 'description': 'Thời gian tạo phiếu (dd/mm/yyyy HH:MM)', 'example': '20/12/2024 14:30'},
    ]

    # Biến giao dịch thừa/thiếu quỹ ATM
    atm_discrepancy_variables = [
        # Thông tin máy ATM
        {'name': 'disc_atm_machine_id', 'description': 'ID máy ATM', 'example': 'ATM-001'},
        {'name': 'disc_atm_serial_number', 'description': 'Số Serial máy ATM', 'example': 'SN123456789'},
        {'name': 'disc_atm_address', 'description': 'Địa chỉ lắp đặt máy ATM', 'example': '123 Đường ABC, Phường XYZ'},
        {'name': 'disc_atm_machine_type', 'description': 'Loại máy ATM', 'example': 'NCR'},
        {'name': 'disc_atm_machine_line', 'description': 'Dòng máy ATM', 'example': 'SelfServ'},

        # Thông tin khách hàng/Giao dịch
        {'name': 'disc_full_name', 'description': 'Họ tên khách hàng', 'example': 'Nguyễn Văn A'},
        {'name': 'disc_account_number', 'description': 'Số tài khoản', 'example': '0123456789'},
        {'name': 'disc_card_number', 'description': 'Số thẻ', 'example': '9704123456789012'},
        {'name': 'disc_trace_number', 'description': 'Số trace', 'example': '123456'},
        {'name': 'disc_transaction_id', 'description': 'ID giao dịch', 'example': 'TXN20241220123456'},

        # Thông tin thừa/thiếu
        {'name': 'disc_type', 'description': 'Loại giao dịch (Thừa/Thiếu)', 'example': 'Thừa'},
        {'name': 'disc_amount', 'description': 'Số tiền thừa/thiếu (có dấu phẩy)', 'example': '500,000'},
        {'name': 'disc_amount_words', 'description': 'Số tiền bằng chữ', 'example': 'Năm trăm nghìn đồng'},

        # Chu kỳ kiểm quỹ - Ngày bắt đầu
        {'name': 'disc_audit_cycle_start', 'description': 'Ngày bắt đầu chu kỳ kiểm quỹ (dd/mm/yyyy)', 'example': '01/12/2024'},
        {'name': 'acs_d1', 'description': 'Ngày bắt đầu - Chữ số thứ nhất', 'example': '0'},
        {'name': 'acs_d2', 'description': 'Ngày bắt đầu - Chữ số thứ hai', 'example': '1'},
        {'name': 'acs_m1', 'description': 'Tháng bắt đầu - Chữ số thứ nhất', 'example': '1'},
        {'name': 'acs_m2', 'description': 'Tháng bắt đầu - Chữ số thứ hai', 'example': '2'},
        {'name': 'acs_y1', 'description': 'Năm bắt đầu - Chữ số thứ nhất', 'example': '2'},
        {'name': 'acs_y2', 'description': 'Năm bắt đầu - Chữ số thứ hai', 'example': '0'},
        {'name': 'acs_y3', 'description': 'Năm bắt đầu - Chữ số thứ ba', 'example': '2'},
        {'name': 'acs_y4', 'description': 'Năm bắt đầu - Chữ số thứ tư', 'example': '4'},

        # Chu kỳ kiểm quỹ - Ngày kết thúc
        {'name': 'disc_audit_cycle_end', 'description': 'Ngày kết thúc chu kỳ kiểm quỹ (dd/mm/yyyy)', 'example': '31/12/2024'},
        {'name': 'ace_d1', 'description': 'Ngày kết thúc - Chữ số thứ nhất', 'example': '3'},
        {'name': 'ace_d2', 'description': 'Ngày kết thúc - Chữ số thứ hai', 'example': '1'},
        {'name': 'ace_m1', 'description': 'Tháng kết thúc - Chữ số thứ nhất', 'example': '1'},
        {'name': 'ace_m2', 'description': 'Tháng kết thúc - Chữ số thứ hai', 'example': '2'},
        {'name': 'ace_y1', 'description': 'Năm kết thúc - Chữ số thứ nhất', 'example': '2'},
        {'name': 'ace_y2', 'description': 'Năm kết thúc - Chữ số thứ hai', 'example': '0'},
        {'name': 'ace_y3', 'description': 'Năm kết thúc - Chữ số thứ ba', 'example': '2'},
        {'name': 'ace_y4', 'description': 'Năm kết thúc - Chữ số thứ tư', 'example': '4'},

        # Trạng thái và ghi chú
        {'name': 'disc_status', 'description': 'Trạng thái xử lý', 'example': 'Chờ xử lý'},
        {'name': 'disc_notes', 'description': 'Ghi chú', 'example': 'Đã liên hệ khách hàng'},

        # Ban quản lý ATM
        {'name': 'disc_team_leader_name', 'description': 'Họ tên Trưởng Ban quản lý ATM', 'example': 'Nguyễn Văn C'},
        {'name': 'disc_team_leader_title', 'description': 'Chức danh Trưởng Ban', 'example': 'Trưởng Ban'},
        {'name': 'disc_treasury_head_name', 'description': 'Họ tên Trưởng phòng KTNQ', 'example': 'Trần Văn D'},
        {'name': 'disc_treasury_head_title', 'description': 'Chức danh Trưởng phòng KTNQ', 'example': 'Trưởng phòng'},
        {'name': 'disc_atm_officer_name', 'description': 'Họ tên Cán bộ phụ trách ATM', 'example': 'Lê Văn E'},
        {'name': 'disc_atm_officer_title', 'description': 'Chức danh Cán bộ phụ trách ATM', 'example': 'Cán bộ'},
        {'name': 'disc_board_decision_number', 'description': 'Số quyết định thành lập Ban quản lý ATM', 'example': '123/QĐ-NHNo-GR'},
        {'name': 'disc_board_decision_date', 'description': 'Ngày quyết định thành lập Ban quản lý ATM', 'example': 'ngày 01 tháng 01 năm 2024'},

        # Metadata
        {'name': 'disc_created_by', 'description': 'Username người tạo giao dịch', 'example': 'admin'},
        {'name': 'disc_created_at', 'description': 'Thời gian tạo giao dịch (dd/mm/yyyy HH:MM)', 'example': '20/12/2024 14:30'},
    ]

    # 5. Biến Doanh nghiệp - From Business model
    business_variables = [
        # Thông tin doanh nghiệp cơ bản
        {'name': 'dn_cif', 'description': 'Mã CIF doanh nghiệp', 'example': 'DN001'},
        {'name': 'dn_so_tai_khoan', 'description': 'Số tài khoản doanh nghiệp', 'example': '1234567890'},
        {'name': 'dn_ten', 'description': 'Tên doanh nghiệp (alias)', 'example': 'Công ty TNHH ABC'},
        {'name': 'dn_ten_doanh_nghiep', 'description': 'Tên doanh nghiệp', 'example': 'Công ty TNHH ABC'},
        {'name': 'dn_ten_bang_hieu', 'description': 'Tên bảng hiệu', 'example': 'Siêu thị ABC'},
        {'name': 'dn_ten_viet_tat', 'description': 'Tên viết tắt doanh nghiệp (chữ cái đầu)', 'example': 'HKDNVA từ HKD Nguyễn Văn A'},
        {'name': 'dn_ten_khong_tien_to', 'description': 'Tên DN không có tiền tố (bỏ HKD/DNTN/CTCP...)', 'example': 'Nguyễn Văn A từ HKD Nguyễn Văn A'},

        # Giấy tờ định danh
        {'name': 'dn_loai_giay_to', 'description': 'Loại giấy tờ (GCN/DKKD/QĐ thành lập)', 'example': 'Giấy chứng nhận đăng ký doanh nghiệp'},
        {'name': 'dn_so_gcn', 'description': 'Số giấy chứng nhận', 'example': '0123456789'},
        {'name': 'dn_ngay_cap_gcn', 'description': 'Ngày cấp GCN (dd/mm/yyyy)', 'example': '15/01/2020'},
        {'name': 'dn_noi_cap_gcn', 'description': 'Nơi cấp GCN', 'example': 'Sở Kế hoạch và Đầu tư TP. HCM'},
        # Từng chữ số GCN (13 chữ số)
        {'name': 'dn_so_gcn_1', 'description': 'GCN - Chữ số thứ 1', 'example': '0'},
        {'name': 'dn_so_gcn_2', 'description': 'GCN - Chữ số thứ 2', 'example': '1'},
        {'name': 'dn_so_gcn_3', 'description': 'GCN - Chữ số thứ 3', 'example': '2'},
        {'name': 'dn_so_gcn_4', 'description': 'GCN - Chữ số thứ 4', 'example': '3'},
        {'name': 'dn_so_gcn_5', 'description': 'GCN - Chữ số thứ 5', 'example': '4'},
        {'name': 'dn_so_gcn_6', 'description': 'GCN - Chữ số thứ 6', 'example': '5'},
        {'name': 'dn_so_gcn_7', 'description': 'GCN - Chữ số thứ 7', 'example': '6'},
        {'name': 'dn_so_gcn_8', 'description': 'GCN - Chữ số thứ 8', 'example': '7'},
        {'name': 'dn_so_gcn_9', 'description': 'GCN - Chữ số thứ 9', 'example': '8'},
        {'name': 'dn_so_gcn_10', 'description': 'GCN - Chữ số thứ 10', 'example': '9'},
        {'name': 'dn_so_gcn_11', 'description': 'GCN - Chữ số thứ 11', 'example': '0'},
        {'name': 'dn_so_gcn_12', 'description': 'GCN - Chữ số thứ 12', 'example': '1'},
        {'name': 'dn_so_gcn_13', 'description': 'GCN - Chữ số thứ 13', 'example': '2'},

        # Mã số thuế
        {'name': 'dn_ma_so_thue', 'description': 'Mã số thuế', 'example': '0123456789'},
        {'name': 'dn_mst', 'description': 'Mã số thuế (alias)', 'example': '0123456789'},
        {'name': 'dn_ngay_cap_mst', 'description': 'Ngày cấp MST (dd/mm/yyyy)', 'example': '15/01/2020'},
        {'name': 'dn_noi_cap_mst', 'description': 'Nơi cấp MST', 'example': 'Chi cục thuế quận 1'},
        # Từng chữ số MST (13 chữ số - HKD có 13 số)
        {'name': 'dn_mst_1', 'description': 'MST - Chữ số thứ 1', 'example': '0'},
        {'name': 'dn_mst_2', 'description': 'MST - Chữ số thứ 2', 'example': '1'},
        {'name': 'dn_mst_3', 'description': 'MST - Chữ số thứ 3', 'example': '2'},
        {'name': 'dn_mst_4', 'description': 'MST - Chữ số thứ 4', 'example': '3'},
        {'name': 'dn_mst_5', 'description': 'MST - Chữ số thứ 5', 'example': '4'},
        {'name': 'dn_mst_6', 'description': 'MST - Chữ số thứ 6', 'example': '5'},
        {'name': 'dn_mst_7', 'description': 'MST - Chữ số thứ 7', 'example': '6'},
        {'name': 'dn_mst_8', 'description': 'MST - Chữ số thứ 8', 'example': '7'},
        {'name': 'dn_mst_9', 'description': 'MST - Chữ số thứ 9', 'example': '8'},
        {'name': 'dn_mst_10', 'description': 'MST - Chữ số thứ 10', 'example': '9'},
        {'name': 'dn_mst_11', 'description': 'MST - Chữ số thứ 11', 'example': '0'},
        {'name': 'dn_mst_12', 'description': 'MST - Chữ số thứ 12', 'example': '1'},
        {'name': 'dn_mst_13', 'description': 'MST - Chữ số thứ 13', 'example': '2'},

        # Liên hệ và kinh doanh
        {'name': 'dn_dia_chi', 'description': 'Địa chỉ doanh nghiệp', 'example': '123 Nguyễn Huệ, Q1, TP.HCM'},
        {'name': 'dn_dien_thoai', 'description': 'Số điện thoại', 'example': '0281234567'},
        {'name': 'dn_linh_vuc_kinh_doanh', 'description': 'Lĩnh vực hoạt động kinh doanh', 'example': 'Sản xuất và kinh doanh'},
        {'name': 'dn_von_dieu_le', 'description': 'Vốn điều lệ (đã format)', 'example': '10.000.000.000'},
        {'name': 'dn_von_dieu_le_raw', 'description': 'Vốn điều lệ (số)', 'example': '10000000000'},

        # Người đại diện pháp luật
        {'name': 'dn_nguoi_dai_dien_ho_ten', 'description': 'NĐD - Họ và tên', 'example': 'Nguyễn Văn A'},
        {'name': 'dn_ndd_ho_ten', 'description': 'NĐD - Họ và tên (alias ngắn)', 'example': 'Nguyễn Văn A'},
        {'name': 'dn_nguoi_dai_dien_ngay_sinh', 'description': 'NĐD - Ngày sinh (dd/mm/yyyy)', 'example': '01/01/1980'},
        {'name': 'dn_ndd_ngay_sinh', 'description': 'NĐD - Ngày sinh (alias)', 'example': '01/01/1980'},
        {'name': 'dn_nguoi_dai_dien_gioi_tinh', 'description': 'NĐD - Giới tính', 'example': 'Nam'},
        {'name': 'dn_ndd_gioi_tinh', 'description': 'NĐD - Giới tính (alias)', 'example': 'Nam'},
        {'name': 'dn_ndd_gioi_tinh_nam', 'description': 'NĐD - Checkbox ☑/☐ khi giới tính Nam', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ndd_gioi_tinh_nu', 'description': 'NĐD - Checkbox ☑/☐ khi giới tính Nữ', 'example': '☑ hoặc ☐'},
        {'name': 'dn_nguoi_dai_dien_nghe_nghiep', 'description': 'NĐD - Nghề nghiệp', 'example': 'Doanh nhân'},
        {'name': 'dn_ndd_nghe_nghiep', 'description': 'NĐD - Nghề nghiệp (alias)', 'example': 'Doanh nhân'},
        {'name': 'dn_nguoi_dai_dien_dien_thoai', 'description': 'NĐD - Số điện thoại', 'example': '0987654321'},
        {'name': 'dn_ndd_dien_thoai', 'description': 'NĐD - Số điện thoại (alias)', 'example': '0987654321'},
        {'name': 'dn_nguoi_dai_dien_loai_giay_to', 'description': 'NĐD - Loại giấy tờ', 'example': 'Căn cước công dân'},
        {'name': 'dn_ndd_loai_giay_to', 'description': 'NĐD - Loại giấy tờ (alias)', 'example': 'Căn cước công dân'},
        {'name': 'dn_ndd_loai_giay_to_cccd', 'description': 'NĐD - Checkbox ☑/☐ khi loại giấy tờ là CCCD', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ndd_loai_giay_to_cccd_chip', 'description': 'NĐD - Checkbox ☑/☐ khi loại giấy tờ là CCCD có chip', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ndd_loai_giay_to_cmnd', 'description': 'NĐD - Checkbox ☑/☐ khi loại giấy tờ là CMND', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ndd_loai_giay_to_passport', 'description': 'NĐD - Checkbox ☑/☐ khi loại giấy tờ là Passport', 'example': '☑ hoặc ☐'},
        {'name': 'dn_nguoi_dai_dien_so_cccd', 'description': 'NĐD - Số CCCD/CMND', 'example': '001234567890'},
        {'name': 'dn_ndd_so_cccd', 'description': 'NĐD - Số CCCD/CMND (alias)', 'example': '001234567890'},
        {'name': 'dn_nguoi_dai_dien_ngay_cap', 'description': 'NĐD - Ngày cấp (dd/mm/yyyy)', 'example': '01/01/2020'},
        {'name': 'dn_ndd_ngay_cap', 'description': 'NĐD - Ngày cấp (alias)', 'example': '01/01/2020'},
        {'name': 'dn_nguoi_dai_dien_noi_cap', 'description': 'NĐD - Nơi cấp', 'example': 'CA TP.HCM'},
        {'name': 'dn_ndd_noi_cap', 'description': 'NĐD - Nơi cấp (alias)', 'example': 'CA TP.HCM'},
        {'name': 'dn_nguoi_dai_dien_ngay_het_han', 'description': 'NĐD - Ngày hết hạn (dd/mm/yyyy)', 'example': '01/01/2035'},
        {'name': 'dn_ndd_ngay_het_han', 'description': 'NĐD - Ngày hết hạn (alias)', 'example': '01/01/2035'},
        {'name': 'dn_nguoi_dai_dien_noi_o_hien_tai', 'description': 'NĐD - Nơi ở hiện tại', 'example': '123 Lê Lợi, Q1, TP.HCM'},
        {'name': 'dn_ndd_noi_o_hien_tai', 'description': 'NĐD - Nơi ở hiện tại (alias)', 'example': '123 Lê Lợi, Q1, TP.HCM'},

        # Kế toán trưởng
        {'name': 'dn_ke_toan_truong_ho_ten', 'description': 'KTT - Họ và tên', 'example': 'Trần Thị B'},
        {'name': 'dn_ktt_ho_ten', 'description': 'KTT - Họ và tên (alias ngắn)', 'example': 'Trần Thị B'},
        {'name': 'dn_ke_toan_truong_ngay_sinh', 'description': 'KTT - Ngày sinh (dd/mm/yyyy)', 'example': '15/05/1985'},
        {'name': 'dn_ktt_ngay_sinh', 'description': 'KTT - Ngày sinh (alias)', 'example': '15/05/1985'},
        {'name': 'dn_ke_toan_truong_gioi_tinh', 'description': 'KTT - Giới tính', 'example': 'Nữ'},
        {'name': 'dn_ktt_gioi_tinh', 'description': 'KTT - Giới tính (alias)', 'example': 'Nữ'},
        {'name': 'dn_ktt_gioi_tinh_nam', 'description': 'KTT - Checkbox ☑/☐ khi giới tính Nam', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ktt_gioi_tinh_nu', 'description': 'KTT - Checkbox ☑/☐ khi giới tính Nữ', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ke_toan_truong_nghe_nghiep', 'description': 'KTT - Nghề nghiệp', 'example': 'Kế toán'},
        {'name': 'dn_ktt_nghe_nghiep', 'description': 'KTT - Nghề nghiệp (alias)', 'example': 'Kế toán'},
        {'name': 'dn_ke_toan_truong_dien_thoai', 'description': 'KTT - Số điện thoại', 'example': '0912345678'},
        {'name': 'dn_ktt_dien_thoai', 'description': 'KTT - Số điện thoại (alias)', 'example': '0912345678'},
        {'name': 'dn_ke_toan_truong_loai_giay_to', 'description': 'KTT - Loại giấy tờ', 'example': 'Căn cước công dân'},
        {'name': 'dn_ktt_loai_giay_to', 'description': 'KTT - Loại giấy tờ (alias)', 'example': 'Căn cước công dân'},
        {'name': 'dn_ktt_loai_giay_to_cccd', 'description': 'KTT - Checkbox ☑/☐ khi loại giấy tờ là CCCD', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ktt_loai_giay_to_cccd_chip', 'description': 'KTT - Checkbox ☑/☐ khi loại giấy tờ là CCCD có chip', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ktt_loai_giay_to_cmnd', 'description': 'KTT - Checkbox ☑/☐ khi loại giấy tờ là CMND', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ktt_loai_giay_to_passport', 'description': 'KTT - Checkbox ☑/☐ khi loại giấy tờ là Passport', 'example': '☑ hoặc ☐'},
        {'name': 'dn_ke_toan_truong_so_cccd', 'description': 'KTT - Số CCCD/CMND', 'example': '001234567891'},
        {'name': 'dn_ktt_so_cccd', 'description': 'KTT - Số CCCD/CMND (alias)', 'example': '001234567891'},
        {'name': 'dn_ke_toan_truong_ngay_cap', 'description': 'KTT - Ngày cấp (dd/mm/yyyy)', 'example': '01/01/2020'},
        {'name': 'dn_ktt_ngay_cap', 'description': 'KTT - Ngày cấp (alias)', 'example': '01/01/2020'},
        {'name': 'dn_ke_toan_truong_noi_cap', 'description': 'KTT - Nơi cấp', 'example': 'CA TP.HCM'},
        {'name': 'dn_ktt_noi_cap', 'description': 'KTT - Nơi cấp (alias)', 'example': 'CA TP.HCM'},
        {'name': 'dn_ke_toan_truong_ngay_het_han', 'description': 'KTT - Ngày hết hạn (dd/mm/yyyy)', 'example': '01/01/2035'},
        {'name': 'dn_ktt_ngay_het_han', 'description': 'KTT - Ngày hết hạn (alias)', 'example': '01/01/2035'},
        {'name': 'dn_ke_toan_truong_noi_o_hien_tai', 'description': 'KTT - Nơi ở hiện tại', 'example': '456 Hai Bà Trưng, Q3, TP.HCM'},
        {'name': 'dn_ktt_noi_o_hien_tai', 'description': 'KTT - Nơi ở hiện tại (alias)', 'example': '456 Hai Bà Trưng, Q3, TP.HCM'},
    ]
    tax_var_names = [
        'ten_nguoi_nop', 'ma_so_thue', 'dia_chi', 'ngay_lap',
        'tinh', 'co_quan_thue', 'xa_phuong', 'ma_co_quan_thu',
        'ten_co_quan_thu', 'ma_dia_ban', 'kho_bac',
        'tong_so_tien', 'so_tien_bang_chu',
        'items', 'item.stt', 'item.ma_tieu_muc', 'item.noi_dung', 'item.so_tien'
    ]
    tax_variables = Variable.objects.filter(name__in=tax_var_names)
    # 6. Biến Tùy chỉnh - From GlobalConfig.custom_variables
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
        'business_variables': business_variables,
        'date_variables': date_variables,
        'service_variables': service_variables,
        'calc_variables': calc_variables,
        'jinja_filters': jinja_filters,
        'jinja_syntax': jinja_syntax,
        'branch_variables': branch_variables,
        'atm_variables': atm_variables,
        'atm_discrepancy_variables': atm_discrepancy_variables,
        'custom_variables': custom_variables,
        'tax_variables': tax_variables,
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
            'description': t.description,
            'preset_values': t.preset_values or {},
            'required_fields': t.required_fields or [],
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

        # Trường bắt buộc của mẫu (vd. Số điện thoại với mẫu Phát hành thẻ Học sinh)
        missing = [f for f in (template.required_fields or []) if not request.POST.get(f, '').strip()]
        if missing:
            labels = {'so_dien_thoai': 'Số điện thoại', 'email': 'Email', 'so_tai_khoan': 'Số tài khoản',
                      'ma_khach_hang': 'Mã khách hàng', 'dia_chi': 'Địa chỉ', 'ngay_sinh': 'Ngày sinh'}
            return HttpResponse('Thiếu thông tin bắt buộc: ' + ', '.join(labels.get(f, f) for f in missing), status=400)

        # Lấy BranchConfig cho user
        config = BranchConfig.get_for_user(request.user)

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
        data['so_the_atm'] = request.POST.get('so_the_atm', '')
        data['so_the'] = data['so_the_atm']  # Alias for convenience

        # FIX: Split card number into individual digits (sothe_1 to sothe_16)
        so_the = data['so_the_atm'] or ''
        so_the_cleaned = ''.join(filter(str.isdigit, so_the))
        so_the_padded = so_the_cleaned.ljust(16)
        for i in range(1, 17):
            data[f'sothe_{i}'] = so_the_padded[i-1] if i <= len(so_the_cleaned) else ''

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
            except (ValueError, TypeError):
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
            except (ValueError, TypeError):
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
            except (ValueError, TypeError):
                # Invalid date format or type - set to None to avoid errors
                data['ngay_het_han_cmnd_obj'] = None

        # Ngày hiện tại cho tính toán (Date object)
        from datetime import datetime
        data['ngay_hien_tai_obj'] = datetime.now().date()  # Date object for calculations

        # Service-specific account and phone logic
        # If Agribank Plus is selected, show account and phone for AP
        if data['dv_bankplus'] == '☑':
            data['so_tai_khoan_AP'] = data['so_tai_khoan']
            data['so_dien_thoai_AP'] = data['so_dien_thoai']
        else:
            data['so_tai_khoan_AP'] = ''
            data['so_dien_thoai_AP'] = ''

        # If SMS Banking is selected, show account and phone for SMS
        if data['dv_sms_banking'] == '☑':
            data['so_tai_khoan_SMS'] = data['so_tai_khoan']
            data['so_dien_thoai_SMS'] = data['so_dien_thoai']
        else:
            data['so_tai_khoan_SMS'] = ''
            data['so_dien_thoai_SMS'] = ''

        # Lỗi khi lưu khách hàng (file Word vẫn tạo) → báo về trang qua header X-Customer-Save-Error
        customer_save_error = ''

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
                customer_save_error = _customer_error_text(e)   # continue with document generation
        else:
            # No customer_id provided - this is a new customer
            # Create or update customer from form data
            try:
                from datetime import datetime
                import logging
                logger = logging.getLogger(__name__)

                # Only process if we have required fields
                so_cmnd = data.get('so_cmnd', '').strip()
                ho_ten = data.get('ho_ten', '').strip()

                if so_cmnd and ho_ten:
                    # Prepare customer data
                    customer_data = {
                        'ma_khach_hang': data.get('ma_khach_hang', ''),
                        'ho_ten': ho_ten,
                        'ho_ten_tieng_anh': data.get('ho_ten_tieng_anh', ''),
                        'gioi_tinh': data.get('gioi_tinh', 'Nam'),
                        'dan_toc': data.get('dan_toc', 'Kinh'),
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

                    # Check if customer with this CMND already exists
                    try:
                        customer = Customer.objects.get(so_cmnd=so_cmnd)
                        # Customer exists - update with new data
                        for field, value in customer_data.items():
                            setattr(customer, field, value)
                        customer.save()
                        logger.info(f"Updated existing customer: {ho_ten} - {so_cmnd}")
                    except Customer.DoesNotExist:
                        # Customer doesn't exist - create new one
                        customer_data['so_cmnd'] = so_cmnd
                        customer_data['created_by'] = request.user
                        customer = Customer.objects.create(**customer_data)
                        logger.info(f"Created new customer: {ho_ten} - {so_cmnd}")

            except Exception as e:
                # Failed to create/update customer, continue with document generation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving customer: {str(e)}")
                customer_save_error = _customer_error_text(e)

        # Để trống "Mã khách hàng" / "Số tài khoản" → in dấu chấm để ghi tay.
        # Làm SAU khi lưu khách hàng để không lưu dấu chấm vào dữ liệu khách hàng.
        fill_empty_print_fields(data)

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
        if customer_save_error:
            from urllib.parse import quote
            response['X-Customer-Save-Error'] = quote(customer_save_error)
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
        branch_config = BranchConfig.get_for_user(request.user)
        preview_data.update(branch_config.get_all_variables())

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

        fill_empty_print_fields(preview_data)

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


def area_lookup(request):
    """
    Trang tra cứu thông tin địa bàn hành chính.
    Sử dụng AddressSelector component và dữ liệu từ dia_danh.json và chuyen_doi.json
    """
    return render(request, 'templates_app/area_lookup.html')


# ==============================================================================
# CALCULATOR
# ==============================================================================

@login_required
def calculator_view(request):
    return render(request, 'templates_app/calculator.html')


# ==============================================================================
# PDF TOOLS (Tách / Ghép PDF)
# ==============================================================================

@login_required
def pdf_tools_view(request):
    return render(request, 'templates_app/pdf_tools.html')


@login_required
@require_http_methods(['POST'])
def pdf_split_view(request):
    """
    Tách PDF theo lựa chọn:
    - mode=all  → tách từng trang thành file riêng, trả về ZIP
    - mode=pages → trích trang theo phạm vi, trả về PDF
    """
    from .pdf_tools_service import validate_pdf, split_to_zip, extract_pages, parse_page_ranges

    uploaded = request.FILES.get('pdf_file')
    if not uploaded:
        return JsonResponse({'error': 'Vui lòng chọn file PDF.'}, status=400)

    is_valid, err = validate_pdf(uploaded)
    if not is_valid:
        return JsonResponse({'error': err}, status=400)

    pdf_bytes = uploaded.read()
    mode = request.POST.get('mode', 'all')
    stem = uploaded.name.rsplit('.', 1)[0]

    try:
        if mode == 'all':
            zip_bytes, total = split_to_zip(pdf_bytes)
            response = HttpResponse(zip_bytes, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="tach_{stem}_{total}trang.zip"'
            return response
        else:
            ranges_str = request.POST.get('page_ranges', '')
            from pypdf import PdfReader
            import io as _io
            total_pages = len(PdfReader(_io.BytesIO(pdf_bytes)).pages)
            page_numbers = parse_page_ranges(ranges_str, total_pages)
            pdf_out = extract_pages(pdf_bytes, page_numbers)
            response = HttpResponse(
                pdf_out,
                content_type='application/pdf',
            )
            response['Content-Disposition'] = f'attachment; filename="trich_{stem}.pdf"'
            return response
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Lỗi xử lý: {str(e)}'}, status=500)


@login_required
@require_http_methods(['POST'])
def pdf_merge_view(request):
    """
    Ghép nhiều file PDF thành một.
    """
    from .pdf_tools_service import validate_pdf, merge_pdfs, MAX_MERGE_FILES

    files = request.FILES.getlist('pdf_files')
    if len(files) < 2:
        return JsonResponse({'error': 'Cần ít nhất 2 file PDF để ghép.'}, status=400)
    if len(files) > MAX_MERGE_FILES:
        return JsonResponse({'error': f'Tối đa {MAX_MERGE_FILES} file mỗi lần ghép.'}, status=400)

    pdf_bytes_list = []
    for f in files:
        is_valid, err = validate_pdf(f)
        if not is_valid:
            return JsonResponse({'error': f'{f.name}: {err}'}, status=400)
        pdf_bytes_list.append(f.read())

    try:
        merged = merge_pdfs(pdf_bytes_list)
    except Exception as e:
        return JsonResponse({'error': f'Lỗi ghép PDF: {str(e)}'}, status=500)

    response = HttpResponse(merged, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="gop_pdf.pdf"'
    return response


# ==============================================================================
# OCR TOOL
# ==============================================================================

@login_required
def ocr_tool_view(request):
    """
    Công cụ OCR: nhận file ảnh hoặc PDF, trích xuất văn bản,
    trả về file Word (.docx) có thể chỉnh sửa.
    POST được gọi bằng fetch (AJAX) — lỗi trả JSON, thành công trả file.
    """
    from .ocr_service import MAX_FILE_SIZE_MB, MAX_PDF_PAGES, validate_file, process_file, build_docx
    ctx = {'max_size': MAX_FILE_SIZE_MB, 'max_pages': MAX_PDF_PAGES}

    if request.method == 'GET':
        return render(request, 'templates_app/ocr_tool.html', ctx)

    def json_error(msg):
        return JsonResponse({'error': msg}, status=400)

    uploaded_file = request.FILES.get('ocr_file')
    if not uploaded_file:
        return json_error('Vui lòng chọn file trước khi gửi.')

    is_valid, error_msg = validate_file(uploaded_file)
    if not is_valid:
        return json_error(error_msg)

    original_name = uploaded_file.name
    ext = os.path.splitext(original_name)[1].lower()

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file_path = os.path.join(tmp_dir, f'input{ext}')
            with open(tmp_file_path, 'wb+') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            page_texts = process_file(tmp_file_path, ext)
        docx_bytes = build_docx(page_texts, original_name)
    except Exception as e:
        return json_error(f'Lỗi khi xử lý file: {str(e)}')

    stem = os.path.splitext(original_name)[0]
    output_filename = f'OCR_{stem}.docx'

    response = HttpResponse(
        docx_bytes,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
    return response


# ==============================================================================
