from django import forms
from django.utils.translation import gettext_lazy as _
from django import forms

class READ_ALL_FORM(forms.Form):
    def __init__(self, *args, **kwargs):
        super(READ_ALL_FORM, self).__init__(*args, **kwargs)
        self.fields['url'] = forms.CharField(max_length=255)