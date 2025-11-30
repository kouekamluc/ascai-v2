"""
Django Allauth adapters for custom user signup.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import SignupForm, LoginForm
from allauth.account.models import EmailAddress
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
        is_new_user = not user.pk
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
            
            # NOTE: Do NOT create EmailAddress here - allauth's setup_user_email will handle it
            # Creating it here causes AssertionError because allauth expects to create it itself
            # We can clean up orphaned EmailAddress records, but don't create new ones
            if is_new_user and user.email:
                # Delete any orphaned EmailAddress records that don't belong to any user
                # or belong to a different user with the same email
                # This prevents issues with email verification for re-registered emails
                EmailAddress.objects.filter(email=user.email).exclude(user=user).delete()
        
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
        Always uses the Railway domain (ascai.up.railway.app) instead of ascai.org.
        The URL is generated without language prefix since it's outside i18n_patterns.
        """
        # Generate the URL path (without language prefix since it's outside i18n_patterns)
        url = reverse("account_confirm_email", args=[emailconfirmation.key])
        
        # Log the generated URL path for debugging
        logger.info(f"Generated email confirmation URL path: {url} for key: {emailconfirmation.key[:10]}...")
        
        # Priority 1: Use request.build_absolute_uri (works when request is available)
        if request:
            absolute_url = request.build_absolute_uri(url)
            logger.info(f"Built absolute URL from request: {absolute_url}")
            # Ensure we're using Railway domain, not ascai.org
            if 'ascai.org' in absolute_url and 'railway.app' not in absolute_url:
                absolute_url = absolute_url.replace('ascai.org', 'ascai.up.railway.app')
                logger.info(f"Replaced ascai.org with Railway domain: {absolute_url}")
            return absolute_url
        
        # Priority 2: Use Railway domain from ALLOWED_HOSTS or environment
        protocol = 'https' if not settings.DEBUG else 'http'
        
        # Check for Railway domain in ALLOWED_HOSTS first
        railway_domain = None
        for host in settings.ALLOWED_HOSTS:
            if 'railway.app' in host and not host.startswith('.'):
                railway_domain = host
                break
        
        # If not found in ALLOWED_HOSTS, check environment variables
        if not railway_domain:
            from decouple import config
            railway_domain = config('RAILWAY_PUBLIC_DOMAIN', default=None)
            if not railway_domain:
                # Check ALLOWED_HOSTS again for any non-wildcard domain
                for host in settings.ALLOWED_HOSTS:
                    if not host.startswith('.') and host not in ['healthcheck.railway.app', '*']:
                        railway_domain = host
                        break
        
        # Priority 3: Fallback to Site model
        if not railway_domain:
            from django.contrib.sites.models import Site
            try:
                site = Site.objects.get_current()
                railway_domain = site.domain
            except Exception:
                pass
        
        # Priority 4: Hardcoded fallback to Railway domain
        if not railway_domain:
            railway_domain = 'ascai.up.railway.app'
            logger.warning(
                f"Could not determine domain from ALLOWED_HOSTS or Site model. "
                f"Using fallback domain: {railway_domain}"
            )
        
        # Ensure we always use Railway domain, not ascai.org
        if railway_domain == 'ascai.org' or railway_domain == 'ascailazio.org':
            railway_domain = 'ascai.up.railway.app'
            logger.info(f"Replaced {railway_domain} with Railway domain: ascai.up.railway.app")
        
        absolute_url = f"{protocol}://{railway_domain}{url}"
        logger.info(f"Final email confirmation URL: {absolute_url}")
        
        return absolute_url
    
    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Send email confirmation with proper error handling and logging.
        This ensures emails are actually sent and logs any failures.
        CRITICAL: Ensure the EmailConfirmation object is saved to the database
        before sending, as allauth sometimes creates it on-the-fly without saving.
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
        
        # Check if this is a database-backed EmailConfirmation or HMAC-based
        # HMAC-based confirmations don't have a 'pk' attribute
        has_pk = hasattr(emailconfirmation, 'pk')
        is_db_confirmation = has_pk
        
        if not is_db_confirmation:
            # HMAC-based confirmation (no database storage)
            logger.info(f"Using HMAC-based EmailConfirmation (no database storage needed)")
            logger.info(f"Confirmation key: {emailconfirmation.key[:20]}...")
        else:
            # Database-backed EmailConfirmation
            # CRITICAL FIX: Ensure EmailConfirmation is saved to database before sending
            # Allauth sometimes creates confirmations on-the-fly that aren't persisted
            if not emailconfirmation.pk:
                logger.warning(f"EmailConfirmation for {email} has no primary key! Saving it now...")
                emailconfirmation.save()
                logger.info(f"✓ Saved EmailConfirmation with key: {emailconfirmation.key[:20]}... (ID: {emailconfirmation.pk})")
            else:
                logger.info(f"EmailConfirmation already exists with key: {emailconfirmation.key[:20]}... (ID: {emailconfirmation.pk})")
            
            # Verify the confirmation exists in the database
            from allauth.account.models import EmailConfirmation
            db_confirmation = EmailConfirmation.objects.filter(pk=emailconfirmation.pk).first()
            if db_confirmation:
                logger.info(f"✓ EmailConfirmation verified in database")
            else:
                logger.error(f"✗ EmailConfirmation NOT found in database! Saving again...")
                emailconfirmation.save()
                logger.info(f"✓ Re-saved EmailConfirmation (ID: {emailconfirmation.pk})")
        
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
        
        # Skip SMTP connection test - it can cause blocking/timeout issues
        # Just try to send the email directly
        
        try:
            # Call parent method to send the email
            # The parent method will automatically call get_email_confirmation_url() 
            # and pass it to the template as 'activate_url'
            logger.info(f"Attempting to send email confirmation to {email}...")
            result = super().send_confirmation_mail(request, emailconfirmation, signup)
            
            # Verify confirmation still exists after sending (it should!)
            # Only check database if it's a database-backed confirmation
            if hasattr(emailconfirmation, 'pk') and emailconfirmation.pk:
                from allauth.account.models import EmailConfirmation
                final_check = EmailConfirmation.objects.filter(pk=emailconfirmation.pk).exists()
                logger.info(f"EmailConfirmation still in database after sending: {final_check}")
            else:
                logger.info(f"HMAC-based confirmation (no database check needed)")
            
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
    
    def send_account_already_exists_mail(self, email):
        """
        Override to prevent email sending errors from crashing the app.
        When a user tries to sign in with Google but account already exists,
        we don't want to crash if email sending fails.
        """
        try:
            logger.info(f"Attempting to send 'account already exists' email to {email}...")
            result = super().send_account_already_exists_mail(email)
            logger.info(f"SUCCESS: 'Account already exists' email sent to {email}")
            return result
        except Exception as e:
            # Log the error but don't crash the app
            logger.error(
                f"Failed to send 'account already exists' email to {email}: {str(e)}",
                exc_info=True
            )
            logger.warning(
                "Email sending failed, but login process will continue. "
                "This is likely due to SMTP blocking on Railway."
            )
            # Return None instead of raising - this prevents 500 errors
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
        CRITICAL: Mark email as verified immediately for Google OAuth users.
        """
        # If the user is already logged in, connect the social account
        if request.user.is_authenticated:
            sociallogin.connect(request, request.user)
            # Ensure email is marked as verified
            if request.user.email:
                EmailAddress.objects.update_or_create(
                    user=request.user,
                    email=request.user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                request.user.email_verified = True
                request.user.save(update_fields=['email_verified'])
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
                
                # CRITICAL: Mark email as verified immediately for existing users signing in with Google
                # This ensures they can login directly without email verification
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                logger.info(
                    f"Linked Google account to existing user: {user.email} (username: {user.username}) - "
                    f"email marked as verified for direct login"
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
                    # Mark email as verified
                    user.email_verified = True
                    user.save(update_fields=['email_verified'])
                    EmailAddress.objects.update_or_create(
                        user=user,
                        email=user.email,
                        defaults={
                            'verified': True,
                            'primary': True
                        }
                    )
    
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
        CRITICAL: Always mark Google OAuth emails as verified to bypass email verification.
        """
        # Check if user already exists before calling super
        email = sociallogin.account.extra_data.get('email', '')
        existing_user = None
        if email:
            try:
                existing_user = User.objects.get(email=email)
            except User.DoesNotExist:
                pass
        
        user = super().save_user(request, sociallogin, form)
        
        # Check if this is a new user or an existing user being linked
        is_new_user = existing_user is None
        
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
            
            # Mark email as verified in allauth's EmailAddress model
            # This prevents the "verify your email" redirect page
            if user.email:
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                logger.info(
                    f"Marked email {user.email} as verified in EmailAddress for Google OAuth user"
                )
            
            logger.info(
                f"New user created via Google OAuth: {user.username} ({user.email}) "
                f"with is_approved=False, is_active=True, email_verified=True"
            )
        else:
            # Existing user linking/signing in with Google account
            # ALWAYS mark email as verified for Google OAuth (Google emails are pre-verified)
            # This ensures existing users can login directly without email verification
            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(
                    f"Marked email_verified=True for existing Google OAuth user: {user.email}"
                )
            
            # CRITICAL: Always mark as verified in EmailAddress - bypasses email verification requirement
            # This is essential for Google OAuth users to login directly
            if user.email:
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                logger.info(
                    f"Marked EmailAddress as verified for Google OAuth user: {user.email} "
                    f"(bypasses email verification requirement for direct login)"
                )
            else:
                logger.warning(f"Google OAuth user {user.username} has no email address!")
                        defaults={
                            'verified': True,
                            'primary': True
                        }
                    )
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

