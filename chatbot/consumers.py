import json
import uuid
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .chatbot_query import CHAT

class ChatConsumer(AsyncWebsocketConsumer):
    bot_chat_instance = CHAT()
    
    async def connect(self):
        self.user_id = uuid.UUID(self.scope['url_route']['kwargs']['user_id'])
        self.group_name = f"chat_{self.user_id}"
        await self.channel_layer.group_add( self.group_name, self.channel_name )
        await self.accept()
       
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard( self.group_name, self.channel_name )

    async def send_message(self, message: str):
        text_data = json.dumps( { 'message': message, }, default=str )
        print('sending: ', text_data )
        await self.send( text_data=text_data )
        


    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        
        print('receved: ', message)
        response_mssg = self.bot_chat_instance.get_response_mssg(message=message)
        await self.send_message( response_mssg )

        