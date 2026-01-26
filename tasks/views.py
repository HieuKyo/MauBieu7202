import json
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone

from .models import Task
from .forms import TaskForm


@login_required
def task_list_view(request):
    """
    Hiển thị danh sách công việc.
    Sắp xếp: Việc gấp lên đầu, sau đó đến hạn chót gần nhất.
    """
    # Annotate để sắp xếp priority (urgent = 0, normal = 1)
    tasks = Task.objects.annotate(
        priority_order=Case(
            When(priority=Task.PRIORITY_URGENT, then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
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

    # Form cho modal thêm mới
    form = TaskForm()

    context = {
        'tasks': tasks,
        'form': form,
        'filter_status': filter_status,
        'filter_category': filter_category,
        'filter_priority': filter_priority,
        'priority_choices': Task.PRIORITY_CHOICES,
        'category_choices': Task.CATEGORY_CHOICES,
        'recurring_choices': Task.RECURRING_CHOICES,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
@require_POST
def task_toggle_api(request):
    """
    API xử lý toggle checkbox (đánh dấu hoàn thành/chưa hoàn thành).
    Khi đánh dấu hoàn thành, nếu task có recurring_type thì tự động tạo bản sao.
    """
    try:
        data = json.loads(request.body)
        task_id = data.get('task_id')
        is_completed = data.get('is_completed', False)

        task = get_object_or_404(Task, id=task_id)
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

    # Tạo task mới (bản sao)
    new_task = Task.objects.create(
        title=original_task.title,
        description=original_task.description,
        due_date=new_due_date,
        is_completed=False,
        priority=original_task.priority,
        category=original_task.category,
        recurring_type=original_task.recurring_type,
        created_by=original_task.created_by,
    )

    return new_task


@login_required
@require_POST
def task_create_api(request):
    """API tạo task mới."""
    try:
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()

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
    task = get_object_or_404(Task, id=task_id)

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
        }
    })


@login_required
@require_POST
def task_update_api(request, task_id):
    """API cập nhật task."""
    try:
        task = get_object_or_404(Task, id=task_id)
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            task = form.save()

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
        task = get_object_or_404(Task, id=task_id)
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
