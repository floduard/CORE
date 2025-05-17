from django import forms
from .models import Resource

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        exclude = ['uploaded_by', 'date_uploaded']  # Don't show these in the form
