from django.db import models
from users.models import Customer, Driver
from phonenumber_field.modelfields import PhoneNumberField
from places.fields import PlacesField
import uuid
from django.utils.translation import gettext_lazy as _, gettext

# Create your models here.
class Package(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PICKING = 'picking'
    STATUS_TRANSIT = 'transiting'
    #Add in awaiting delivery state
    STATUS_DELIVERING = 'delivering'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELED = 'canceled'
    STATUSES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_PICKING, 'Picking'),
        (STATUS_DELIVERING, 'Delivering'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELED, 'Canceled'),
    )
    #remove
    # WEIGHT_CHOICES = [ ('<2', '<2'), ('2-5', '2-5'), 
    #                   ('5-10', '5-10'), ('>10', '>10'),
    #                   ]
    TIME_SLOTS = (
        (0, '8:00 - 12:00'),
        (1, '13:00 - 18:00'),
        (2, _('no preference'))
    )

    package_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # sender_id = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)
    sender_phone = PhoneNumberField(region='TW', blank=False)
    sender_address = PlacesField(blank = True, verbose_name=_("sender address"))
    recipient_name = models.CharField(max_length=200, blank=False)
    recipient_phone = PhoneNumberField(region='TW' , blank=False, verbose_name=_("recipient phone"))
    recipient_address = PlacesField(blank=True, verbose_name=_("recipient address"))
    package_description = models.CharField(max_length=200  , blank=False, verbose_name=_("package description"))
    fragile = models.BooleanField(verbose_name=_("fragile?"))
    preferred_time = models.IntegerField(choices = TIME_SLOTS, default = 2, verbose_name = _("preferred time window"))
    frozen = models.BooleanField(verbose_name=_("does the package need to be refrigerated?"))
    #estimate_package_weight = models.CharField(max_length=5, choices=WEIGHT_CHOICES, default='<2')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUS_PENDING)
    duration = models.IntegerField(null=True, blank=True, default=0)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    width = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0, verbose_name=_("width"))
    height = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0, verbose_name=_("height"))
    depth = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0, verbose_name=_("depth"))
    estimate_package_weight_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0, verbose_name=_("estimated package weight"))
    
    class Meta:
        db_table = "Packages"
        
    def __str__(self):
        return f"{self.recipient_name}, {self.recipient_phone}"
    
class Route(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #Add status state (Unassigned, Assigned, Completed)
    parcels = models.ManyToManyField(Package, related_name='route', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


    def __str__(self):
        return f'{self.id}'
    
    def get_formatted_route(self):
        formatted_route = ''

        for parcel in self.parcels.all():
            formatted_route += f"{parcel.sender_address}"
            if parcel != self.parcels.all().last():
                formatted_route += " -> "

        return formatted_route.strip()
    
    def get_formatted_items(self):
        formatted_route = ''

        for parcel in self.parcels.all():
            formatted_route += f"{parcel.package_description}"
            if parcel != self.parcels.all().last():
                formatted_route += ", "
        return formatted_route.strip()
    
    def get_created_date(self):
        return f'{self.created_at}'
    
    def get_size(self):
        try:
            return self.parcels.all().count()
        except Exception as e:
            pass
        return 0