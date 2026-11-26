from django import template

register = template.Library()


@register.simple_tag
def bia_so_cho_xu_ly(user):
    """Số tập chứng từ đang chờ user xử lý (KSV / Hậu kiểm nhận, GDV đem GĐ ký) — cho huy hiệu tab."""
    if not user.is_authenticated:
        return 0
    from templates_app.bia_giao_nhan_views import so_cho_xu_ly
    return so_cho_xu_ly(user)
