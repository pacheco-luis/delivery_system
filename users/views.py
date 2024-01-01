from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# from django.contrib.auth.models import User
from .models import User
from .forms import CustomUserCreationForm, CustomerForm, DriverForm

# Create your views here.
# @login_required(login_url='users:login')
# def home(request):
#     return render(request, 'users/home.html')

def loginCustomer(request):
    page = 'customer'
    if request.user.is_authenticated:
        return redirect('package_request_app:home')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email, is_customer=True)
            user = authenticate(request, email=email, password=password)
        except:
            messages.error(request, 'Email does not exist')
            return redirect('users:login-customer')

        if user is not None:
            login(request, user)
            return redirect('package_request_app:home')
        else:
            messages.error(request, 'Username and password do not match')
            return redirect('users:login-customer')

    context = {'page': page}
    return render(request, 'sign-in.html', context)

def loginDriver(request):
    page = 'driver'
    if request.user.is_authenticated:
        return redirect('package_request_app:home')

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email, is_driver=True)
            user = authenticate(request, email=email, password=password)
        except:
            messages.error(request, 'Email does not exist')
            return redirect('users:login-driver')

        if user is not None:
            login(request, user)
            return redirect('package_request_app:home')
        else:
            messages.error(request, 'Username and password do not match')
            return redirect('users:login-driver')

    context = {'page': page}
    return render(request, 'sign-in.html', context)

def logoutCustomer(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('users:login-customer')

def logoutDriver(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('users:login-driver')

def registerCustomer(request):
    page = 'customer'
    if request.user.is_authenticated:
        return redirect('package_request_app:home')
    
    form = CustomUserCreationForm()
    context = {'page': page, 'form': form}

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.is_customer = True
            user.save()

            messages.success(request, 'User account was created')

            login(request, user)
            return redirect('package_request_app:home')
        else:
            # messages.error(request, 'An error has occurred during registration')
            messages.error(request, form.errors )

    return render(request, 'sign-up.html', context)

def registerDriver(request):
    page = 'driver'
    if request.user.is_authenticated:
        return redirect('package_request_app:home')
    form = CustomUserCreationForm()
    context = {'page': page, 'form': form}

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.email = user.email.lower()
            user.is_driver = True
            user.save()

            messages.success(request, 'User account was created')

            login(request, user)
            return redirect('package_request_app:home')
        else:
            # messages.error(request, 'An error has occurred during registration')
            messages.error(request, form.errors)

    return render(request, 'sign-up.html', context)

@login_required(login_url='users:login')
def driverAccount(request):
    account = request.user.driver
    context = {'account': account}
    return render(request, 'users/account.html', context)

@login_required(login_url='users:login')
def customerAccount(request):
    account = request.user.customer
    context = {'account': account}
    return render(request, 'users/account.html', context)

@login_required(login_url='users:login')
def editCustomerAccount(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account was updated')
            return redirect('users:customer-account')
    context = {'form': form}
    return render(request, 'users/account_form.html', context)

@login_required(login_url='users:login')
def editDriverAccount(request):
    driver = request.user.driver
    form = DriverForm(instance=driver)
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES, instance=driver)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account was updated')
            return redirect('users:driver-account')
    context = {'form': form}
    return render(request, 'users/account_form.html', context)
