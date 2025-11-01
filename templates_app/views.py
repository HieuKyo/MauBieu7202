from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.db.models import Q, Exists, OuterRef
from django.views.decorators.http import require_http_methods
from .models import Category, Template, Variable, TemplateVariable, Customer, GlobalConfig
from .forms import DynamicTemplateForm, CustomerForm, GlobalConfigForm
from .utils import render_word_template
import os
import json


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


@login_required
@require_http_methods(["POST"])
def customer_create_view(request):
    """Tạo khách hàng mới"""
    form = CustomerForm(request.POST)
    if form.is_valid():
        customer = form.save(commit=False)
        customer.created_by = request.user
        customer.save()
        return JsonResponse({
            'success': True,
            'message': 'Đã thêm khách hàng thành công',
            'customer_id': customer.id,
            'customer_name': customer.ho_ten
        })
    else:
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({
            'success': False,
            'errors': errors
        }, status=400)


@login_required
@require_http_methods(["POST"])
def customer_update_view(request, customer_id):
    """Cập nhật thông tin khách hàng"""
    customer = get_object_or_404(Customer, id=customer_id)
    form = CustomerForm(request.POST, instance=customer)
    if form.is_valid():
        form.save()
        return JsonResponse({
            'success': True,
            'message': 'Đã cập nhật thông tin khách hàng'
        })
    else:
        errors = {field: error[0] for field, error in form.errors.items()}
        return JsonResponse({
            'success': False,
            'errors': errors
        }, status=400)


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
        'mst': 'Mã số thuế',
        'dia_chi_chi_nhanh': 'Địa chỉ chi nhánh',
        'giao_dich_vien': 'Giao dịch viên',
        'kiem_soat_vien': 'Kiểm soát viên',
        'giam_doc': 'Giám đốc',
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

    # 2. Biến Ngày tháng - Derived from ngay_sinh
    date_variables = [
        {'name': 'd1', 'description': 'Ngày sinh - Chữ số thứ nhất', 'example': 'Nếu ngày sinh là 05/03/1990 → d1 = 0'},
        {'name': 'd2', 'description': 'Ngày sinh - Chữ số thứ hai', 'example': 'Nếu ngày sinh là 05/03/1990 → d2 = 5'},
        {'name': 'm1', 'description': 'Tháng sinh - Chữ số thứ nhất', 'example': 'Nếu ngày sinh là 05/03/1990 → m1 = 0'},
        {'name': 'm2', 'description': 'Tháng sinh - Chữ số thứ hai', 'example': 'Nếu ngày sinh là 05/03/1990 → m2 = 3'},
        {'name': 'y1', 'description': 'Năm sinh - Chữ số thứ nhất', 'example': 'Nếu ngày sinh là 05/03/1990 → y1 = 1'},
        {'name': 'y2', 'description': 'Năm sinh - Chữ số thứ hai', 'example': 'Nếu ngày sinh là 05/03/1990 → y2 = 9'},
        {'name': 'y3', 'description': 'Năm sinh - Chữ số thứ ba', 'example': 'Nếu ngày sinh là 05/03/1990 → y3 = 9'},
        {'name': 'y4', 'description': 'Năm sinh - Chữ số thứ tư', 'example': 'Nếu ngày sinh là 05/03/1990 → y4 = 0'},
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

        # Service checkboxes (3 main services only)
        data['dv_sms_banking'] = checkbox(request.POST.get('dv_sms_banking') == 'on')
        data['dv_bankplus'] = checkbox(request.POST.get('dv_bankplus') == 'on')
        data['dv_e_mobile'] = checkbox(request.POST.get('dv_e_mobile') == 'on')

        # Set other service checkboxes to unchecked for compatibility with old templates
        for field in ['dv_thu_ho_tien_nuoc', 'dv_thu_ho_tien_dien', 'dv_thu_ho_vien_thong',
                      'dv_thu_ho_truyen_hinh', 'dv_thu_ho_internet', 'dv_e_internet', 'dv_e_pay',
                      'dv_smart_otp', 'dv_token', 'kenh_mobile', 'kenh_internet']:
            data[field] = '☐'

        # Special checkboxes
        data['the_hang_chuan'] = checkbox(data['hang_the'] == 'Hạng chuẩn')
        data['the_hang_vang'] = checkbox(data['hang_the'] == 'Hạng vàng')
        data['the_ghi_no_noi_dia'] = checkbox(data['loai_the'] == 'Thẻ Ghi nợ nội địa')
        data['tk_ngau_nhien'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản ngẫu nhiên')
        data['tk_theo_yeu_cau'] = checkbox(data['loai_tai_khoan'] == 'Tài khoản số theo yêu cầu')

        # Print info
        data['ngay_in'] = request.POST.get('ngay_in', '')

        # Date variables (from ngay_sinh)
        if data['ngay_sinh']:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['ngay_sinh'], '%Y-%m-%d')
                date_str = date_obj.strftime('%d%m%Y')
                data['d1'], data['d2'] = date_str[0], date_str[1]
                data['m1'], data['m2'] = date_str[2], date_str[3]
                data['y1'], data['y2'], data['y3'], data['y4'] = date_str[4], date_str[5], date_str[6], date_str[7]
            except:
                pass

        # Date variables (from ngay_cap_cmnd)
        if data['ngay_cap_cmnd']:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['ngay_cap_cmnd'], '%Y-%m-%d')
                date_str = date_obj.strftime('%d%m%Y')
                data['dcc1'], data['dcc2'] = date_str[0], date_str[1]
                data['mcc1'], data['mcc2'] = date_str[2], date_str[3]
                data['ycc1'], data['ycc2'], data['ycc3'], data['ycc4'] = date_str[4], date_str[5], date_str[6], date_str[7]
            except:
                pass

        # Date variables (from ngay_het_han_cmnd)
        if data['ngay_het_han_cmnd']:
            try:
                from datetime import datetime
                date_obj = datetime.strptime(data['ngay_het_han_cmnd'], '%Y-%m-%d')
                date_str = date_obj.strftime('%d%m%Y')
                data['dhh1'], data['dhh2'] = date_str[0], date_str[1]
                data['mhh1'], data['mhh2'] = date_str[2], date_str[3]
                data['yhh1'], data['yhh2'], data['yhh3'], data['yhh4'] = date_str[4], date_str[5], date_str[6], date_str[7]
            except:
                pass

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

        # Branch data from GlobalConfig
        data['ten_chi_nhanh'] = config.ten_chi_nhanh
        data['ten_chi_nhanh_hoa'] = config.ten_chi_nhanh_hoa
        data['mst'] = config.mst
        data['giao_dich_vien'] = config.giao_dich_vien
        data['kiem_soat_vien'] = config.kiem_soat_vien
        data['giam_doc'] = config.giam_doc
        data['dia_chi_chi_nhanh'] = config.dia_chi_chi_nhanh

        # Custom variables
        if config.custom_variables:
            data.update(config.custom_variables)

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
