from django import forms
from .models import *

class CybercrimeForm(forms.ModelForm):
    class Meta:
        model = CybercrimeType
        fields = ['name', 'description']
