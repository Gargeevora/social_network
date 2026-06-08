from .models import Notification


def create_notification(recipient, sender, notification_type, message, link=None):
    # dont create notification if sender and recipient are same
    if recipient == sender:
        return
    
    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        message=message,
        link=link,
    )