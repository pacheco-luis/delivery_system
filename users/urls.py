from django.urls import path
from . import views

urlpatterns = [
    # authentication urls
    path('login/', views.loginUser, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerUser, name='register'),

    # customer urls
    path('account/', views.account, name='account'),
    path('edit-account/', views.editAccount, name='edit-account'),
]