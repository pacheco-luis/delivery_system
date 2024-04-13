from django.urls import path, reverse_lazy

from django.contrib.auth import views as auth_views
from . import views


app_name = 'users'
urlpatterns = [
    # authentication urls
    path('login/', views.login_user, name='login'),
    path('logout/customer/', views.logoutCustomer, name='logout-customer'),
    path('logout/driver/', views.logoutDriver, name='logout-driver'),
    path('register/', views.register, name='register'),
    path('register/customer/', views.registerCustomer, name='register-customer'),
    path('register/driver/', views.registerDriver, name='register-driver'),

    # reset password urls
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name="reset_password.html",
                                              email_template_name='reset_password_email.html',
                                              subject_template_name='reset_password_subject.txt',
                                              success_url=reverse_lazy('users:password_reset_done')),
         name='reset_password'),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="reset_password_sent.html"),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="reset.html",
                                                    success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="reset_password_complete.html"),
         name='password_reset_complete'),

    # customer urls
    path('account/customer/', views.customerAccount, name='customer-account'),
    path('account/driver/', views.driverAccount, name='driver-account'),
    path('edit-customer-account/', views.editCustomerAccount, name='edit-customer-account'),
    path('edit-driver-account/', views.editDriverAccount, name='edit-driver-account'),
    
    # company contact information and about info
    path('company-info/', views.viewCompanyInformation, name="view-company-info")
]
