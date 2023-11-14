from django.db import models
from users.models import Customer
from phonenumber_field.modelfields import PhoneNumberField
from places.fields import PlacesField
import uuid

# Create your models here.
class Package(models.Model):
    WEIGHT_CHOICES = [ ('<2', '<2'), ('2-5', '2-5'), 
                      ('5-10', '5-10'), ('>10', '>10'),
                      ]
    package_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender_id = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    sender_phone = PhoneNumberField(region='TW', blank=False)
    sender_address = PlacesField(blank = True)
    recipient_name = models.CharField(max_length=200, blank=False)
    recipient_phone = PhoneNumberField(region='TW' , blank=False)
    recipient_address = PlacesField(blank=True)
    package_description = models.CharField(max_length=200  , blank=False)
    fragile = models.BooleanField()
    estimate_package_weight = models.CharField( max_length=5, choices=WEIGHT_CHOICES )
    order_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "Packages"
        
    def __str__(self):
        return f"{self.sender_id}, {self.recipient_name}, {self.recipient_phone}"
    