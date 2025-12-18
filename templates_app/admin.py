from django.contrib import admin
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.http import HttpResponse
from .models import (
    Category, Template, Variable, TemplateVariable, Customer, Business, GlobalConfig,
    DetailedFeeTier, OnRequestFeeTier, BeautifulNumber,
    BankStatement, Transaction,
    UserProfile, Course, CourseEnrollment,
    ATM, ATMManagementBoard, Vehicle, Person, ATMReplenishment, ATMDiscrepancy
)
from .import_helpers import (
    import_variables_from_csv,
    import_variables_from_excel,
    import_templates_bulk,
    export_variables_to_csv,
    export_variables_to_excel
)


# KHÔNG SỬ DỤNG Variable và TemplateVariable nữa
# Hệ thống sử dụng Customer model fields + GlobalConfig variables
# Giữ lại code để backward compatible với data cũ

# class TemplateVariableInline(admin.TabularInline):
#     """Inline để quản lý biến của template"""
#     model = TemplateVariable
#     extra = 1
#     autocomplete_fields = ['variable']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin cho Khách hàng"""
    list_display = ['ma_khach_hang', 'ho_ten', 'so_cmnd', 'so_dien_thoai', 'ngay_sinh', 'created_at', 'created_by']
    list_filter = ['nghe_nghiep', 'gioi_tinh', 'created_at', 'created_by']
    search_fields = ['ma_khach_hang', 'ho_ten', 'so_cmnd', 'so_dien_thoai', 'email']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    ordering = ['-created_at']

    fieldsets = (
        ('Mã khách hàng', {
            'fields': ('ma_khach_hang',)
        }),
        ('Thông tin cá nhân', {
            'fields': ('ho_ten', 'ngay_sinh', 'gioi_tinh')
        }),
        ('Giấy tờ tùy thân', {
            'fields': ('so_cmnd', 'ngay_cap_cmnd', 'noi_cap_cmnd')
        }),
        ('Thông tin liên hệ', {
            'fields': ('dia_chi', 'so_dien_thoai', 'email')
        }),
        ('Địa chỉ chi tiết (Address Selector)', {
            'fields': ('province', 'district', 'ward', 'hamlet', 'full_address'),
            'description': 'Thông tin địa chỉ chi tiết được điền tự động từ Address Selector Component'
        }),
        ('Thông tin nghề nghiệp', {
            'fields': ('nghe_nghiep', 'noi_lam_viec')
        }),
        ('Thông tin tài khoản', {
            'fields': ('so_tai_khoan', 'loai_tai_khoan')
        }),
        ('Ghi chú & Metadata', {
            'fields': ('ghi_chu', 'created_at', 'updated_at', 'created_by')
        }),
    )

    def save_model(self, request, obj, form, change):
        """Tự động gán người tạo khi tạo mới khách hàng"""
        if not change:  # Chỉ khi tạo mới
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    """Admin cho Doanh nghiệp"""
    list_display = ['cif', 'ten_doanh_nghiep', 'ma_so_thue', 'dien_thoai', 'nguoi_dai_dien_ho_ten', 'created_at']
    list_filter = ['loai_giay_to', 'created_at']
    search_fields = ['cif', 'ten_doanh_nghiep', 'ma_so_thue', 'so_gcn', 'dien_thoai']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Thông tin doanh nghiệp', {
            'fields': ('cif', 'so_tai_khoan', 'ten_doanh_nghiep')
        }),
        ('Giấy tờ định danh', {
            'fields': ('loai_giay_to', 'so_gcn', 'ngay_cap_gcn', 'noi_cap_gcn')
        }),
        ('Mã số thuế', {
            'fields': ('ma_so_thue', 'ngay_cap_mst', 'noi_cap_mst')
        }),
        ('Thông tin liên hệ', {
            'fields': ('dia_chi', 'dien_thoai')
        }),
        ('Thông tin kinh doanh', {
            'fields': ('linh_vuc_kinh_doanh', 'von_dieu_le')
        }),
        ('Người đại diện pháp luật', {
            'fields': (
                'nguoi_dai_dien_ho_ten',
                'nguoi_dai_dien_ngay_sinh',
                'nguoi_dai_dien_gioi_tinh',
                'nguoi_dai_dien_nghe_nghiep',
                'nguoi_dai_dien_loai_giay_to',
                'nguoi_dai_dien_so_cccd',
                'nguoi_dai_dien_ngay_cap',
                'nguoi_dai_dien_noi_cap',
                'nguoi_dai_dien_ngay_het_han',
                'nguoi_dai_dien_noi_o_hien_tai'
            )
        }),
        ('Kế toán trưởng', {
            'fields': (
                'ke_toan_truong_ho_ten',
                'ke_toan_truong_ngay_sinh',
                'ke_toan_truong_gioi_tinh',
                'ke_toan_truong_nghe_nghiep',
                'ke_toan_truong_loai_giay_to',
                'ke_toan_truong_so_cccd',
                'ke_toan_truong_ngay_cap',
                'ke_toan_truong_noi_cap',
                'ke_toan_truong_ngay_het_han',
                'ke_toan_truong_noi_o_hien_tai'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin cho Danh mục"""
    from .forms import CategoryAdminForm
    form = CategoryAdminForm

    list_display = ['name', 'order', 'created_at']
    list_editable = ['order']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'description', 'order')
        }),
        ('Cấu hình hiển thị form', {
            'fields': ('visible_field_groups',),
            'description': '<p><strong>Chọn các nhóm trường sẽ hiển thị trong form nhập liệu</strong></p>'
                          '<p>Khi người dùng chọn danh mục này, chỉ các nhóm trường được chọn mới hiển thị. '
                          'Điều này giúp đơn giản hóa form cho từng loại mẫu biểu.</p>'
                          '<p><em>Ví dụ:</em> Danh mục "Dịch vụ Ngân hàng" có thể chỉ hiển thị: '
                          'Thông tin cá nhân, Giấy tờ tùy thân, Thông tin tài khoản và Đăng ký dịch vụ.</p>'
        }),
    )


# Variable Admin - KHÔNG SỬ DỤNG NỮA
# Hệ thống chuyển sang dùng Customer fields + GlobalConfig
# Comment out để ẩn khỏi admin interface

# @admin.register(Variable)
# class VariableAdmin(admin.ModelAdmin):
#     """Admin cho Biến"""
#     list_display = ['name', 'label', 'field_type', 'required', 'created_at']
#     list_filter = ['field_type', 'required']
#     search_fields = ['name', 'label']
#     ordering = ['name']
#
#     change_list_template = 'admin/variable_changelist.html'
#
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('import/', self.admin_site.admin_view(self.import_variables_view), name='variable_import'),
#             path('export/csv/', self.admin_site.admin_view(self.export_csv_view), name='variable_export_csv'),
#             path('export/excel/', self.admin_site.admin_view(self.export_excel_view), name='variable_export_excel'),
#         ]
#         return custom_urls + urls
#
#     def import_variables_view(self, request):
#         """View để import biến từ CSV/Excel"""
#         if request.method == 'POST':
#             file = request.FILES.get('file')
#             if not file:
#                 messages.error(request, 'Vui lòng chọn file để import')
#                 return redirect('..')
#
#             # Determine file type
#             if file.name.endswith('.csv'):
#                 success, errors = import_variables_from_csv(file)
#             elif file.name.endswith('.xlsx'):
#                 success, errors = import_variables_from_excel(file)
#             else:
#                 messages.error(request, 'Chỉ hỗ trợ file .csv hoặc .xlsx')
#                 return redirect('..')
#
#             # Show results
#             if success:
#                 messages.success(request, f'Đã import thành công {success} biến')
#             if errors:
#                 for error in errors[:10]:  # Show first 10 errors
#                     messages.warning(request, error)
#                 if len(errors) > 10:
#                     messages.warning(request, f'... và {len(errors) - 10} lỗi khác')
#
#             return redirect('..')
#
#         return render(request, 'admin/variable_import.html', {
#             'title': 'Import Biến',
#             'site_title': admin.site.site_title,
#             'site_header': admin.site.site_header,
#         })
#
#     def export_csv_view(self, request):
#         """Export biến ra CSV"""
#         response = HttpResponse(export_variables_to_csv(), content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename="variables.csv"'
#         return response
#
#     def export_excel_view(self, request):
#         """Export biến ra Excel"""
#         output = export_variables_to_excel()
#         response = HttpResponse(
#             output.read(),
#             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#         )
#         response['Content-Disposition'] = 'attachment; filename="variables.xlsx"'
#         return response


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    """Admin cho Mẫu biểu"""
    list_display = ['name', 'category', 'is_active', 'order', 'created_at']
    list_filter = ['category', 'is_active', 'allowed_groups']
    list_editable = ['is_active', 'order']
    search_fields = ['name', 'description']
    filter_horizontal = ['allowed_groups']
    # inlines = [TemplateVariableInline]  # KHÔNG SỬ DỤNG NỮA - Variables không dùng
    ordering = ['category', 'order', 'name']

    change_list_template = 'admin/template_changelist.html'
    change_form_template = 'admin/template_change_form.html'

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('category', 'name', 'description', 'file')
        }),
        ('Cấu hình', {
            'fields': ('is_active', 'order', 'allowed_groups')
        }),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Override to add variable context to the change form"""
        from .models import GlobalConfig

        # Build variable lists for the sidebar
        # 1. Customer variables
        customer_variables = []
        for field in Customer._meta.get_fields():
            if field.concrete and not field.many_to_many and not field.one_to_many:
                field_name = field.name
                if field_name not in ['id', 'created_at', 'updated_at', 'created_by']:
                    verbose = getattr(field, 'verbose_name', field_name)
                    customer_variables.append({
                        'name': field_name,
                        'description': verbose,
                    })

        # 2. Date variables
        date_variables = [
            {'name': 'd1', 'description': 'Ngày sinh - Chữ số thứ nhất'},
            {'name': 'd2', 'description': 'Ngày sinh - Chữ số thứ hai'},
            {'name': 'm1', 'description': 'Tháng sinh - Chữ số thứ nhất'},
            {'name': 'm2', 'description': 'Tháng sinh - Chữ số thứ hai'},
            {'name': 'y1', 'description': 'Năm sinh - Chữ số thứ nhất'},
            {'name': 'y2', 'description': 'Năm sinh - Chữ số thứ hai'},
            {'name': 'y3', 'description': 'Năm sinh - Chữ số thứ ba'},
            {'name': 'y4', 'description': 'Năm sinh - Chữ số thứ tư'},
        ]

        # 3. Branch variables
        branch_variables = [
            {'name': 'ten_chi_nhanh', 'description': 'Tên chi nhánh'},
            {'name': 'ten_chi_nhanh_hoa', 'description': 'Tên chi nhánh (IN HOA)'},
            {'name': 'mst', 'description': 'Mã số thuế'},
            {'name': 'gcndkdn', 'description': 'Giấy chứng nhận đăng ký kinh doanh'},
            {'name': 'mst_chi_nhanh', 'description': 'Mã số thuế chi nhánh'},
            {'name': 'nguoi_dai_dien', 'description': 'Người đại diện'},
            {'name': 'chuc_vu', 'description': 'Chức vụ'},
            {'name': 'so_uy_quyen', 'description': 'Số uỷ quyền'},
            {'name': 'dien_thoai_chi_nhanh', 'description': 'Điện thoại chi nhánh'},
            {'name': 'giao_dich_vien', 'description': 'Họ tên giao dịch viên'},
            {'name': 'kiem_soat_vien', 'description': 'Họ tên kiểm soát viên'},
            {'name': 'giam_doc', 'description': 'Họ tên giám đốc chi nhánh'},
            {'name': 'dia_chi_chi_nhanh', 'description': 'Địa chỉ chi nhánh'},
        ]

        # 4. Custom variables
        config = GlobalConfig.get_instance()
        custom_variables = []
        if config.custom_variables:
            for var_name, var_value in config.custom_variables.items():
                custom_variables.append({
                    'name': var_name,
                    'description': 'Biến tùy chỉnh',
                    'example': var_value[:50] if var_value else ''
                })

        # Add to context
        extra_context = extra_context or {}
        extra_context.update({
            'customer_variables': customer_variables,
            'date_variables': date_variables,
            'branch_variables': branch_variables,
            'custom_variables': custom_variables,
            'total_variables_count': len(customer_variables) + len(date_variables) + len(branch_variables) + len(custom_variables),
        })

        return super().changeform_view(request, object_id, form_url, extra_context)

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
            # variable_ids = request.POST.getlist('variables')  # KHÔNG DÙNG NỮA
            group_ids = request.POST.getlist('groups')

            if not files:
                messages.error(request, 'Vui lòng chọn ít nhất một file .docx')
                return redirect('..')

            if not category_id:
                messages.error(request, 'Vui lòng chọn danh mục')
                return redirect('..')

            # Import templates (không cần variables nữa)
            success, errors = import_templates_bulk(
                files,
                category_id,
                None,  # variable_ids - không dùng nữa
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
            # 'variables': Variable.objects.all().order_by('name'),  # KHÔNG DÙNG NỮA
            'groups': Group.objects.all().order_by('name'),
        }
        return render(request, 'admin/template_bulk_import.html', context)


# TemplateVariable Admin - KHÔNG SỬ DỤNG NỮA
# @admin.register(TemplateVariable)
# class TemplateVariableAdmin(admin.ModelAdmin):
#     """Admin cho liên kết Template-Variable"""
#     list_display = ['template', 'variable', 'order']
#     list_filter = ['template__category', 'template']
#     list_editable = ['order']
#     search_fields = ['template__name', 'variable__name']
#     autocomplete_fields = ['template', 'variable']
#     ordering = ['template', 'order']


# Tùy chỉnh tiêu đề admin - Agribank Chi nhánh Giá Rai Bạc Liêu
admin.site.site_header = "Agribank Chi nhánh Giá Rai Bạc Liêu - Hệ thống Quản lý Mẫu biểu"
admin.site.site_title = "Agribank Giá Rai Admin"
admin.site.index_title = "Quản lý hệ thống Mẫu biểu"


# ====================
# Beautiful Number Fee Management
# ====================

@admin.register(DetailedFeeTier)
class DetailedFeeTierAdmin(admin.ModelAdmin):
    """Admin cho Biểu phí chi tiết"""
    list_display = ['quantity', 'fee_type', 'min_fee', 'max_fee', 'formatted_fee_range']
    list_filter = ['fee_type']
    list_editable = ['min_fee', 'max_fee']
    ordering = ['quantity', 'fee_type']

    fieldsets = (
        ('Thông tin bậc phí', {
            'fields': ('quantity', 'fee_type')
        }),
        ('Mức phí', {
            'fields': ('min_fee', 'max_fee'),
            'description': '<p>Để <strong>Phí tối đa</strong> trống để hiển thị "Thỏa thuận"</p>'
        }),
    )

    def formatted_fee_range(self, obj):
        """Format hiển thị khoảng phí"""
        if obj.max_fee:
            return f"{obj.min_fee:,} - {obj.max_fee:,} VNĐ"
        return f"Từ {obj.min_fee:,} VNĐ (Thỏa thuận)"
    formatted_fee_range.short_description = 'Khoảng phí'


@admin.register(OnRequestFeeTier)
class OnRequestFeeTierAdmin(admin.ModelAdmin):
    """Admin cho Biểu phí chọn số theo yêu cầu"""
    list_display = ['quantity_range', 'min_fee', 'max_fee', 'formatted_fee_range']
    list_editable = ['min_fee', 'max_fee']
    ordering = ['min_quantity']

    fieldsets = (
        ('Số lượng số đẹp', {
            'fields': ('min_quantity', 'max_quantity')
        }),
        ('Mức phí', {
            'fields': ('min_fee', 'max_fee')
        }),
    )

    def quantity_range(self, obj):
        """Format hiển thị khoảng số lượng"""
        return f"{obj.min_quantity} - {obj.max_quantity}"
    quantity_range.short_description = 'Số lượng'

    def formatted_fee_range(self, obj):
        """Format hiển thị khoảng phí"""
        return f"{obj.min_fee:,} - {obj.max_fee:,} VNĐ"
    formatted_fee_range.short_description = 'Khoảng phí'


@admin.register(BeautifulNumber)
class BeautifulNumberAdmin(admin.ModelAdmin):
    """Admin cho Danh sách số đẹp có sẵn"""
    list_display = ['account_number', 'category', 'price_tier', 'formatted_fee', 'is_available', 'updated_at']
    list_filter = ['is_available', 'category', 'price_tier', 'created_at']
    list_editable = ['is_available']
    search_fields = ['account_number', 'description']
    ordering = ['price_tier', 'category', 'account_number']
    date_hierarchy = 'created_at'

    # Thêm actions
    actions = ['mark_as_sold', 'mark_as_available', 'delete_selected']

    # Thêm change_list_template để hiển thị nút import
    change_list_template = 'admin/beautiful_number_changelist.html'

    fieldsets = (
        ('Thông tin số tài khoản', {
            'fields': ('account_number', 'category', 'description')
        }),
        ('Phí dịch vụ', {
            'fields': ('price_tier', 'fee')
        }),
        ('Trạng thái', {
            'fields': ('is_available',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def formatted_fee(self, obj):
        """Format hiển thị phí"""
        return f"{obj.fee:,} VNĐ"
    formatted_fee.short_description = 'Phí'

    def get_readonly_fields(self, request, obj=None):
        """Make account_number readonly after creation"""
        if obj:  # editing an existing object
            return self.readonly_fields + ['account_number']
        return self.readonly_fields

    # ===== BULK ACTIONS =====

    @admin.action(description='Đánh dấu đã bán (không còn)')
    def mark_as_sold(self, request, queryset):
        """Bulk action: Đánh dấu số đã bán"""
        updated = queryset.update(is_available=False)
        self.message_user(request, f'Đã đánh dấu {updated} số là "Đã bán"', messages.SUCCESS)

    @admin.action(description='Đánh dấu còn hàng')
    def mark_as_available(self, request, queryset):
        """Bulk action: Đánh dấu số còn hàng"""
        updated = queryset.update(is_available=True)
        self.message_user(request, f'Đã đánh dấu {updated} số là "Còn hàng"', messages.SUCCESS)

    # ===== CUSTOM VIEWS =====

    def get_urls(self):
        """Thêm custom URLs"""
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.admin_site.admin_view(self.import_numbers_view), name='beautiful_number_import'),
        ]
        return custom_urls + urls

    def import_numbers_view(self, request):
        """View để import số đẹp từ text hoặc file"""
        from .beautiful_number_services import analyze_account_number

        if request.method == 'POST':
            # Lấy input từ form
            numbers_text = request.POST.get('numbers_text', '').strip()
            file = request.FILES.get('numbers_file')
            default_category = request.POST.get('category', BeautifulNumber.CATEGORY_TAI_LOC)

            # Parse numbers from text or file
            numbers = []
            if numbers_text:
                # Split by comma, semicolon, or newline
                import re
                numbers = re.split(r'[,;\n\r]+', numbers_text)
            elif file:
                # Read from file
                content = file.read().decode('utf-8')
                import re
                numbers = re.split(r'[,;\n\r]+', content)

            if not numbers:
                messages.error(request, 'Vui lòng nhập danh sách số hoặc upload file')
                return redirect('.')

            # Process each number
            created_count = 0
            updated_count = 0
            skipped_count = 0
            errors = []

            for num_str in numbers:
                num_str = num_str.strip()
                if not num_str:
                    continue

                # Validate number format
                if len(num_str) != 13:
                    errors.append(f'{num_str}: Phải có 13 chữ số')
                    continue

                if not num_str.startswith('7202'):
                    errors.append(f'{num_str}: Phải bắt đầu bằng 7202')
                    continue

                # Check if exists - if so, mark as sold
                existing = BeautifulNumber.objects.filter(account_number=num_str).first()
                if existing:
                    existing.is_available = False
                    existing.save()
                    updated_count += 1
                    continue

                # Analyze number to get fee and category
                analysis = analyze_account_number(num_str)

                if analysis.get('error'):
                    errors.append(f'{num_str}: {analysis.get("error")}')
                    continue

                # Determine category
                if analysis.get('is_special'):
                    category = BeautifulNumber.CATEGORY_DAC_BIET
                else:
                    category = default_category

                # Determine price tier
                from .views import get_price_tier_from_fee
                price_tier = get_price_tier_from_fee(analysis['fee_min_vat'])

                # Create beautiful number (mark as sold since import list = sold list)
                try:
                    BeautifulNumber.objects.create(
                        account_number=num_str,
                        category=category,
                        price_tier=price_tier,
                        fee=analysis['fee_min_vat'],
                        description=analysis.get('description', ''),
                        is_available=False  # Số import = số đã bán
                    )
                    created_count += 1
                except Exception as e:
                    errors.append(f'{num_str}: {str(e)}')

            # Show results
            if created_count > 0:
                messages.success(request, f'✓ Đã thêm {created_count} số đẹp mới (đánh dấu "Đã bán")')
            if updated_count > 0:
                messages.success(request, f'✓ Đã đánh dấu "Đã bán" cho {updated_count} số đã tồn tại')
            if errors:
                for error in errors[:10]:  # Show first 10 errors
                    messages.warning(request, f'⚠ {error}')
                if len(errors) > 10:
                    messages.warning(request, f'... và {len(errors) - 10} lỗi khác')

            return redirect('..')

        # GET request - show form
        context = {
            'title': 'Import số đẹp',
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
            'category_choices': BeautifulNumber.CATEGORY_CHOICES,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
        }
        return render(request, 'admin/beautiful_number_import.html', context)


# ====================
# Bank Statement Admin
# ====================

class TransactionInline(admin.TabularInline):
    """Inline hiển thị các giao dịch trong sao kê"""
    model = Transaction
    extra = 0
    readonly_fields = ['stt', 'transaction_date', 'debit_amount', 'credit_amount',
                       'balance', 'bank_name', 'account_number', 'beneficiary_name',
                       'description', 'transaction_type']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    """Admin cho BankStatement"""
    list_display = ['file_name', 'uploaded_at', 'total_transactions', 'total_debit_display',
                    'total_credit_display', 'final_balance_display', 'uploaded_by']
    list_filter = ['uploaded_at', 'uploaded_by']
    search_fields = ['file_name']
    readonly_fields = ['uploaded_at', 'file_name', 'total_transactions', 'total_debit',
                       'total_credit', 'final_balance', 'processed', 'uploaded_by']
    inlines = [TransactionInline]

    def total_debit_display(self, obj):
        return f"{obj.total_debit:,.0f} VNĐ"
    total_debit_display.short_description = "Tổng ghi nợ"

    def total_credit_display(self, obj):
        return f"{obj.total_credit:,.0f} VNĐ"
    total_credit_display.short_description = "Tổng ghi có"

    def final_balance_display(self, obj):
        return f"{obj.final_balance:,.0f} VNĐ"
    final_balance_display.short_description = "Số dư cuối"

    def has_add_permission(self, request):
        # Không cho phép thêm mới từ admin (phải upload từ form)
        return False

    def has_delete_permission(self, request, obj=None):
        # Chỉ cho phép xóa nếu là superuser
        return request.user.is_superuser


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin cho Transaction"""
    list_display = ['stt', 'statement_file', 'transaction_date', 'debit_amount_display',
                    'credit_amount_display', 'balance_display', 'bank_name',
                    'account_number', 'transaction_type']
    list_filter = ['transaction_date', 'transaction_type', 'bank_name']
    search_fields = ['description', 'beneficiary_name', 'account_number']
    readonly_fields = ['statement', 'stt', 'transaction_date', 'debit_amount', 'credit_amount',
                       'balance', 'bank_name', 'account_number', 'beneficiary_name',
                       'description', 'transaction_type', 'raw_trcdnm', 'raw_tomgntno']
    date_hierarchy = 'transaction_date'

    def statement_file(self, obj):
        return obj.statement.file_name
    statement_file.short_description = "File sao kê"

    def debit_amount_display(self, obj):
        if obj.debit_amount > 0:
            return f"{obj.debit_amount:,.0f}"
        return "-"
    debit_amount_display.short_description = "Ghi nợ"

    def credit_amount_display(self, obj):
        if obj.credit_amount > 0:
            return f"{obj.credit_amount:,.0f}"
        return "-"
    credit_amount_display.short_description = "Ghi có"

    def balance_display(self, obj):
        return f"{obj.balance:,.0f}"
    balance_display.short_description = "Số dư"

    def has_add_permission(self, request):
        # Không cho phép thêm mới từ admin
        return False

    def has_delete_permission(self, request, obj=None):
        # Chỉ cho phép xóa nếu là superuser
        return request.user.is_superuser


# ====================
# Employee Management Admin
# ====================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin cho Hồ sơ nhân viên"""
    list_display = ['employee_code', 'full_name', 'user', 'branch', 'department', 'position', 'phone']
    list_filter = ['branch', 'department', 'position', 'job_function']
    search_fields = ['employee_code', 'full_name', 'user__username', 'phone']
    ordering = ['employee_code']

    fieldsets = (
        ('Thông tin tài khoản', {
            'fields': ('user', 'employee_code')
        }),
        ('Thông tin cá nhân', {
            'fields': ('full_name', 'dob', 'gender', 'phone', 'address')
        }),
        ('Giấy tờ tùy thân', {
            'fields': ('id_card_number', 'id_card_date', 'id_card_place')
        }),
        ('Thông tin công việc', {
            'fields': ('branch', 'department', 'job_function', 'position')
        }),
    )


# ====================
# E-Learning Admin
# ====================

class CourseEnrollmentInline(admin.TabularInline):
    """Inline để quản lý học viên của khóa học"""
    model = CourseEnrollment
    extra = 0
    fields = ['user', 'is_completed', 'completion_date']
    readonly_fields = ['completion_date']
    autocomplete_fields = ['user']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin cho Khóa học"""
    list_display = ['name', 'start_date', 'end_date', 'get_enrollment_count', 'created_at']
    list_filter = ['start_date', 'end_date']
    search_fields = ['name', 'description']
    ordering = ['-start_date']
    inlines = [CourseEnrollmentInline]

    fieldsets = (
        ('Thông tin khóa học', {
            'fields': ('name', 'description')
        }),
        ('Thời gian', {
            'fields': ('start_date', 'end_date')
        }),
    )

    def get_enrollment_count(self, obj):
        """Hiển thị số lượng học viên"""
        stats = obj.get_completion_stats()
        return f"{stats['completed']}/{stats['total']}"
    get_enrollment_count.short_description = 'Học viên (Hoàn thành/Tổng)'


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    """Admin cho Ghi danh khóa học"""
    list_display = ['course', 'user', 'is_completed', 'completion_date', 'enrolled_at']
    list_filter = ['is_completed', 'course', 'enrolled_at']
    search_fields = ['course__name', 'user__username', 'user__profile__full_name']
    ordering = ['-enrolled_at']
    autocomplete_fields = ['course', 'user']

    fieldsets = (
        ('Thông tin ghi danh', {
            'fields': ('course', 'user')
        }),
        ('Trạng thái', {
            'fields': ('is_completed', 'completion_date')
        }),
    )

    readonly_fields = ['enrolled_at']


# ====================
# ATM Management Admin
# ====================

@admin.register(ATM)
class ATMAdmin(admin.ModelAdmin):
    """Admin cho Máy ATM"""
    list_display = ['machine_id', 'serial_number', 'address', 'machine_type', 'machine_line', 'installation_date', 'is_active']
    list_filter = ['is_active', 'machine_type']
    list_editable = ['is_active']
    search_fields = ['machine_id', 'serial_number', 'address', 'machine_type']
    ordering = ['machine_id']

    fieldsets = (
        ('Thông tin máy ATM', {
            'fields': ('machine_id', 'serial_number', 'address', 'machine_type', 'machine_line', 'installation_date')
        }),
        ('Trạng thái', {
            'fields': ('is_active',)
        }),
    )


@admin.register(ATMManagementBoard)
class ATMManagementBoardAdmin(admin.ModelAdmin):
    """Admin cho Ban quản lý ATM"""
    list_display = ['position', 'full_name', 'title', 'is_active']
    list_filter = ['position', 'is_active']
    list_editable = ['is_active']
    ordering = ['position']

    fieldsets = (
        ('Thông tin chức vụ', {
            'fields': ('position', 'full_name', 'title')
        }),
        ('Trạng thái', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Admin cho Phương tiện"""
    list_display = ['license_plate', 'vehicle_type', 'is_active']
    list_filter = ['is_active']
    list_editable = ['is_active']
    search_fields = ['license_plate', 'vehicle_type']
    ordering = ['license_plate']

    fieldsets = (
        ('Thông tin phương tiện', {
            'fields': ('license_plate', 'vehicle_type')
        }),
        ('Trạng thái', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Admin cho Nhân viên vận chuyển"""
    list_display = ['person_type', 'full_name', 'id_number', 'id_issue_date', 'is_active']
    list_filter = ['person_type', 'is_active']
    list_editable = ['is_active']
    search_fields = ['full_name', 'id_number']
    ordering = ['person_type', 'full_name']

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('person_type', 'full_name')
        }),
        ('Giấy tờ tùy thân', {
            'fields': ('id_number', 'id_issue_date', 'id_issue_place')
        }),
        ('Trạng thái', {
            'fields': ('is_active',)
        }),
    )


@admin.register(ATMReplenishment)
class ATMReplenishmentAdmin(admin.ModelAdmin):
    """Admin cho Phiếu tiếp quỹ ATM"""
    list_display = ['atm', 'replenishment_date', 'total_amount_display', 'vehicle', 'driver', 'created_by']
    list_filter = ['replenishment_date', 'atm', 'created_by']
    search_fields = ['atm__machine_id', 'atm__address']
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'total_amount_display']
    ordering = ['-replenishment_date', '-created_at']
    date_hierarchy = 'replenishment_date'

    fieldsets = (
        ('Thông tin tiếp quỹ', {
            'fields': ('atm', 'replenishment_date')
        }),
        ('Số lượng tờ tiền', {
            'fields': ('bills_50k', 'bills_100k', 'bills_200k', 'bills_500k', 'total_amount_display'),
            'description': 'Nhập số lượng tờ tiền theo từng mệnh giá'
        }),
        ('Lệnh điều chuyển', {
            'fields': ('vehicle', 'driver', 'guard')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_amount_display(self, obj):
        """Hiển thị tổng số tiền"""
        return f"{obj.total_amount:,} VNĐ"
    total_amount_display.short_description = 'Tổng số tiền'

    def save_model(self, request, obj, form, change):
        """Tự động gán người tạo khi tạo mới"""
        if not change:  # Chỉ khi tạo mới
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ATMDiscrepancy)
class ATMDiscrepancyAdmin(admin.ModelAdmin):
    """Admin cho Giao dịch thừa/thiếu quỹ ATM"""
    list_display = [
        'atm', 'full_name', 'discrepancy_type', 'amount_display',
        'audit_cycle_display', 'status', 'created_by', 'created_at'
    ]
    list_filter = ['discrepancy_type', 'status', 'atm', 'audit_cycle_start', 'created_by']
    search_fields = [
        'atm__machine_id', 'full_name', 'account_number',
        'card_number', 'trace_number', 'transaction_id'
    ]
    readonly_fields = ['created_by', 'created_at', 'updated_at', 'amount_words_display']
    list_editable = ['status']
    ordering = ['-audit_cycle_end', '-created_at']
    date_hierarchy = 'audit_cycle_end'

    fieldsets = (
        ('Thông tin máy ATM', {
            'fields': ('atm',)
        }),
        ('Thông tin khách hàng/Giao dịch', {
            'fields': ('full_name', 'account_number', 'card_number', 'trace_number', 'transaction_id')
        }),
        ('Thông tin thừa/thiếu', {
            'fields': ('discrepancy_type', 'amount', 'amount_words_display'),
            'description': 'Nhập số tiền thừa hoặc thiếu'
        }),
        ('Chu kỳ kiểm quỹ', {
            'fields': ('audit_cycle_start', 'audit_cycle_end')
        }),
        ('Xử lý', {
            'fields': ('status', 'notes')
        }),
        ('Thông tin hệ thống', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def amount_display(self, obj):
        """Hiển thị số tiền"""
        return f"{obj.amount:,} VNĐ"
    amount_display.short_description = 'Số tiền'

    def amount_words_display(self, obj):
        """Hiển thị số tiền bằng chữ"""
        return obj.get_amount_in_words()
    amount_words_display.short_description = 'Số tiền bằng chữ'

    def audit_cycle_display(self, obj):
        """Hiển thị chu kỳ kiểm quỹ"""
        return f"{obj.audit_cycle_start.strftime('%d/%m/%Y')} - {obj.audit_cycle_end.strftime('%d/%m/%Y')}"
    audit_cycle_display.short_description = 'Chu kỳ kiểm quỹ'

    def save_model(self, request, obj, form, change):
        """Tự động gán người tạo khi tạo mới"""
        if not change:  # Chỉ khi tạo mới
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

