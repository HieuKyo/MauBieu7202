"""
Decorators cho phân quyền trong app Salary
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def group_required(*group_names):
    """
    Decorator kiểm tra user thuộc group nào đó
    Sử dụng: @group_required('Admins', 'GiaoDichViens')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            user_groups = request.user.groups.values_list('name', flat=True)
            if any(group in user_groups for group in group_names):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'Bạn không có quyền truy cập trang này.')
            return redirect('salary:access_denied')
        return wrapper
    return decorator


def admins_only(view_func):
    """Decorator chỉ cho phép Admins truy cập"""
    return group_required('Admins')(view_func)


def giaodichvien_or_admin(view_func):
    """Decorator cho phép GiaoDichViens hoặc Admins truy cập"""
    return group_required('Admins', 'GiaoDichViens')(view_func)
