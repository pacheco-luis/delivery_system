from django import forms
from package_request.models import Package
from stations.models import Station
from places.fields import PlacesField
from django.utils.translation import gettext_lazy as _

class SENDER_FORM(forms.ModelForm):
    sender_phone = forms.CharField( 
        label = _("Sender phone:"),
        required=False,
        widget = forms.TextInput( attrs={'required': 'True'})
    )
    
    class Meta:
        model = Package
        fields = ['sender_phone', 'sender_address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sender_phone'].widget.attrs.update({'placeholder': '0987654321'})
        self.fields['sender_address'].widget.attrs.update({'required': 'true'})
        

class RECEIVER_FORM(forms.ModelForm):
    recipient_name = forms.CharField(
        label = _("Recipient name:"),
        required=False,
        widget = forms.TextInput( attrs={'required': 'True'} )
        )
    
    class Meta:
        model = Package
        fields = ['recipient_name', 'recipient_phone', 'recipient_address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient_name'].widget.attrs.update({'placeholder': 'John Doe'})
        self.fields['recipient_phone'].widget.attrs.update({'placeholder': '0987654321'})
        self.fields['recipient_address'].widget.attrs.update({'required': 'true'})
        
class PACKAGE_FORM(forms.ModelForm):
    package_description = forms.CharField(
        label=_("Package description"),
        required=False,
        widget = forms.TextInput( attrs={'required': 'True'} ) 
        )
    estimate_package_weight = forms.ChoiceField ( 
        label=_("Estimated package weight:"),
        required=False, 
        widget = forms.Select( attrs={'required': 'True'} ),
        choices=Package.WEIGHT_CHOICES 
    )
    
    class Meta:
        model = Package
        fields = ['package_description', 'estimate_package_weight', 'fragile', 'frozen', 'width', 'height', 'depth', 'estimate_package_weight_value']
        
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # self.fields['recipient_name'].widget.attrs.update({'placeholder': 'John Doe'})
        # self.fields['recipient_phone'].widget.attrs.update({'placeholder': '0987654321'})
        # self.fields['recipient_address'].widget.attrs.update({'placeholder': 'house NO, street, post code, city, county'})

class DRIVER_FILTER_QUERY_FORM(forms.Form):
    
    def __init__(self, *args, **kwargs):
        super(DRIVER_FILTER_QUERY_FORM, self).__init__(*args, **kwargs)
        
        stations = Station.objects.filter(active=True)
        choices = [(station.alias, station.alias) for station in stations]
        
        self.fields['station'] = forms.ChoiceField(
            choices=[('None', 'Select your station')] + choices,
            initial='None',  # Set initial value
            widget=forms.Select(attrs={
                'class': 'form-control' 'dropdown',
                'aria-label': 'from_station',
                'aria-describedby': 'basic-addon1',
                'style': 'color: #000'
            })
        )

        # self.fields['to_station'] = forms.ChoiceField(
        #     choices=[('None', 'Select a station')] + choices,
        #     initial='None',  # Set initial value
        #     widget=forms.Select(attrs={
        #         'class': 'form-control' 'dropdown',
        #         'aria-label': 'to_station',
        #         'aria-describedby': 'basic-addon1',
        #         'style': 'color: #000'
        #     })
        # )