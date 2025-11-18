"""
URL configuration for templates_app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

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

    # Bank Statement Analyzer
    path('bank-statement/upload/', views.bank_statement_upload, name='bank_statement_upload'),
    path('bank-statement/result/<int:statement_id>/', views.bank_statement_result, name='bank_statement_result'),
    path('bank-statement/export/<int:statement_id>/', views.bank_statement_export, name='bank_statement_export'),

    # Employee Management
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/import/', views.employee_import_excel, name='employee_import_excel'),
    path('employees/import/template/', views.download_employee_template, name='download_employee_template'),
    path('employees/create/', views.employee_create_manual, name='employee_create_manual'),
    path('employees/<int:employee_id>/update/', views.employee_update_manual, name='employee_update_manual'),
    path('employees/<int:employee_id>/delete/', views.employee_delete_manual, name='employee_delete_manual'),

    # E-Learning
    path('elearning/', views.course_dashboard, name='course_dashboard'),
    path('elearning/courses/create/', views.course_create, name='course_create'),
    path('elearning/courses/<int:course_id>/add-students/', views.course_add_students, name='course_add_students'),
    path('elearning/enrollment/<int:enrollment_id>/toggle/', views.course_toggle_completion, name='course_toggle_completion'),
]
