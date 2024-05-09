from django.db import models
from users.models import User
import uuid


# Create your models here.

class QA(models.Model):
    question = models.TextField(max_length=255)
    answer = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "QAs"
        
    def __str__(self) -> str:
        return f'{self.id}\n{self.id,}'

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='conversation', unique=True)
    
    def get_messages(self) -> list :
        return [ message.message_as_json() for message in self.messages.all() ]
        

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def message_as_json(self) -> dict :
        message = {}
        message["id"] = self.id.hex
        message["sender"] = self.sender
        message["content"] = self.content
        message["timestamp"] = self.timestamp
        
        return message