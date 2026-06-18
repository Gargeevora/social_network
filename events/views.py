from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Event, RepresentativeRequest
from .forms import EventForm, RepresentativeRequestForm
from .models import Event, RepresentativeRequest, EventInterest
from notifications.utils import create_notification
from accounts.decorators import verified_student_required

def event_list_view(request):
    query = request.GET.get('q', '')
    events = Event.objects.filter(
        event_date__gte=timezone.now().date()
    ).order_by('event_date')

    if query:
        events = events.filter(event_name__icontains=query)

    return render(request, 'events/event_list.html', {
        'events': events,
        'query': query,
    })


def event_detail_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_interested = False
    if request.user.is_authenticated:
        is_interested = EventInterest.objects.filter(event=event, user=request.user).exists()
    
    return render(request, 'events/event_detail.html', {
        'event': event,
        'is_interested': is_interested,
    })

@login_required
@verified_student_required
def announce_event_view(request):
    # check if user is college representative
    if not request.user.is_college_representative:
        # check if already sent a request
        already_requested = RepresentativeRequest.objects.filter(
            user=request.user
        ).exists()
        return render(request, 'events/not_representative.html', {
            'already_requested': already_requested,
        })

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            messages.success(request, 'Event announced successfully.')
            return redirect('events:list')
    else:
        form = EventForm()

    return render(request, 'events/announce_event.html', {'form': form})


@login_required
@verified_student_required
def request_representative_view(request):
    # check if already requested
    if RepresentativeRequest.objects.filter(user=request.user).exists():
        messages.info(request, 'You have already sent a representative request.')
        return redirect('events:announce')

    if request.method == 'POST':
        form = RepresentativeRequestForm(request.POST)
        if form.is_valid():
            rep_request = RepresentativeRequest.objects.create(
                user=request.user
            )

            # send email to admin
            send_mail(
                subject=f'College Representative Request — {request.user.student_name}',
                message=f"""
New College Representative Request on Social Network

Student Details:
- Name: {request.user.student_name}
- Email: {request.user.email}
- College: {request.user.college_name}
- Branch: {request.user.branch}
- Year: {request.user.year}
- City: {request.user.city}
- Phone: {request.user.phone_number}

Reason:
{form.cleaned_data['reason']}

To approve this request, go to Django Admin:
http://127.0.0.1:8000/admin/accounts/customuser/
Find this user and set 'is_college_representative' to True.
Also go to:
http://127.0.0.1:8000/admin/events/representativerequest/
And update the request status to Approved.
                """,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            messages.success(request, 'Your request has been sent to the admin. You will be notified once approved.')
            return redirect('events:list')
    else:
        form = RepresentativeRequestForm()

    return render(request, 'events/request_representative.html', {'form': form})


@login_required
def toggle_interest_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    interest, created = EventInterest.objects.get_or_create(event=event, user=request.user)
    
    if not created:
        interest.delete()
        messages.info(request, 'Removed from interested events.')
    else:
        messages.success(request, 'Marked as interested. You will be notified of any updates.')
    
    return redirect('events:detail', pk=pk)


@login_required
def edit_event_view(request, pk):
    event = get_object_or_404(Event, pk=pk, organizer=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            
            # notify interested users
            interested_users = EventInterest.objects.filter(event=event).select_related('user')
            for interest in interested_users:
                create_notification(
                    recipient=interest.user,
                    sender=request.user,
                    notification_type='comment',
                    message=f'The event "{event.event_name}" has been updated. Check the latest details.',
                    link=f'/events/{event.pk}/'
                )
            
            messages.success(request, 'Event updated successfully. Interested users have been notified.')
            return redirect('events:detail', pk=pk)
    else:
        form = EventForm(instance=event)
    
    return render(request, 'events/edit_event.html', {'form': form, 'event': event})