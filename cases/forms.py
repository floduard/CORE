from django import forms
from .models import *
from datetime import date

class CybercrimeForm(forms.ModelForm):
    class Meta:
        model = CybercrimeType
        fields = ['name', 'description', 'details']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control form-control-sm shadow-sm',
                'placeholder': 'Enter category name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control form-control-sm shadow-sm',
                'rows': 3,
                'placeholder': 'Short description',
            }),
            'details': forms.Textarea(attrs={
                'class': 'form-control form-control-sm shadow-sm',
                'rows': 4,
                'placeholder': 'Detailed explanation (optional)',
            }),
        }

class CybercrimeReportForm(forms.ModelForm):
    class Meta:
        model = CybercrimeReport
        fields = [
            'crime_type', 'description', 'date',
            'country', 'province_city', 'district',
            'evidence', 'suspects','additional_contacts'
        ]
        widgets = {
            'crime_type': forms.Select(attrs={'class': 'form-select','placeholder': 'Choose a crime type...'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe the incident...'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'province_city': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'suspects': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Optional names, emails,phone numbers, etc.'}),
            'evidence': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'additional_contacts': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'optional phone, emails, etc. as means to  contact you...'}),
        }

    def clean_evidence(self):
        file = self.cleaned_data.get('evidence')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError("File too large (max 10MB).")
            if not file.content_type in ['application/pdf', 'image/jpeg', 'image/png', 'video/mp4','audio/mp3','audio/wav']:
                raise forms.ValidationError("Invalid file type. Only PDF, JPG, PNG, MP4, MP3, or WAV allowed.")
        return file
    
    def __init__(self, *args, **kwargs):
        super(CybercrimeReportForm, self).__init__(*args, **kwargs)
        self.fields['crime_type'].queryset = CybercrimeType.objects.all()
        
    def clean_date(self):
        input_date = self.cleaned_data['date']
        if input_date > date.today():
            raise forms.ValidationError("Date cannot be in the future.")
        return input_date


# forms.py

class AssignCaseForm(forms.ModelForm):
    class Meta:
        model = CybercrimeReport # or your Report model
        fields = ['assignee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assignee'].queryset = User.objects.filter(role='officer')
        self.fields['assignee'].label = "Select Officer"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        case = kwargs.get('instance')
        if case :
            self.fields['assignee'].queryset = User.objects.filter(role='officer')
            self.fields['assignee'].queryset = User.objects.filter(role='officer')


class AdditionalEvidenceForm(forms.ModelForm):
    class Meta:
        model = AdditionalEvidence
        fields = ['file']
        