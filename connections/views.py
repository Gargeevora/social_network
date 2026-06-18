from notifications.utils import create_notification
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Connection
from accounts.models import CustomUser
from accounts.decorators import verified_student_required

@login_required
@verified_student_required
def send_request_view(request, user_id):
    receiver = get_object_or_404(CustomUser, pk=user_id)

    if receiver == request.user:
        messages.error(request, 'You cannot send a friend request to yourself.')
        return redirect('posts:feed')

    # check if connection already exists
    existing = Connection.objects.filter(
        sender=request.user, receiver=receiver
    ).first() or Connection.objects.filter(
        sender=receiver, receiver=request.user
    ).first()

    if existing:
        if existing.status == 'accepted':
            messages.info(request, 'You are already connected with this user.')
        elif existing.status == 'pending':
            messages.info(request, 'Friend request already sent.')
        elif existing.status == 'rejected':
            existing.status = 'pending'
            existing.sender = request.user
            existing.receiver = receiver
            existing.save()
            messages.success(request, f'Friend request sent to {receiver.student_name}.')
        return redirect('posts:feed')

    Connection.objects.create(sender=request.user, receiver=receiver)
    create_notification(
    recipient=receiver,
    sender=request.user,
    notification_type='friend_request',
    message=f'{request.user.student_name} sent you a friend request.',
    link='/connections/requests/'
)
    messages.success(request, f'Friend request sent to {receiver.student_name}.')
    return redirect('posts:feed')


@login_required
@verified_student_required
def accept_request_view(request, request_id):
    connection = get_object_or_404(Connection, pk=request_id, receiver=request.user)
    connection.status = 'accepted'
    connection.save()
    create_notification(
    recipient=connection.sender,
    sender=request.user,
    notification_type='friend_accepted',
    message=f'{request.user.student_name} accepted your friend request.',
    link=f'/accounts/profile/{request.user.pk}/'
)
    messages.success(request, f'You are now connected with {connection.sender.student_name}.')
    return redirect('connections:requests')


@login_required
def reject_request_view(request, request_id):
    connection = get_object_or_404(Connection, pk=request_id, receiver=request.user)
    connection.status = 'rejected'
    connection.save()
    messages.info(request, 'Friend request rejected.')
    return redirect('connections:requests')


@login_required
def friend_requests_view(request):
    incoming_requests = Connection.objects.filter(
        receiver=request.user,
        status='pending'
    ).order_by('-created_at')

    return render(request, 'connections/friend_requests.html', {
        'incoming_requests': incoming_requests,
    })


@login_required
def friends_list_view(request):
    sent = Connection.objects.filter(
        sender=request.user, status='accepted'
    ).values_list('receiver', flat=True)

    received = Connection.objects.filter(
        receiver=request.user, status='accepted'
    ).values_list('sender', flat=True)

    friend_ids = list(sent) + list(received)
    friends = CustomUser.objects.filter(pk__in=friend_ids)

    return render(request, 'connections/friends_list.html', {
        'friends': friends,
    })

@login_required
def unfriend_view(request, user_id):
    other_user = get_object_or_404(CustomUser, pk=user_id)
    
    connection = Connection.objects.filter(
        sender=request.user, receiver=other_user
    ).first() or Connection.objects.filter(
        sender=other_user, receiver=request.user
    ).first()
    
    if connection:
        connection.delete()
        messages.success(request, f'You unfriended {other_user.student_name}.')
    
    return redirect('connections:friends')