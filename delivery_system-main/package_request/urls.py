from django.urls import path
from . import views

app_name = 'package_request_app'
urlpatterns = [
    path('', views.RequestForm, name='request_form'),
    path('successful/', views.sucess, name='successful'),
    path('package_list/', views.all_packages, name = 'package_list'),
    path('delete_request/<id>', views.delete_request, name = 'delete_request')
]
