from django import forms
from stations.models import Station
from places.fields import PlacesField
from django.utils.translation import gettext_lazy as _
from collections import OrderedDict

class STATIONS_FORM(forms.ModelForm):
    id=forms.CharField(max_length=50, required=True)
    class Meta:
        model = Station
        fields = [
        'alias',
        'address',
        'radius',
        'active',
        ]
        
    def __init__(self, *args, **kwargs):
        super(STATIONS_FORM, self).__init__(*args, **kwargs)

        # Reconstructing fields in the desired order
        ordered_fields = OrderedDict()
        ordered_fields['id'] = self.fields['id']
        for field_name in self.Meta.fields:
            if field_name != 'id':
                ordered_fields[field_name] = self.fields[field_name]
        self.fields = ordered_fields
        