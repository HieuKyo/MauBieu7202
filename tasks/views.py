import json
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Case, When, Value, IntegerField, Q
from django.utils import timezone

from .models import Task
from .forms import TaskForm


# Chức vụ NHAN_VIEN không được giao việc
EMPLOYEE_POSITION = 'NHAN_VIEN'


def can_assign_tasks(user):
    """
    Kiểm tra user có quyền giao việc hay không.
    - superuser: luôn được
    - Có profile với chức vụ KHÁC NHAN_VIEN: được
    - Không có profile hoặc chức vụ là NHAN_VIEN: không được
    """
    if user.is_superuser:
        return True
    try:
        profile = user.profile
        # Có chức vụ và chức vụ khác Nhân viên => được giao việc
        return profile.position and profile.position != EMPLOYEE_POSITION
    except Exception:
        return False


@login_required
def task_list_view(request):
    """
    Hiển thị danh sách công việc với phân quyền người dùng (User Isolation).
    Chỉ hiển thị:
    - Task do user tạo (created_by == request.user)
    - HOẶC task được giao cho user (assigned_to == request.user)

    Sắp xếp: Việc gấp lên đầu, sau đó đến hạn chót gần nhất.
    """
    user = request.user

    # User Isolation: Chỉ lấy task của user hoặc được giao cho user
    tasks = Task.objects.filter(
        Q(created_by=user) | Q(assigned_to=user)
    ).annotate(
        priority_order=Case(
            When(priority=Task.PRIORITY_URGENT, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).select_related('created_by', 'assigned_to', 'created_by__profile', 'assigned_to__profile'
    ).order_by('is_completed', 'priority_order', 'due_date', '-created_at')

    # Lọc theo trạng thái nếu có
    filter_status = request.GET.get('status', 'all')
    if filter_status == 'pending':
        tasks = tasks.filter(is_completed=False)
    elif filter_status == 'completed':
        tasks = tasks.filter(is_completed=True)

    # Lọc theo category nếu có
    filter_category = request.GET.get('category', '')
    if filter_category:
        tasks = tasks.filter(category=filter_category)

    # Lọc theo priority nếu có
    filter_priority = request.GET.get('priority', '')
    if filter_priority:
        tasks = tasks.filter(priority=filter_priority)

    # Lọc theo loại task (của tôi / được giao)
    filter_task_type = request.GET.get('task_type', '')
    if filter_task_type == 'own':
        tasks = tasks.filter(created_by=user)
    elif filter_task_type == 'assigned':
        tasks = tasks.filter(assigned_to=user).exclude(created_by=user)

    # Annotate task type for each task for display
    task_list = []
    for task in tasks:
        task.task_type = task.get_task_type_for_user(user)
        task_list.append(task)

    # Kiểm tra quyền giao việc
    user_can_assign = can_assign_tasks(user)

    # Form cho modal thêm mới (truyền user để kiểm tra quyền)
    form = TaskForm(can_assign=user_can_assign)

    context = {
        'tasks': task_list,
        'form': form,
        'filter_status': filter_status,
        'filter_category': filter_category,
        'filter_priority': filter_priority,
        'filter_task_type': filter_task_type,
        'priority_choices': Task.PRIORITY_CHOICES,
        'category_choices': Task.CATEGORY_CHOICES,
        'recurring_choices': Task.RECURRING_CHOICES,
        'current_user': user,
        'can_assign': user_can_assign,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
@require_POST
def task_toggle_api(request):
    """
    API xử lý toggle checkbox (đánh dấu hoàn thành/chưa hoàn thành).
    Khi đánh dấu hoàn thành, nếu task có recurring_type thì tự động tạo bản sao.

    User phải là người tạo hoặc người được giao mới được phép toggle.
    """
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        is_completed = data.get('is_completed', False)

        # User Isolation: Chỉ cho phép toggle task của mình hoặc được giao
        task = get_object_or_404(
            Task,
            Q(created_by=request.user) | Q(assigned_to=request.user),
            id=task_id
        )
        task.is_completed = is_completed

        new_task = None

        # Nếu đánh dấu hoàn thành và task có recurring_type
        if is_completed and task.recurring_type != Task.RECURRING_NONE:
            new_task = create_recurring_task(task)

        task.save()

        response_data = {
            'success': True,
            'message': 'Cập nhật thành công!',
            'task': {
                'id': task.id,
                'title': task.title,
                'is_completed': task.is_completed,
            }
        }

        # Thêm thông tin task mới nếu có
        if new_task:
            response_data['new_task'] = {
                'id': new_task.id,
                'title': new_task.title,
                'due_date': new_task.due_date.strftime('%d/%m/%Y') if new_task.due_date else None,
                'message': f'Đã tạo công việc lặp lại mới: "{new_task.title}"'
            }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Dữ liệu không hợp lệ!'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)


def create_recurring_task(original_task):
    """
    Tạo bản sao của task với due_date được cộng thêm.
    - Monthly: cộng 1 tháng
    - Quarterly: cộng 3 tháng

    Giữ nguyên assigned_to để người được giao cũng nhận task mới.
    """
    # Tính toán due_date mới
    if original_task.due_date:
        if original_task.recurring_type == Task.RECURRING_MONTHLY:
            new_due_date = original_task.due_date + relativedelta(months=1)
        elif original_task.recurring_type == Task.RECURRING_QUARTERLY:
            new_due_date = original_task.due_date + relativedelta(months=3)
        else:
            new_due_date = original_task.due_date
    else:
        # Nếu không có due_date, tính từ ngày hiện tại
        today = timezone.now().date()
        if original_task.recurring_type == Task.RECURRING_MONTHLY:
            new_due_date = today + relativedelta(months=1)
        elif original_task.recurring_type == Task.RECURRING_QUARTERLY:
            new_due_date = today + relativedelta(months=3)
        else:
            new_due_date = None

    # Tạo task mới (bản sao) - giữ nguyên assigned_to
    new_task = Task.objects.create(
        title=original_task.title,
        description=original_task.description,
        due_date=new_due_date,
        is_completed=False,
        priority=original_task.priority,
        category=original_task.category,
        recurring_type=original_task.recurring_type,
        created_by=original_task.created_by,
        assigned_to=original_task.assigned_to,  # Giữ nguyên người được giao
    )

    return new_task


@login_required
@require_POST
def task_create_api(request):
    """API tạo task mới."""
    try:
        user_can_assign = can_assign_tasks(request.user)
        form = TaskForm(request.POST, can_assign=user_can_assign)

        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user

            # Bảo vệ server-side: nhân viên không được giao việc
            if not user_can_assign:
                task.assigned_to = None

            task.save()

            # Determine task type for current user
            task_type = task.get_task_type_for_user(request.user)

            return JsonResponse({
                'success': True,
                'message': 'Tạo công việc thành công!',
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description or '',
                    'due_date': task.due_date.strftime('%d/%m/%Y') if task.due_date else '',
                    'priority': task.priority,
                    'priority_display': task.get_priority_display(),
                    'category': task.category,
                    'category_display': task.get_category_display(),
                    'recurring_type': task.recurring_type,
                    'recurring_type_display': task.get_recurring_type_display(),
                    'is_completed': task.is_completed,
                    'priority_display_class': task.priority_display_class,
                    'category_badge_class': task.category_badge_class,
                    'recurring_badge_class': task.recurring_badge_class,
                    'assigned_to_id': task.assigned_to.id if task.assigned_to else None,
                    'assigned_to_display': task.assigned_to_display,
                    'created_by_display': task.created_by_display,
                    'task_type': task_type,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ!',
                'errors': form.errors
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)


@login_required
def task_detail_api(request, task_id):
    """API lấy chi tiết task để edit."""
    # User Isolation: Chỉ cho phép xem task của mình hoặc được giao
    task = get_object_or_404(
        Task,
        Q(created_by=request.user) | Q(assigned_to=request.user),
        id=task_id
    )

    return JsonResponse({
        'success': True,
        'task': {
            'id': task.id,
            'title': task.title,
            'description': task.description or '',
            'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else '',
            'priority': task.priority,
            'category': task.category,
            'recurring_type': task.recurring_type,
            'is_completed': task.is_completed,
            'assigned_to': task.assigned_to.id if task.assigned_to else '',
            'assigned_to_display': task.assigned_to_display,
            'created_by_display': task.created_by_display,
        }
    })


@login_required
@require_POST
def task_update_api(request, task_id):
    """API cập nhật task."""
    try:
        # User Isolation: Chỉ cho phép update task của mình hoặc được giao
        task = get_object_or_404(
            Task,
            Q(created_by=request.user) | Q(assigned_to=request.user),
            id=task_id
        )

        user_can_assign = can_assign_tasks(request.user)
        form = TaskForm(request.POST, instance=task, can_assign=user_can_assign)

        if form.is_valid():
            task = form.save(commit=False)

            # Bảo vệ server-side: nhân viên không được giao việc
            if not user_can_assign:
                task.assigned_to = None

            task.save()

            # Determine task type for current user
            task_type = task.get_task_type_for_user(request.user)

            return JsonResponse({
                'success': True,
                'message': 'Cập nhật thành công!',
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description or '',
                    'due_date': task.due_date.strftime('%d/%m/%Y') if task.due_date else '',
                    'priority': task.priority,
                    'priority_display': task.get_priority_display(),
                    'category': task.category,
                    'category_display': task.get_category_display(),
                    'recurring_type': task.recurring_type,
                    'recurring_type_display': task.get_recurring_type_display(),
                    'is_completed': task.is_completed,
                    'priority_display_class': task.priority_display_class,
                    'category_badge_class': task.category_badge_class,
                    'recurring_badge_class': task.recurring_badge_class,
                    'assigned_to_id': task.assigned_to.id if task.assigned_to else None,
                    'assigned_to_display': task.assigned_to_display,
                    'created_by_display': task.created_by_display,
                    'task_type': task_type,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Dữ liệu không hợp lệ!',
                'errors': form.errors
            }, status=400)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)


@login_required
@require_POST
def task_delete_api(request, task_id):
    """API xóa task."""
    try:
        # User Isolation: Chỉ người tạo mới được xóa task
        task = get_object_or_404(Task, id=task_id, created_by=request.user)
        task_title = task.title
        task.delete()

        return JsonResponse({
            'success': True,
            'message': f'Đã xóa công việc "{task_title}"!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        }, status=500)
