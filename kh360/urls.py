from django.urls import path

from . import views

app_name = 'kh360'

urlpatterns = [
    path('', views.tra_cuu, name='tra_cuu'),
    path('kh/<str:ma_kh>/', views.ho_so, name='ho_so'),
    path('kh/<str:ma_kh>/ghi-chu/', views.luu_ghi_chu, name='luu_ghi_chu'),
    path('cap-nhat/', views.cap_nhat, name='cap_nhat'),
    path('cap-nhat/gan-to-chuc/', views.gan_to_chuc, name='gan_to_chuc'),
    path('bien-dong/', views.bien_dong, name='bien_dong'),
    path('thong-ke/', views.thong_ke, name='thong_ke'),
    path('thong-ke/so-tiet-kiem/', views.thong_ke_so, name='thong_ke_so'),
    path('thong-ke/tien-vay/', views.thong_ke_vay, name='thong_ke_vay'),
]
