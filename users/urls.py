from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # authentication
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),

    # customer
    path('account/', views.account, name='account'),
    path('edit-account/', views.editAccount, name='edit-account'),
]