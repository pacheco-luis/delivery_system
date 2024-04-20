from django.db import models
from users.models import Customer, Driver
from stations.models import Station
from phonenumber_field.modelfields import PhoneNumberField
from places.fields import PlacesField
import uuid
from django.utils.translation import gettext_lazy as _, gettext
from django.core.validators import MinValueValidator
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer
from io import BytesIO
from django.core.files.base import ContentFile

# Create your models here.
class Package(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ASSIGNED = 'assigned'  #preparing to pick up
    STATUS_PICKING = 'picking'
    STATUS_TRANSIT = 'transiting'
    #Add in awaiting delivery state
    STATUS_DELIVERING = 'delivering'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELED = 'canceled'
    STATUSES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_ASSIGNED, 'Assigned'),
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
        (2, _('No Preference'))
    )

    package_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # sender_id = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.CASCADE)
    sender_phone = PhoneNumberField(region='TW', blank=False)
    sender_address = PlacesField(blank = True, verbose_name=_("sender address"))
    recipient_name = models.CharField(max_length=200, blank=False)
    recipient_phone = PhoneNumberField(region='TW' , blank=False, verbose_name=_("recipient phone:"))
    recipient_address = PlacesField(blank=True, verbose_name=_("recipient address"))
    package_description = models.CharField(max_length=200  , blank=False, verbose_name=_("package description:"))
    fragile = models.BooleanField(verbose_name=_("fragile?"))
    preferred_time = models.IntegerField(choices = TIME_SLOTS, default = 2, verbose_name = _("preferred delivery time:"))
    frozen = models.BooleanField(verbose_name=_("does the package need to be refrigerated?"))
    #estimate_package_weight = models.CharField(max_length=5, choices=WEIGHT_CHOICES, default='<2')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUS_PENDING)
    duration = models.IntegerField(null=True, blank=True, default=0)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    width = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=0, verbose_name=_("width: (cm)"))
    height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=0, verbose_name=_("height: (cm)"))
    depth = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=0, verbose_name=_("depth: (cm)"))
    estimate_package_weight_value = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=0, verbose_name=_("package weight: (kg)"))
    qrcode = models.ImageField(upload_to='jobs/qrcode/', blank=True)

    pickup_photo = models.ImageField(upload_to='jobs/pickup/', blank=True)
    delivery_photo = models.ImageField(upload_to='jobs/delivery/', blank=True)
    
    class Meta:
        db_table = "Packages"
        
    def __str__(self):
        return f"{self.recipient_name}, {self.recipient_phone}"
    
    @property
    def create_qrcode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )
        qr.add_data(str(self.package_id))
        qr.make(fit=True)
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer()
        )
        # Save the QR code image to the model's qrcode field
        # Generate a file name for the image
        filename = f'{self.package_id}.png'
        # Create a BytesIO object to hold the image data
        buffer = BytesIO()
        # Save the image to the BytesIO buffer
        img.save(buffer, format='PNG')
        # Create a ContentFile object from the BytesIO buffer
        file_buffer = ContentFile(buffer.getvalue())
        # Assign the ContentFile to the model's ImageField
        self.qrcode.save(filename, file_buffer, save=True)
    
    def get_sender_coor(self) -> tuple:
        return (float(self.sender_address.latitude), float(self.sender_address.longitude))
    
    def get_recipient_coor(self) -> tuple:
        return (float(self.recipient_address.latitude), float(self.recipient_address.longitude))
    
    def get_sender_station(self):
        stations = Station.objects.all()
        for station in stations: 
            if station.dist( self.get_sender_coor() ) <= station.radius:
                return station
        return None
    
    def get_recipient_station(self):
        stations = Station.objects.all()
        for station in stations:
            if station.dist( self.get_recipient_coor() ) <= station.radius:
                return station
        return None
    
class Route(models.Model):
    STATUS_UNASSIGNED = 'unassigned'
    STATUS_ASSIGNED = 'assigned'
    STATUS_COMPLETED = 'completed'
    
    STATUSES = (
        ( STATUS_UNASSIGNED, STATUS_UNASSIGNED),
        ( STATUS_ASSIGNED, STATUS_ASSIGNED),
        ( STATUS_COMPLETED, STATUS_COMPLETED)
        
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    #Add status state (Unassigned, Assigned, Completed)
    parcels = models.ManyToManyField(Package, related_name='route', blank=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, related_name='route', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    status = models.CharField(max_length=10, choices=STATUSES, default=STATUS_UNASSIGNED)
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True)
    


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