from django.urls import path
from . import views

app_name = 'package_request_app'
urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('user_home/', views.home, name='home'),
    path('delivery-request/step1/', views.sender_form_handler, name='request_form_1_of_3'),
    path('delivery-request/step2/', views.receiver_form_handler, name='request_form_2_of_3'),
    path('delivery-request/step3/', views.package_form_handler, name='request_form_3_of_3'),
    path('successful/', views.sucess, name='successful'),
    path('package_list/', views.all_packages, name = 'package_list'),
    path('delete_request/<id>', views.delete_request, name = 'delete_request')
]
