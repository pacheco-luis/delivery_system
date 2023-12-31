from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

# from django.contrib.auth.models import User
from .models import User, Customer, Driver

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1','password2']
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'username', 'email', 'address', 'phone_number', 'profile_image']

class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'username', 'email', 'address', 'phone_number', 'profile_image']
