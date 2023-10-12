from django.db.models.signals import post_save, post_delete
from django.core.mail import send_mail
from django.conf import settings

# from django.contrib.auth.models import User
from .models import User, Customer, Driver

# Authentication signals
def createCustomer(sender, instance, created, **kwargs):
    user = instance
    account = None
    
    if created and user.is_customer:
        account = Customer.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
        )
    if created and user.is_driver:
        account = Driver.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
        )
    if account:
        subject = "Welcome to the Delivery App"
        message = "We are glad you are here. Thank you for joining us."

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [account.email],
            fail_silently=False,
        )

# Customer signals
def updateAccount(sender, instance, created, **kwargs):
    account = instance
    user = account.user
    if created == False:
        user.first_name = account.first_name
        user.last_name = account.last_name
        user.username = account.username
        user.email = account.email
        user.save()

def deleteAccount(sender, instance, **kwargs):
    user = instance.user
    user.delete()

post_save.connect(createCustomer, sender=User)
post_save.connect(updateAccount, sender=Customer)
post_save.connect(updateAccount, sender=Driver)
post_delete.connect(deleteAccount, sender=Customer)
post_delete.connect(deleteAccount, sender=Driver)
