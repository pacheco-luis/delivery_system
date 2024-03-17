from django.forms import ModelForm, TextInput, EmailInput
from django.contrib.auth.forms import UserCreationForm

# from django.contrib.auth.models import User
from .models import User, Customer, Driver

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        #add phone number to fields
        fields = ['first_name', 'last_name', 'username', 'email', 'password1','password2']
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'username', 'email', 'address', 'phone_number', 'profile_image']
        widgets = {
            'first_name': TextInput(attrs={'class': 'custom-input'}),
            'last_name': TextInput(attrs={'class': 'custom-input'}),
            'username': TextInput(attrs={'class': 'custom-input'}),
            'email': EmailInput(attrs={'class': 'custom-input'}),
            'address': TextInput(attrs={'class': 'custom-input'}),
            'phone_number': TextInput(attrs={'class': 'custom-input'}),
        }

class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'username', 'email', 'address', 'phone_number', 'profile_image']
