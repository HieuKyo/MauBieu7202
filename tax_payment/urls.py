from django.urls import path
from . import views

app_name = 'tax_payment'

urlpatterns = [
    # Main views
    path('', views.tax_payment_create, name='create'),
    path('list/', views.tax_statement_list, name='list'),
    path('export/<int:statement_id>/', views.export_tax_statement, name='export'),
    path('edit/<int:pk>/', views.tax_payment_edit, name='edit'),
    path('delete/<int:pk>/', views.tax_payment_delete, name='delete'),
    # AJAX endpoints cho cascading dropdown
    path('ajax/get-co-quan-thue/', views.get_co_quan_thue, name='ajax_get_co_quan_thue'),
    path('ajax/get-xa-phuong/', views.get_xa_phuong, name='ajax_get_xa_phuong'),
    path('ajax/get-location-details/', views.get_location_details, name='ajax_get_location_details'),
    path('ajax/search-sub-entry/', views.search_sub_entry, name='ajax_search_sub_entry'),
    path('ajax/search-sub-entries/', views.search_sub_entries, name='ajax_search_sub_entries'),
]
