from django.forms import ModelForm

from .models import Parcel

class ParcelForm(ModelForm):
    class Meta:
        model = Parcel
        fields = [
            'name',
            'description',
            'weight',
            'sender_name',
            'sender_phone',
            'sender_address',
            'recipient_name',
            'recipient_phone',
            'recipient_address'
        ]