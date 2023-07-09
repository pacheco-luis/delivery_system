from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'users/home.html')

def userAccount(request):
    return render(request, 'users/account.html')