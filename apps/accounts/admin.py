"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from allauth.account.models import EmailAddress
import logging

from .models import User, UserDocument

logger = logging.getLogger(__name__)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    """
    list_display = ['username', 'email', 'full_name', 'role', 'is_approved', 'email_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_approved', 'email_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'full_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('ASCAI Lazio Information'), {
            'fields': ('role', 'phone', 'bio', 'avatar', 'language_preference', 'is_approved')
        }),
        (_('Extended Profile'), {
            'fields': (
                'full_name', 'city_in_lazio', 'university', 'field_of_study',
                'profession', 'occupation', 'arrival_year', 'date_of_birth',
                'email_verified', 'notification_preferences'
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('ASCAI Lazio Information'), {
            'fields': ('role', 'phone', 'language_preference', 'is_approved')
        }),
    )
    
    actions = ['approve_users', 'reject_users', 'verify_emails', 'mark_emails_unverified', 'resend_verification_emails']
    
    def save_model(self, request, obj, form, change):
        """Override save to auto-approve superusers and staff."""
        # Store previous approval status to detect changes
        was_approved = False
        if change and obj.pk:
            try:
                old_obj = User.objects.get(pk=obj.pk)
                was_approved = old_obj.is_approved
            except User.DoesNotExist:
                pass
        
        # Superusers must always be staff and active
        if obj.is_superuser:
            obj.is_staff = True
            obj.is_active = True
            obj.is_approved = True
        elif obj.is_staff:
            obj.is_active = True
            obj.is_approved = True
        
        super().save_model(request, obj, form, change)
        
        # Send approval email if status changed from False to True
        # (The signal will handle this, but we ensure it works here too)
        if change and not was_approved and obj.is_approved and obj.email:
            try:
                self._send_approval_email(obj)
            except Exception as e:
                logger.error(f"Failed to send approval email in admin save: {str(e)}", exc_info=True)
    
    def approve_users(self, request, queryset):
        """Approve selected users and activate them."""
        # Get users who were not approved before (to send emails only to newly approved)
        # Store their IDs and emails before update
        users_to_approve = list(queryset.filter(is_approved=False).values_list('id', 'email'))
        
        # Update all selected users
        updated = queryset.update(is_approved=True, is_active=True)
        
        # Send approval emails to users who were just approved
        # We need to refetch users after update since queryset.update() doesn't refresh objects
        emails_sent = 0
        for user_id, user_email in users_to_approve:
            if user_email:
                try:
                    # Refetch the user to get updated data
                    user = User.objects.get(pk=user_id)
                    self._send_approval_email(user)
                    emails_sent += 1
                except User.DoesNotExist:
                    logger.warning(f"User with id {user_id} not found after approval update")
                except Exception as e:
                    logger.error(f"Failed to send approval email to {user_email}: {str(e)}", exc_info=True)
        
        message = f'{updated} user(s) approved and activated successfully.'
        if emails_sent > 0:
            message += f' {emails_sent} approval email(s) sent.'
        self.message_user(request, message)
    approve_users.short_description = _('Approve selected users')
    
    def _send_approval_email(self, user):
        """Helper method to send approval email to a user."""
        if not user.email:
            return
        
        try:
            # Get site URL from Django Sites framework
            try:
                site = Site.objects.get_current()
                site_url = f"https://{site.domain}" if not site.domain.startswith('http') else site.domain
            except Exception:
                # Fallback if Site framework not configured
                site_url = getattr(settings, 'SITE_URL', 'https://ascailazio.org')
            
            login_url = f"{site_url}/accounts/login/"
            context = {
                'user': user,
                'username': user.get_display_name(),
                'login_url': login_url,
            }
            
            # Render email template
            email_html = render_to_string(
                'accounts/email/account_approved.html',
                context,
                using='django'
            )
            
            # Prepare plain text version
            email_text = f"""
{_('Hello')} {user.get_display_name()},

{_('Great news! Your account has been approved by an administrator.')}

{_('You can now log in to your account and access all features of the ASCAI Lazio platform.')}

{_('Login URL')}: {login_url}

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
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            logger.info(f"Approval email sent successfully to {user.email} for user {user.username}")
            
        except Exception as e:
            logger.error(f"Failed to send approval email to {user.email}: {str(e)}", exc_info=True)
            raise
    
    def reject_users(self, request, queryset):
        """Reject selected users."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} user(s) rejected.')
    reject_users.short_description = _('Reject selected users')

    def verify_emails(self, request, queryset):
        """Mark selected users' emails as verified (including allauth records)."""
        updated = queryset.update(email_verified=True)
        for user in queryset:
            if not user.email:
                continue
            EmailAddress.objects.filter(user=user).exclude(email=user.email).update(primary=False)
            EmailAddress.objects.update_or_create(
                user=user,
                email=user.email,
                defaults={'verified': True, 'primary': True}
            )
        self.message_user(request, f'{updated} user email(s) marked as verified.')
    verify_emails.short_description = _('Verify selected user emails')

    def mark_emails_unverified(self, request, queryset):
        """Mark selected users' emails as unverified."""
        updated = queryset.update(email_verified=False)
        EmailAddress.objects.filter(user__in=queryset).update(verified=False)
        self.message_user(request, f'{updated} user email(s) marked as unverified.')
    mark_emails_unverified.short_description = _('Unverify selected user emails')
    
    def resend_verification_emails(self, request, queryset):
        """
        Resend verification emails to selected users.
        Supports unlimited resends - always deletes old confirmations before creating new ones.
        Can be called multiple times without restrictions.
        """
        from allauth.account.models import EmailConfirmation
        from allauth.account.adapter import get_adapter
        
        adapter = get_adapter(request)
        emails_sent = 0
        errors = []
        
        for user in queryset:
            if not user.email:
                continue
            
            try:
                # Get or create EmailAddress for the user
                email_address, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': False,
                        'primary': True
                    }
                )
                
                # Reset to unverified if it was already verified (allows resending)
                if not created and email_address.verified:
                    email_address.verified = False
                    email_address.save()
                    logger.info(f"Reset EmailAddress verification status for {user.email} to allow resend")
                
                # IMPORTANT: Delete ALL old email confirmations FIRST
                # This ensures unlimited resends - no restrictions on how many times this can be called
                deleted_count = EmailConfirmation.objects.filter(email_address=email_address).delete()[0]
                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} old email confirmation(s) for {user.email} before creating new one")
                
                # Create new email confirmation (this will always work since we deleted old ones)
                emailconfirmation = EmailConfirmation.create(email_address)
                
                # Send the confirmation email
                adapter.send_confirmation_mail(request, emailconfirmation, signup=False)
                
                emails_sent += 1
                logger.info(f"Verification email resent to {user.email} for user {user.username} (unlimited resends allowed)")
                
            except Exception as e:
                error_msg = f"Failed to resend verification email to {user.email}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(user.email)
        
        # Build success message
        message = f'Verification email(s) sent to {emails_sent} user(s).'
        if errors:
            message += f' Failed to send to: {", ".join(errors[:5])}'
            if len(errors) > 5:
                message += f' (and {len(errors) - 5} more)'
        
        self.message_user(request, message)
    resend_verification_emails.short_description = _('Resend verification emails to selected users (unlimited resends)')


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    """Admin interface for user documents."""
    list_display = ['user', 'document_type', 'is_verified', 'uploaded_at']
    list_filter = ['document_type', 'is_verified', 'uploaded_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'uploaded_at']
    fieldsets = (
        (_('Document Information'), {
            'fields': ('user', 'document_type', 'file', 'is_verified', 'notes')
        }),
        (_('Timestamps'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_documents', 'unverify_documents']
    
    def verify_documents(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, _('{} documents verified.').format(updated))
    verify_documents.short_description = _('Verify selected documents')
    
    def unverify_documents(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, _('{} documents unverified.').format(updated))
    unverify_documents.short_description = _('Unverify selected documents')

