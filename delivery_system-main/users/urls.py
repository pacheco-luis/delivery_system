from django.urls import path, include
from . import views

app_name = 'users'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),
    path('account/', views.customerAccount, name='account'),
    path('edit-account/', views.editAccount, name='edit-account'),
]