from django.shortcuts import render

# Create your views here.

def conversation(request):
    return render( request, 'chatbot.html', context={} )