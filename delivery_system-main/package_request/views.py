from django.http import HttpResponse
from django.shortcuts import redirect, render
from package_request.forms import SENDER_FORM
from django.contrib import messages
from users.models import Customer
from package_request.models import Package
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
# from users import Customer


# Create your views here.

@login_required
def sucess( request ):
    return render( request, "successful_request.html")

@login_required
def RequestForm(request):
        
    if request.method == 'POST':
        sender = SENDER_FORM(request.POST)
        user_obj = Customer.objects.get(user=request.user)
        if user_obj.phone_number is None or user_obj.address is None:
            messages.error(request,'Please update your phone number and address, then make a request!')
            return redirect( 'users:edit-account')
    
        elif sender.is_valid():
            sender_instance = sender.save(commit=False)
            sender_instance.sender_id = request.user.customer
            sender_instance.sender_phone = user_obj.phone_number
            sender_instance.sender_address = user_obj.address
            sender_instance.save()
            return redirect('package_request_app:successful')
        else:
            return render(request,"request.html", {'sender_form': SENDER_FORM(request.POST)} )
        
    context = {
        'sender_form': SENDER_FORM(),
    }
    return render(request,"request.html", context=context)

@login_required
def all_packages(request):
    package_list = Package.objects.all()
    return render(request, 'package_list.html', {'package_list' : package_list})

def delete_request(request, id):
    delete_obj = Package.objects.get(pk = id)
    delete_obj.delete()
   
    return redirect ('package_request_app:package_list')