import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from .tokens import email_verification_token
import os


def send_verification_email(request, user):
    token = email_verification_token.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = f"https://social-network-p1mg.onrender.com/accounts/verify-email/{uid}/{token}/"

    if user.is_college_admin:
        subject = f"Verify your College Admin account — {user.college.name}"
        template = 'accounts/college_admin_verification_email.html'
    else:
        subject = "Verify your Social Network email"
        template = 'accounts/verification_email.html'

    message = render_to_string(template, {
        'user': user,
        'verification_link': verification_link,
    })

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": user.email, "name": user.student_name}],
        sender={"email": os.getenv('EMAIL_HOST_USER'), "name": "Social Network"},
        subject=subject,
        html_content=message
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print(f"Email sending failed: {e}")


def send_login_alert_email(user):
    message = render_to_string('accounts/login_alert_email.html', {
        'user': user,
    })

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": user.email, "name": user.student_name}],
        sender={"email": os.getenv('EMAIL_HOST_USER'), "name": "Social Network"},
        subject="New login to your Social Network account",
        html_content=message
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print(f"Email sending failed: {e}")