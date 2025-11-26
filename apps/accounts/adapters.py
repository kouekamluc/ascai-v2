"""
Django Allauth adapters for custom user signup.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomLoginForm(LoginForm):
    """
    Custom login form that checks user approval status.
    """
    
    def clean(self):
        """
        Validate login and check if user is approved.
        """
        cleaned_data = super().clean()
        login = cleaned_data.get('login')
        password = cleaned_data.get('password')
        
        if login and password:
            # Try to get user by username or email
            try:
                user = User.objects.get(username=login)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=login)
                except User.DoesNotExist:
                    # Let parent form handle authentication error
                    return cleaned_data
            
            # Superusers bypass all checks (is_active and is_approved)
            if user.is_superuser:
                return cleaned_data
            
            # Check if user is active (non-superusers only)
            if not user.is_active:
                raise ValidationError(
                    _('Your account is inactive. Please contact an administrator.')
                )
            
            # Check if user is approved (non-superusers only)
            if not user.is_approved:
                raise ValidationError(
                    _('Your account is pending admin approval. Please wait for approval before logging in.')
                )
        
        return cleaned_data


class CustomSignupForm(SignupForm):
    """
    Custom signup form that includes additional fields.
    """
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
            'placeholder': _('Phone number (optional)')
        }),
        label=_('Phone Number')
    )
    
    role = forms.ChoiceField(
        choices=[
            ('student', _('Student')),
            ('mentor', _('Mentor')),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
        }),
        initial='student',
        label=_('I am a')
    )
    
    language_preference = forms.ChoiceField(
        choices=User.LANGUAGE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green',
        }),
        initial='en',
        label=_('Language Preference')
    )
    
    def save(self, request):
        """
        Save the user with custom fields and set approval status.
        """
        user = super().save(request)
        
        # Set custom fields
        user.phone = self.cleaned_data.get('phone', '')
        user.role = self.cleaned_data.get('role', 'student')
        user.language_preference = self.cleaned_data.get('language_preference', 'en')
        
        # Set approval status - require admin approval
        user.is_approved = False
        user.is_active = False  # Inactive until approved
        
        user.save()
        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom account adapter to handle signup with custom fields.
    """
    
    def get_login_form_class(self):
        """
        Return the custom login form class.
        """
        return CustomLoginForm
    
    def get_signup_form_class(self):
        """
        Return the custom signup form class.
        """
        return CustomSignupForm
    
    def save_user(self, request, user, form, commit=True):
        """
        Save the user with custom fields.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Set custom fields from form
        if hasattr(form, 'cleaned_data'):
            user.phone = form.cleaned_data.get('phone', '')
            user.role = form.cleaned_data.get('role', 'student')
            user.language_preference = form.cleaned_data.get('language_preference', 'en')
        
        # Set approval status - require admin approval
        user.is_approved = False
        user.is_active = False  # Inactive until approved
        
        if commit:
            user.save()
        
        return user
    
    def is_open_for_signup(self, request):
        """
        Allow signup by default.
        """
        return True
    
    def is_account_active(self, user):
        """
        Check if account is active. Superusers bypass this check.
        This prevents redirect to /accounts/inactive/ for superusers.
        """
        # Superusers can always log in, even if is_active is False
        if user.is_superuser:
            return True
        # For regular users, check is_active
        return user.is_active

