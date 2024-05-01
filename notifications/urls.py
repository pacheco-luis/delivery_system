from django.urls import path
from django.urls import path, reverse_lazy
from . import views

app_name = 'notifications_app'
urlpatterns = [
    path('notifications_viewer/', views.notifications_viewer, name='notifications_viewer'),
    path('view_notification/<id>/', views.view_notification, name='view_notification'),
    path('read_all_notifications/', views.read_all_notifications, name='read_all_notifications'),
    path('notification/unread/<id>/', views.unread_notification, name='unread_notification'),
]