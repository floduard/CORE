from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('officer', 'Officer'),
        ('citizen', 'Citizen'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = PhoneNumberField(region='RW', blank=True, null=True)
    email = models.EmailField(unique=True) 
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True)
    birth_date = models.DateField(null=True, blank=True)
    badge_id = models.CharField(max_length=10, blank=True)
    department = models.CharField(max_length=100, blank=True)
    office_name = models.CharField(max_length=100, blank=True)
    managed_since = models.DateField(auto_now_add=True,null=True, blank=True)
    id_number = models.CharField(
    max_length=16,
    validators=[
        RegexValidator(
            regex=r'^[1-9]\d{15}$',
            message="ID must be exactly 16 digits",
            code='invalid_id_number'
        )
    ],

    unique=True,
    null=True,
    blank = True,
)
    def get_profile(self):
        if self.role == 'citizen':
            return getattr(self, 'citizenprofile', None)
        elif self.role == 'officer':
            return getattr(self, 'officerprofile', None)
        elif self.role == 'admin':
            return getattr(self, 'adminprofile', None)
    

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=512)
    url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
   
    class Meta:
        ordering = ['-created_at']


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']



class UserMFA(models.Model):
    METHOD_CHOICES = [
        ('qrcode', 'Authenticator App (QR Code)'),
        ('email', 'Email Code'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='qrcode')
    secret = models.CharField(max_length=32, blank=True, null=True)
    email_code = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)
    email_code_created = models.DateTimeField(blank=True, null=True)  # NEW

    def available_methods(self):
        return self.METHOD_CHOICES
    def __str__(self):
        return f"MFA for {self.user.username}"

