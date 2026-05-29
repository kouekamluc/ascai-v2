"""
Allauth adapters and forms for the account lifecycle.
"""
from urllib.parse import urlencode

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.urls import reverse

from apps.core.email_utils import get_email_branding_context

from .forms import CustomLoginForm, CustomSignupForm


class CustomAccountAdapter(DefaultAccountAdapter):
    """Keeps the account flow centered on email/password and approval rules."""

    verification_sent_route_name = "account_email_verification_notice"

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

        user.is_approved = False
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
        return self._build_absolute_account_url(request=request, url=url)

    def get_reset_password_from_key_url(self, key):
        url = reverse(
            "account_reset_password_from_key",
            kwargs={"uidb36": "UID", "key": "KEY"},
        ).replace("UID-KEY", key)
        return self._build_absolute_account_url(request=self.request, url=url)

    def render_mail(self, template_prefix, email, context, headers=None):
        email_context = get_email_branding_context(request=context.get("request"))
        email_context.update(context)
        return super().render_mail(template_prefix, email, email_context, headers=headers)

    def respond_email_verification_sent(self, request, user):
        return HttpResponseRedirect(self._build_verification_sent_url(request, user))

    def get_signup_redirect_url(self, request):
        return self._build_verification_sent_url(request, getattr(request, "user", None))

    def _build_verification_sent_url(self, request, user):
        base_url = resolve_url(self.verification_sent_route_name)
        email = getattr(user, "email", "")
        if email:
            return f"{base_url}?{urlencode({'email': email})}"
        return base_url

    def _build_absolute_account_url(self, *, request, url):
        if request:
            return request.build_absolute_uri(url)

        protocol = "https" if not settings.DEBUG else "http"
        domain = getattr(settings, "SITE_URL", "").rstrip("/")
        if domain.startswith(("http://", "https://")):
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
