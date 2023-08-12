from django import forms
from package_request.models import Package

class SENDER_FORM(forms.ModelForm):
    class Meta:
        model = Package
        exclude = ['sender_id', 'sender_phone', 'sender_address']
