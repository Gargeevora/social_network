from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def verified_student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_college_admin or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        if not request.user.is_college_verified:
            messages.error(request, 'Your college admin has not approved your profile yet. Please wait for approval. If it takes too long, contact your college admin.')
            return redirect(request.META.get('HTTP_REFERER', 'posts:feed'))
        return view_func(request, *args, **kwargs)
    return wrapper