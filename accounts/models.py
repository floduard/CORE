from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('officer', 'Officer'),
        ('citizen', 'Citizen'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True) 
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True)
    birth_date = models.DateField(null=True, blank=True)
    badge_id = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    office_name = models.CharField(max_length=100, blank=True)
    managed_since = models.DateField(null=True, blank=True)
    id_number = models.CharField(max_length=20, blank=True)

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
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']