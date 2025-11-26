"""
Django Allauth adapters for custom user signup.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import User
import logging

logger = logging.getLogger(__name__)


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
    
    def get_email_confirmation_url(self, request, emailconfirmation):
        """
        Returns the email confirmation URL using absolute URLs for production.
        This ensures email links work correctly in production environments.
        """
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        # Use request.build_absolute_uri to get absolute URL
        # This is critical for production where relative URLs won't work in emails
        if request:
            return request.build_absolute_uri(url)
        # Fallback: construct from settings if request is not available
        from django.contrib.sites.models import Site
        try:
            site = Site.objects.get_current()
            protocol = 'https' if not settings.DEBUG else 'http'
            return f"{protocol}://{site.domain}{url}"
        except Exception:
            # Last resort fallback
            return url
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send email confirmation with proper error handling and logging.
        This ensures emails are actually sent and logs any failures.
        The parent method automatically uses get_email_confirmation_url() to get the activate_url
        and passes it to the email template context.
        """
        from django.conf import settings
        from django.core.mail import get_connection
        
        # Log email sending attempt with configuration details
        email = emailconfirmation.email_address.email
        username = emailconfirmation.email_address.user.username
        
        logger.info(
            f"Sending email confirmation to {email} for user {username}"
        )
        logger.info(
            f"Email backend: {settings.EMAIL_BACKEND}, "
            f"Host: {getattr(settings, 'EMAIL_HOST', 'N/A')}, "
            f"Port: {getattr(settings, 'EMAIL_PORT', 'N/A')}, "
            f"User: {getattr(settings, 'EMAIL_HOST_USER', 'N/A')}"
        )
        
        # Verify email backend is not console in production
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            logger.error(
                f"ERROR: Console email backend is active! Email to {email} will not be sent. "
                "Please configure SMTP backend in production."
            )
        
        try:
            # Test connection if using SMTP
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
                try:
                    connection = get_connection()
                    connection.open()
                    logger.info("SMTP connection test successful")
                    connection.close()
                except Exception as conn_error:
                    logger.error(
                        f"SMTP connection test failed: {str(conn_error)}. "
                        "Email may not be sent. Please check your email configuration."
                    )
                    # Don't fail here, try to send anyway
            
            # Call parent method to send the email
            # The parent method will automatically call get_email_confirmation_url() 
            # and pass it to the template as 'activate_url'
            result = super().send_confirmation_mail(request, emailconfirmation, signup)
            
            logger.info(
                f"✓ Email confirmation sent successfully to {email}"
            )
            
            return result
        except Exception as e:
            # Log the error with full details
            logger.error(
                f"✗ Failed to send email confirmation to {email}: {str(e)}",
                exc_info=True
            )
            logger.error(
                f"Email configuration check: "
                f"Backend={settings.EMAIL_BACKEND}, "
                f"Host={getattr(settings, 'EMAIL_HOST', 'Not set')}, "
                f"User={getattr(settings, 'EMAIL_HOST_USER', 'Not set')}, "
                f"Password={'Set' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'Not set'}"
            )
            # Re-raise to ensure the error is visible and user knows email wasn't sent
            raise
    
    def render_mail(self, template_prefix, email, context, headers=None):
        """
        Override to ensure activate_url is always an absolute URL in the context.
        This is called by send_confirmation_mail to render the email template.
        """
        # Ensure activate_url is in context and is absolute
        if 'activate_url' in context:
            # If it's already absolute, use it; otherwise make it absolute
            activate_url = context['activate_url']
            if not activate_url.startswith('http'):
                # This shouldn't happen if get_email_confirmation_url works correctly,
                # but this is a safety check
                logger.warning(f"activate_url is not absolute: {activate_url}")
        return super().render_mail(template_prefix, email, context, headers)

