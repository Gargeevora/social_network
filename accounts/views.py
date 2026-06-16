from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .models import CustomUser
from .forms import RegisterForm, LoginForm, EditProfileForm
from .utils import send_verification_email, send_login_alert_email
from .tokens import email_verification_token
from posts.models import Post
from connections.models import Connection
import cloudinary.uploader
from django.contrib.auth import update_session_auth_hash
from books.models import Book, PurchaseRequest
from events.models import Event, EventInterest
from .models import College, CollegeAdminInvite
from django.utils import timezone
from django.conf import settings
from .forms import CollegeAdminRegisterForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            
            # if user exists but unverified delete and allow re-register
            CustomUser.objects.filter(email=email, is_email_verified=False).delete()
            
            user = form.save(commit=False)
            user.is_email_verified = False
            user.save()
            send_verification_email(request, user)
            messages.success(request, 'Registration successful. Please check your email to verify your account.')
            return redirect('accounts:verify_email')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        attempts = request.session.get('login_attempts', 0)
        if attempts >= 5:
            messages.error(request, 'Too many login attempts. Please wait and try again.')
            return render(request, 'accounts/login.html', {'form': LoginForm()})

        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if not user.is_email_verified:
                    messages.error(request, 'Please verify your email before logging in.')
                    return redirect('accounts:login')
                request.session['login_attempts'] = 0
                login(request, user)
                send_login_alert_email(user)
                return redirect('home')

        request.session['login_attempts'] = attempts + 1
        messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        user.is_email_verified = True
        user.save()
        messages.success(request, 'Email verified successfully. You can now login.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Verification link is invalid or has expired.')
        return redirect('accounts:login')


def verify_email_notice_view(request):
    return render(request, 'accounts/verify_email.html')


@login_required
def profile_view(request):
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')

    sent = Connection.objects.filter(sender=request.user, status='accepted').values_list('receiver', flat=True)
    received = Connection.objects.filter(receiver=request.user, status='accepted').values_list('sender', flat=True)
    friends_count = len(list(sent) + list(received))

    return render(request, 'accounts/profile.html', {
        'user_posts': user_posts,
        'friends_count': friends_count,
    })


@login_required
def user_profile_view(request, user_id):
    profile_user = get_object_or_404(CustomUser, pk=user_id)
    user_posts = Post.objects.filter(author=profile_user).order_by('-created_at')

    sent = Connection.objects.filter(sender=profile_user, status='accepted').values_list('receiver', flat=True)
    received = Connection.objects.filter(receiver=profile_user, status='accepted').values_list('sender', flat=True)
    friends_count = len(list(sent) + list(received))

    connection = Connection.objects.filter(
        sender=request.user, receiver=profile_user
    ).first() or Connection.objects.filter(
        sender=profile_user, receiver=request.user
    ).first()

    connection_status = None
    if connection:
        connection_status = connection.status
        if connection.status == 'pending' and connection.receiver == request.user:
            connection_status = 'received'

    return render(request, 'accounts/user_profile.html', {
        'profile_user': profile_user,
        'user_posts': user_posts,
        'friends_count': friends_count,
        'connection_status': connection_status,
        'connection': connection,
        'is_own_profile': request.user == profile_user,
    })


@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def report_issue_view(request):
    from dashboard.models import UserComplaint
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        complaint_type = request.POST.get('complaint_type')
        description = request.POST.get('description')
        
        # verify email and password
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            messages.error(request, 'Invalid email or password. Please try again.')
            return redirect('accounts:report_issue')
        
        if user != request.user:
            messages.error(request, 'Email does not match your logged in account.')
            return redirect('accounts:report_issue')
        
        UserComplaint.objects.create(
            user=user,
            complaint_type=complaint_type,
            issue=description
        )
        
        messages.success(request, 'Your complaint has been submitted. Admin will review it shortly.')
        return redirect('posts:feed')
    
    return render(request, 'accounts/report_issue.html')

def resend_verification_email_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email, is_email_verified=False)
            send_verification_email(request, user)
            messages.success(request, 'Verification email sent. Please check your inbox.')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No unverified account found with this email.')
        return redirect('accounts:resend_verification')
    
    return render(request, 'accounts/resend_verification.html')



@login_required
def delete_account_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect password. Account not deleted.')
            return redirect('accounts:delete_account')
        
        user = request.user
        
        # Notify buyers whose purchase requests were approved by this seller
        approved_requests = PurchaseRequest.objects.filter(
            book__seller=user, status='approved'
        ).select_related('buyer', 'book')
        
        for req in approved_requests:
            create_notification(
                recipient=req.buyer,
                sender=None,
                notification_type='other',
                message=f'The account of the seller for "{req.book.book_name}" no longer exists.',
                link='/books/'
            )
        
        # Notify interested users about organizer's events being removed
        organized_events = Event.objects.filter(organizer=user)
        for event in organized_events:
            interested = EventInterest.objects.filter(event=event).select_related('user')
            for interest in interested:
                create_notification(
                    recipient=interest.user,
                    sender=None,
                    notification_type='other',
                    message=f'The organizer account for "{event.event_name}" no longer exists. The event has been removed.',
                    link='/events/'
                )
        
        # Delete Cloudinary images
        for field_name in ['profile_photo', 'cover_photo', 'id_card_photo']:
            field = getattr(user, field_name, None)
            if field:
                try:
                    cloudinary.uploader.destroy(field.name)
                except Exception:
                    pass
        
        for post in user.posts.all():
            if post.image:
                try:
                    cloudinary.uploader.destroy(post.image.name)
                except Exception:
                    pass
        
        for book in user.books_selling.all():
            if book.book_photo:
                try:
                    cloudinary.uploader.destroy(book.book_photo.name)
                except Exception:
                    pass
        
        for event in organized_events:
            if event.cover_image:
                try:
                    cloudinary.uploader.destroy(event.cover_image.name)
                except Exception:
                    pass
        
        logout(request)
        user.delete()
        
        messages.success(request, 'Your account and all associated data have been permanently deleted.')
        return redirect('home')
    
    return render(request, 'accounts/delete_account.html')

def college_admin_register_view(request, token):
    try:
        invite = CollegeAdminInvite.objects.get(token=token, is_used=False)
    except CollegeAdminInvite.DoesNotExist:
        ip = request.META.get('REMOTE_ADDR', 'Unknown')
        from django.core.mail import send_mail
        send_mail(
            subject='Suspicious access to college admin registration',
            message=f'Someone tried to access an invalid/used admin invite link.\n\nToken: {token}\nIP Address: {ip}\nTime: {timezone.now()}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
        messages.error(request, 'This invite link is invalid or has already been used.')
        return redirect('home')

    if request.method == 'POST':
        form = CollegeAdminRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_email_verified = False
            user.is_college_admin = True
            user.college = invite.college
            user.college_name = invite.college.name
            user.branch = 'Administration'
            user.year = 0
            user.save()

            invite.is_used = True
            invite.used_at = timezone.now()
            invite.save()

            send_verification_email(request, user)
            messages.success(request, f'Registration successful for {invite.college.name} admin account. Please verify your email.')
            return redirect('accounts:verify_email')
    else:
        form = CollegeAdminRegisterForm()

    return render(request, 'accounts/college_admin_register.html', {
        'form': form,
        'college': invite.college,
    })