from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import secrets


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_email_verified', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Auth fields
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    phone_number = models.CharField(max_length=15)
    is_college_representative = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, null=True)
    is_college_admin = models.BooleanField(default=False)
    college = models.ForeignKey('College', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    is_college_verified = models.BooleanField(default=False)
    college_locked = models.BooleanField(default=False)
    
    # Profile fields
    student_name = models.CharField(max_length=100)
    college_name = models.CharField(max_length=200)
    branch = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()  # 1, 2, 3, 4
    city = models.CharField(max_length=100)
    address = models.TextField()
    id_card_photo = models.ImageField(upload_to='id_cards/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['student_name', 'college_name', 'branch', 'year', 'city', 'address']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.student_name} ({self.email})"


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='email_token')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # Token expires after 24 hours
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)

    def __str__(self):
        return f"Token for {self.user.email}"
    

class College(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class CollegeAdminInvite(models.Model):
    college = models.OneToOneField(College, on_delete=models.CASCADE, related_name='admin_invite')
    token = models.CharField(max_length=64, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    used_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invite for {self.college.name} - {'Used' if self.is_used else 'Active'}"