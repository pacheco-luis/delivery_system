from django.urls import path
from . import views

app_name = 'chatbot_app'
urlpatterns = [
    # this url was only used to developing the chat interface
    # path('chatbot/', views.conversation, name='chatbot'),
]
