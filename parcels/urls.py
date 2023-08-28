from django.urls import path
from . import views

urlpatterns = [
    # customer urls
    path('', views.home, name='home'),
    path('parcels/', views.parcels, name='parcels'),
    path('parcel/<str:pk>/', views.parcel, name='parcel'),
    path('create-parcel/', views.createParcel, name='create-parcel'),
    path('update-parcel/<str:pk>/', views.updateParcel, name='update-parcel'),
    path('delete-parcel/<str:pk>/', views.deleteParcel, name='delete-parcel'),
]
