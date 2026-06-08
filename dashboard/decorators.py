from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('accounts:login')
        if not request.user.is_superuser:
            messages.error(request, 'You are not authorized to access this page.')
            return redirect('posts:feed')
        return view_func(request, *args, **kwargs)
    return wrapper