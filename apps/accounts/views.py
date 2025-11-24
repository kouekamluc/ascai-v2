"""
Views for accounts app.
"""
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import CreateView, FormView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
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
    
    def form_valid(self, form):
        """Handle valid login."""
        user = form.get_user()
        
        # Check if user is approved
        if not user.is_approved:
            messages.error(
                self.request,
                _('Your account is pending admin approval. Please wait for approval before logging in.')
            )
            return self.form_invalid(form)
        
        # Check if user is active
        if not user.is_active:
            messages.error(
                self.request,
                _('Your account is inactive. Please contact an administrator.')
            )
            return self.form_invalid(form)
        
        login(self.request, user)
        messages.success(self.request, _('Welcome back, {}!').format(user.username))
        
        # Handle HTMX requests
        if self.request.headers.get('HX-Request'):
            return JsonResponse({
                'success': True,
                'redirect': str(self.success_url)
            })
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Handle invalid form submission."""
        messages.error(self.request, _('Invalid username or password.'))
        return super().form_invalid(form)


@login_required
def profile(request):
    """User profile view."""
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })

