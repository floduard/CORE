from .models import Notification


def notify_user(recipient, message, url=None):
    Notification.objects.create(recipient=recipient, message=message, url=url)
