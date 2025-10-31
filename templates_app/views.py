from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.db.models import Q, Exists, OuterRef
from django.views.decorators.http import require_http_methods
from .models import Category, Template, Variable, TemplateVariable
from .forms import DynamicTemplateForm
from .utils import render_word_template
import os


@login_required
def dashboard_view(request):
    """
    Trang chủ - Hiển thị danh sách danh mục
    Chỉ hiển thị danh mục có ít nhất 1 template mà user có quyền truy cập
    """
    user = request.user

    # Nếu là superuser, hiển thị tất cả danh mục có template active
    if user.is_superuser:
        categories = Category.objects.filter(
            templates__is_active=True
        ).distinct()
    else:
        # Lọc danh mục có ít nhất 1 template mà user có quyền truy cập
        # Template được phép truy cập khi:
        # 1. Không có group nào được gán (allowed_groups rỗng)
        # 2. User thuộc một trong các group được gán
        user_groups = user.groups.all()

        categories = Category.objects.filter(
            templates__is_active=True
        ).filter(
            Q(templates__allowed_groups__isnull=True) |
            Q(templates__allowed_groups__in=user_groups)
        ).distinct()

    context = {
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
    Hiển thị form nhập liệu cho một template
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

    if request.method == 'POST':
        form = DynamicTemplateForm(request.POST, template=template)
        if form.is_valid():
            # Lưu dữ liệu vào session để generate document
            request.session[f'template_{template_id}_data'] = form.cleaned_data
            return redirect('generate_document', template_id=template_id)
    else:
        form = DynamicTemplateForm(template=template)

    context = {
        'template': template,
        'form': form,
        'category': template.category,
    }
    return render(request, 'templates_app/template_form.html', context)


@login_required
def generate_document_view(request, template_id):
    """
    Tạo file Word từ template và dữ liệu đã nhập
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
