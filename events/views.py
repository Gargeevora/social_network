from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Event, RepresentativeRequest
from .forms import EventForm, RepresentativeRequestForm


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
    return render(request, 'events/event_detail.html', {'event': event})


@login_required
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