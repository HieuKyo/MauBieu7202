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
]
