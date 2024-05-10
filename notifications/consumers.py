import json
import uuid
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from package_request.models import Package
import urllib
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # for key, value in self.scope.items():
        # print( f'\t{key}:\t{value}' )
        
        self.user_id = uuid.UUID(self.scope['url_route']['kwargs']['user_id'])
        self.group_name = f"user_{self.user_id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({ 
                                            'user_id': event['user_id'],
                                            'id': event['id'],
                                            'message': event['message'],
                                            'n_type': event['n_type'],
                                            'read': str(event['read']),
                                            'created': event['created'],
                                            },  default=str))

    async def notify_user_status_change(self, event):
        # Check if the status change event is relevant to this user
        if event['user_id'] == self.user_id:
            # print( 'sending' )
            # Send notification to the user
            await self.send_notification(event)