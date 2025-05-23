from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth.forms import PasswordChangeForm

class CitizenRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'citizen'
        if commit:
            user.save()
        return user



class CombinedUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address',
            'profile_picture', 'gender', 'birth_date', 'badge_id',
            'department', 'office_name', 'managed_since', 'id_number',
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'managed_since': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Hide role-specific fields
        if user:
            role = user.role
            if role == 'citizen':
                self.fields['badge_id'].widget = forms.HiddenInput()
                self.fields['department'].widget = forms.HiddenInput()
                self.fields['office_name'].widget = forms.HiddenInput()
                self.fields['managed_since'].widget = forms.HiddenInput()
            elif role == 'officer':
                self.fields['id_number'].widget = forms.HiddenInput()
                self.fields['birth_date'].widget = forms.HiddenInput()
                self.fields['office_name'].widget = forms.HiddenInput()
                self.fields['managed_since'].widget = forms.HiddenInput()
            elif role == 'admin':
                self.fields['id_number'].widget = forms.HiddenInput()
                self.fields['birth_date'].widget = forms.HiddenInput()
                self.fields['badge_id'].widget = forms.HiddenInput()
                self.fields['department'].widget = forms.HiddenInput()


class OfficerCreationForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})