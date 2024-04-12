from collections import OrderedDict
from django import forms
from users.models import User
from django.utils.translation import gettext


class ASSIGN_CLUSTER_FORM(forms.Form):
    cluster_id = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'id': 'cluster_id',
        'text': 'text',
        'readonly':'',
        'class': 'form-control assign_form_input',
        'placeholder': 'cluster id',
        'aria-label': 'cluster id',
        'aria-describedby': 'basic-addon1'
    }))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        driver_choices = [(str('None'), str('None'))]
        drivers = User.objects.filter(is_driver=True, is_active=True)
        for driver in drivers:
            driver_choices.append((str(driver.username), str(driver.username)))
        self.fields['driver_username'] = forms.ChoiceField(choices=driver_choices, widget=forms.Select(attrs={
            'id': 'driver_username',
            'class': 'form-control assign_form_input',
            'aria-label': 'Username',
            'aria-describedby': 'basic-addon1',
            'style': 'color: #000;'
        }))

class USERS_QUERY_FILTER(forms.Form):
    def __init__(self, *args, **kwargs):
        super(USERS_QUERY_FILTER, self).__init__(*args, **kwargs)
        
        user_types = [
                        ('is_customer' , 'Customers'),
                        ('is_driver','Drivers'),
                        ('is_superuser','Admins'),
                        ('is_manager','Managers'),
                        ('is_staff','Staff')
                    ]

        self.fields['Users'] = forms.ChoiceField(
            choices=[(gettext('All Users'), gettext('All Users'))] + user_types,
            initial= 'All Users',  #    initial value
            widget=forms.Select(attrs={
                'class': 'form-control dropdown',
                'aria-label': 'from_station',
                'aria-describedby': 'basic-addon1',
                'style': 'color: #000'
            })
        )

class EDIT_USER_FORM(forms.Form):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = ['username', 'role', 'active', 'joined']
        
        for field in fields:
            if field != 'active':
                self.fields[field] = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
                    'id': field,
                    'name': field,
                    'class': 'form-control assign_form_input',
                    'readonly': 'readonly',
                    'aria-label': 'field',
                    'aria-describedby': 'basic-addon1',
                    'style': 'color: #000 !important;'
                }))
            
            else:
                self.fields[field] = forms.BooleanField( required=False )

    def __str__(self) -> str:
        return super().__str__()
    
    def set_username(self, username):
        self.username=username    
    def set_role(self, role):
        self.role=role    
    def set_active(self, active):
        self.active=active
    def set_joined(self, joined):
        self.joined=joined

class SEARCH_USER_FORM(forms.Form):
    username_search = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
                    'id': 'username_search',
                    'placeholder': 'search by username',
                    'class': 'form-control',
                    'aria-label': 'field',
                    'aria-describedby': 'basic-addon1',
                    'style': 'color: #000 !important;'
                }))