from django.urls import path
from . import views

urlpatterns = [
    # customer urls
    path('', views.home, name='home'),
    path('parcels/', views.parcels, name='parcels'),
]

