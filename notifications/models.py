from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('friend_request', 'Friend Request'),
        ('friend_accepted', 'Friend Request Accepted'),
        ('purchase_request', 'Purchase Request'),
        ('purchase_approved', 'Purchase Approved'),
        ('purchase_rejected', 'Purchase Rejected'),
        ('representative_approved', 'Representative Access Approved'),
        ('representative_rejected', 'Representative Access Rejected'),
        ('like', 'Post Liked'),
        ('comment', 'Post Commented'),
        ('other', 'Other'),
    ]

    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.student_name}"
