from django import forms
from .models import *

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        exclude = ['uploaded_by', 'date_uploaded']  # Don't show these in the form

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter your message here'})
        }

class AdminReplyForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['admin_reply']
        widgets = {
            'admin_reply': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter your reply here'})
        }