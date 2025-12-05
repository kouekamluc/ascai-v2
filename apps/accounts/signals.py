"""
Signals for accounts app.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
import logging

from .models import User

logger = logging.getLogger(__name__)

# Import allauth signals if available
# Signals are imported in apps.py ready() method, so allauth should be loaded by then
ALLAUTH_AVAILABLE = False
try:
    from allauth.account.signals import email_confirmed, email_address_verified
    from allauth.socialaccount.signals import social_account_added, pre_social_login
    from allauth.account.models import EmailAddress
    ALLAUTH_AVAILABLE = True
except ImportError:
    # Allauth signals not available - this is normal if allauth is not installed
    # or if signals are being imported before allauth is fully loaded
    # Signals will be registered when this module is imported from apps.py ready() method
    pass


@receiver(pre_save, sender=User)
def store_previous_approval_status(sender, instance, **kwargs):
    """
    Store the previous approval status before saving.
    This allows us to detect when is_approved changes from False to True.
    """
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            instance._previous_is_approved = old_instance.is_approved
        except User.DoesNotExist:
            instance._previous_is_approved = False
    else:
        # New user, no previous status
        instance._previous_is_approved = False


@receiver(post_save, sender=User)
def send_approval_email(sender, instance, created, **kwargs):
    """
    Send email notification when a user is approved.
    This handles both individual saves and bulk updates (if called properly).
    """
    # Check if user was just approved (changed from False to True)
    previous_status = getattr(instance, '_previous_is_approved', False)
    current_status = instance.is_approved
    
    # Only send email if:
    # 1. User was not approved before (previous_status is False)
    # 2. User is now approved (current_status is True)
    # 3. User has an email address
    # 4. This is not a new user being created with approval (to avoid duplicate emails)
    if not previous_status and current_status and instance.email:
        # Skip if this is a new user being created with approval already set
        # (they might get a welcome email separately)
        if created and current_status:
            # New user created with approval - still send the email
            pass
        elif created:
            # New user created without approval - don't send yet
            return
        
        try:
            # Get user's language preference for email
            user_language = instance.language_preference or 'en'
            
            # Get site URL from Django Sites framework
            try:
                site = Site.objects.get_current()
                site_domain = site.domain
                # Ensure we use Railway domain, not ascai.org
                if site_domain == 'ascai.org' or site_domain == 'ascailazio.org':
                    site_domain = 'ascai.up.railway.app'
                site_url = f"https://{site_domain}" if not site_domain.startswith('http') else site_domain
            except Exception:
                # Fallback to Railway domain
                site_url = getattr(settings, 'SITE_URL', 'https://ascai.up.railway.app')
            
            # Prepare email context
            context = {
                'user': instance,
                'username': instance.get_display_name(),
                'login_url': f"{site_url}/accounts/login/",
            }
            
            # Render email template
            # Try to use user's language preference, fallback to default
            try:
                email_html = render_to_string(
                    'accounts/email/account_approved.html',
                    context,
                    using='django'
                )
            except Exception as e:
                logger.warning(f"Could not render email template with user language {user_language}, using default: {e}")
                email_html = render_to_string(
                    'accounts/email/account_approved.html',
                    context,
                    using='django'
                )
            
            # Prepare plain text version
            email_text = f"""
{_('Hello')} {instance.get_display_name()},

{_('Great news! Your account has been approved by an administrator.')}

{_('You can now log in to your account and access all features of the ASCAI Lazio platform.')}

{_('Login URL')}: {context['login_url']}

{_('Thank you for your patience.')}

---
{_('ASCAI Lazio - Association of Cameroonian Students and Academics in Lazio')}
"""
            
            # Send email
            send_mail(
                subject=_('Your ASCAI Lazio Account Has Been Approved'),
                message=email_text.strip(),
                html_message=email_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
            
            logger.info(f"Approval email sent successfully to {instance.email} for user {instance.username}")
            
        except Exception as e:
            # Log error but don't fail the save operation
            logger.error(f"Failed to send approval email to {instance.email}: {str(e)}", exc_info=True)


# Signal to sync User.email_verified when EmailAddress is verified
# Only register allauth signals if allauth is available
if ALLAUTH_AVAILABLE:
    @receiver(email_confirmed)
    def update_user_email_verified(sender, request, email_address, **kwargs):
        """
        Update User.email_verified when email is confirmed via allauth.
        This ensures the User model stays in sync with EmailAddress.verified.
        """
        try:
            user = email_address.user
            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(f"Updated email_verified=True for user {user.username} after email confirmation")
        except Exception as e:
            logger.error(f"Failed to update email_verified for user {email_address.user.username}: {str(e)}", exc_info=True)
    
    @receiver(email_address_verified)
    def sync_email_verified_on_verification(sender, request, email_address, **kwargs):
        """
        Alternative signal handler for email verification.
        This is called when an email address is verified.
        """
        try:
            user = email_address.user
            if not user.email_verified:
                user.email_verified = True
                user.save(update_fields=['email_verified'])
                logger.info(f"Updated email_verified=True for user {user.username} via email_address_verified signal")
        except Exception as e:
            logger.error(f"Failed to update email_verified via email_address_verified signal: {str(e)}", exc_info=True)
    
    @receiver(social_account_added)
    def mark_email_verified_for_social_account(sender, request, sociallogin, **kwargs):
        """
        Mark email as verified when a social account (Google OAuth) is added.
        This ensures Google OAuth users don't need to verify their email.
        CRITICAL: This signal fires when social account is connected, ensuring email is verified immediately.
        """
        try:
            if sociallogin.account.provider == 'google':
                user = sociallogin.user
                if user and user.email:
                    # Force mark email as verified in EmailAddress
                    email_address, created = EmailAddress.objects.update_or_create(
                        user=user,
                        email=user.email,
                        defaults={
                            'verified': True,
                            'primary': True
                        }
                    )
                    # Force verification to True (in case defaults didn't work)
                    email_address.verified = True
                    email_address.save()
                    
                    # Mark in User model
                    user.email_verified = True
                    user.save(update_fields=['email_verified'])
                    
                    logger.info(
                        f"SIGNAL (social_account_added): FORCED email verification for Google OAuth user: {user.email} "
                        f"(email_address created={created}, verified={email_address.verified}, user.email_verified={user.email_verified})"
                    )
        except Exception as e:
            logger.error(f"Failed to mark email as verified for social account: {str(e)}", exc_info=True)
    
    # Also handle the pre_social_login signal more aggressively
    if ALLAUTH_AVAILABLE:
        try:
            from allauth.socialaccount.signals import pre_social_login
            @receiver(pre_social_login)
            def force_email_verified_before_social_login(sender, request, sociallogin, **kwargs):
                """
                CRITICAL: Force email to be verified BEFORE allauth processes the social login.
                This ensures allauth sees the email as verified and doesn't redirect to verification page.
                """
                try:
                    if sociallogin.account.provider == 'google':
                        email = sociallogin.account.extra_data.get('email')
                        if email:
                            # Mark all email addresses in sociallogin as verified
                            for email_address in sociallogin.email_addresses:
                                email_address.verified = True
                                logger.info(f"SIGNAL (pre_social_login): FORCED email verified in sociallogin: {email_address.email}")
                            
                            # If user exists, mark email as verified in database immediately
                            try:
                                user = User.objects.get(email=email)
                                EmailAddress.objects.update_or_create(
                                    user=user,
                                    email=email,
                                    defaults={
                                        'verified': True,
                                        'primary': True
                                    }
                                )
                                user.email_verified = True
                                user.save(update_fields=['email_verified'])
                                logger.info(f"SIGNAL (pre_social_login): Marked email as verified for existing user: {email}")
                            except User.DoesNotExist:
                                # User will be created, email will be marked verified in save_user
                                logger.info(f"SIGNAL (pre_social_login): User doesn't exist yet, will be created and verified")
                except Exception as e:
                    logger.error(f"Failed to force email verification in pre_social_login: {str(e)}", exc_info=True)
        except (ImportError, AttributeError):
            pass
    
    # Also handle pre_social_login signal to mark email verified even earlier
    try:
        from allauth.socialaccount.signals import pre_social_login
        @receiver(pre_social_login)
        def mark_email_verified_before_social_login(sender, request, sociallogin, **kwargs):
            """
            CRITICAL: Mark email as verified BEFORE social login completes.
            This ensures email is verified before allauth checks for verification.
            This is the EARLIEST point we can intercept, before allauth processes the callback.
            """
            try:
                if sociallogin.account.provider == 'google':
                    email = sociallogin.account.extra_data.get('email')
                    if email:
                        # CRITICAL: Mark all email addresses in sociallogin object as verified
                        # This is what allauth checks during the callback
                        for email_address in sociallogin.email_addresses:
                            email_address.verified = True
                            logger.info(f"SIGNAL (pre_social_login): FORCED email verified in sociallogin object: {email_address.email}")
                        
                        # Also check if user exists and mark in database
                        try:
                            user = User.objects.get(email=email)
                            # Mark email as verified IMMEDIATELY in database
                            email_address, created = EmailAddress.objects.update_or_create(
                                user=user,
                                email=email,
                                defaults={
                                    'verified': True,
                                    'primary': True
                                }
                            )
                            email_address.verified = True
                            email_address.save()
                            user.email_verified = True
                            user.save(update_fields=['email_verified'])
                            logger.info(
                                f"SIGNAL (pre_social_login): Marked email as verified in database BEFORE login: {email}"
                            )
                        except User.DoesNotExist:
                            # User doesn't exist yet, will be handled in save_user
                            # But we've already marked it as verified in sociallogin object
                            logger.info(f"SIGNAL (pre_social_login): User doesn't exist yet, email marked as verified in sociallogin object")
            except Exception as e:
                logger.error(f"Failed to mark email as verified in pre_social_login: {str(e)}", exc_info=True)
    except (ImportError, AttributeError):
        pass

