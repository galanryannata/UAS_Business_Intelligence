from django.contrib import admin
from django.urls import path, include  # ⬅️ tambahkan include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),  # ⬅️ ini menampilkan dashboard di root "/"
]
