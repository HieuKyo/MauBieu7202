"""
URL configuration for templates_app
"""
from django.urls import path
from . import views
from . import customer_views
from . import tools_views
from . import permission_views
from . import business_views
from . import beautiful_number_views
from . import bank_statement_views
from . import elearning_views
from . import employee_views
from . import atm_views
from . import report_views
from . import report_huy_dong_von_views
from . import report_thu_ho_views
from . import kpi_views
from . import td_views
from . import hdv_reg_views
from . import qr_reg_views
from . import cash_drawer_views
from . import can_doi_views
from . import bia_chung_tu_views
from . import spdv_kpi_views
from . import customer_export
from . import customer_cif_tools
from . import customer_cccd_images
from . import customer_signature
from . import student_registration

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
    path('customers/', customer_views.customer_list_view, name='customer_list'),
    path('customers/export/', customer_export.customer_export_view, name='customer_export'),
    path('customers/update-codes/', customer_cif_tools.customer_update_codes_view, name='customer_update_codes'),
    path('customers/signature-folders/', customer_cif_tools.customer_signature_folders_view, name='customer_signature_folders'),
    path('customers/students/import/', student_registration.student_import_view, name='student_import'),
    path('customers/batch-print/', student_registration.student_batch_print_view, name='student_batch_print'),
    path('customers/students/keys/', student_registration.student_keys_view, name='student_keys'),
    path('customers/cccd-anh/in-lo/', customer_cccd_images.cccd_batch_print_view, name='cccd_batch_print'),
    path('customers/<int:customer_id>/cccd-anh/<str:side>/', customer_cccd_images.customer_cccd_image_view, name='customer_cccd_image'),
    path('customers/<int:customer_id>/signatures/', customer_signature.customer_signatures_view, name='customer_signatures'),
    path('customers/<int:customer_id>/signatures/<str:name>/', customer_signature.customer_signature_file_view, name='customer_signature_file'),
    path('customers/<int:customer_id>/signatures/<str:name>/delete/', customer_signature.customer_signature_delete_view, name='customer_signature_delete'),
    path('api/customers/search/', customer_views.customer_search_api, name='customer_search_api'),
    path('api/customers/<int:customer_id>/', customer_views.customer_get, name='customer_get'),
    path('api/customers/<int:customer_id>/data/', customer_views.customer_data_api, name='customer_data_api'),
    path('api/customers/<int:customer_id>/detail/', customer_views.customer_detail_api, name='customer_detail_api'),
    path('api/customers/create/', customer_views.customer_create_view, name='customer_create'),
    path('api/customers/<int:customer_id>/update/', customer_views.customer_update_view, name='customer_update'),
    path('api/customers/<int:customer_id>/delete/', customer_views.customer_delete_view, name='customer_delete'),
    path('api/customers/import-excel/', customer_views.customer_import_excel, name='customer_import_excel'),
    path('api/customers/import/tsv/', customer_views.customer_import_tsv, name='customer_import_tsv'),

    # Business (Doanh nghiệp)
    path('businesses/', business_views.business_list_view, name='business_list'),
    path('api/businesses/search/', business_views.business_search_api, name='business_search_api'),
    path('api/businesses/<int:business_id>/data/', business_views.business_data_api, name='business_data_api'),

    # Business Dashboard and CRUD
    path('business/', business_views.business_dashboard, name='business_dashboard'),
    path('business/create/', business_views.business_create, name='business_create'),
    path('business/<int:business_id>/edit/', business_views.business_edit, name='business_edit'),
    path('business/<int:business_id>/delete/', business_views.business_delete, name='business_delete'),
    path('business/<int:business_id>/template/<int:template_id>/', business_views.business_load_data, name='business_load_data'),
    path('api/businesses/import/tsv/', business_views.business_import_tsv, name='business_import_tsv'),

    # Global Configuration (Branch + Custom Variables)
    path('branch-config/', views.branch_config_view, name='branch_config'),
    path('api/custom-variables/add/', views.add_custom_variable, name='add_custom_variable'),
    path('api/custom-variables/update/', views.update_custom_variable, name='update_custom_variable'),
    path('api/custom-variables/delete/', views.delete_custom_variable, name='delete_custom_variable'),

    # Variable Library
    path('variable-library/', views.variable_library_view, name='variable_library'),

    # Beautiful Number Fee Lookup
    path('beautiful-number-lookup/', beautiful_number_views.beautiful_number_lookup, name='beautiful_number_lookup'),
    path('beautiful-number-list/', beautiful_number_views.beautiful_number_list, name='beautiful_number_list'),
    path('beautiful-number-list/export/', beautiful_number_views.beautiful_number_list_export_csv, name='beautiful_number_list_export_csv'),
    path('api/beautiful-numbers/generate/', beautiful_number_views.generate_beautiful_numbers_ajax, name='generate_beautiful_numbers'),
    path('api/beautiful-numbers/refresh/', beautiful_number_views.refresh_beautiful_numbers_ajax, name='refresh_beautiful_numbers'),

    # Area Lookup
    path('area-lookup/', tools_views.area_lookup, name='area_lookup'),

    # OCR Tool
    path('ocr-tool/', tools_views.ocr_tool_view, name='ocr_tool'),

    # Calculator
    path('calculator/', tools_views.calculator_view, name='calculator'),

    # PDF Tools
    path('pdf-tools/', tools_views.pdf_tools_view, name='pdf_tools'),
    path('pdf-tools/split/', tools_views.pdf_split_view, name='pdf_split'),
    path('pdf-tools/merge/', tools_views.pdf_merge_view, name='pdf_merge'),

    # Bank Statement Analyzer
    path('bank-statement/upload/', bank_statement_views.bank_statement_upload, name='bank_statement_upload'),
    path('bank-statement/result/<int:statement_id>/', bank_statement_views.bank_statement_result, name='bank_statement_result'),
    path('bank-statement/export/<int:statement_id>/', bank_statement_views.bank_statement_export, name='bank_statement_export'),
    path('bank-statement/huong-dan/', bank_statement_views.bank_statement_huong_dan, name='bank_statement_huong_dan'),
    path('bank-statement/import-names/<int:statement_id>/', bank_statement_views.bank_statement_import_names, name='bank_statement_import_names'),

    # Employee Management
    path('employees/', employee_views.employee_list, name='employee_list'),
    path('employees/export/', employee_views.employee_export_excel, name='employee_export_excel'),
    path('employees/import/', employee_views.employee_import_excel, name='employee_import_excel'),
    path('employees/import/template/', employee_views.download_employee_template, name='download_employee_template'),
    path('employees/create/', employee_views.employee_create_manual, name='employee_create_manual'),
    path('employees/<int:employee_id>/update/', employee_views.employee_update_manual, name='employee_update_manual'),
    path('employees/<int:employee_id>/delete/', employee_views.employee_delete_manual, name='employee_delete_manual'),

    # E-Learning
    path('elearning/', elearning_views.course_dashboard, name='course_dashboard'),
    path('elearning/courses/create/', elearning_views.course_create, name='course_create'),
    path('elearning/courses/<int:course_id>/edit/', elearning_views.course_edit, name='course_edit'),
    path('elearning/courses/<int:course_id>/delete/', elearning_views.course_delete, name='course_delete'),
    path('elearning/courses/<int:course_id>/add-students/', elearning_views.course_add_students, name='course_add_students'),
    path('elearning/courses/<int:course_id>/remove-student/<int:user_id>/', elearning_views.course_remove_student, name='course_remove_student'),
    path('elearning/enrollment/<int:enrollment_id>/toggle/', elearning_views.course_toggle_completion, name='course_toggle_completion'),
    path('elearning/courses/<int:course_id>/chua-hoc/in/', elearning_views.course_print_not_enrolled, name='course_print_not_enrolled'),
    path('elearning/search/learner/', elearning_views.course_search_by_learner, name='course_search_by_learner'),
    path('elearning/search/department/', elearning_views.course_search_by_department, name='course_search_by_department'),

    # ATM Management
    path('atm/', atm_views.atm_dashboard, name='atm_dashboard'),
    path('atm/guide/download/', atm_views.atm_guide_download, name='atm_guide_download'),
    path('atm/replenishment/create/', atm_views.atm_replenishment_create, name='atm_replenishment_create'),
    path('atm/replenishment/list/', atm_views.atm_replenishment_list, name='atm_replenishment_list'),
    path('atm/replenishment/<int:replenishment_id>/edit/', atm_views.atm_replenishment_edit, name='atm_replenishment_edit'),
    path('atm/replenishment/<int:replenishment_id>/delete/', atm_views.atm_replenishment_delete, name='atm_replenishment_delete'),
    path('atm/replenishment/<int:replenishment_id>/template/<int:template_id>/', atm_views.atm_load_replenishment_data, name='atm_load_replenishment_data'),

    # ATM Discrepancy Management
    path('atm/discrepancy/list/', atm_views.atm_discrepancy_list, name='atm_discrepancy_list'),
    path('atm/discrepancy/create/', atm_views.atm_discrepancy_create, name='atm_discrepancy_create'),
    path('atm/discrepancy/<int:discrepancy_id>/edit/', atm_views.atm_discrepancy_edit, name='atm_discrepancy_edit'),
    path('atm/discrepancy/<int:discrepancy_id>/delete/', atm_views.atm_discrepancy_delete, name='atm_discrepancy_delete'),
    path('atm/discrepancy/cycle/<str:atm_id>/<str:start_date>/<str:end_date>/word/', atm_views.atm_discrepancy_group_word, name='atm_discrepancy_group_word'),
    path('atm/discrepancy/<int:discrepancy_id>/template/<int:template_id>/', atm_views.atm_load_discrepancy_data, name='atm_load_discrepancy_data'),
    path('atm/discrepancy/cycle/<str:atm_id>/<str:start_date>/<str:end_date>/template/<int:template_id>/', atm_views.atm_load_discrepancy_cycle_template, name='atm_load_discrepancy_cycle_template'),

    # Lịch trực xe
    path('atm/vehicle-duty-schedule/', atm_views.vehicle_duty_schedule, name='vehicle_duty_schedule'),

    # ATM Travel Claim (Bảng kê thanh toán + Giấy đi đường)
    path('atm/travel-claim/', atm_views.atm_travel_claim, name='atm_travel_claim'),
    path('atm/travel-claim/payment-statement/word/', atm_views.atm_payment_statement_word, name='atm_payment_statement_word'),
    path('atm/travel-claim/travel-log/zip/', atm_views.atm_travel_log_word, name='atm_travel_log_zip'),

    # Reports Module
    path('reports/', report_views.report_hub, name='report_hub'),
    path('reports/lai-ton-dong/', report_views.lai_ton_dong_report_view, name='lai_ton_dong_report'),
    path('reports/lai-ton-dong/process/', report_views.process_lai_ton_dong_report, name='process_lai_ton_dong'),
    path('reports/phat-hanh-the/', report_views.phat_hanh_the_report_view, name='phat_hanh_the_report'),
    path('reports/phat-hanh-the/process/', report_views.process_phat_hanh_the_report, name='process_phat_hanh_the'),
    path('reports/phat-hanh-the/process-print/', report_views.process_phat_hanh_the_for_print, name='process_phat_hanh_the_for_print'),
    path('reports/phat-hanh-the/process-thang/', report_views.process_phat_hanh_the_thang, name='process_phat_hanh_the_thang'),
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
    path('reports/huy-dong-von/', report_huy_dong_von_views.huy_dong_von_report_view, name='huy_dong_von_report'),
    path('reports/huy-dong-von/process/', report_huy_dong_von_views.process_huy_dong_von_report, name='process_huy_dong_von'),
    path('reports/thu-ho-hoc-phi-dien-luc/', report_thu_ho_views.thu_ho_hoc_phi_report_view, name='thu_ho_hoc_phi_report'),
    path('reports/thu-ho-hoc-phi-dien-luc/process/', report_thu_ho_views.process_thu_ho_hoc_phi_report, name='process_thu_ho_hoc_phi'),
    path('reports/thu-ho-hoc-phi-dien-luc/download/', report_thu_ho_views.download_thu_ho_hoc_phi_report, name='download_thu_ho_hoc_phi'),

    # Đăng ký chỉ tiêu Huy động vốn
    path('hdv/dashboard/', hdv_reg_views.hdv_dashboard_view, name='hdv_dashboard'),
    path('hdv/bao-cao/', hdv_reg_views.hdv_reports_view, name='hdv_reports'),
    path('hdv/bao-cao/export/', hdv_reg_views.hdv_reports_export_view, name='hdv_reports_export'),
    path('hdv/dang-ky/', hdv_reg_views.hdv_registration_list_view, name='hdv_registration_list'),
    path('hdv/dang-ky/in/', hdv_reg_views.hdv_registration_print_view, name='hdv_registration_print'),
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
    path('qr/dang-ky/xuat-file/', qr_reg_views.qr_registration_export_view, name='qr_registration_export'),
    path('qr/huong-dan/', qr_reg_views.qr_huong_dan_word_view, name='qr_huong_dan'),
    path('hdv/import/', hdv_reg_views.hdv_import_upload_view, name='hdv_import_upload'),

    # Thống kê chỉ tiêu Sản phẩm dịch vụ (Kế toán Ngân quỹ)
    path('spdv-kpi/', spdv_kpi_views.spdv_kpi_dashboard, name='spdv_kpi_dashboard'),
    path('spdv-kpi/import/', spdv_kpi_views.spdv_kpi_import, name='spdv_kpi_import'),
    path('spdv-kpi/targets/', spdv_kpi_views.spdv_kpi_target_set, name='spdv_kpi_target_set'),
    path('spdv-kpi/detail/<int:user_id>/<str:metric_type>/', spdv_kpi_views.spdv_kpi_gdv_detail, name='spdv_kpi_gdv_detail'),
    path('spdv-kpi/detail/<int:user_id>/<str:metric_type>/export/', spdv_kpi_views.spdv_kpi_gdv_detail_export, name='spdv_kpi_gdv_detail_export'),

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

    # Tạo bìa chứng từ (Kế toán Ngân quỹ)
    path('bia-chung-tu/', bia_chung_tu_views.bia_list, name='bia_chung_tu_list'),
    path('bia-chung-tu/cap-so/', bia_chung_tu_views.bia_cap_so, name='bia_chung_tu_cap_so'),
    path('bia-chung-tu/<int:pk>/sua/', bia_chung_tu_views.bia_edit, name='bia_chung_tu_edit'),
    path('bia-chung-tu/<int:pk>/xoa/', bia_chung_tu_views.bia_delete, name='bia_chung_tu_delete'),
    path('bia-chung-tu/luu-so-to/', bia_chung_tu_views.bia_save_so_to, name='bia_chung_tu_save_so_to'),
    path('bia-chung-tu/import/', bia_chung_tu_views.bia_import, name='bia_chung_tu_import'),
    path('bia-chung-tu/import/xac-nhan/', bia_chung_tu_views.bia_import_confirm, name='bia_chung_tu_import_confirm'),
    path('bia-chung-tu/in/', bia_chung_tu_views.bia_print, name='bia_chung_tu_print'),
    path('bia-chung-tu/huong-dan/', bia_chung_tu_views.bia_huong_dan, name='bia_chung_tu_huong_dan'),

    # Permission Management
    path('permissions/', permission_views.permission_management_view, name='permission_management'),
    path('permissions/users/<int:user_id>/superuser/', permission_views.update_superuser_status, name='update_superuser_status'),
    path('permissions/users/<int:user_id>/groups/', permission_views.update_user_groups, name='update_user_groups'),
    path('permissions/users/<int:user_id>/permissions/', permission_views.get_user_permissions_detail, name='get_user_permissions_detail'),

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
    path('tin-dung/so-sanh/', td_views.td_so_sanh_view, name='td_so_sanh'),
    path('tin-dung/api/so-sanh-records/', td_views.td_so_sanh_records_api, name='td_so_sanh_records_api'),
    # Backward compat
    path('tin-dung/xuat-bao-cao/', td_views.td_export_word_view, name='td_export'),

]
