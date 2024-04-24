from django.urls import path
from . import views


app_name = 'chatbot'
urlpatterns = [
    path('/chatbot/', views.conversation, name='chatbot'),
]
