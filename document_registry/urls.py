from django.urls import path
from . import views

app_name = 'document_registry'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Outgoing
    path('van-ban-di/', views.outgoing_list, name='outgoing_list'),
    path('van-ban-di/them/', views.outgoing_create, name='outgoing_create'),
    path('van-ban-di/<int:pk>/sua/', views.outgoing_edit, name='outgoing_edit'),
    path('van-ban-di/<int:pk>/xoa/', views.outgoing_delete, name='outgoing_delete'),
    # Incoming
    path('van-ban-den/', views.incoming_list, name='incoming_list'),
    path('van-ban-den/them/', views.incoming_create, name='incoming_create'),
    path('van-ban-den/<int:pk>/sua/', views.incoming_edit, name='incoming_edit'),
    path('van-ban-den/<int:pk>/xoa/', views.incoming_delete, name='incoming_delete'),
    # Export Excel
    path('van-ban-di/xuat-excel/', views.outgoing_export_excel, name='outgoing_export_excel'),
    path('van-ban-den/xuat-excel/', views.incoming_export_excel, name='incoming_export_excel'),
]
