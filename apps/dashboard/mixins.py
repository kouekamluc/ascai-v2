"""
Mixins for dashboard views.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


class DashboardRequiredMixin(LoginRequiredMixin):
    """
    Mixin that ensures user is authenticated and approved.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _('Please log in to access the reserved area.'))
            return redirect('account_login')
        
        if not request.user.is_approved and not request.user.is_superuser:
            messages.error(
                request,
                _('Your account is pending admin approval. You will receive an email when your account is approved.')
            )
            return redirect('core:home')
        
        return super().dispatch(request, *args, **kwargs)

