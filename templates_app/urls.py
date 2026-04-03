"""
URL configuration for templates_app
"""
from django.urls import path
from . import views
from . import report_views
from . import kpi_views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard (News Feed)
    path('', views.dashboard_view, name='dashboard'),

    # In mẫu biểu (Print Templates - chức năng Dashboard cũ)
    path('print-templates/', views.print_templates_view, name='print_templates'),

    # Category
    path('category/<int:category_id>/', views.category_detail_view, name='category_detail'),

    # Template
    path('template/<int:template_id>/', views.template_form_view, name='template_form'),
    path('template/<int:template_id>/generate/', views.generate_document_view, name='generate_document'),
    path('template/<int:template_id>/preview/', views.print_preview_view, name='print_preview'),
    path('template/<int:template_id>/preview/update/', views.update_preview_data, name='update_preview_data'),

    # New Dashboard API endpoints
    path('api/categories/<int:category_id>/templates/', views.category_templates_api, name='category_templates_api'),
    path('template/<int:template_id>/generate-direct/', views.generate_document_direct, name='generate_document_direct'),

    # Customer
    path('customers/', views.customer_list_view, name='customer_list'),
    path('api/customers/search/', views.customer_search_api, name='customer_search_api'),
    path('api/customers/<int:customer_id>/', views.customer_get, name='customer_get'),
    path('api/customers/<int:customer_id>/data/', views.customer_data_api, name='customer_data_api'),
    path('api/customers/<int:customer_id>/detail/', views.customer_detail_api, name='customer_detail_api'),
    path('api/customers/create/', views.customer_create_view, name='customer_create'),
    path('api/customers/<int:customer_id>/update/', views.customer_update_view, name='customer_update'),
    path('api/customers/<int:customer_id>/delete/', views.customer_delete_view, name='customer_delete'),
    path('api/customers/import-excel/', views.customer_import_excel, name='customer_import_excel'),
    path('api/customers/import/tsv/', views.customer_import_tsv, name='customer_import_tsv'),

    # Webcam Capture & Printing
    path('webcam/', views.webcam_dashboard_view, name='webcam_dashboard'),
    path('customers/<int:customer_id>/capture/', views.customer_capture_docs_view, name='customer_capture_docs'),
    path('api/customers/<int:customer_id>/save-images/', views.customer_save_images_view, name='customer_save_images'),
    path('customers/<int:customer_id>/print/', views.print_customer_docs_view, name='print_customer_docs'),

    # Business (Doanh nghiệp)
    path('businesses/', views.business_list_view, name='business_list'),
    path('api/businesses/search/', views.business_search_api, name='business_search_api'),
    path('api/businesses/<int:business_id>/data/', views.business_data_api, name='business_data_api'),

    # Business Dashboard and CRUD
    path('business/', views.business_dashboard, name='business_dashboard'),
    path('business/create/', views.business_create, name='business_create'),
    path('business/<int:business_id>/edit/', views.business_edit, name='business_edit'),
    path('business/<int:business_id>/delete/', views.business_delete, name='business_delete'),
    path('business/<int:business_id>/template/<int:template_id>/', views.business_load_data, name='business_load_data'),
    path('api/businesses/import/tsv/', views.business_import_tsv, name='business_import_tsv'),

    # Global Configuration (Branch + Custom Variables)
    path('branch-config/', views.branch_config_view, name='branch_config'),
    path('api/custom-variables/add/', views.add_custom_variable, name='add_custom_variable'),
    path('api/custom-variables/update/', views.update_custom_variable, name='update_custom_variable'),
    path('api/custom-variables/delete/', views.delete_custom_variable, name='delete_custom_variable'),

    # Variable Library
    path('variable-library/', views.variable_library_view, name='variable_library'),

    # Beautiful Number Fee Lookup
    path('beautiful-number-lookup/', views.beautiful_number_lookup, name='beautiful_number_lookup'),
    path('beautiful-number-list/', views.beautiful_number_list, name='beautiful_number_list'),
    path('api/beautiful-numbers/generate/', views.generate_beautiful_numbers_ajax, name='generate_beautiful_numbers'),

    # Test Address Selector
    path('test-address-selector/', views.test_address_selector, name='test_address_selector'),

    # Area Lookup
    path('area-lookup/', views.area_lookup, name='area_lookup'),

    # Bank Statement Analyzer
    path('bank-statement/upload/', views.bank_statement_upload, name='bank_statement_upload'),
    path('bank-statement/result/<int:statement_id>/', views.bank_statement_result, name='bank_statement_result'),
    path('bank-statement/export/<int:statement_id>/', views.bank_statement_export, name='bank_statement_export'),

    # Employee Management
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/export/', views.employee_export_excel, name='employee_export_excel'),
    path('employees/import/', views.employee_import_excel, name='employee_import_excel'),
    path('employees/import/template/', views.download_employee_template, name='download_employee_template'),
    path('employees/create/', views.employee_create_manual, name='employee_create_manual'),
    path('employees/<int:employee_id>/update/', views.employee_update_manual, name='employee_update_manual'),
    path('employees/<int:employee_id>/delete/', views.employee_delete_manual, name='employee_delete_manual'),

    # E-Learning
    path('elearning/', views.course_dashboard, name='course_dashboard'),
    path('elearning/courses/create/', views.course_create, name='course_create'),
    path('elearning/courses/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('elearning/courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('elearning/courses/<int:course_id>/add-students/', views.course_add_students, name='course_add_students'),
    path('elearning/courses/<int:course_id>/remove-student/<int:user_id>/', views.course_remove_student, name='course_remove_student'),
    path('elearning/enrollment/<int:enrollment_id>/toggle/', views.course_toggle_completion, name='course_toggle_completion'),

    # ATM Management
    path('atm/', views.atm_dashboard, name='atm_dashboard'),
    path('atm/replenishment/create/', views.atm_replenishment_create, name='atm_replenishment_create'),
    path('atm/replenishment/list/', views.atm_replenishment_list, name='atm_replenishment_list'),
    path('atm/replenishment/<int:replenishment_id>/template/<int:template_id>/', views.atm_load_replenishment_data, name='atm_load_replenishment_data'),

    # ATM Discrepancy Management
    path('atm/discrepancy/list/', views.atm_discrepancy_list, name='atm_discrepancy_list'),
    path('atm/discrepancy/create/', views.atm_discrepancy_create, name='atm_discrepancy_create'),
    path('atm/discrepancy/<int:discrepancy_id>/edit/', views.atm_discrepancy_edit, name='atm_discrepancy_edit'),
    path('atm/discrepancy/<int:discrepancy_id>/delete/', views.atm_discrepancy_delete, name='atm_discrepancy_delete'),
    path('atm/discrepancy/<int:discrepancy_id>/template/<int:template_id>/', views.atm_load_discrepancy_data, name='atm_load_discrepancy_data'),

    # Reports Module
    path('reports/', report_views.report_hub, name='report_hub'),
    path('reports/lai-ton-dong/', report_views.lai_ton_dong_report_view, name='lai_ton_dong_report'),
    path('reports/lai-ton-dong/process/', report_views.process_lai_ton_dong_report, name='process_lai_ton_dong'),
    path('reports/phat-hanh-the/', report_views.phat_hanh_the_report_view, name='phat_hanh_the_report'),
    path('reports/phat-hanh-the/process/', report_views.process_phat_hanh_the_report, name='process_phat_hanh_the'),
    path('reports/phat-hanh-the/process-print/', report_views.process_phat_hanh_the_for_print, name='process_phat_hanh_the_for_print'),
    path('reports/phat-hanh-the/print-preview/', report_views.phat_hanh_the_print_preview, name='phat_hanh_the_print_preview'),
    path('reports/mail-envelope/', report_views.mail_envelope_tracking_view, name='mail_envelope_tracking'),
    path('reports/mail-envelope/save/', report_views.save_mail_envelope, name='save_mail_envelope'),
    path('reports/mail-envelope/report/', report_views.mail_envelope_report_view, name='mail_envelope_report'),
    path('reports/dien-luc/', report_views.dien_luc_report_view, name='dien_luc_report'),
    path('reports/atm-fund-balance/', report_views.atm_fund_balance_view, name='atm_fund_balance'),

    # Permission Management
    path('permissions/', views.permission_management_view, name='permission_management'),
    path('permissions/users/<int:user_id>/superuser/', views.update_superuser_status, name='update_superuser_status'),
    path('permissions/users/<int:user_id>/groups/', views.update_user_groups, name='update_user_groups'),
    path('permissions/users/<int:user_id>/permissions/', views.get_user_permissions_detail, name='get_user_permissions_detail'),

    # KPI Dashboard (Django integrated - no Streamlit)
    path('kpi-dashboard/', kpi_views.kpi_dashboard_view, name='kpi_dashboard'),
    path('kpi-dashboard/process/', kpi_views.kpi_process_view, name='kpi_process'),

    # ATM Transaction Report (trong hệ thống báo cáo)
    path('reports/atm-transaction/', report_views.atm_transaction_report, name='atm_transaction_report'),
    path('reports/atm-transaction/import/', report_views.atm_transaction_import, name='atm_transaction_import'),
    path('reports/atm-transaction/delete/<int:upload_id>/', report_views.atm_transaction_delete, name='atm_transaction_delete'),
    path('reports/atm-transaction/detail/<str:atm_no>/', report_views.atm_transaction_detail, name='atm_transaction_detail'),

    # Báo cáo Đóng/Mở tài khoản
    path('reports/dong-mo-tai-khoan/', report_views.dong_mo_tai_khoan_report_view, name='dong_mo_tai_khoan_report'),
    path('reports/dong-mo-tai-khoan/process/', report_views.process_dong_mo_tai_khoan_report, name='process_dong_mo_tai_khoan'),

]
