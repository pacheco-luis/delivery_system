from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, CustomerForm

# Create your views here.
@login_required(login_url='users:login')
def home(request):
    return render(request, 'users/home.html')

def loginUser(request):
    if request.user.is_authenticated:
        return redirect('users:home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'Username does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username and password do not match')

    return render(request, 'sign-in.html')

def logoutUser(request):
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('users:login')

def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()
    context = {'page': page, 'form': form}

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created')

            login(request, user)
            return redirect('users:home')
        else:
            messages.error(request, 'An error has occurred during registration')

    return render(request, 'users/sign-up.html', context)

@login_required(login_url='users:login')
def account(request):
    customer = request.user.customer
    context = {'customer': customer}
    return render(request, 'users/account.html', context)

@login_required(login_url='users:login')
def editAccount(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)
    if request.method == 'POST':
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account was updated')
            return redirect('users:account')
    context = {'form': form}
    return render(request, 'users/account_form.html', context)


