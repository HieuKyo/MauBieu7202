"""
Views quản lý phân quyền người dùng: superuser, nhóm, xem chi tiết quyền.
"""
# Standard library imports
import json

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

# Local application imports
from .models import Template


# ===================================
# PERMISSION MANAGEMENT VIEWS
# ===================================

@login_required
def permission_management_view(request):
    """
    Trang quản lý phân quyền - Chỉ Superuser có quyền truy cập
    Hiển thị danh sách tất cả users và quyền của họ
    """
    # Kiểm tra quyền Superuser
    if not request.user.is_superuser:
        messages.error(request, 'Bạn không có quyền truy cập trang này!')
        return redirect('dashboard')

    # Lấy danh sách tất cả users
    users = User.objects.all().select_related('profile').prefetch_related('groups')

    # Lấy danh sách tất cả groups
    all_groups = Group.objects.all().order_by('name')

    # Lấy tất cả templates để hiển thị permission
    templates = Template.objects.filter(is_active=True).prefetch_related('allowed_groups')

    # Tạo dictionary để lưu thông tin quyền của từng user
    users_permissions = []
    for user in users:
        user_groups = user.groups.all()

        # Lấy templates mà user có quyền truy cập
        if user.is_superuser:
            accessible_templates_count = templates.count()
        else:
            accessible_templates_count = templates.filter(
                Q(allowed_groups__isnull=True) |
                Q(allowed_groups__in=user_groups)
            ).distinct().count()

        users_permissions.append({
            'user': user,
            'groups': user_groups,
            'accessible_templates_count': accessible_templates_count,
        })

    context = {
        'users_permissions': users_permissions,
        'all_groups': all_groups,
        'total_templates': templates.count(),
    }

    return render(request, 'templates_app/permission_management.html', context)


@login_required
@require_http_methods(["POST"])
def update_superuser_status(request, user_id):
    """
    API endpoint để cập nhật trạng thái Superuser của user
    """
    # Kiểm tra quyền Superuser
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Bạn không có quyền thực hiện thao tác này!'
        }, status=403)

    try:
        user = get_object_or_404(User, id=user_id)

        # Không cho phép tự bỏ quyền Superuser của chính mình
        if user == request.user:
            return JsonResponse({
                'success': False,
                'error': 'Bạn không thể thay đổi quyền Superuser của chính mình!'
            }, status=400)

        # Lấy giá trị mới từ request
        data = json.loads(request.body)
        is_superuser = data.get('is_superuser', False)

        # Cập nhật
        user.is_superuser = is_superuser
        user.is_staff = is_superuser  # Superuser cũng cần is_staff để truy cập admin
        user.save()

        return JsonResponse({
            'success': True,
            'message': f'Đã {"cấp" if is_superuser else "thu hồi"} quyền Superuser cho {user.username}',
            'is_superuser': user.is_superuser
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi cập nhật: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def update_user_groups(request, user_id):
    """
    API endpoint để cập nhật danh sách nhóm của user
    """
    # Kiểm tra quyền Superuser
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Bạn không có quyền thực hiện thao tác này!'
        }, status=403)

    try:
        user = get_object_or_404(User, id=user_id)

        # Lấy danh sách group IDs từ request
        data = json.loads(request.body)
        group_ids = data.get('group_ids', [])

        # Cập nhật groups
        user.groups.clear()
        if group_ids:
            groups = Group.objects.filter(id__in=group_ids)
            user.groups.set(groups)

        # Lấy thông tin groups đã cập nhật
        updated_groups = user.groups.all()

        return JsonResponse({
            'success': True,
            'message': f'Đã cập nhật nhóm cho {user.username}',
            'groups': [{'id': g.id, 'name': g.name} for g in updated_groups]
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi cập nhật: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_user_permissions_detail(request, user_id):
    """
    API endpoint để lấy chi tiết quyền của user
    Trả về danh sách templates mà user có quyền truy cập
    """
    # Kiểm tra quyền Superuser
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Bạn không có quyền thực hiện thao tác này!'
        }, status=403)

    try:
        user = get_object_or_404(User, id=user_id)
        user_groups = user.groups.all()

        # Lấy tất cả templates
        all_templates = Template.objects.filter(is_active=True).select_related('category').prefetch_related('allowed_groups')

        # Phân loại templates
        accessible_templates = []
        for template in all_templates:
            can_access = False
            reason = ""

            if user.is_superuser:
                can_access = True
                reason = "Superuser"
            elif template.allowed_groups.count() == 0:
                can_access = True
                reason = "Public (Không giới hạn)"
            elif template.allowed_groups.filter(id__in=[g.id for g in user_groups]).exists():
                can_access = True
                template_groups = template.allowed_groups.filter(id__in=[g.id for g in user_groups])
                reason = f"Qua nhóm: {', '.join([g.name for g in template_groups])}"

            if can_access:
                accessible_templates.append({
                    'id': template.id,
                    'name': template.name,
                    'category': template.category.name,
                    'reason': reason
                })

        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'is_superuser': user.is_superuser,
                'groups': [{'id': g.id, 'name': g.name} for g in user_groups]
            },
            'accessible_templates': accessible_templates,
            'total_accessible': len(accessible_templates),
            'total_templates': all_templates.count()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Lỗi khi lấy thông tin: {str(e)}'
        }, status=500)
