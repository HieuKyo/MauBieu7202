from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('send/', views.send_message, name='send'),
    path('<int:message_id>/read/', views.mark_read, name='mark_read'),
    path('<int:message_id>/delete/', views.delete_message, name='delete'),
    path('api/check/', views.api_check, name='api_check'),
]