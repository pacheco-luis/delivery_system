from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from notifications.models import Notification

# Create your views here.

@login_required(login_url='users:login')
def notifications_viewer(request):
    
    context = {
        'user_id' : request.user.id,
        'notifications': Notification.objects.filter(user=request.user),
    }
    return render(request, 'notifications_viewer.html', context=context)

def view_notification(request, id):
    
    context = {
        'user_id' : request.user.id,
    }
    return render(request, 'notifications_viewer.html', context=context)