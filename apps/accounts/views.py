"""
Views for the accounts app.
"""
import logging
from urllib.parse import urlencode

from allauth.account.models import EmailAddress, EmailConfirmation, get_emailconfirmation_model
from allauth.account.views import ConfirmEmailView, EmailVerificationSentView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.urls import reverse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .models import User

logger = logging.getLogger(__name__)


@login_required
def profile(request):
    """User profile view."""
    return render(request, "accounts/profile.html", {"user": request.user})


class CustomConfirmEmailView(ConfirmEmailView):
    """
    Render branded confirmation states instead of the stock allauth pages.
    """

    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            self.object = None
        if not self.object:
            return render(self.request, "account/email_confirm.html", {"confirmation": None})

        if self.object.email_address.verified:
            return render(
                self.request,
                "account/email_confirmed.html",
                {
                    "email_address": self.object.email_address,
                    "user": self.object.email_address.user,
                },
            )

        return render(
            self.request,
            "account/email_confirm.html",
            {"confirmation": self.object},
        )

    def post(self, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            self.object = None
        if not self.object:
            return render(self.request, "account/email_confirm.html", {"confirmation": None})

        email_address = self.object.email_address
        response = super().post(*args, **kwargs)
        email_address.refresh_from_db()

        if email_address.verified:
            user = email_address.user
            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=["email_verified"])

            return render(
                self.request,
                "account/email_confirmed.html",
                {"email_address": email_address, "user": user},
            )

        return response


def resend_verification_email(request):
    """
    Resend a verification email for the provided address.
    """
    from allauth.account.adapter import get_adapter

    adapter = get_adapter(request)
    email = request.POST.get("email") if request.method == "POST" else request.GET.get("email")

    if request.user.is_authenticated:
        messages.info(
            request,
            _("Please use the email management page to resend verification emails."),
        )
        return redirect("account_email")

    if not email:
        messages.error(request, _("Please provide an email address."))
        return redirect("account_email_verification_notice")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, _("No account found with this email address."))
        return redirect("account_login")
    except User.MultipleObjectsReturned:
        user = User.objects.filter(email=email).first()

    email_address, _created = EmailAddress.objects.get_or_create(
        user=user,
        email=email,
        defaults={"verified": False, "primary": True},
    )
    if email_address.verified:
        messages.info(request, _("This email address is already verified. Please log in."))
        return redirect("account_login")

    try:
        confirmation_model = get_emailconfirmation_model()
        if confirmation_model is EmailConfirmation:
            EmailConfirmation.objects.filter(email_address=email_address).delete()
        emailconfirmation = confirmation_model.create(email_address)
        if getattr(emailconfirmation, "pk", None) is None and confirmation_model is EmailConfirmation:
            emailconfirmation.save()
        adapter.send_confirmation_mail(request, emailconfirmation, signup=False)
        messages.success(
            request,
            _("Verification email has been sent to {}. Check your inbox and spam folder.").format(
                email
            ),
        )
    except Exception as exc:
        logger.error(
            "Failed to resend verification email to %s: %s", email, exc, exc_info=True
        )
        messages.error(
            request,
            _("Failed to send verification email. Please try again later or contact support."),
        )

    return redirect(
        f"{reverse('account_email_verification_notice')}?{urlencode({'email': email})}"
    )


def email_verification_required_view(request):
    """
    Friendly fallback when allauth sends users to the bare confirm-email route.
    """
    if request.user.is_authenticated:
        messages.info(
            request,
            _(
                "Your email is not verified yet. Please check your inbox or resend the verification email."
            ),
        )
        return redirect("account_email")
    return redirect("account_login")


class CustomEmailVerificationSentView(EmailVerificationSentView):
    """Use the branded verification-sent page without any social-auth branching."""

    template_name = "account/email_verification_sent.html"
