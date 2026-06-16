from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from accounts.models import CustomUser
from posts.models import Post
from books.models import Book, PurchaseRequest
from events.models import Event, RepresentativeRequest
from connections.models import Connection
from notifications.utils import create_notification
from .models import Complaint, AuditLog
from .decorators import admin_required
from .models import Complaint, AuditLog, UserComplaint
from accounts.models import College, CollegeAdminInvite


def log_action(admin, action, target_user=None, details=None):
    AuditLog.objects.create(
        admin=admin,
        action=action,
        target_user=target_user,
        details=details
    )


@admin_required
def dashboard_home_view(request):
    total_users = CustomUser.objects.filter(is_superuser=False).count()
    total_posts = Post.objects.count()
    total_books = Book.objects.count()
    total_events = Event.objects.count()
    pending_complaints = Complaint.objects.filter(status='pending').count()
    pending_rep_requests = RepresentativeRequest.objects.filter(status='pending').count()
    blocked_users = CustomUser.objects.filter(is_active=False, is_superuser=False).count()
    recent_logs = AuditLog.objects.all()[:10]

    return render(request, 'dashboard/dashboard_home.html', {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_books': total_books,
        'total_events': total_events,
        'pending_complaints': pending_complaints,
        'pending_rep_requests': pending_rep_requests,
        'blocked_users': blocked_users,
        'recent_logs': recent_logs,
    })


@admin_required
def users_view(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.filter(is_superuser=False).order_by('-date_joined')

    if query:
        users = users.filter(student_name__icontains=query)

    return render(request, 'dashboard/users.html', {
        'users': users,
        'query': query,
    })


@admin_required
def block_user_view(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id, is_superuser=False)

    if user.is_active:
        user.is_active = False
        user.save()
        action = 'blocked'

        # notify user by notification
        create_notification(
            recipient=user,
            sender=request.user,
            notification_type='comment',
            message='Your account has been blocked by the admin. Contact support if you think this is a mistake.',
            link='/accounts/login/'
        )

        # send email to user
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject='Your Social Network account has been blocked',
            message=f'Hi {user.student_name}, your account has been blocked by the admin. If you think this is a mistake please contact support.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )

        log_action(request.user, f'Blocked user {user.student_name}', target_user=user)
        messages.success(request, f'{user.student_name} has been blocked.')
    else:
        user.is_active = True
        user.save()

        create_notification(
            recipient=user,
            sender=request.user,
            notification_type='comment',
            message='Your account has been unblocked by the admin. You can now login.',
            link='/accounts/login/'
        )

        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject='Your Social Network account has been unblocked',
            message=f'Hi {user.student_name}, your account has been unblocked. You can now login.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=True,
        )

        log_action(request.user, f'Unblocked user {user.student_name}', target_user=user)
        messages.success(request, f'{user.student_name} has been unblocked.')

    return redirect('dashboard:users')


@admin_required
def complaints_view(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'dashboard/complaints.html', {
        'complaints': complaints,
    })


@admin_required
def resolve_complaint_view(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    complaint.status = 'resolved'
    complaint.resolved_at = timezone.now()
    complaint.save()
    log_action(request.user, f'Resolved complaint #{complaint.pk}', target_user=complaint.accused)
    messages.success(request, 'Complaint marked as resolved.')
    return redirect('dashboard:complaints')


@admin_required
def dismiss_complaint_view(request, complaint_id):
    complaint = get_object_or_404(Complaint, pk=complaint_id)
    complaint.status = 'dismissed'
    complaint.resolved_at = timezone.now()
    complaint.save()
    log_action(request.user, f'Dismissed complaint #{complaint.pk}', target_user=complaint.accused)
    messages.success(request, 'Complaint dismissed.')
    return redirect('dashboard:complaints')


@admin_required
def representative_requests_view(request):
    requests = RepresentativeRequest.objects.all().order_by('-requested_at')
    return render(request, 'dashboard/representative_requests.html', {
        'rep_requests': requests,
    })


@admin_required
def approve_representative_view(request, request_id):
    rep_request = get_object_or_404(RepresentativeRequest, pk=request_id)
    rep_request.status = 'approved'
    rep_request.reviewed_at = timezone.now()
    rep_request.save()
    rep_request.user.is_college_representative = True
    rep_request.user.save()

    create_notification(
        recipient=rep_request.user,
        sender=request.user,
        notification_type='representative_approved',
        message='Your college representative request has been approved. You can now announce events.',
        link='/events/announce/'
    )

    from django.core.mail import send_mail
    from django.conf import settings
    send_mail(
        subject='College Representative Request Approved — Social Network',
        message=f'Hi {rep_request.user.student_name}, your college representative request has been approved. You can now announce events on Social Network.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[rep_request.user.email],
        fail_silently=True,
    )

    log_action(request.user, f'Approved representative request for {rep_request.user.student_name}', target_user=rep_request.user)
    messages.success(request, f'{rep_request.user.student_name} approved as college representative.')
    return redirect('dashboard:representative_requests')


@admin_required
def reject_representative_view(request, request_id):
    rep_request = get_object_or_404(RepresentativeRequest, pk=request_id)
    rep_request.status = 'rejected'
    rep_request.reviewed_at = timezone.now()
    rep_request.save()
    rep_request.user.is_college_representative = False
    rep_request.user.save()

    create_notification(
        recipient=rep_request.user,
        sender=request.user,
        notification_type='representative_rejected',
        message='Your college representative request has been rejected by the admin.',
        link='/events/list/'
    )

    log_action(request.user, f'Rejected representative request for {rep_request.user.student_name}', target_user=rep_request.user)
    messages.success(request, f'{rep_request.user.student_name} representative request rejected.')
    return redirect('dashboard:representative_requests')


@admin_required
def audit_log_view(request):
    logs = AuditLog.objects.all()
    return render(request, 'dashboard/audit_log.html', {
        'logs': logs,
    })

@admin_required
def remove_representative_view(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id, is_superuser=False)
    user.is_college_representative = False
    user.save()

    # update representative request status
    RepresentativeRequest.objects.filter(user=user).update(status='rejected')

    create_notification(
        recipient=user,
        sender=request.user,
        notification_type='representative_rejected',
        message='Your college representative access has been removed by the admin.',
        link='/events/list/'
    )

    from django.core.mail import send_mail
    from django.conf import settings
    send_mail(
        subject='College Representative Access Removed — Social Network',
        message=f'Hi {user.student_name}, your college representative access has been removed by the admin. Contact support if you think this is a mistake.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
        fail_silently=True,
    )

    log_action(request.user, f'Removed representative access from {user.student_name}', target_user=user)
    messages.success(request, f'{user.student_name} representative access removed.')
    return redirect('dashboard:users')

@admin_required
def user_complaints_view(request):
    complaints = UserComplaint.objects.all().order_by('-created_at')
    return render(request, 'dashboard/user_complaints.html', {
        'complaints': complaints,
    })


@admin_required
def resolve_user_complaint_view(request, complaint_id):
    from .models import UserComplaint
    complaint = get_object_or_404(UserComplaint, pk=complaint_id)
    complaint.status = 'resolved'
    complaint.save()
    log_action(request.user, f'Resolved user complaint #{complaint.pk}', target_user=complaint.user)
    messages.success(request, 'Complaint marked as resolved.')
    return redirect('dashboard:user_complaints')

@admin_required
def user_complaint_detail_view(request, complaint_id):
    from .models import UserComplaint
    complaint = get_object_or_404(UserComplaint, pk=complaint_id)
    return render(request, 'dashboard/user_complaint_detail.html', {
        'complaint': complaint,
    })


@admin_required
def colleges_view(request):
    colleges = College.objects.all().order_by('name')
    return render(request, 'dashboard/colleges.html', {'colleges': colleges})


@admin_required
def add_college_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        
        if College.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A college with this name already exists.')
        elif College.objects.filter(code__iexact=code).exists():
            messages.error(request, 'A college with this code already exists.')
        else:
            College.objects.create(name=name, code=code.upper())
            messages.success(request, f'College "{name}" added successfully.')
        
        return redirect('dashboard:colleges')
    
    return redirect('dashboard:colleges')


@admin_required
def generate_invite_view(request, college_id):
    college = get_object_or_404(College, pk=college_id)
    
    invite, created = CollegeAdminInvite.objects.get_or_create(college=college)
    
    if not created and invite.is_used:
        # regenerate token for reuse
        invite.token = ''
        invite.is_used = False
        invite.used_at = None
        invite.save()
    
    log_action(request.user, f'Generated admin invite for {college.name}', target_user=None)
    messages.success(request, f'Invite link generated for {college.name}.')
    return redirect('dashboard:colleges')