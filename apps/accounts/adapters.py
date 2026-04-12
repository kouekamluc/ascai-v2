"""
Allauth adapters and forms for the account lifecycle.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.forms import LoginForm, SignupForm
from allauth.account.models import EmailAddress
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .models import User


class CustomLoginForm(LoginForm):
    """Login form that enforces ASCAI approval rules."""

    def clean(self):
        cleaned_data = super().clean()
        login_value = cleaned_data.get("login")
        password = cleaned_data.get("password")

        if not login_value or not password:
            return cleaned_data

        try:
            user = User.objects.get(username=login_value)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=login_value)
            except User.DoesNotExist:
                return cleaned_data

        if user.is_superuser:
            return cleaned_data

        if not user.is_active:
            raise ValidationError(
                _("Your account is inactive. Please contact an administrator.")
            )

        if not user.is_approved:
            raise ValidationError(
                _(
                    "Your account is pending admin approval. Please wait for approval before logging in."
                )
            )

        return cleaned_data


class CustomSignupForm(SignupForm):
    """Signup form with the extra profile fields used on the site."""

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 focus:border-cameroon-green focus:ring-2 focus:ring-cameroon-green",
                "placeholder": _("Phone number (optional)"),
            }
        ),
        label=_("Phone Number"),
    )
    role = forms.ChoiceField(
        choices=[("student", _("Student")), ("mentor", _("Mentor"))],
        initial="student",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 focus:border-cameroon-green focus:ring-2 focus:ring-cameroon-green",
            }
        ),
        label=_("I am a"),
    )
    language_preference = forms.ChoiceField(
        choices=User.LANGUAGE_CHOICES,
        initial="en",
        widget=forms.Select(
            attrs={
                "class": "w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 focus:border-cameroon-green focus:ring-2 focus:ring-cameroon-green",
            }
        ),
        label=_("Language Preference"),
    )

    def save(self, request):
        user = super().save(request)
        user.phone = self.cleaned_data.get("phone", "")
        user.role = self.cleaned_data.get("role", "student")
        user.language_preference = self.cleaned_data.get("language_preference", "en")
        user.is_approved = True
        user.is_active = True
        user.save()
        return user


class CustomAccountAdapter(DefaultAccountAdapter):
    """Keeps the account flow centered on email/password and approval rules."""

    def get_login_form_class(self):
        return CustomLoginForm

    def get_signup_form_class(self):
        return CustomSignupForm

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)

        if hasattr(form, "cleaned_data"):
            user.phone = form.cleaned_data.get("phone", "")
            user.role = form.cleaned_data.get("role", "student")
            user.language_preference = form.cleaned_data.get(
                "language_preference", "en"
            )

        user.is_approved = True
        user.is_active = True

        if commit:
            user.save()
            if user.email:
                EmailAddress.objects.filter(email=user.email).exclude(user=user).delete()

        return user

    def is_open_for_signup(self, request):
        return True

    def is_account_active(self, user):
        if user.is_superuser:
            return True
        return user.is_active

    def get_email_confirmation_url(self, request, emailconfirmation):
        url = reverse("account_confirm_email", args=[emailconfirmation.key])

        if request:
            return request.build_absolute_uri(url)

        protocol = "https" if not settings.DEBUG else "http"
        domain = getattr(settings, "SITE_URL", "").rstrip("/")
        if domain.startswith("http://") or domain.startswith("https://"):
            return f"{domain}{url}"

        if domain:
            return f"{protocol}://{domain}{url}"

        allowed_host = next(
            (
                host
                for host in settings.ALLOWED_HOSTS
                if host not in {"*", "healthcheck.railway.app"} and not host.startswith(".")
            ),
            "ascai.up.railway.app",
        )
        return f"{protocol}://{allowed_host}{url}"
