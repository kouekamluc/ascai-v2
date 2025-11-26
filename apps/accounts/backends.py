"""
Custom authentication backends.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ApprovalRequiredBackend(ModelBackend):
    """
    Authentication backend that checks if user is approved before allowing login.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user and check approval status.
        """
        # Try to get user by username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Try to get user by email
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        
        # Check password
        if user.check_password(password):
            # Superusers bypass all checks (is_active and is_approved)
            if user.is_superuser:
                return user
            
            # Check if user is active (non-superusers only)
            if not user.is_active:
                return None
            
            # Check if user is approved (non-superusers only)
            if not user.is_approved:
                # Don't raise exception here, just return None
                # The form will handle displaying the error message
                return None
            
            return user
        
        return None






