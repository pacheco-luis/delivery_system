from django.urls import path
from . import views

urlpatterns = [
    path('notification_viewer/', views.notification_viewer, name='notification_viewer')
]