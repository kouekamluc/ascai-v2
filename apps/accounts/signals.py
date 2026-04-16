"""
Signals for the accounts app.
"""
import logging

from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from apps.core.email_utils import send_branded_email

from .models import User

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=User)
def store_previous_approval_status(sender, instance, **kwargs):
    """Keep the previous approval value so we can send approval mail once."""
    if not instance.pk:
        instance._previous_is_approved = False
        return

    try:
        old_instance = User.objects.get(pk=instance.pk)
        instance._previous_is_approved = old_instance.is_approved
    except User.DoesNotExist:
        instance._previous_is_approved = False


def _build_site_url():
    try:
        site = Site.objects.get_current()
        domain = site.domain
        if domain.startswith("http://") or domain.startswith("https://"):
            return domain
        return f"https://{domain}"
    except Exception:
        return getattr(settings, "SITE_URL", "https://ascai.up.railway.app")


def _send_approval_email(user):
    if not user.email:
        return

    site_url = _build_site_url().rstrip("/")
    login_url = f"{site_url}/accounts/login/"
    context = {
        "user": user,
        "username": user.get_display_name(),
        "login_url": login_url,
    }
    email_text = f"""
{_('Hello')} {user.get_display_name()},

{_('Great news! Your account has been approved by an administrator.')}

{_('You can now log in to your account and access all features of the ASCAI Lazio platform.')}

{_('Login URL')}: {login_url}

{_('Thank you for your patience.')}
"""

    send_branded_email(
        subject=_("Your ASCAI Lazio Account Has Been Approved"),
        text_body=email_text,
        template_name="accounts/email/account_approved.html",
        context=context,
        site_url=site_url,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


@receiver(post_save, sender=User)
def send_approval_email(sender, instance, created, **kwargs):
    """Send a single approval email when a user becomes approved."""
    previous_status = getattr(instance, "_previous_is_approved", False)
    if created or previous_status or not instance.is_approved or not instance.email:
        return

    try:
        _send_approval_email(instance)
    except Exception as exc:
        logger.error(
            "Failed to send approval email to %s: %s",
            instance.email,
            exc,
            exc_info=True,
        )


@receiver(email_confirmed)
def sync_user_email_verified(sender, email_address, **kwargs):
    """Keep User.email_verified synchronized with allauth EmailAddress records."""
    try:
        user = email_address.user
        if not user.email_verified:
            user.email_verified = True
            user.save(update_fields=["email_verified"])
        EmailAddress.objects.filter(user=user, email=user.email).update(
            verified=True, primary=True
        )
    except Exception as exc:
        logger.error(
            "Failed to sync email verification for %s: %s",
            getattr(email_address, "email", "unknown"),
            exc,
            exc_info=True,
        )
