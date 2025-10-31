from django.contrib import admin
from .models import Category, Template, Variable, TemplateVariable


class TemplateVariableInline(admin.TabularInline):
    """Inline để quản lý biến của template"""
    model = TemplateVariable
    extra = 1
    autocomplete_fields = ['variable']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin cho Danh mục"""
    list_display = ['name', 'order', 'created_at']
    list_editable = ['order']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    """Admin cho Biến"""
    list_display = ['name', 'label', 'field_type', 'required', 'created_at']
    list_filter = ['field_type', 'required']
    search_fields = ['name', 'label']
    ordering = ['name']


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """Admin cho Mẫu biểu"""
    list_display = ['name', 'category', 'is_active', 'order', 'created_at']
    list_filter = ['category', 'is_active', 'allowed_groups']
    list_editable = ['is_active', 'order']
    search_fields = ['name', 'description']
    filter_horizontal = ['allowed_groups']
    inlines = [TemplateVariableInline]
    ordering = ['category', 'order', 'name']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('category', 'name', 'description', 'file')
        }),
        ('Cấu hình', {
            'fields': ('is_active', 'order', 'allowed_groups')
        }),
    )


@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    """Admin cho liên kết Template-Variable"""
    list_display = ['template', 'variable', 'order']
    list_filter = ['template__category', 'template']
    list_editable = ['order']
    search_fields = ['template__name', 'variable__name']
    autocomplete_fields = ['template', 'variable']
    ordering = ['template', 'order']


# Tùy chỉnh tiêu đề admin
admin.site.site_header = "Hệ thống Quản lý Mẫu biểu"
admin.site.site_title = "Mẫu biểu Admin"
admin.site.index_title = "Quản lý hệ thống"
