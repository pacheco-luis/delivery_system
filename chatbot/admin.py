from django.contrib import admin
from .models import QA, Conversation, Message

# Register your models here.

admin.site.register(QA)
admin.site.register(Conversation)
admin.site.register(Message)