"""
URLs cho app Salary
"""
from django.urls import path
from . import views

app_name = 'salary'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Upload
    path('upload/', views.upload_file, name='upload'),
    
    # Processing History
    path('history/', views.processing_history, name='history'),
    path('history/<int:pk>/', views.processing_detail, name='processing_detail'),
    path('history/<int:pk>/download/', views.download_output_file, name='download_output'),
    
    # Beneficiaries
    path('beneficiaries/', views.beneficiary_list, name='beneficiary_list'),
    
    # Company Accounts
    path('accounts/', views.company_account_list, name='company_account_list'),
    path('api/accounts/search/', views.company_account_search, name='company_account_search'),

    # Access Denied
    path('access-denied/', views.access_denied, name='access_denied'),
]
