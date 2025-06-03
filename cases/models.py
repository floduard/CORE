from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
User = get_user_model()


class CybercrimeType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    details= models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CybercrimeReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_investigation', 'Under Investigation'),
        ('postponed', 'Postponed'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
        ('irrelevant', 'Irrelevant'),
         ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
        ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    crime_type = models.ForeignKey(CybercrimeType, on_delete=models.CASCADE)
    description = models.TextField()
    date = models.DateField()
    country = models.CharField(default="Rwanda", max_length=100)
    province_city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    evidence = models.FileField(upload_to='evidence/', blank=True, null=True)
    suspects = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    more_details = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    tracking_id = models.CharField(max_length=12, unique=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    additional_contacts = models.TextField(blank=True, null=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignee', blank=True, null=True)
    request_more_info = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.status == 'closed' and not self.recommendations:
            raise ValidationError('Recommendations are required for closed cases')
            if self.priority == 'critical' and not self.evidence:
                raise ValidationError('Evidence is required for critical priority reports.')
    

    def __str__(self):
        return str(self.crime_type)

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            import uuid
            self.tracking_id = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)


class CaseAssignmentHistory(models.Model):
    case = models.ForeignKey( CybercrimeReport, on_delete=models.CASCADE, related_name='assignment_history')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_made')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assignments_received')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case.tracking_id} → {self.assigned_to} on {self.timestamp:%Y-%m-%d %H:%M}"


class AdditionalEvidence(models.Model):
    report = models.ForeignKey(CybercrimeReport, on_delete=models.CASCADE, related_name='additional_evidences')
    file = models.FileField(upload_to='evidence/additional/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # optional



# models.py
class Suspect(models.Model):
    case_report = models.ForeignKey(CybercrimeReport, on_delete=models.CASCADE, related_name='suspect')
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=20, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    contact_info = models.TextField(blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

