from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.forms import PasswordChangeForm
from phonenumber_field.formfields import PhoneNumberField as PhoneNumberFormField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.core.validators import RegexValidator
from django.forms import TextInput

class CitizenRegisterForm(UserCreationForm):    
    
    class Meta:
        model = User
        fields = ['username', 'email','phone', 'password1', 'password2']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control','placeholder': '07xxxxxxxx'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'citizen'
        if commit:
            user.save()
        return user
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email
    
    


class CombinedUserProfileForm(forms.ModelForm):
   
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'profile_picture', 'gender', 'birth_date', 'badge_id',
            'department', 'office_name', 'id_number',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control','placeholder': '07xxxxxxxx'}),
            'id_number': forms.TextInput(attrs={'inputmode': 'numeric', 'pattern': '[1-9][0-9]{15}'}),
            
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['email'].disabled = True

        # Hide role-specific fields
        if user:
            role = user.role
            if role == 'citizen':
                self.fields['badge_id'].widget = forms.HiddenInput()
                self.fields['department'].widget = forms.HiddenInput()
                self.fields['office_name'].widget = forms.HiddenInput()
                
            elif role == 'officer':
                self.fields['id_number'].widget = forms.HiddenInput()
                self.fields['office_name'].widget = forms.HiddenInput()
                
            elif role == 'admin':
                self.fields['id_number'].widget = forms.HiddenInput()
                self.fields['badge_id'].widget = forms.HiddenInput()
                self.fields['department'].widget = forms.HiddenInput()

   
    
   
class OfficerCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name','phone','gender','profile_picture', 'role']
    widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control','placeholder': '07xxxxxxxx'}),          
            
        }

    def save(self, commit=True):
        User = super().save(commit=False)
        if commit:
            User.save()
        return User
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email
    
    

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})