from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/packaging-trend/', views.packaging_trend_dashboard, name='packaging_trend_dashboard'),
]
