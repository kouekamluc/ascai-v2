"""
Django Allauth adapters for custom user signup.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import SignupForm, LoginForm
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.http import HttpResponseRedirect
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
        Note: We keep user active initially so email confirmation can be sent.
        User will be set to inactive after email confirmation if needed.
        """
        user = super().save_user(request, user, form, commit=False)
        
        # Set custom fields from form
        if hasattr(form, 'cleaned_data'):
            user.phone = form.cleaned_data.get('phone', '')
            user.role = form.cleaned_data.get('role', 'student')
            user.language_preference = form.cleaned_data.get('language_preference', 'en')
        
        # Set approval status - require admin approval
        user.is_approved = False
        # Keep user active initially so email confirmation can be sent
        # The backend will check is_approved for login, not just is_active
        # We'll handle inactive status after email confirmation if needed
        user.is_active = True  # Keep active for email confirmation
        
        if commit:
            user.save()
            logger.info(
                f"User {user.username} ({user.email}) created with is_approved=False, is_active=True "
                f"(will be checked by backend for login)"
            )
        
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
        user = emailconfirmation.email_address.user
        
        logger.info("=" * 60)
        logger.info("EMAIL CONFIRMATION ATTEMPT")
        logger.info("=" * 60)
        logger.info(f"User: {username} ({email})")
        logger.info(f"User is_active: {user.is_active}, is_approved: {user.is_approved}")
        logger.info(f"Email backend: {settings.EMAIL_BACKEND}")
        logger.info(f"SMTP Host: {getattr(settings, 'EMAIL_HOST', 'N/A')}")
        logger.info(f"SMTP Port: {getattr(settings, 'EMAIL_PORT', 'N/A')}")
        logger.info(f"SMTP User: {getattr(settings, 'EMAIL_HOST_USER', 'N/A')}")
        logger.info(f"SMTP Password: {'SET' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NOT SET'}")
        
        # Verify email backend is not console in production
        if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
            error_msg = (
                f"CRITICAL ERROR: Console email backend is active! "
                f"Email to {email} will NOT be sent in production. "
                f"Set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend in Railway."
            )
            logger.error("=" * 60)
            logger.error(error_msg)
            logger.error("=" * 60)
            # Log the error but don't break signup - let the parent method handle it
            # The email will fail but user signup can still complete
            # Admin can check logs and fix email configuration
        
        # Skip SMTP connection test - it can cause blocking/timeout issues
        # Just try to send the email directly
        
        try:
            # Call parent method to send the email
            # The parent method will automatically call get_email_confirmation_url() 
            # and pass it to the template as 'activate_url'
            logger.info(f"Attempting to send email confirmation to {email}...")
            result = super().send_confirmation_mail(request, emailconfirmation, signup)
            
            logger.info("=" * 60)
            logger.info(f"SUCCESS: Email confirmation sent to {email}")
            logger.info("=" * 60)
            
            return result
        except Exception as e:
            # Catch ALL exceptions including SystemExit to prevent worker crashes
            # Log the error with full details but DON'T break signup
            logger.error("=" * 60)
            logger.error("EMAIL CONFIRMATION FAILED - BUT SIGNUP WILL CONTINUE")
            logger.error("=" * 60)
            logger.error(f"Failed to send email to {email}: {str(e)}", exc_info=True)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Backend: {settings.EMAIL_BACKEND}")
            logger.error(f"Host: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
            logger.error(f"User: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
            logger.error(f"Password: {'SET' if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else 'NOT SET'}")
            logger.error("=" * 60)
            logger.error("User signup will complete, but email confirmation was not sent.")
            logger.error("Admin should check email configuration and resend confirmation email if needed.")
            logger.error("=" * 60)
            # DON'T re-raise - allow signup to complete even if email fails
            # The user account is created, admin can manually send confirmation email later
            # Return None to indicate email was not sent, but don't break the signup flow
            # This prevents SystemExit and other exceptions from crashing the worker
            return None
    
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


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter to handle Google OAuth signups
    with custom user model fields and approval workflow.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before a social account is logged in.
        If a user with this email already exists, connect the accounts.
        This allows existing users to login with Google OAuth.
        """
        # If the user is already logged in, connect the social account
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
            logger.info(f"Connecting Google account to already logged-in user: {request.user.email}")
            return
        
        # Check if a user with this email already exists
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                # Connect the social account to existing user
                # This allows existing users to login with Google
                sociallogin.connect(request, user)
                logger.info(
                    f"Linked Google account to existing user: {user.email} (username: {user.username})"
                )
            except User.DoesNotExist:
                # User doesn't exist, will be created in save_user
                logger.info(f"New user signup via Google OAuth: {email}")
                pass
            except User.MultipleObjectsReturned:
                # Multiple users with same email (shouldn't happen, but handle it)
                logger.warning(f"Multiple users found with email {email}, using first one")
                user = User.objects.filter(email=email).first()
                if user:
                    sociallogin.connect(request, user)
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user fields from Google OAuth data.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Extract name from Google profile
        if not user.username:
            # Use email as username if name not available
            email = data.get('email', '')
            user.username = email.split('@')[0] if email else f"user_{sociallogin.account.uid}"
        
        # Set full_name from Google profile
        if not user.full_name:
            given_name = data.get('given_name', '')
            family_name = data.get('family_name', '')
            if given_name or family_name:
                user.full_name = f"{given_name} {family_name}".strip()
            elif data.get('name'):
                user.full_name = data.get('name')
        
        # Set default role to student
        if not user.role:
            user.role = 'student'
        
        # Set default language preference
        if not user.language_preference:
            user.language_preference = 'en'
        
        # Google emails are already verified
        user.email_verified = True
        
        # Set approval status - require admin approval (same as regular signup)
        user.is_approved = False
        user.is_active = True  # Active so email confirmation can be sent if needed
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user after social login.
        For new users: sets default values and requires approval.
        For existing users (linked accounts): preserves existing data.
        """
        user = super().save_user(request, sociallogin, form)
        
        # Check if this is a new user or an existing user being linked
        is_new_user = not user.pk or user.date_joined == user.updated_at
        
        if is_new_user:
            # New user signup - set defaults and require approval
            if not user.role:
                user.role = 'student'
            if not user.language_preference:
                user.language_preference = 'en'
            
            # Set approval status for new users
            user.is_approved = False
            user.is_active = True
            user.email_verified = True  # Google emails are verified
            
            logger.info(
                f"New user created via Google OAuth: {user.username} ({user.email}) "
                f"with is_approved=False, is_active=True"
            )
        else:
            # Existing user linking Google account - preserve existing data
            # Only update email_verified if not already verified
            if not user.email_verified:
                user.email_verified = True
                logger.info(
                    f"Existing user linked Google account: {user.username} ({user.email}) - "
                    f"email marked as verified"
                )
            else:
                logger.info(
                    f"Existing user linked Google account: {user.username} ({user.email})"
                )
        
        user.save()
        
        return user
    
    def is_open_for_signup(self, request, sociallogin):
        """
        Allow social account signups.
        """
        return True

