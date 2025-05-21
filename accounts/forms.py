from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *

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

class CitizenProfileForm(forms.ModelForm):
    class Meta:
        model = CitizenProfile
        fields = ['gender', 'profile_picture', 'id_number', 'birth_date']

class OfficerProfileForm(forms.ModelForm):
    class Meta:
        model = OfficerProfile
        fields = ['badge_id', 'gender', 'profile_picture', 'department']

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = AdminProfile
        fields = ['profile_picture','gender', 'office_name', 'managed_since']



class OfficerCreationForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
