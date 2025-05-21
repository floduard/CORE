from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('definition', 'Definition'),
        ('file', 'File'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('course', 'Course'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField()

    upload = models.FileField(upload_to='resources/files/', blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_uploaded = models.DateTimeField(auto_now_add=True)  # ✅ Ensure this exists

    def __str__(self):
        return self.name


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    admin_reply = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Feedback from {self.user.username}"