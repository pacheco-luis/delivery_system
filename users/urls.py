from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sign-in/', views.signInUser, name='sign-in'),
    path('sign-out/', views.signOutUser, name='sign-out'),
    path('sign-up/', views.signUpUser, name='sign-up'),
    path('account/', views.customerAccount, name='account'),
]