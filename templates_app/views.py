from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Q, Exists, OuterRef
from django.views.decorators.http import require_http_methods
from .models import Category, Template, Variable, TemplateVariable, Customer, GlobalConfig, remove_vietnamese_diacritics
from .forms import DynamicTemplateForm, CustomerForm, GlobalConfigForm
from .utils import render_word_template
from .issueby_mapping import get_issueby_name
import os
import json
import re
from datetime import date, datetime
import io


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
        form = DynamicTemplateForm(request.POST, template=template)
        if form.is_valid():
            # Lưu dữ liệu vào session để generate document
            # Bao gồm cả customer_id để lấy date variables
            session_data = form.cleaned_data.copy()
            if customer_id:
                session_data['_customer_id'] = customer_id
            request.session[f'template_{template_id}_data'] = session_data
            return redirect('generate_document', template_id=template_id)
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
    """Trang đăng nhập"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
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
    ]

    # 2.5. Biến điều kiện dịch vụ
    service_variables = [
        {'name': 'so_tai_khoan_AP', 'description': 'Số tài khoản (chỉ khi chọn Agribank Plus mà không chọn SMS Banking)', 'example': '1234567890'},
        {'name': 'so_dien_thoai_AP', 'description': 'Số điện thoại (chỉ khi chọn Agribank Plus mà không chọn SMS Banking)', 'example': '0987654321'},
        {'name': 'so_tai_khoan_SMS', 'description': 'Số tài khoản (chỉ khi chọn SMS Banking mà không chọn Agribank Plus)', 'example': '1234567890'},
        {'name': 'so_dien_thoai_SMS', 'description': 'Số điện thoại (chỉ khi chọn SMS Banking mà không chọn Agribank Plus)', 'example': '0987654321'},
        {'name': 'the_hang_chuan', 'description': 'Checkbox ☑/☐ khi chọn Hạng chuẩn', 'example': '☑ hoặc ☐'},
        {'name': 'the_hang_vang', 'description': 'Checkbox ☑/☐ khi chọn Hạng vàng', 'example': '☑ hoặc ☐'},
        {'name': 'the_ghi_no_noi_dia', 'description': 'Checkbox ☑/☐ khi chọn Thẻ Ghi nợ nội địa', 'example': '☑ hoặc ☐'},
        {'name': 'tk_ngau_nhien', 'description': 'Checkbox ☑/☐ khi chọn Tài khoản ngẫu nhiên', 'example': '☑ hoặc ☐'},
        {'name': 'tk_theo_yeu_cau', 'description': 'Checkbox ☑/☐ khi chọn Tài khoản số theo yêu cầu', 'example': '☑ hoặc ☐'},
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
    Generate document trực tiếp từ form data (không cần lưu customer)
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

        # Banking
        data['so_tai_khoan'] = request.POST.get('so_tai_khoan', '')
        data['loai_tai_khoan'] = request.POST.get('loai_tai_khoan', '')
        data['so_tai_khoan_yc'] = request.POST.get('so_tai_khoan_yc', '')
        data['loai_tien_te'] = request.POST.get('loai_tien_te', 'VND')

        # Card
        data['loai_the'] = request.POST.get('loai_the', '')
        data['hang_the'] = request.POST.get('hang_the', '')

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
        data['nghe_nghiep_cong_nhan'] = checkbox(nghe_nghiep == 'Công nhân')
        data['nghe_nghiep_kinh_doanh'] = checkbox(nghe_nghiep == 'Kinh doanh tự do')
        data['nghe_nghiep_hoc_sinh_sinh_vien'] = checkbox(nghe_nghiep == 'Học sinh/Sinh viên')
        data['nghe_nghiep_noi_tro'] = checkbox(nghe_nghiep == 'Nội trợ')
        data['nghe_nghiep_khac'] = checkbox(nghe_nghiep == 'Khác')

        # Checkbox - Hạng thẻ
        data['the_hang_chuan'] = checkbox(data['hang_the'] == 'Hạng chuẩn')
        data['the_hang_vang'] = checkbox(data['hang_the'] == 'Hạng vàng')
        data['the_hang_bach_kim'] = checkbox(data['hang_the'] == 'Hạng bạch kim')

        # Checkbox - Loại thẻ
        data['the_ghi_no_noi_dia'] = checkbox(data['loai_the'] == 'Thẻ Ghi nợ nội địa')
        data['the_ghi_no_quoc_te'] = checkbox(data['loai_the'] == 'Thẻ Ghi nợ quốc tế')
        data['the_tin_dung'] = checkbox(data['loai_the'] == 'Thẻ tín dụng')
        data['loai_the_jcb'] = checkbox(data['loai_the'] == 'JCB')
        data['loai_the_visa'] = checkbox(data['loai_the'] == 'Visa')
        data['loai_the_mastercard'] = checkbox(data['loai_the'] == 'Mastercard')
        data['loai_the_khac'] = checkbox(data['loai_the'] not in ['Thẻ Ghi nợ nội địa', 'Thẻ Ghi nợ quốc tế', 'Thẻ tín dụng', 'JCB', 'Visa', 'Mastercard'])

        # Checkbox - Loại tiền
        data['loai_tien_vnd'] = checkbox(data['loai_tien_te'] == 'VND')
        data['loai_tien_usd'] = checkbox(data['loai_tien_te'] == 'USD')
        data['loai_tien_eur'] = checkbox(data['loai_tien_te'] == 'EUR')

        # Checkbox - Loại tài khoản
        data['tk_ngau_nhien'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản ngẫu nhiên')
        data['tk_theo_yeu_cau'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản số theo yêu cầu')

        # Note: Card name (tên trên thẻ) is auto-filled into tables
        # by _render_card_name_tables() in utils.py
        # No need to generate individual character variables

        # Print info
        ngay_in_str = request.POST.get('ngay_in', '')
        if ngay_in_str:
            try:
                from datetime import datetime
                # 1. Parse chuỗi 'YYYY-MM-DD' từ form
                date_obj = datetime.strptime(ngay_in_str, '%Y-%m-%d')
                
                # 2. Định dạng lại thành 'DD/MM/YYYY'
                formatted_date = date_obj.strftime('%d/%m/%Y')
                
                # 3. Gán vào cả 'ngay_in' và 'ngay_lap' (vì template Mau_1a.docx dùng 'ngay_lap')
                data['ngay_in'] = formatted_date
                data['ngay_lap'] = formatted_date
            except ValueError:
                # Nếu có lỗi, dùng giá trị gốc
                data['ngay_in'] = ngay_in_str
                data['ngay_lap'] = ngay_in_str
        else:
            data['ngay_in'] = ''
            data['ngay_lap'] = ''

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
            except:
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
            except:
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
            except:
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
                                        except:
                                            try:
                                                parsed_date = datetime.strptime(str(value), '%Y-%m-%d')
                                                data[field_name] = parsed_date.date()
                                            except:
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
