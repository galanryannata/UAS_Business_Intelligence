from django.urls import path
from . import views

urlpatterns = [
    path('shipping-cost/', views.shipping_cost_dashboard, name='shipping_cost_dashboard'),
]
