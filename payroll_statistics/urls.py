"""
URL Configuration cho app Payroll Statistics
"""
from django.urls import path
from . import views

app_name = 'payroll_statistics'

urlpatterns = [
    path('', views.statistics_view, name='statistics'),
    path('upload/', views.upload_view, name='upload'),
    path('api/data/', views.statistics_data_api, name='statistics_data_api'),
]
