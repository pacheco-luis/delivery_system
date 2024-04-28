from django.urls import path
from . import views

app_name = 'notifications_app'
urlpatterns = [
    # path('notification_viewer/', views.notification_viewer, name='notification_viewer')
    path('notifications_viewer/', views.notifications_viewer, name='notifications_viewer'),
    path('view_notification/<id>/', views.view_notification, name='view_notification'),
]