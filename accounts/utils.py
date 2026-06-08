from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .tokens import email_verification_token


def send_verification_email(request, user):
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    verification_link = f"http://127.0.0.1:8000/accounts/verify-email/{uid}/{token}/"
    
    subject = 'Verify your Social Network email'
    message = render_to_string('accounts/verification_email.html', {
        'user': user,
        'verification_link': verification_link,
    })
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
        html_message=message,
    )
    
    subject = 'Verify your College Network email'
    message = render_to_string('accounts/verification_email.html', {
        'user': user,
        'verification_link': verification_link,
    })
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
        html_message=message,
    )


def send_login_alert_email(user):
    subject = 'New login to your College Network account'
    message = render_to_string('accounts/login_alert_email.html', {
        'user': user,
    })
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
        html_message=message,
    )