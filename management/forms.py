from django import forms
from users.models import User  # Adjust import as needed


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
