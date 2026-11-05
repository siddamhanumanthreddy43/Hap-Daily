from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def owner_required(view_func):
    """
    Decorator for views that checks if the logged-in user is an OWNER or superuser.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access the owner portal.")
            return redirect(f"/users/login/?next={request.path}")
        if not request.user.is_owner_user:
            messages.error(request, "Access restricted. Only store owners and administrators can access this area.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def customer_required(view_func):
    """
    Decorator for views that checks if user is logged in.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to view your orders and checkout.")
            return redirect(f"/users/login/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

