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
from allauth.account.views import ConfirmEmailView
from allauth.account.models import EmailConfirmation
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
        # Get the confirmation object
        self.object = self.get_object()
        
        # Check if email is already verified
        if self.object and self.object.email_address.verified:
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

