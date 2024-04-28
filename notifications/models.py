from django.db import models
from users.models import User
from package_request.models import Package
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from datetime import datetime

# Create your models here.

class Notification(models.Model):
    TYPE_GENERAL =  'general'
    TYPE_DELIVERING = 'delivering'
    TYPE_PICKING = 'picking'
    
    TYPES = (
        (TYPE_GENERAL, TYPE_GENERAL.capitalize()),
        (TYPE_DELIVERING, TYPE_DELIVERING.capitalize()),
        (TYPE_PICKING, TYPE_PICKING.capitalize()),
    )
    
    message = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPES, default=TYPE_GENERAL)
    parcel=models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created=models.DateTimeField(auto_now_add=True, editable=False)
    read=models.BooleanField(default=False)

    
    def __str__(self):
        return self.message

    def notify_picking(self, old_status, new_status):
        '''notifies picking parcel to respective user websockets'''
        
        channel_layer = get_channel_layer()
        if timezone.is_naive(self.created):
            created = timezone.make_aware(self.created, timezone.utc)
        else:
            created = self.created
        created = created.astimezone(timezone.get_current_timezone())
        created = created.strftime('%B %d, %Y, %I:%M %p').lower().replace("am", "A.M.").replace("pm", "P.M.")
        
        async_to_sync(channel_layer.group_send)(
            f"user_{self.user.id}",
            {
                'type': 'notify_user_status_change',
                'user_id': self.user.id,
                'id': self.id,
                'message': self.message,
                'n_type': self.type,
                'read': self.read,
                'created': created,
            }
        )
        
    def notify_delivering(self, old_status, new_status):
        '''notifies delivering parcel to respective user websockets'''
        
        channel_layer = get_channel_layer()
        if timezone.is_naive(self.created):
            created = timezone.make_aware(self.created, timezone.utc)
        else:
            created = self.created
        created = created.astimezone(timezone.get_current_timezone())
        created = created.strftime('%B %d, %Y, %I:%M %p').lower().replace("am", "A.M.").replace("pm", "P.M.")
        
        async_to_sync(channel_layer.group_send)(
            f"user_{self.user.id}",
            {
                'type': 'notify_user_status_change',
                'user_id': self.user.id,
                'id': self.id,
                'message': self.message,
                'n_type': self.type,
                'read': self.read,
                'created': created,
            }
        )