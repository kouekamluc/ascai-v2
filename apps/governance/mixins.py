"""
Mixins for governance views.
"""
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _


class GovernanceRequiredMixin(LoginRequiredMixin):
    """
    Mixin that ensures user is authenticated and approved.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, _('Please log in to access governance features.'))
            return redirect('account_login')
        
        if not request.user.is_approved and not request.user.is_superuser:
            messages.error(
                request,
                _('Your account is pending admin approval.')
            )
            return redirect('core:home')
        
        return super().dispatch(request, *args, **kwargs)


class ExecutiveBoardRequiredMixin(GovernanceRequiredMixin, PermissionRequiredMixin):
    """
    Mixin for views that require executive board management permissions.
    """
    permission_required = 'governance.manage_executive_board'
    raise_exception = True


class AssemblyManagementRequiredMixin(GovernanceRequiredMixin, PermissionRequiredMixin):
    """
    Mixin for views that require assembly management permissions.
    """
    permission_required = 'governance.manage_assembly'
    raise_exception = True


class FinancialManagementRequiredMixin(GovernanceRequiredMixin, PermissionRequiredMixin):
    """
    Mixin for views that require financial management permissions.
    """
    permission_required = 'governance.manage_finances'
    raise_exception = True


class ExpenseApprovalRequiredMixin(GovernanceRequiredMixin, PermissionRequiredMixin):
    """
    Mixin for views that require expense approval permissions.
    """
    permission_required = 'governance.approve_expense'
    raise_exception = True







