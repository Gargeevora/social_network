from django.shortcuts import render
from notifications.models import Notification

def home_view(request):
    return render(request, 'home.html')

from django.shortcuts import redirect

def home_view(request):
    return redirect('posts:feed')

from django.shortcuts import render, redirect


def home_view(request):
    if request.user.is_authenticated:
        return redirect('posts:feed')
    return render(request, 'home.html')

def terms_view(request):
    return render(request, 'terms.html')