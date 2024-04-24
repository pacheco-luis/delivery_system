from django.shortcuts import render

# Create your views here.

def conversation(request):
    return render( 'chatbot/templates/chatbot.html', context={} )