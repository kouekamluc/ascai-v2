"""
Forms for accounts app.
"""
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form with admin approval flow.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-all duration-200 bg-white text-gray-900 placeholder-gray-400',
            'placeholder': _('Email address'),
            'autocomplete': 'email',
            'autocorrect': 'off',
            'autocapitalize': 'none',
            'spellcheck': 'false'
        })
    )
    
    phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-all duration-200 bg-white text-gray-900 placeholder-gray-400',
            'placeholder': _('Phone number (optional)'),
            'autocomplete': 'tel',
            'autocorrect': 'off',
            'autocapitalize': 'none',
            'spellcheck': 'false'
        })
    )
    
    role = forms.ChoiceField(
        choices=[('student', _('Student')), ('mentor', _('Mentor'))],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-all duration-200 bg-white text-gray-900 appearance-none cursor-pointer'
        })
    )
    
    language_preference = forms.ChoiceField(
        choices=User.LANGUAGE_CHOICES,
        initial='en',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-all duration-200 bg-white text-gray-900 appearance-none cursor-pointer'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone', 'role', 'language_preference')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-all duration-200 bg-white text-gray-900 placeholder-gray-400',
                'placeholder': _('Username'),
                'autocomplete': 'username',
                'autocorrect': 'off',
                'autocapitalize': 'none',
                'spellcheck': 'false'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name.startswith('password'):
                # Remove help_text as we're handling validation messages manually in the template
                field.help_text = ''
                autocomplete_value = 'new-password' if field_name == 'password1' else 'new-password'
                field.widget.attrs.update({
                    'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-all duration-200 bg-white text-gray-900 placeholder-gray-400',
                    'placeholder': field.label,
                    'autocomplete': autocomplete_value,
                    'autocorrect': 'off',
                    'autocapitalize': 'none',
                    'spellcheck': 'false'
                })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_approved = False  # Require admin approval
        user.is_active = False  # Inactive until approved
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form with Tailwind styling and approval checks.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-all duration-200 bg-white text-gray-900 placeholder-gray-400',
            'placeholder': _('Username'),
            'autocomplete': 'username',
            'autocorrect': 'off',
            'autocapitalize': 'none',
            'spellcheck': 'false'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-cameroon-green focus:border-cameroon-green transition-all duration-200 bg-white text-gray-900 placeholder-gray-400',
            'placeholder': _('Password'),
            'autocomplete': 'current-password',
            'autocorrect': 'off',
            'autocapitalize': 'none',
            'spellcheck': 'false'
        })
    )
    
    def clean(self):
        """Validate credentials and check user approval status."""
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username is not None and password:
            # First try to get the user to check status before authentication
            try:
                user = User.objects.get(username=username)
                
                # Check password first to verify credentials
                if not user.check_password(password):
                    # Password is wrong
                    raise forms.ValidationError(
                        _('Invalid password. Please try again.'),
                        code='invalid_password',
                    )
                
                # Superusers bypass all checks (is_active and is_approved)
                if user.is_superuser:
                    self.user_cache = user
                    return self.cleaned_data
                
                # Check if user is active (non-superusers only)
                if not user.is_active:
                    raise forms.ValidationError(
                        _('Your account is inactive. Please contact an administrator.'),
                        code='inactive',
                    )
                
                # Check if user is approved (non-superusers only)
                if not user.is_approved:
                    raise forms.ValidationError(
                        _('Your account is pending admin approval. Please wait for approval before logging in.'),
                        code='not_approved',
                    )
                
                # Store authenticated user
                self.user_cache = user
                
            except User.DoesNotExist:
                # Try by email
                try:
                    user = User.objects.get(email=username)
                    
                    if not user.check_password(password):
                        raise forms.ValidationError(
                            _('Invalid username or password. Please check your credentials.'),
                            code='invalid_login',
                        )
                    
                    # Superusers bypass all checks (is_active and is_approved)
                    if user.is_superuser:
                        self.user_cache = user
                        return self.cleaned_data
                    
                    if not user.is_active:
                        raise forms.ValidationError(
                            _('Your account is inactive. Please contact an administrator.'),
                            code='inactive',
                        )
                    
                    if not user.is_approved:
                        raise forms.ValidationError(
                            _('Your account is pending admin approval. Please wait for approval before logging in.'),
                            code='not_approved',
                        )
                    
                    self.user_cache = user
                except User.DoesNotExist:
                    # User doesn't exist - try authentication to get standard error
                    self.user_cache = authenticate(
                        self.request,
                        username=username,
                        password=password
                    )
                    if self.user_cache is None:
                        raise forms.ValidationError(
                            _('Invalid username or password. Please check your credentials.'),
                            code='invalid_login',
                        )
            
            # Confirm login is allowed (Django's built-in check)
            self.confirm_login_allowed(self.user_cache)
        
        return self.cleaned_data
