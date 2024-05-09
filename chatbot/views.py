from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notifications.views import update_context

# Create your views here.

@login_required(login_url='users:login')
def conversation(request):
    return render( request, 'chatbot.html', context=update_context(request, {}) )