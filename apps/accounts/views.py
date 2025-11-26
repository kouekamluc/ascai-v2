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
    """
    def post(self, *args, **kwargs):
        """Handle email confirmation POST request."""
        # Get the confirmation object before processing
        self.object = self.get_object()
        
        # Call parent method to confirm email
        response = super().post(*args, **kwargs)
        
        # If confirmation was successful, show styled success page
        # Refresh the object to get updated verification status
        if self.object:
            self.object.email_address.refresh_from_db()
            if self.object.email_address.verified:
                return render(self.request, 'account/email_confirmed.html', {
                    'email_address': self.object.email_address,
                    'user': self.object.email_address.user
                })
        
        return response

