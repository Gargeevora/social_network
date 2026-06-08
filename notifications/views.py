from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    # mark all as read
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'notifications/notifications.html', {
        'notifications': notifications,
    })


@login_required
def mark_read_view(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')


def get_unread_count(user):
    if user.is_authenticated:
        return Notification.objects.filter(recipient=user, is_read=False).count()
    return 0
