from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, CitizenProfile, OfficerProfile, AdminProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'citizen':
            CitizenProfile.objects.create(user=instance)
        elif instance.role == 'officer':
            OfficerProfile.objects.create(user=instance)
        elif instance.role == 'admin':
            AdminProfile.objects.create(user=instance)
