from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Main view
    path('', views.task_list_view, name='list'),

    # API endpoints
    path('api/toggle/', views.task_toggle_api, name='toggle_api'),
    path('api/create/', views.task_create_api, name='create_api'),
    path('api/<int:task_id>/', views.task_detail_api, name='detail_api'),
    path('api/<int:task_id>/update/', views.task_update_api, name='update_api'),
    path('api/<int:task_id>/delete/', views.task_delete_api, name='delete_api'),
]
