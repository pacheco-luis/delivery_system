from django.db import models
from users.models import User
from package_request.models import Package
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your models here.

class Notification(models.Model):
    message = models.CharField(max_length=100)
    parcel=models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date=models.DateField(auto_now=True)
    read=models.BooleanField(default=False)

    
    def __str__(self):
        return self.message

    def notify_picking(self, old_status, new_status):
        '''notifies the customer associated with this package through websockets and creates a notification object'''
        
        channel_layer = get_channel_layer()
        
        print( '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n' , channel_layer )
        print( '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n' , f"user_{self.user.id}" )
        
        async_to_sync(channel_layer.group_send)(
            f"user_{self.user.id}",
            {
                'type': 'notify_user_status_change',
                'user_id': self.user.id,
                'message': "Your package is about to be picked up."
            }
        )
        
    def notify_delivering(self, old_status, new_status):
        '''creates a notification object and notifies the customer associated with this package through websockets'''
        
        channel_layer = get_channel_layer()
        
        print( '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n' , channel_layer )
        print( '$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n' , f"user_{self.user.id}" )
        
        async_to_sync(channel_layer.group_send)(
            f"user_{self.user.id}",
            {
                'type': 'notify_user_status_change',
                'user_id': self.user.id,
                'message': "Your package is about to be delivered."
            }
        )