"""
URL Configuration cho module KPI Tool
"""
from django.urls import path
from . import views

app_name = 'kpi_tool'

urlpatterns = [
    # Trang chủ
    path('', views.index, name='index'),

    # Upload file DBF
    path('upload/', views.upload_view, name='upload'),

    # Danh sách lô
    path('batches/', views.batch_list, name='batch_list'),

    # Chi tiết lô
    path('batch/<int:batch_id>/', views.batch_detail, name='batch_detail'),

    # Xuất Excel theo file
    path('batch/<int:batch_id>/export/', views.export_excel, name='export_excel'),

    # Xuất Excel theo tháng (tổng hợp tất cả file)
    path('export-monthly/<str:teller_id>/<int:month>/<int:year>/', views.export_monthly_excel, name='export_monthly_excel'),

    # Import quy tắc
    path('import-rules/', views.import_rules_view, name='import_rules'),

    # Danh sách quy tắc
    path('rules/', views.rule_list, name='rule_list'),
]
