from django.db.models.signals import post_save, post_delete
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.models import User
from .models import Customer

# Authentication signals
def createCustomer(sender, instance, created, **kwargs):
    if created:
        user = instance
        customer = Customer.objects.create(
            user=user,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
        )

        subject = "Welcome to the Delivery App"
        message = "We are glad you are here. Thank you for joining us."

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [customer.email],
            fail_silently=False,
        )

# Customer signals
def updateCustomer(sender, instance, created, **kwargs):
    customer = instance
    user = customer.user
    if created == False:
        user.first_name = customer.first_name
        user.last_name = customer.last_name
        user.username = customer.username
        user.email = customer.email
        user.save()

def deleteCustomer(sender, instance, **kwargs):
    user = instance.user
    user.delete()

post_save.connect(createCustomer, sender=User)
post_delete.connect(deleteCustomer, sender=Customer)
