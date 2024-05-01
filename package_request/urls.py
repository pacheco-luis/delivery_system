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
    path('package_history/', views.package_history, name = 'package_history'),
    path('job_list/', views.all_jobs, name = 'job_list'),
    path('job_list/<id>/', views.job_detail, name = 'job_detail'),
    path('job_current/', views.current_job, name = 'job_current'),
    path('job_completed/', views.completed_job, name = 'job_completed'),
    path('api/job_list/', views.api_all_jobs, name = 'api_job_list'),
    path('api/job_list/current/<id>/update/', views.api_take_photo, name = 'api_job_list_current'),
    path('delete_request/<id>/', views.delete_request, name = 'delete_request'),
    path('cluster_route/<id>/', views.cluster_route, name = 'cluster_route'),
    path('jobs/delivery/', views.job_deliver, name = 'job_deliver'),
    path('jobs/delivery/route/', views.cluster_route_deliver, name = 'cluster_route_deliver'),
    path('jobs/delivery/route/<id>/camera/', views.take_photo, name = 'take_photo'),
    path('unauthorized/', views.unauthorized, name = '401'),
    path('job_list/packages', views.select_packages, name = 'select_packages'),
    
    # path('job_type_selection', views.job_type_selection, name = 'job_selector' ),
    # path('route_list/', views.create_routes, name = 'route_list'),
    path('route_list/<id>/', views.job_details, name = 'job_details'),

    path('job_scanner/', views.job_scanner, name = 'job_scanner'),
    path('success_or_fail/', views.success_or_fail, name = 'success_or_fail'),
]
