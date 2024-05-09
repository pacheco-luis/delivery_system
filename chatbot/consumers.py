# import json
# import uuid
# from asgiref.sync import async_to_sync, sync_to_async
# from channels.generic.websocket import AsyncWebsocketConsumer
# import json

# from users.models import User
# from .chatbot_query import CHAT
# from .models import Conversation, Message

# class ChatConsumer(AsyncWebsocketConsumer):
#     bot_chat_instance = CHAT()
    
#     async def connect(self):
#         self.user_id = uuid.UUID(self.scope['url_route']['kwargs']['user_id'])
#         self.group_name = f"chat_{self.user_id}"
#         await self.channel_layer.group_add( self.group_name, self.channel_name )
#         await self.accept()
       
    
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard( self.group_name, self.channel_name )

#     async def send_message(self, message: str):
#         text_data = json.dumps( { 'message': message, }, default=str )
        
#         print('sending: ', text_data )

#         # creating new message sent by bot to user
#         self.create_message( user=None, content=message )
        
#         await self.send( text_data=text_data )

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
        
#         print('receved: ', message)
#         response_mssg = self.bot_chat_instance.get_response_mssg(message=message)
        
#         # creating new message sent by user to bot
#         user = User.objects.get(id=self.user_id) 
#         self.create_message( user=user, content=response_mssg)
        
#         await self.send_message( response_mssg )
    
#     def create_message(self, user, content ):
#         q_user = sync_to_async( User.objects.get(id=self.user_id) )
#         q_conv = sync_to_async(Conversation.objects.get_or_create( user=q_user )[0])
#         sync_to_async(Message.objects.create(conversation=q_conv, sender=user, content=content))
        
import json
import uuid
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from users.models import User
from .chatbot_query import CHAT
from .models import Conversation, Message

class ChatConsumer(AsyncWebsocketConsumer):
    bot_chat_instance = CHAT()
    
    async def connect(self):
        self.user_id = uuid.UUID(self.scope['url_route']['kwargs']['user_id'])
        self.group_name = f"chat_{self.user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_message(self, message: str):
        text_data = json.dumps({'message': message}, default=str)
        print('sending:', text_data)
        await self.create_message(user=None, content=message)
        await self.send(text_data=text_data)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print('received:', message)
        response_mssg = self.bot_chat_instance.get_response_mssg(message=message)
        user = await sync_to_async(User.objects.get)(id=self.user_id)
        await self.create_message(user=user, content=message)
        await self.send_message(response_mssg)

    async def create_message(self, user, content):
        q_user = await sync_to_async(User.objects.get)(id=self.user_id)
        q_conv, created = await sync_to_async(Conversation.objects.get_or_create)(user=q_user)
        await sync_to_async(Message.objects.create)(conversation=q_conv, sender=user, content=content)
