from django.urls import path
from . import views

app_name = "savings_calculator"

urlpatterns = [
    path("", views.calculator_view, name="calculator"),
    path("api/rates/", views.api_get_rates, name="api_rates"),
    path("api/calculate/", views.api_calculate, name="api_calculate"),
    path("trai-phieu/", views.bond_calculator_view, name="bond_calculator"),
    path("api/bond-calculate/", views.api_bond_calculate, name="api_bond_calculate"),
]
