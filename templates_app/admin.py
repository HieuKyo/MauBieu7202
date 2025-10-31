from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
from .models import Category, Template, Variable, TemplateVariable
from .import_helpers import (
    import_variables_from_csv,
    import_variables_from_excel,
    import_templates_bulk,
    export_variables_to_csv,
    export_variables_to_excel
)


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

    change_list_template = 'admin/variable_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.admin_site.admin_view(self.import_variables_view), name='variable_import'),
            path('export/csv/', self.admin_site.admin_view(self.export_csv_view), name='variable_export_csv'),
            path('export/excel/', self.admin_site.admin_view(self.export_excel_view), name='variable_export_excel'),
        ]
        return custom_urls + urls

    def import_variables_view(self, request):
        """View để import biến từ CSV/Excel"""
        if request.method == 'POST':
            file = request.FILES.get('file')
            if not file:
                messages.error(request, 'Vui lòng chọn file để import')
                return redirect('..')

            # Determine file type
            if file.name.endswith('.csv'):
                success, errors = import_variables_from_csv(file)
            elif file.name.endswith('.xlsx'):
                success, errors = import_variables_from_excel(file)
            else:
                messages.error(request, 'Chỉ hỗ trợ file .csv hoặc .xlsx')
                return redirect('..')

            # Show results
            if success:
                messages.success(request, f'Đã import thành công {success} biến')
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f'... và {len(errors) - 10} lỗi khác')

            return redirect('..')

        return render(request, 'admin/variable_import.html', {
            'title': 'Import Biến',
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
        })

    def export_csv_view(self, request):
        """Export biến ra CSV"""
        response = HttpResponse(export_variables_to_csv(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="variables.csv"'
        return response

    def export_excel_view(self, request):
        """Export biến ra Excel"""
        output = export_variables_to_excel()
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="variables.xlsx"'
        return response


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

    change_list_template = 'admin/template_changelist.html'

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('category', 'name', 'description', 'file')
        }),
        ('Cấu hình', {
            'fields': ('is_active', 'order', 'allowed_groups')
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-import/', self.admin_site.admin_view(self.bulk_import_view), name='template_bulk_import'),
        ]
        return custom_urls + urls

    def bulk_import_view(self, request):
        """View để import nhiều template cùng lúc"""
        if request.method == 'POST':
            files = request.FILES.getlist('files')
            category_id = request.POST.get('category')
            variable_ids = request.POST.getlist('variables')
            group_ids = request.POST.getlist('groups')

            if not files:
                messages.error(request, 'Vui lòng chọn ít nhất một file .docx')
                return redirect('..')

            if not category_id:
                messages.error(request, 'Vui lòng chọn danh mục')
                return redirect('..')

            # Import templates
            success, errors = import_templates_bulk(
                files,
                category_id,
                variable_ids if variable_ids else None,
                group_ids if group_ids else None
            )

            # Show results
            if success:
                messages.success(request, f'Đã import thành công {success} mẫu biểu')
            if errors:
                for error in errors[:10]:
                    messages.warning(request, error)
                if len(errors) > 10:
                    messages.warning(request, f'... và {len(errors) - 10} lỗi khác')

            return redirect('..')

        # Prepare context for form
        from django.contrib.auth.models import Group
        context = {
            'title': 'Import nhiều Mẫu biểu',
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
            'categories': Category.objects.all().order_by('order', 'name'),
            'variables': Variable.objects.all().order_by('name'),
            'groups': Group.objects.all().order_by('name'),
        }
        return render(request, 'admin/template_bulk_import.html', context)


@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    """Admin cho liên kết Template-Variable"""
    list_display = ['template', 'variable', 'order']
    list_filter = ['template__category', 'template']
    list_editable = ['order']
    search_fields = ['template__name', 'variable__name']
    autocomplete_fields = ['template', 'variable']
    ordering = ['template', 'order']


# Tùy chỉnh tiêu đề admin - Agribank branding
admin.site.site_header = "AGRIBANK - Hệ thống Quản lý Mẫu biểu"
admin.site.site_title = "Agribank Admin"
admin.site.index_title = "Quản lý hệ thống Mẫu biểu"
