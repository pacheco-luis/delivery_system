from django.db import models
from users.models import Customer
from phonenumber_field.modelfields import PhoneNumberField
#from phonenumber_field.modelfields import PhoneNumberField
# from django.utils import timezone

# Create your models here.
class Package(models.Model):
    WEIGHT_CHOICES = [ ('<2', '<2'), ('2-5', '2-5'), 
                      ('5-10', '5-10'), ('>10', '>10'),
                      ]
    sender_id = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    sender_phone = PhoneNumberField(region='TW')
    sender_address = models.CharField(max_length=200)
    recipient_name = models.CharField(max_length=200)
    recipient_phone = PhoneNumberField(region='TW')
    recipient_address = models.CharField(max_length=200)
    package_description = models.CharField(max_length=200)
    fragile = models.BooleanField()
    estimate_package_weight = models.CharField( max_length=5, choices=WEIGHT_CHOICES )
    order_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "Packages"
    def __str__(self):
        return f"{self.sender_id}, {self.recipient_name}, {self.recipient_phone}"