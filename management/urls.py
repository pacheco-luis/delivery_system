from django.urls import path, reverse_lazy

from django.contrib.auth import views as auth_views
from . import views


app_name = 'management'
urlpatterns = [
    # authentication urls
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
