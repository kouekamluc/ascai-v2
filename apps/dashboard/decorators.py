"""
Decorators for dashboard access control.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def dashboard_required(view_func):
    """
    Decorator that checks if user is authenticated and approved.
    Redirects to login if not authenticated, or shows error if not approved.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _('Please log in to access the reserved area.'))
            return redirect('account_login')
        
        if not request.user.is_approved and not request.user.is_superuser:
            messages.error(
                request,
                _('Your account is pending admin approval. You will receive an email when your account is approved.')
            )
            return redirect('core:home')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

