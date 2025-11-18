from django import template

register = template.Library()


@register.filter(name='has_elearning_manage_permission')
def has_elearning_manage_permission(user):
    """
    Kiểm tra xem user có quyền quản lý e-learning không (tạo/sửa/xóa khóa học)
    Trả về True nếu user là superuser hoặc thuộc nhóm "Phòng Tổng hợp"
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(name='Phòng Tổng hợp').exists()


@register.filter(name='has_employee_import_permission')
def has_employee_import_permission(user):
    """
    Kiểm tra xem user có quyền import nhân viên không
    Chỉ superuser có quyền
    """
    if not user or not user.is_authenticated:
        return False

    return user.is_superuser
