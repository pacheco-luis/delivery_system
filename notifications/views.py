from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='users:login')
def notification_viewer(request):
    context = {
        'user_id' : request.user.id
    }
    return render(request, 'notif_index.html', context=context)