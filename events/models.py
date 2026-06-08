from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class RepresentativeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='representative_request')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.student_name} - {self.status}"


class Event(models.Model):
    organizer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='events')
    
    # Event details
    event_name = models.CharField(max_length=200)
    about = models.TextField()
    cover_image = models.ImageField(upload_to='event_covers/')
    place = models.CharField(max_length=200)
    event_date = models.DateField()
    last_registration_date = models.DateField()
    fees = models.PositiveIntegerField(default=0)  # 0 means free
    contact_number = models.CharField(max_length=15)
    registration_link = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.event_name} by {self.organizer.college_name}"

    def is_registration_open(self):
        return timezone.now().date() <= self.last_registration_date

    def is_upcoming(self):
        return timezone.now().date() <= self.event_date