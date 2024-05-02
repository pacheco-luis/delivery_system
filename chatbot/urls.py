from django.urls import path
from . import views

app_name = 'chatbot_app'
urlpatterns = [
    path('chatbot/', views.conversation, name='chatbot'),
]
