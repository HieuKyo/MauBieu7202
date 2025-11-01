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

    # Customer
    path('customers/', views.customer_list_view, name='customer_list'),
    path('api/customers/search/', views.customer_search_api, name='customer_search_api'),
    path('api/customers/<int:customer_id>/', views.customer_data_api, name='customer_data_api'),
    path('api/customers/<int:customer_id>/detail/', views.customer_detail_api, name='customer_detail_api'),
    path('api/customers/create/', views.customer_create_view, name='customer_create'),
    path('api/customers/<int:customer_id>/update/', views.customer_update_view, name='customer_update'),
    path('api/customers/<int:customer_id>/delete/', views.customer_delete_view, name='customer_delete'),

    # Branch Configuration
    path('branch-config/', views.branch_config_view, name='branch_config'),
]
