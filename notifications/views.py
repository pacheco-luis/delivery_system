from uuid import UUID
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from notifications.forms import READ_ALL_FORM
from notifications.models import Notification
from package_request.models import Package
from chatbot.models import Conversation

# Create your views here.

@login_required
def update_context(request, context: dict ) -> dict:
    '''updates the context dictionary to contain user_id, notificaitons and notifications_count for the navigation bar'''
    context['user_id']=request.user.id.hex,
    context['nav_notifications']=Notification.objects.filter( user=request.user )[:3]
    context['nav_notifications_count']=Notification.objects.filter( user=request.user, read=False ).count()
    context["chat_messages"] = Conversation.objects.get_or_create(user=request.user)[0].get_messages()
    
    return context

@login_required(login_url='users:login')
def notifications_viewer(request):
    
    if not request.user.is_driver and  not request.user.is_customer:
        return redirect( 'package_request_app:401' )
    
    context = {
        'all_notifications': Notification.objects.filter(user=request.user).order_by('created').reverse()
    }
        
    return render(request, 'notifications_viewer.html', context=update_context(request, context))

def view_notification(request, id):
    print('viewing')
    if Notification.objects.get( id=id ).parcel.status != Package.STATUS_COMPLETED:
        return redirect( 'package_request_app:package_list')

    return redirect( 'package_request_app:package_history' )

def unread_notification(request, id):
    try:
        Notification.objects.filter( id=id ).update( read=False )
    except Exception as e:
        pass
    
    return redirect( 'notifications_app:notifications_viewer' )

@login_required(login_url='users:login')
def read_all_notifications(request):

    if request.method == 'POST' :
        url = request.POST.get('url', '')
        Notification.objects.filter(user=request.user, read=False).update(read=True)    
    
    return redirect( url )
    