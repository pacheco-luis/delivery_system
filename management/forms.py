from django import forms

class ASSIGN_CLUSTER_FORM(forms.Form):
    cluster_id = forms.CharField( max_length=50, required=True, widget=forms.TextInput(attrs={
        'id':'cluster_id',
        'text':'text',
        # 'disabled': '',
        'class':'form-control assign_form_input',
        'placeholder':'cluster id',
        'aria-label':'cluster id',
        'aria-describedby':'basic-addon1'
    }))
    driver_username = forms.CharField( max_length=50, required=True, widget=forms.TextInput(attrs={
        'id':'driver_username',
        'type':'text',
        'class':'form-control assign_form_input',
        'placeholder':'driver username',
        'aria-label':'Username',
        'aria-describedby':'basic-addon1'
    }))
    