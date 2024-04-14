from django.urls import path, reverse_lazy

from django.contrib.auth import views as auth_views
from . import views


app_name = 'management'
urlpatterns = [
    # authentication urls
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_routes/create/assign/', views.create_assign_routes, name='routes'),
    path('admin_stations/', views.admin_stations, name='admin_stations'),
    path('admin_all_users/', views.admin_all_users, name='admin_all_users'),
    path('admin_packages/', views.admin_packages, name='admin_packages'),
]
