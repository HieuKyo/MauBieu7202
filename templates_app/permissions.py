"""
Permission utilities for filtering categories and templates based on user access.

This module provides centralized permission checking functions to reduce code duplication
in views.
"""

from django.db.models import Q


def get_accessible_categories_for_user(user, category_model):
    """
    Get all categories accessible to a user based on their groups and superuser status.

    Args:
        user: Django User object
        category_model: Category model class

    Returns:
        QuerySet: Categories the user can access

    Logic:
        - Superusers can access all categories
        - Regular users can access categories that have:
          - Templates with no group restrictions, OR
          - Templates assigned to their groups
    """
    if user.is_superuser:
        # Superusers see all categories
        return category_model.objects.all().order_by('order', 'name')

    # Regular users see categories with templates they can access
    user_groups = user.groups.all()
    categories = category_model.objects.filter(
        Q(templates__allowed_groups__isnull=True) |
        Q(templates__allowed_groups__in=user_groups)
    ).distinct().order_by('order', 'name')

    return categories


def get_accessible_templates_for_category(user, category, template_model):
    """
    Get all templates in a category that are accessible to a user.

    Args:
        user: Django User object
        category: Category object
        template_model: Template model class

    Returns:
        QuerySet: Templates in the category that the user can access

    Logic:
        - Superusers can access all active templates
        - Regular users can access active templates that:
          - Have no group restrictions, OR
          - Are assigned to their groups
    """
    if user.is_superuser:
        # Superusers see all active templates
        return category.templates.filter(is_active=True).order_by('order', 'name')

    # Regular users see templates they have access to
    user_groups = user.groups.all()
    templates = category.templates.filter(
        Q(allowed_groups__isnull=True) |
        Q(allowed_groups__in=user_groups)
    ).filter(is_active=True).distinct().order_by('order', 'name')

    return templates


def user_can_access_template(user, template):
    """
    Check if a user can access a specific template.

    Args:
        user: Django User object
        template: Template object

    Returns:
        bool: True if user can access, False otherwise

    Logic:
        - Superusers can access all templates
        - If template has no group restrictions, all users can access
        - Otherwise, user must be in one of the template's allowed groups
    """
    if user.is_superuser:
        return True

    # If template has no group restrictions, allow all users
    if template.allowed_groups.count() == 0:
        return True

    # Check if user is in any of the template's allowed groups
    return template.allowed_groups.filter(id__in=user.groups.all()).exists()


def filter_categories_with_accessible_templates(categories, user):
    """
    Filter categories and add accessible_templates attribute to each.

    This is commonly used in dashboard and list views to show categories
    with only the templates the user can access.

    Args:
        categories: QuerySet of Category objects
        user: Django User object

    Returns:
        list: Categories with accessible_templates attribute added

    Example usage:
        categories = Category.objects.all()
        filtered = filter_categories_with_accessible_templates(categories, request.user)
        for category in filtered:
            print(category.accessible_templates)  # Only templates user can access
    """
    filtered_categories = []

    for category in categories:
        if user.is_superuser:
            # Superusers see all active templates
            category.accessible_templates = category.templates.filter(is_active=True)
        else:
            # Regular users see templates they have access to
            user_groups = user.groups.all()
            category.accessible_templates = category.templates.filter(
                Q(allowed_groups__isnull=True) |
                Q(allowed_groups__in=user_groups)
            ).filter(is_active=True).distinct()

        filtered_categories.append(category)

    return filtered_categories


def get_user_template_count(user, template_model):
    """
    Get the total number of templates a user can access.

    Args:
        user: Django User object
        template_model: Template model class

    Returns:
        int: Number of accessible templates

    Example:
        >>> count = get_user_template_count(request.user, Template)
        >>> print(f"You have access to {count} templates")
    """
    if user.is_superuser:
        return template_model.objects.filter(is_active=True).count()

    user_groups = user.groups.all()
    return template_model.objects.filter(
        Q(allowed_groups__isnull=True) |
        Q(allowed_groups__in=user_groups)
    ).filter(is_active=True).distinct().count()


def get_templates_by_group(group, template_model):
    """
    Get all templates assigned to a specific group.

    Args:
        group: Django Group object
        template_model: Template model class

    Returns:
        QuerySet: Templates assigned to the group

    Example:
        >>> from django.contrib.auth.models import Group
        >>> group = Group.objects.get(name='Branch Managers')
        >>> templates = get_templates_by_group(group, Template)
    """
    return template_model.objects.filter(
        allowed_groups=group,
        is_active=True
    ).distinct().order_by('order', 'name')
