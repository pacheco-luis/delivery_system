from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Parcel

# Create your views here.
@login_required(login_url='login')
def home(request):
    return render(request, 'customer/home.html')

@login_required(login_url='login')
def parcels(request):
    customer = request.user.customer
    parcels = Parcel.objects.filter(customer=customer)
    context = { 'parcels': parcels }
    return render(request, 'customer/parcels.html', context)

@login_required(login_url='login')
def parcel(request, pk):
    customer = request.user.customer
    parcel = Parcel.objects.get(id=pk, customer=customer)
    context = { 'parcel': parcel }
    return render(request, 'customer/single-parcel.html', context)