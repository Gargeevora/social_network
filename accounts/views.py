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