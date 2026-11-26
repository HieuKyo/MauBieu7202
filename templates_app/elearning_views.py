"""
Views E-Learning: quản lý khóa học, học viên, tra cứu theo người học/phòng ban.
"""

# Django imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods


# ====================
# E-Learning Views
# ====================

def check_elearning_manage_permission(user):
    """
    Kiểm tra quyền quản lý e-learning (tạo/sửa/xóa khóa học)
    Chỉ Superuser và cán bộ có hồ sơ Phòng ban = Phòng Tổng hợp có quyền
    """
    if user.is_superuser:
        return True
    try:
        return user.profile.department == 'TONG_HOP'
    except Exception:
        return False


def check_elearning_search_permission(user):
    """
    Kiểm tra quyền tra cứu e-learning
    Superuser, Phòng Tổng hợp và Trưởng phòng có quyền
    """
    if check_elearning_manage_permission(user):
        return True
    try:
        return user.profile.position == 'TRUONG_PHONG'
    except Exception:
        return False


@login_required
def course_dashboard(request):
    """
    Dashboard hiển thị danh sách khóa học (accordion style)
    - Quản lý (Superuser, Phòng Tổng hợp): Xem tất cả khóa học và tất cả học viên
    - Nhân viên: Chỉ xem khóa học được giao và chỉ thấy bản thân
    """
    from .models import Course, CourseEnrollment

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
        'can_search': check_elearning_search_permission(request.user),
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


@login_required
def course_print_not_enrolled(request, course_id):
    """
    Xuất file PDF danh sách nhân viên đã ghi danh nhưng chưa hoàn thành 1 khóa
    học (không tính người chưa được ghi danh vào khóa).
    Chỉ Superuser và Phòng Tổng hợp có quyền
    """
    import io
    from unidecode import unidecode
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import ParagraphStyle

    from .models import Course, UserProfile
    from .cash_drawer_views import FONT_REGULAR, FONT_BOLD

    if not check_elearning_manage_permission(request.user):
        messages.error(request, 'Bạn không có quyền in danh sách này')
        return redirect('course_dashboard')

    course = get_object_or_404(Course, id=course_id)

    not_completed_user_ids = course.enrollments.filter(is_completed=False).values_list('user_id', flat=True)
    not_enrolled = UserProfile.objects.filter(
        user_id__in=not_completed_user_ids
    ).select_related('user').order_by('department', 'full_name')

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=15 * mm, bottomMargin=15 * mm, leftMargin=15 * mm, rightMargin=15 * mm,
    )

    title_style = ParagraphStyle('Title', fontName=FONT_BOLD, fontSize=14, leading=18)
    info_style = ParagraphStyle('Info', fontName=FONT_REGULAR, fontSize=10, leading=14)

    elements = [
        Paragraph('DANH SÁCH NHÂN VIÊN CHƯA HỌC', title_style),
        Spacer(1, 4 * mm),
        Paragraph(f"Khóa học: {course.name}", info_style),
    ]
    if course.description.strip():
        elements.append(Paragraph(f"Mã khóa học: {course.description.strip()}", info_style))
    elements += [
        Paragraph(
            f"Thời gian: {course.start_date.strftime('%d/%m/%Y')} — {course.end_date.strftime('%d/%m/%Y')}",
            info_style,
        ),
        Paragraph(f"Tổng số nhân viên chưa hoàn thành: {not_enrolled.count()}", info_style),
        Spacer(1, 5 * mm),
    ]

    data = [['#', 'Mã NV', 'Họ và tên', 'Chức vụ']]
    for i, profile in enumerate(not_enrolled, start=1):
        data.append([
            str(i), profile.employee_code, profile.full_name, profile.get_position_display(),
        ])

    table = Table(data, colWidths=[10 * mm, 30 * mm, 90 * mm, 40 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), FONT_BOLD),
        ('FONTNAME', (0, 1), (-1, -1), FONT_REGULAR),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B1E2D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
    ]))
    elements.append(table)

    doc.build(elements)
    buf.seek(0)

    safe_name = ''.join(c if c.isalnum() else '_' for c in unidecode(course.name)).strip('_')
    resp = HttpResponse(buf.getvalue(), content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="ChuaHoc_{safe_name}.pdf"'
    resp['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return resp


@login_required
def course_search_by_learner(request):
    """
    Tra cứu khóa học theo người học
    Superuser và Phòng Tổng hợp: tìm tất cả nhân viên
    Trưởng phòng: chỉ tìm trong phòng ban của mình
    """
    from .models import UserProfile, CourseEnrollment
    from django.db.models import Q

    if not check_elearning_search_permission(request.user):
        messages.error(request, 'Bạn không có quyền tra cứu')
        return redirect('course_dashboard')

    is_full_manager = check_elearning_manage_permission(request.user)
    dept_filter = None
    if not is_full_manager:
        try:
            dept_filter = request.user.profile.department
        except Exception:
            dept_filter = None

    query = request.GET.get('q', '').strip()
    results = []

    if query:
        profile_qs = UserProfile.objects.filter(
            Q(full_name__icontains=query) | Q(employee_code__icontains=query)
        ).select_related('user').order_by('full_name')

        if dept_filter:
            profile_qs = profile_qs.filter(department=dept_filter)

        for profile in profile_qs:
            enrollments = CourseEnrollment.objects.filter(
                user=profile.user
            ).select_related('course').order_by('course__start_date')
            results.append({
                'profile': profile,
                'enrollments': enrollments,
                'total': enrollments.count(),
                'completed': enrollments.filter(is_completed=True).count(),
            })

    return render(request, 'templates_app/course_search_learner.html', {
        'query': query,
        'results': results,
        'is_full_manager': is_full_manager,
        'dept_filter': dept_filter,
    })


@login_required
def course_search_by_department(request):
    """
    Tra cứu khóa học theo phòng ban
    Superuser và Phòng Tổng hợp: chọn bất kỳ phòng ban nào
    Trưởng phòng: chỉ xem được phòng ban của mình (tự động chọn)
    """
    from .models import UserProfile, CourseEnrollment, Course

    if not check_elearning_search_permission(request.user):
        messages.error(request, 'Bạn không có quyền tra cứu')
        return redirect('course_dashboard')

    is_full_manager = check_elearning_manage_permission(request.user)
    dept_choices = UserProfile.DEPARTMENT_CHOICES

    # Trưởng phòng bị giới hạn ở phòng ban của mình
    locked_dept = None
    if not is_full_manager:
        try:
            locked_dept = request.user.profile.department
        except Exception:
            locked_dept = None

    selected_dept = locked_dept if locked_dept else request.GET.get('dept', '')
    courses_data = []

    if selected_dept:
        dept_user_ids = UserProfile.objects.filter(
            department=selected_dept
        ).values_list('user_id', flat=True)

        courses = Course.objects.all().order_by('start_date')
        for course in courses:
            enrollments = CourseEnrollment.objects.filter(
                course=course,
                user_id__in=dept_user_ids
            ).select_related('user__profile')
            if enrollments.exists():
                courses_data.append({
                    'course': course,
                    'enrollments': enrollments,
                    'total': enrollments.count(),
                    'completed': enrollments.filter(is_completed=True).count(),
                })

    return render(request, 'templates_app/course_search_department.html', {
        'dept_choices': dept_choices,
        'selected_dept': selected_dept,
        'courses_data': courses_data,
        'is_full_manager': is_full_manager,
        'locked_dept': locked_dept,
    })
