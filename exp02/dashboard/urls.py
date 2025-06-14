from django.urls import path
from .views import shipping_risk_dashboard

urlpatterns = [
    path('', shipping_risk_dashboard, name='shipping-risk-dashboard'),
]
