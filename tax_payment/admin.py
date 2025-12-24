from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import TaxLocation, TaxSubEntry, TaxPaymentStatement, TaxPaymentItem
import openpyxl
import pandas as pd


@admin.register(TaxLocation)
class TaxLocationAdmin(admin.ModelAdmin):
    list_display = ['tinh', 'co_quan_thue_group', 'xa_phuong', 'ma_co_quan_thu', 'ma_dia_ban']
    list_filter = ['tinh', 'co_quan_thue_group']
    search_fields = ['tinh', 'xa_phuong', 'ma_co_quan_thu', 'ten_co_quan_thu']
    ordering = ['tinh', 'co_quan_thue_group', 'xa_phuong']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.admin_site.admin_view(self.import_tax_locations), name='tax_location_import'),
        ]
        return custom_urls + urls

    def import_tax_locations(self, request):
        """View để import Cơ quan thu từ file Excel"""
        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                messages.error(request, 'Vui lòng chọn file để import!')
                return redirect('..')

            try:
                # Đọc file Excel
                if excel_file.name.endswith('.csv'):
                    df = pd.read_csv(excel_file, encoding='utf-8-sig')
                else:
                    df = pd.read_excel(excel_file)

                # Chuẩn hóa tên cột
                df.columns = df.columns.str.strip()

                created_count = 0
                updated_count = 0

                for index, row in df.iterrows():
                    try:
                        tinh = str(row.get('Tỉnh', '')).strip() if pd.notna(row.get('Tỉnh')) else ''
                        co_quan_thue = str(row.get('Cơ quan thuế', '')).strip() if pd.notna(row.get('Cơ quan thuế')) else ''
                        xa = str(row.get('Xã', '')).strip() if pd.notna(row.get('Xã')) else ''
                        ma_co_quan_thu = str(row.get('Mã cơ quan thu', '')).strip() if pd.notna(row.get('Mã cơ quan thu')) else ''
                        ten_co_quan_thu = str(row.get('Tên cơ quan thu', '')).strip() if pd.notna(row.get('Tên cơ quan thu')) else ''
                        kbnn = str(row.get('KBNN', '')).strip() if pd.notna(row.get('KBNN')) else ''
                        ma_db = str(row.get('Mã DB', '')).strip() if pd.notna(row.get('Mã DB')) else ''

                        if not ma_co_quan_thu:
                            continue

                        obj, created = TaxLocation.objects.update_or_create(
                            ma_co_quan_thu=ma_co_quan_thu,
                            defaults={
                                'tinh': tinh,
                                'co_quan_thue_group': co_quan_thue,
                                'xa_phuong': xa,
                                'ten_co_quan_thu': ten_co_quan_thu,
                                'kho_bac': kbnn,
                                'ma_dia_ban': ma_db
                            }
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    except Exception as e:
                        messages.warning(request, f'Lỗi dòng {index + 2}: {str(e)}')

                messages.success(request, f'Import thành công! Tạo mới: {created_count}, Cập nhật: {updated_count}')
                return redirect('..')

            except Exception as e:
                messages.error(request, f'Lỗi khi đọc file: {str(e)}')
                return redirect('..')

        # GET request - hiển thị form upload
        context = {
            'title': 'Import Danh mục Cơ quan thu',
            'site_header': admin.site.site_header,
            'site_title': admin.site.site_title,
        }
        return render(request, 'admin/tax_payment/import_tax_locations.html', context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(TaxSubEntry)
class TaxSubEntryAdmin(admin.ModelAdmin):
    list_display = ['ma_tieu_muc', 'ten_tieu_muc']
    search_fields = ['ma_tieu_muc', 'ten_tieu_muc']
    ordering = ['ma_tieu_muc']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import/', self.admin_site.admin_view(self.import_tax_subentries), name='tax_subentry_import'),
        ]
        return custom_urls + urls

    def import_tax_subentries(self, request):
        """View để import Tiểu mục từ file Excel"""
        if request.method == 'POST':
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                messages.error(request, 'Vui lòng chọn file để import!')
                return redirect('..')

            try:
                # Đọc file Excel
                if excel_file.name.endswith('.csv'):
                    df = pd.read_csv(excel_file, encoding='utf-8-sig')
                else:
                    df = pd.read_excel(excel_file)

                # Chuẩn hóa tên cột
                df.columns = df.columns.str.strip()

                created_count = 0
                updated_count = 0

                for index, row in df.iterrows():
                    try:
                        # Tự động mapping tên cột
                        ma_tieu_muc = None
                        ten_tieu_muc = None

                        for col in df.columns:
                            if 'mã' in col.lower() and 'tiểu mục' in col.lower():
                                ma_tieu_muc = str(row[col]).strip() if pd.notna(row[col]) else ''
                            elif 'tên' in col.lower() or 'gọi' in col.lower():
                                ten_tieu_muc = str(row[col]).strip() if pd.notna(row[col]) else ''

                        # Fallback
                        if not ma_tieu_muc and 'Mã số Tiểu mục' in df.columns:
                            ma_tieu_muc = str(row['Mã số Tiểu mục']).strip() if pd.notna(row['Mã số Tiểu mục']) else ''
                        if not ten_tieu_muc and 'TÊN GỌI' in df.columns:
                            ten_tieu_muc = str(row['TÊN GỌI']).strip() if pd.notna(row['TÊN GỌI']) else ''

                        if not ma_tieu_muc or not ten_tieu_muc:
                            continue

                        obj, created = TaxSubEntry.objects.update_or_create(
                            ma_tieu_muc=ma_tieu_muc,
                            defaults={
                                'ten_tieu_muc': ten_tieu_muc
                            }
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                    except Exception as e:
                        messages.warning(request, f'Lỗi dòng {index + 2}: {str(e)}')

                messages.success(request, f'Import thành công! Tạo mới: {created_count}, Cập nhật: {updated_count}')
                return redirect('..')

            except Exception as e:
                messages.error(request, f'Lỗi khi đọc file: {str(e)}')
                return redirect('..')

        # GET request - hiển thị form upload
        context = {
            'title': 'Import Danh mục Tiểu mục',
            'site_header': admin.site.site_header,
            'site_title': admin.site.site_title,
        }
        return render(request, 'admin/tax_payment/import_tax_subentries.html', context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context=extra_context)


class TaxPaymentItemInline(admin.TabularInline):
    model = TaxPaymentItem
    extra = 1
    fields = ['stt', 'ma_tieu_muc', 'noi_dung', 'so_tien']


@admin.register(TaxPaymentStatement)
class TaxPaymentStatementAdmin(admin.ModelAdmin):
    list_display = ['ten_nguoi_nop', 'ma_so_thue', 'ngay_lap', 'tong_so_tien', 'created_at']
    list_filter = ['ngay_lap', 'created_at']
    search_fields = ['ten_nguoi_nop', 'ma_so_thue']
    ordering = ['-created_at']
    inlines = [TaxPaymentItemInline]
    readonly_fields = ['created_at', 'updated_at']
