from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Parcel
from .forms import ParcelForm

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

@login_required(login_url='login')
def createParcel(request):
    customer = request.user.customer
    form = ParcelForm()

    if request.method == 'POST':
        form = ParcelForm(request.POST)
        if form.is_valid():
            parcel = form.save(commit=False)
            parcel.customer = customer
            parcel.save()

            messages.success(request, 'Parcel was created successfully')

            return redirect('parcels')

    context = { 'form': form }
    return render(request, 'customer/parcel_form.html', context)

@login_required(login_url='login')
def updateParcel(request, pk):
    parcel = Parcel.objects.get(id=pk)
    form = ParcelForm(instance=parcel)

    if request.method == 'POST':
        form = ParcelForm(request.POST, instance=parcel)
        if form.is_valid():
            form.save()

            messages.success(request, 'Parcel was updated successfully')

            return redirect('parcels')
    
    context = { 'form': form }
    return render(request, 'customer/parcel_form.html', context)

@login_required(login_url='login')
def deleteParcel(request, pk):
    parcel = Parcel.objects.get(id=pk)

    if request.method == 'POST':
        parcel.delete()

        messages.success(request, 'Parcel was deleted successfully')

        return redirect('parcels')
    
    context = { 'parcel': parcel }
    return render(request, 'delete_confirm.html', context)