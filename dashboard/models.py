from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    COMPLAINT_TYPES = [
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('fake_account', 'Fake Account'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('other', 'Other'),
    ]

    complainant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='complaints_filed')
    accused = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='complaints_against')
    complaint_type = models.CharField(max_length=30, choices=COMPLAINT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(blank=True, null=True)
    admin_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.complainant.student_name} complained about {self.accused.student_name}"


class AuditLog(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=255)
    target_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_targets')
    timestamp = models.DateTimeField(default=timezone.now)
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.admin.student_name} — {self.action} at {self.timestamp}"
    
class UserComplaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
    ]

    COMPLAINT_TYPES = [
        ('technical_issue', 'Technical Issue'),
        ('account_problem', 'Account Problem'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_complaints')
    complaint_type = models.CharField(max_length=30, choices=COMPLAINT_TYPES, default='other')
    issue = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    admin_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Complaint by {self.user.student_name}"
