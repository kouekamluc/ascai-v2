"""
Views for accounts app.
"""
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _, get_language
from django.conf import settings
from django.http import JsonResponse
from allauth.account.views import ConfirmEmailView, EmailVerificationSentView
from allauth.account.models import EmailConfirmation, EmailAddress
from allauth.socialaccount.views import SignupView as SocialSignupView, OAuthCallbackView
from allauth.socialaccount.views import ConnectionsView
from allauth.socialaccount.models import SocialAccount
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User
import logging

logger = logging.getLogger(__name__)


class RegisterView(CreateView):
    """
    User registration view with admin approval flow.
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:register_success')
    
    def form_valid(self, form):
        """Handle valid form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Registration successful! Your account is pending admin approval. You will receive an email when your account is approved.')
        )
        return response


def register_success(request):
    """Display registration success message."""
    return render(request, 'accounts/register_success.html')


class LoginView(FormView):
    """
    User login view with HTMX support.
    """
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('core:home')
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect if user is already authenticated."""
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        """Get the success URL with proper language prefix."""
        # Get the current language from the request
        current_language = get_language()
        
        # Build the home URL based on language prefix setting
        # Since prefix_default_language=False, only non-default languages get prefix
        if current_language != settings.LANGUAGE_CODE:
            # Non-default language: add language prefix
            return f'/{current_language}/'
        else:
            # Default language: no prefix
            return '/'
    
    def form_valid(self, form):
        """Handle valid login."""
        user = form.get_user()
        
        # Authenticate the user
        login(self.request, user)
        messages.success(self.request, _('Welcome back, {}!').format(user.username))
        
        # Redirect to dashboard if approved, otherwise home
        if user.is_approved or user.is_superuser:
            redirect_url = '/dashboard/'
            current_language = get_language()
            if current_language != settings.LANGUAGE_CODE:
                redirect_url = f'/{current_language}/dashboard/'
        else:
            # Get the redirect URL with proper language prefix
            redirect_url = self.get_success_url()
        
        # Handle HTMX requests
        if self.request.headers.get('HX-Request'):
            return JsonResponse({
                'success': True,
                'redirect': redirect_url
            })
        
        return redirect(redirect_url)
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        # Error messages are already added by the form's clean method
        return super().form_invalid(form)


@login_required
def profile(request):
    """User profile view."""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })


class CustomConfirmEmailView(ConfirmEmailView):
    """
    Custom email confirmation view that shows a styled success page.
    Handles both GET and POST requests to show the confirmation form and success page.
    """
    def get(self, *args, **kwargs):
        """Handle GET request - show confirmation form using our styled template."""
        # Log the key being used
        key = kwargs.get('key', 'NO KEY PROVIDED')
        logger.info(f"CustomConfirmEmailView GET: Received confirmation key: {key[:20]}... (length: {len(key)})")
        
        try:
            # Try to find the confirmation directly to debug
            from allauth.account.models import EmailConfirmation
            try:
                confirmation_query = EmailConfirmation.objects.filter(key=key)
                logger.info(f"CustomConfirmEmailView: Found {confirmation_query.count()} confirmation(s) with key {key[:20]}...")
                
                if confirmation_query.exists():
                    confirmation_obj = confirmation_query.first()
                    logger.info(f"CustomConfirmEmailView: Confirmation details - Email: {confirmation_obj.email_address.email}, "
                              f"Created: {confirmation_obj.created}, Verified: {confirmation_obj.email_address.verified}")
                else:
                    logger.warning(f"CustomConfirmEmailView: No EmailConfirmation found in database for key: {key[:20]}...")
                    # Check if there are any confirmations at all
                    all_confirmations = EmailConfirmation.objects.all()[:5]
                    logger.info(f"CustomConfirmEmailView: Sample of existing confirmation keys: "
                              f"{[c.key[:20] + '...' for c in all_confirmations]}")
            except Exception as e:
                logger.error(f"CustomConfirmEmailView: Error querying EmailConfirmation: {str(e)}", exc_info=True)
            
            # Get the confirmation object using parent's method
            self.object = self.get_object()
            
            if self.object is None:
                logger.warning(f"CustomConfirmEmailView: get_object() returned None for key: {key[:20]}...")
                return render(self.request, 'account/email_confirm.html', {
                    'confirmation': None
                })
            
            logger.info(f"CustomConfirmEmailView: Found confirmation for email: {self.object.email_address.email}")
            
            # Check if email is already verified
            if self.object.email_address.verified:
                # If already verified, show success page
                logger.info(f"CustomConfirmEmailView: Email {self.object.email_address.email} already verified, showing success page")
                return render(self.request, 'account/email_confirmed.html', {
                    'email_address': self.object.email_address,
                    'user': self.object.email_address.user
                })
            
            # Render our styled template (works for both valid confirmation and invalid/None)
            return render(self.request, 'account/email_confirm.html', {
                'confirmation': self.object
            })
        except Exception as e:
            logger.error(f"CustomConfirmEmailView GET error: {str(e)}", exc_info=True)
            return render(self.request, 'account/email_confirm.html', {
                'confirmation': None
            })
    
    def post(self, *args, **kwargs):
        """Handle email confirmation POST request."""
        # Get the confirmation object before processing
        self.object = self.get_object()
        
        if not self.object:
            # If no confirmation object, show our styled error page
            logger.warning("CustomConfirmEmailView: No confirmation object found for POST request")
            return render(self.request, 'account/email_confirm.html', {
                'confirmation': None
            })
        
        # Store the email address and its initial verified status
        email_address = self.object.email_address
        was_verified_before = email_address.verified
        
        logger.info(
            f"CustomConfirmEmailView: Processing email confirmation for {email_address.email} "
            f"(currently verified: {was_verified_before})"
        )
        
        # Call parent method to confirm email
        try:
            response = super().post(*args, **kwargs)
        except Exception as e:
            logger.error(f"CustomConfirmEmailView: Error during email confirmation: {str(e)}", exc_info=True)
            # Show our styled error page instead of AllAuth's default
            return render(self.request, 'account/email_confirm.html', {
                'confirmation': None
            })
        
        # Refresh the email address to get updated verification status
        email_address.refresh_from_db()
        
        logger.info(
            f"CustomConfirmEmailView: Email confirmation processed. "
            f"Email verified: {email_address.verified} (was: {was_verified_before})"
        )
        
        # Update User.email_verified field if email was just verified
        if email_address.verified and not was_verified_before:
            user = email_address.user
            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(f"Updated email_verified=True for user {user.username} after email confirmation")
        
        # If confirmation was successful (email is now verified), show styled success page
        if email_address.verified and not was_verified_before:
            logger.info(f"CustomConfirmEmailView: Showing styled success page for {email_address.email}")
            # Return our styled success page instead of redirect
            return render(self.request, 'account/email_confirmed.html', {
                'email_address': email_address,
                'user': email_address.user
            })
        
        # If already verified, also show success page
        if email_address.verified:
            logger.info(f"CustomConfirmEmailView: Email {email_address.email} was already verified, showing success page")
            return render(self.request, 'account/email_confirmed.html', {
                'email_address': email_address,
                'user': email_address.user
            })
        
        # Otherwise, return the parent's response (for errors, etc.)
        logger.debug("CustomConfirmEmailView: Returning parent's response")
        return response


def resend_verification_email(request):
    """
    Allow users to resend verification emails.
    Can be accessed by authenticated users who haven't verified their email,
    or by providing an email address (for unauthenticated users who just signed up).
    Supports unlimited resends - always deletes old confirmations before creating new ones.
    """
    from allauth.account.models import EmailAddress, EmailConfirmation
    from allauth.account.adapter import get_adapter
    
    adapter = get_adapter(request)
    
    # Handle both GET and POST requests
    if request.method == 'POST':
        email = request.POST.get('email')
    else:
        email = request.GET.get('email')
    
    # If user is authenticated, redirect them to allauth's email management page
    # This is the recommended way as it uses allauth's built-in functionality
    if request.user.is_authenticated:
        messages.info(request, _('Please use the email management page to resend verification emails.'))
        return redirect('account_email')
        
    else:
        # For unauthenticated users, email is required
        if not email:
            messages.error(request, _('Please provide an email address.'))
            return redirect('account_email_verification_sent')
        
        try:
            user = User.objects.get(email=email)
            # Don't allow resending for verified emails
            try:
                email_address = EmailAddress.objects.get(user=user, email=email)
                if email_address.verified:
                    messages.info(request, _('This email address is already verified. Please log in.'))
                    return redirect('account_login')
            except EmailAddress.DoesNotExist:
                pass
        except User.DoesNotExist:
            messages.error(request, _('No account found with this email address.'))
            return redirect('account_login')
        except User.MultipleObjectsReturned:
            # Shouldn't happen with unique emails, but handle it
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, _('No account found with this email address.'))
                return redirect('account_login')
    
    # Get or create EmailAddress
    email_address, created = EmailAddress.objects.get_or_create(
        user=user,
        email=email,
        defaults={
            'verified': False,
            'primary': True
        }
    )
    
    # Ensure it's marked as unverified (allows resending even if it was verified)
    if email_address.verified:
        email_address.verified = False
        email_address.save()
        logger.info(f"Reset EmailAddress verification status for {email} to allow resend")
    
    try:
        # IMPORTANT: Delete ALL old email confirmations for this email address FIRST
        # This ensures we can always create a new one and send it, regardless of how many
        # times this has been called. No rate limiting - unlimited resends allowed.
        deleted_count = EmailConfirmation.objects.filter(email_address=email_address).delete()[0]
        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} old email confirmation(s) for {email} before creating new one")
        
        # Create new email confirmation
        emailconfirmation = EmailConfirmation.create(email_address)
        # EmailConfirmation.create() saves automatically, but let's verify
        if not emailconfirmation.pk:
            emailconfirmation.save()
        logger.info(
            f"Created EmailConfirmation for {email} - "
            f"Key: {emailconfirmation.key[:20]}..., "
            f"ID: {emailconfirmation.pk}, "
            f"Created: {emailconfirmation.created}"
        )
        
        # Verify it exists in the database
        db_confirmation = EmailConfirmation.objects.filter(pk=emailconfirmation.pk).first()
        if db_confirmation:
            logger.info(f"✓ EmailConfirmation verified in database with key: {db_confirmation.key[:20]}...")
        else:
            logger.error(f"✗ EmailConfirmation NOT found in database after creation!")
        
        # Send the confirmation email using the adapter
        adapter.send_confirmation_mail(request, emailconfirmation, signup=False)
        
        messages.success(
            request,
            _('Verification email has been sent to {}. Check your inbox and spam folder.').format(email)
        )
        logger.info(f"Verification email resent to {email} for user {user.username} (unlimited resends allowed)")
        
    except Exception as e:
        logger.error(f"Failed to resend verification email to {email}: {str(e)}", exc_info=True)
        messages.error(
            request,
            _('Failed to send verification email. Please try again later or contact support.')
        )
    
    # Redirect to email verification sent page
    redirect_url = 'account_email_verification_sent'
    if not request.user.is_authenticated and email:
        # Add email to query string for unauthenticated users
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        url = reverse(redirect_url)
        return HttpResponseRedirect(f"{url}?email={email}")
    
    return redirect(redirect_url)


class CustomSocialSignupView(SocialSignupView):
    """
    Custom social signup view that ensures Google OAuth users bypass email verification.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to mark email as verified for Google OAuth users before processing.
        """
        # Check if this is a Google OAuth login
        if request.user.is_authenticated:
            user = request.user
            # Check if user has a Google social account
            has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
            
            if has_google_account and user.email:
                # Force mark email as verified
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(f"CUSTOM VIEW: Marked email as verified for Google OAuth user: {user.email}")
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Override form_valid to ensure email is verified before redirect.
        """
        response = super().form_valid(form)
        
        # After form is valid, ensure email is verified for Google OAuth users
        if self.request.user.is_authenticated:
            user = self.request.user
            has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
            
            if has_google_account and user.email:
                # Force mark email as verified
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(f"CUSTOM VIEW form_valid: Marked email as verified for Google OAuth user: {user.email}")
        
        return response


class CustomConnectionsView(ConnectionsView):
    """
    Custom connections view that ensures Google OAuth users bypass email verification.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to mark email as verified for Google OAuth users.
        """
        if request.user.is_authenticated:
            user = request.user
            has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
            
            if has_google_account and user.email:
                # Force mark email as verified
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(f"CUSTOM CONNECTIONS VIEW: Marked email as verified for Google OAuth user: {user.email}")
        
        return super().dispatch(request, *args, **kwargs)


class CustomOAuthCallbackView(OAuthCallbackView):
    """
    Custom OAuth callback view that bypasses email verification for Google OAuth users.
    This intercepts the OAuth callback and ensures email verification is skipped.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to handle Google OAuth callbacks and bypass email verification.
        """
        # Get the provider from the request
        provider = kwargs.get('provider', '')
        
        # For Google OAuth, mark email as verified before processing
        if provider == 'google':
            logger.info(f"CUSTOM OAUTH CALLBACK: Intercepting Google OAuth callback")
        
        # Call parent dispatch to process the callback
        response = super().dispatch(request, *args, **kwargs)
        
        # After callback processing, if user is authenticated and has Google account,
        # ensure email is verified and redirect appropriately
        if request.user.is_authenticated and provider == 'google':
            user = request.user
            has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
            
            if has_google_account and user.email:
                # Force mark email as verified
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(f"CUSTOM OAUTH CALLBACK: Marked email as verified for Google OAuth user: {user.email}")
                
                # If response is a redirect to email verification, redirect to dashboard instead
                if hasattr(response, 'url') and 'confirm-email' in response.url:
                    if user.is_approved or user.is_superuser:
                        current_language = get_language()
                        if current_language != settings.LANGUAGE_CODE:
                            return redirect(f'/{current_language}/dashboard/')
                        return redirect('/dashboard/')
                    else:
                        return redirect('/')
        
        return response


def email_verification_required_view(request):
    """
    View to handle /accounts/confirm-email/ route (without key).
    This is called by allauth when email verification is required.
    For Google OAuth users, we bypass email verification and redirect to dashboard.
    Note: User might not be authenticated yet when this view is called after social login callback.
    """
    # If user is authenticated, check if they have Google OAuth and redirect
    if request.user.is_authenticated:
        user = request.user
        # Check if user has a Google social account
        has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
        
        if has_google_account:
            # For Google OAuth users, mark email as verified and redirect to dashboard
            if user.email:
                # Force mark email as verified
                EmailAddress.objects.update_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': True,
                        'primary': True
                    }
                )
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(
                    f"EMAIL_VERIFICATION_REQUIRED_VIEW: Bypassed email verification for Google OAuth user: {user.email}"
                )
            
            # Redirect to dashboard instead of showing email verification page
            if user.is_approved or user.is_superuser:
                current_language = get_language()
                if current_language != settings.LANGUAGE_CODE:
                    return redirect(f'/{current_language}/dashboard/')
                return redirect('/dashboard/')
            else:
                return redirect('/')
    
    # If user is not authenticated, redirect to login
    # They'll be redirected back here after login, and we'll handle it then
    return redirect('account_login')


class CustomEmailVerificationSentView(EmailVerificationSentView):
    """
    Custom email verification sent view that redirects Google OAuth users directly to dashboard.
    This view is called when allauth wants to show the email verification page.
    For Google OAuth users, we bypass this and redirect to dashboard instead.
    """
    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch to check if user has Google OAuth and redirect accordingly.
        """
        if request.user.is_authenticated:
            user = request.user
            # Check if user has a Google social account
            has_google_account = SocialAccount.objects.filter(user=user, provider='google').exists()
            
            if has_google_account:
                # For Google OAuth users, mark email as verified and redirect to dashboard
                if user.email:
                    # Force mark email as verified
                    EmailAddress.objects.update_or_create(
                        user=user,
                        email=user.email,
                        defaults={
                            'verified': True,
                            'primary': True
                        }
                    )
                    user.email_verified = True
                    user.save(update_fields=['email_verified'])
                    logger.info(
                        f"CUSTOM EMAIL VERIFICATION VIEW: Bypassed email verification for Google OAuth user: {user.email}"
                    )
                
                # Redirect to dashboard instead of showing email verification page
                if user.is_approved or user.is_superuser:
                    current_language = get_language()
                    if current_language != settings.LANGUAGE_CODE:
                        return redirect(f'/{current_language}/dashboard/')
                    return redirect('/dashboard/')
                else:
                    return redirect('/')
        
        # For regular users, show the email verification page
        return super().dispatch(request, *args, **kwargs)

