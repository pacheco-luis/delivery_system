from django import forms
from package_request.models import Package
from places.fields import PlacesField

class SENDER_FORM(forms.ModelForm):
    sender_phone = forms.CharField( required=False, widget = forms.TextInput( attrs={'required': 'True'} ) )
    
    class Meta:
        model = Package
        fields = ['sender_phone', 'sender_address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sender_phone'].widget.attrs.update({'placeholder': '0987654321'})
        self.fields['sender_address'].widget.attrs.update({'required': 'true'})
        

class RECEIVER_FORM(forms.ModelForm):
    recipient_name = forms.CharField( required=False,widget = forms.TextInput( attrs={'required': 'True'} ) )
    
    class Meta:
        model = Package
        fields = ['recipient_name', 'recipient_phone', 'recipient_address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient_name'].widget.attrs.update({'placeholder': 'John Doe'})
        self.fields['recipient_phone'].widget.attrs.update({'placeholder': '0987654321'})
        self.fields['recipient_address'].widget.attrs.update({'required': 'true'})
        
class PACKAGE_FORM(forms.ModelForm):
    package_description = forms.CharField( required=False, widget = forms.TextInput( attrs={'required': 'True'} ) )
    estimate_package_weight = forms.ChoiceField ( required=False, widget = forms.Select( attrs={'required': 'True'} ), choices=Package.WEIGHT_CHOICES )
    
    class Meta:
        model = Package
        fields = ['package_description', 'estimate_package_weight', 'fragile', 'width', 'height', 'depth', 'estimate_package_weight_value']
        
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        # self.fields['recipient_name'].widget.attrs.update({'placeholder': 'John Doe'})
        # self.fields['recipient_phone'].widget.attrs.update({'placeholder': '0987654321'})
        # self.fields['recipient_address'].widget.attrs.update({'placeholder': 'house NO, street, post code, city, county'})


