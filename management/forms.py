from django import forms
from django.db import models
from users.models import User, Driver


class ASSIGN_CLUSTER_FORM(forms.Form):
    DRIVER_USERNAMES = [ ( str(driver.username), str(driver.username) ) for driver in User.objects.filter( is_driver=True, is_active=True ) ]
    DRIVER_USERNAMES.insert(0, (str('None'),str('None')))
    
    cluster_id = forms.CharField( max_length=50, required=True, widget=forms.TextInput(attrs={
        'id':'cluster_id',
        'text':'text',
        # 'disabled': '',
        'class':'form-control assign_form_input',
        'placeholder':'cluster id',
        'aria-label':'cluster id',
        'aria-describedby':'basic-addon1'
    }))
    
    driver_username = forms.ChoiceField( choices=DRIVER_USERNAMES )
    driver_username.widget.attrs.update(
            {
            'id':'driver_username',
            'class':'form-control assign_form_input',
            'aria-label':'Username',
            'aria-describedby':'basic-addon1',
            'style':'color: #000;'
            }
        )