from django import template

register = template.Library()


@register.filter(name='has_elearning_permission')
def has_elearning_permission(user):
    """
    Kiểm tra xem user có quyền quản lý e-learning không
    Trả về True nếu user là superuser hoặc thuộc nhóm "Phòng Tổng hợp"
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(name='Phòng Tổng hợp').exists()
