from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User

# Create your views here.
@login_required(login_url='sign-in')
def home(request):
    return render(request, 'users/home.html')

def signInUser(request):
    if request.user.is_authenticated:
        return redirect('home')

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

    return render(request, 'users/sign-in-sign-up.html')

def signOutUser(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('sign-in')

@login_required(login_url='sign-in')
def customerAccount(request):
    return render(request, 'users/account.html')
