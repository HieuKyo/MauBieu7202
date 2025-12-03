"""
Template tags cho app Salary
"""
from django import template

register = template.Library()


@register.filter
def has_group(user, group_name):
    """
    Kiểm tra user có thuộc group không
    Sử dụng: {% if request.user|has_group:"Admins" %}
    """
    if user.is_superuser:
        return True
    return user.groups.filter(name=group_name).exists()


@register.filter
def has_any_group(user, group_names):
    """
    Kiểm tra user có thuộc bất kỳ group nào không
    Sử dụng: {% if request.user|has_any_group:"Admins,GiaoDichViens" %}
    """
    if user.is_superuser:
        return True
    groups = [g.strip() for g in group_names.split(',')]
    return user.groups.filter(name__in=groups).exists()
