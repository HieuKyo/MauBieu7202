from django.urls import path

from . import views

app_name = 'led_board'

urlpatterns = [
    path('', views.board, name='board'),
    path('du-lieu/', views.board_data, name='data'),
    path('tat-may/', views.shutdown_signal, name='shutdown_signal'),
    path('anh/<int:pk>/', views.slide_image, name='slide_image'),
    path('nhap-ty-gia/', views.rate_edit, name='rate_edit'),
    path('lich-su/', views.rate_history, name='rate_history'),
    path('trinh-chieu/', views.slide_settings, name='slide_settings'),
]
