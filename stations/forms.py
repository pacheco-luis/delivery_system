from django import forms
from stations.models import Stations
from places.fields import PlacesField
from django.utils.translation import gettext_lazy as _

class SENDER_FORM(forms.ModelForm):
    class Meta:
        model = Stations
        exclude='station_id'
