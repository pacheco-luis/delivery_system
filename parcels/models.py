from django.db import models
import uuid

from users.models import Customer

# Create your models here.
class Parcel(models.Model):
    WEIGHT_RANGE_EXTRA_SMALL = "extra_small"
    WEIGHT_RANGE_SMALL = "small"
    WEIGHT_RANGE_MEDIUM = "medium"
    WEIGHT_RANGE_LARGE = "large"
    WEIGHT_RANGES = [
        (WEIGHT_RANGE_EXTRA_SMALL, 'Up to 2 kg'),
        (WEIGHT_RANGE_SMALL, '2-5 kg'),
        (WEIGHT_RANGE_MEDIUM, '5-10 kg'),
        (WEIGHT_RANGE_LARGE, '10 kg and above'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending'
    STATUS_EN_ROUTE_TO_PICKUP = 'en_route_to_pickup'
    STATUS_IN_TRANSIT = 'in_transit'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    PARCEL_STATUSES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_EN_ROUTE_TO_PICKUP, 'En Route to Pickup'),
        (STATUS_IN_TRANSIT, 'In Transit'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(max_length=255, null=True, blank=True)
    weight = models.CharField(max_length=20, choices=WEIGHT_RANGES, default=WEIGHT_RANGE_EXTRA_SMALL)
    status = models.CharField(max_length=20, choices=PARCEL_STATUSES, default=STATUS_DRAFT)
    sender_name = models.CharField(max_length=255, null=True, blank=True)
    sender_phone = models.CharField(max_length=15, null=True, blank=True)
    sender_address = models.CharField(max_length=255, null=True, blank=True)
    recipient_name = models.CharField(max_length=255, null=True, blank=True)
    recipient_phone = models.CharField(max_length=15, null=True, blank=True)
    recipient_address = models.CharField(max_length=255, null=True, blank=True)
    pickedup_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name