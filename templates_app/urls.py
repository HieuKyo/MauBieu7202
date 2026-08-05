"""
URL configuration for templates_app
"""
from django.urls import path
from . import views
from . import report_views
from . import kpi_views
from . import td_views
from . import hdv_reg_views
from . import qr_reg_views
from . import cash_drawer_views
from . import can_doi_views

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
    path('beautiful-number-list/export/', views.beautiful_number_list_export_csv, name='beautiful_number_list_export_csv'),
    path('api/beautiful-numbers/generate/', views.generate_beautiful_numbers_ajax, name='generate_beautiful_numbers'),
    path('api/beautiful-numbers/refresh/', views.refresh_beautiful_numbers_ajax, name='refresh_beautiful_numbers'),

    # Test Address Selector
    path('test-address-selector/', views.test_address_selector, name='test_address_selector'),

    # Area Lookup
    path('area-lookup/', views.area_lookup, name='area_lookup'),

    # OCR Tool
    path('ocr-tool/', views.ocr_tool_view, name='ocr_tool'),

    # Calculator
    path('calculator/', views.calculator_view, name='calculator'),

    # PDF Tools
    path('pdf-tools/', views.pdf_tools_view, name='pdf_tools'),
    path('pdf-tools/split/', views.pdf_split_view, name='pdf_split'),
    path('pdf-tools/merge/', views.pdf_merge_view, name='pdf_merge'),

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
    path('elearning/courses/<int:course_id>/chua-hoc/in/', views.course_print_not_enrolled, name='course_print_not_enrolled'),
    path('elearning/search/learner/', views.course_search_by_learner, name='course_search_by_learner'),
    path('elearning/search/department/', views.course_search_by_department, name='course_search_by_department'),

    # ATM Management
    path('atm/', views.atm_dashboard, name='atm_dashboard'),
    path('atm/replenishment/create/', views.atm_replenishment_create, name='atm_replenishment_create'),
    path('atm/replenishment/list/', views.atm_replenishment_list, name='atm_replenishment_list'),
    path('atm/replenishment/<int:replenishment_id>/edit/', views.atm_replenishment_edit, name='atm_replenishment_edit'),
    path('atm/replenishment/<int:replenishment_id>/delete/', views.atm_replenishment_delete, name='atm_replenishment_delete'),
    path('atm/replenishment/<int:replenishment_id>/template/<int:template_id>/', views.atm_load_replenishment_data, name='atm_load_replenishment_data'),

    # ATM Discrepancy Management
    path('atm/discrepancy/list/', views.atm_discrepancy_list, name='atm_discrepancy_list'),
    path('atm/discrepancy/create/', views.atm_discrepancy_create, name='atm_discrepancy_create'),
    path('atm/discrepancy/<int:discrepancy_id>/edit/', views.atm_discrepancy_edit, name='atm_discrepancy_edit'),
    path('atm/discrepancy/<int:discrepancy_id>/delete/', views.atm_discrepancy_delete, name='atm_discrepancy_delete'),
    path('atm/discrepancy/cycle/<str:atm_id>/<str:start_date>/<str:end_date>/word/', views.atm_discrepancy_group_word, name='atm_discrepancy_group_word'),
    path('atm/discrepancy/<int:discrepancy_id>/template/<int:template_id>/', views.atm_load_discrepancy_data, name='atm_load_discrepancy_data'),
    path('atm/discrepancy/cycle/<str:atm_id>/<str:start_date>/<str:end_date>/template/<int:template_id>/', views.atm_load_discrepancy_cycle_template, name='atm_load_discrepancy_cycle_template'),

    # Lịch trực xe
    path('atm/vehicle-duty-schedule/', views.vehicle_duty_schedule, name='vehicle_duty_schedule'),

    # ATM Travel Claim (Bảng kê thanh toán + Giấy đi đường)
    path('atm/travel-claim/', views.atm_travel_claim, name='atm_travel_claim'),
    path('atm/travel-claim/payment-statement/word/', views.atm_payment_statement_word, name='atm_payment_statement_word'),
    path('atm/travel-claim/travel-log/zip/', views.atm_travel_log_word, name='atm_travel_log_zip'),

    # Reports Module
    path('reports/', report_views.report_hub, name='report_hub'),
    path('reports/lai-ton-dong/', report_views.lai_ton_dong_report_view, name='lai_ton_dong_report'),
    path('reports/lai-ton-dong/process/', report_views.process_lai_ton_dong_report, name='process_lai_ton_dong'),
    path('reports/phat-hanh-the/', report_views.phat_hanh_the_report_view, name='phat_hanh_the_report'),
    path('reports/phat-hanh-the/process/', report_views.process_phat_hanh_the_report, name='process_phat_hanh_the'),
    path('reports/phat-hanh-the/process-print/', report_views.process_phat_hanh_the_for_print, name='process_phat_hanh_the_for_print'),
    path('reports/phat-hanh-the/print-preview/', report_views.phat_hanh_the_print_preview, name='phat_hanh_the_print_preview'),
    path('reports/phat-hanh-the/process-visa/', report_views.process_visa_card_report, name='process_visa_card'),
    path('reports/phat-hanh-the/process-visa-print/', report_views.process_visa_card_for_print, name='process_visa_card_for_print'),
    path('reports/mail-envelope/', report_views.mail_envelope_tracking_view, name='mail_envelope_tracking'),
    path('reports/mail-envelope/save/', report_views.save_mail_envelope, name='save_mail_envelope'),
    path('reports/mail-envelope/report/', report_views.mail_envelope_report_view, name='mail_envelope_report'),
    path('reports/tiet-kiem-tra-lai/', report_views.tiet_kiem_tra_lai_view, name='tiet_kiem_tra_lai'),
    path('reports/tiet-kiem-tra-lai/detail/<str:metric_key>/', report_views.tiet_kiem_tra_lai_detail, name='tiet_kiem_tra_lai_detail'),
    path('reports/tiet-kiem-tra-lai/download/<str:metric_key>/', report_views.tiet_kiem_tra_lai_download, name='tiet_kiem_tra_lai_download'),
    path('reports/dien-luc/', report_views.dien_luc_report_view, name='dien_luc_report'),
    path('reports/dien-luc/process/', report_views.process_dien_luc_report, name='process_dien_luc'),
    path('reports/atm-fund-balance/', report_views.atm_fund_balance_view, name='atm_fund_balance'),
    path('reports/huy-dong-von/', report_views.huy_dong_von_report_view, name='huy_dong_von_report'),
    path('reports/huy-dong-von/process/', report_views.process_huy_dong_von_report, name='process_huy_dong_von'),
    path('reports/thu-ho-hoc-phi-dien-luc/', report_views.thu_ho_hoc_phi_report_view, name='thu_ho_hoc_phi_report'),
    path('reports/thu-ho-hoc-phi-dien-luc/process/', report_views.process_thu_ho_hoc_phi_report, name='process_thu_ho_hoc_phi'),
    path('reports/thu-ho-hoc-phi-dien-luc/download/', report_views.download_thu_ho_hoc_phi_report, name='download_thu_ho_hoc_phi'),

    # Đăng ký chỉ tiêu Huy động vốn
    path('hdv/dashboard/', hdv_reg_views.hdv_dashboard_view, name='hdv_dashboard'),
    path('hdv/bao-cao/', hdv_reg_views.hdv_reports_view, name='hdv_reports'),
    path('hdv/bao-cao/export/', hdv_reg_views.hdv_reports_export_view, name='hdv_reports_export'),
    path('hdv/dang-ky/', hdv_reg_views.hdv_registration_list_view, name='hdv_registration_list'),
    path('hdv/dang-ky/create/', hdv_reg_views.hdv_registration_create_view, name='hdv_registration_create'),
    path('hdv/dang-ky/<int:pk>/update/', hdv_reg_views.hdv_registration_update_view, name='hdv_registration_update'),
    path('hdv/dang-ky/<int:pk>/delete/', hdv_reg_views.hdv_registration_delete_view, name='hdv_registration_delete'),
    path('hdv/api/can-bo/', hdv_reg_views.hdv_employee_lookup_view, name='hdv_employee_lookup'),
    path('hdv/dang-ky/mau-tai-ve/', hdv_reg_views.hdv_registration_template_download_view, name='hdv_registration_template_download'),
    path('hdv/dang-ky/upload/', hdv_reg_views.hdv_registration_import_view, name='hdv_registration_import'),
    path('hdv/duyet/', hdv_reg_views.hdv_approval_list_view, name='hdv_approval_list'),
    path('hdv/duyet/<int:pk>/', hdv_reg_views.hdv_approve_view, name='hdv_approve'),
    path('hdv/add-chi-tieu/', hdv_reg_views.hdv_add_chi_tieu_list_view, name='hdv_add_chi_tieu_list'),
    path('hdv/add-chi-tieu/<int:pk>/', hdv_reg_views.hdv_add_chi_tieu_view, name='hdv_add_chi_tieu'),
    path('hdv/add-chi-tieu/in/', hdv_reg_views.hdv_add_chi_tieu_print_view, name='hdv_add_chi_tieu_print'),

    # Đăng ký bảng QR
    path('qr/dashboard/', qr_reg_views.qr_dashboard_view, name='qr_dashboard'),
    path('qr/dang-ky/', qr_reg_views.qr_registration_list_view, name='qr_registration_list'),
    path('qr/dang-ky/create/', qr_reg_views.qr_registration_create_view, name='qr_registration_create'),
    path('qr/dang-ky/<int:pk>/update/', qr_reg_views.qr_registration_update_view, name='qr_registration_update'),
    path('qr/dang-ky/<int:pk>/delete/', qr_reg_views.qr_registration_delete_view, name='qr_registration_delete'),
    path('qr/dang-ky/mau-tai-ve/', qr_reg_views.qr_registration_template_download_view, name='qr_registration_template_download'),
    path('qr/dang-ky/upload/', qr_reg_views.qr_registration_import_view, name='qr_registration_import'),
    path('hdv/import/', hdv_reg_views.hdv_import_upload_view, name='hdv_import_upload'),

    # Bảng kê tiền mặt (Kế toán Ngân quỹ)
    path('cash/bang-ke/', cash_drawer_views.cash_statement_view, name='cash_statement'),
    path('cash/bang-ke/submit/', cash_drawer_views.cash_statement_submit_view, name='cash_statement_submit'),
    path('cash/bang-ke/<int:pk>/pdf/', cash_drawer_views.cash_statement_print_pdf_view, name='cash_statement_print_pdf'),
    path('cash/bang-ke/<int:pk>/pdf-day-du/', cash_drawer_views.cash_statement_full_pdf_view, name='cash_statement_full_pdf'),
    path('cash/bang-ke/<int:pk>/pdf-nop-tien/', cash_drawer_views.cash_statement_nop_tien_pdf_view, name='cash_statement_nop_tien_pdf'),
    path('cash/de-nghi-tiep-quy/submit/', cash_drawer_views.cash_de_nghi_submit_view, name='cash_de_nghi_submit'),
    path('cash/de-nghi-tiep-quy/<int:pk>/pdf/', cash_drawer_views.cash_de_nghi_pdf_view, name='cash_de_nghi_pdf'),
    path('cash/reset/', cash_drawer_views.cash_drawer_reset_view, name='cash_drawer_reset'),
    path('cash/lich-su/', cash_drawer_views.cash_drawer_history_view, name='cash_drawer_history'),
    path('cash/lich-su/<int:pk>/sua/', cash_drawer_views.cash_statement_edit_view, name='cash_statement_edit'),
    path('cash/lich-su/<int:pk>/sua/submit/', cash_drawer_views.cash_statement_edit_submit_view, name='cash_statement_edit_submit'),
    path('cash/lich-su/<int:pk>/xoa/', cash_drawer_views.cash_statement_delete_view, name='cash_statement_delete'),
    path('cash/cau-hinh-in/', cash_drawer_views.cash_print_config_view, name='cash_print_config'),
    path('cash/cau-hinh-in/trang/submit/', cash_drawer_views.cash_print_config_trang_submit_view, name='cash_print_config_trang_submit'),
    path('cash/cau-hinh-in/trang/preview/', cash_drawer_views.cash_print_config_preview_view, name='cash_print_config_preview'),
    path('cash/cau-hinh-in/nop-tien/submit/', cash_drawer_views.cash_print_config_nop_tien_submit_view, name='cash_print_config_nop_tien_submit'),
    path('cash/cau-hinh-in/nop-tien/preview/', cash_drawer_views.cash_print_config_nop_tien_preview_view, name='cash_print_config_nop_tien_preview'),
    path('cash/cau-hinh-in/thu/submit/', cash_drawer_views.cash_print_config_thu_submit_view, name='cash_print_config_thu_submit'),
    path('cash/cau-hinh-in/thu/preview/', cash_drawer_views.cash_print_config_thu_preview_view, name='cash_print_config_thu_preview'),
    path('cash/cau-hinh-in/chi/submit/', cash_drawer_views.cash_print_config_chi_submit_view, name='cash_print_config_chi_submit'),
    path('cash/cau-hinh-in/chi/preview/', cash_drawer_views.cash_print_config_chi_preview_view, name='cash_print_config_chi_preview'),
    path('cash/cau-hinh-in/de-nghi/submit/', cash_drawer_views.cash_print_config_de_nghi_submit_view, name='cash_print_config_de_nghi_submit'),
    path('cash/cau-hinh-in/de-nghi/preview/', cash_drawer_views.cash_print_config_de_nghi_preview_view, name='cash_print_config_de_nghi_preview'),

    # Đọc Cân đối (Kế toán Ngân quỹ)
    path('can-doi/upload/', can_doi_views.can_doi_upload, name='can_doi_upload'),
    path('can-doi/result/<int:upload_id>/', can_doi_views.can_doi_result, name='can_doi_result'),

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

    # Phân tích danh mục tín dụng (MSIT80 offline)
    path('tin-dung/phan-tich/', td_views.td_upload_view, name='td_analysis'),
    path('tin-dung/dashboard/', td_views.td_dashboard_view, name='td_dashboard'),
    path('tin-dung/api/filter/', td_views.td_filter_api, name='td_filter_api'),
    path('tin-dung/api/so-sanh/', td_views.td_so_sanh_api, name='td_so_sanh_api'),
    path('tin-dung/api/snapshots/', td_views.td_snapshots_api, name='td_snapshots_api'),
    path('tin-dung/xuat-word/', td_views.td_export_word_view, name='td_export_word'),
    path('tin-dung/xuat-excel/', td_views.td_export_excel_view, name='td_export_excel'),
    path('tin-dung/ftp-config/', td_views.td_ftp_config_view, name='td_ftp_config'),
    path('tin-dung/ftp-config/<int:pk>/delete/', td_views.td_ftp_delete_view, name='td_ftp_delete'),
    path('tin-dung/faq/', td_views.td_faq_view, name='td_faq'),
    path('tin-dung/debug-cols/', td_views.td_debug_cols_view, name='td_debug_cols'),
    path('tin-dung/so-sanh/', td_views.td_so_sanh_view, name='td_so_sanh'),
    path('tin-dung/api/so-sanh-records/', td_views.td_so_sanh_records_api, name='td_so_sanh_records_api'),
    # Backward compat
    path('tin-dung/xuat-bao-cao/', td_views.td_export_word_view, name='td_export'),

]
