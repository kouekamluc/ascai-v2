"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.sites.models import Site
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from allauth.account.models import EmailAddress
from unfold.admin import ModelAdmin
from config.admin import BaseAdmin
import logging

from apps.core.email_utils import send_branded_email

from .models import User, UserDocument

logger = logging.getLogger(__name__)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Custom admin interface for User model.
    """
    list_display = ['username', 'email', 'full_name', 'role', 'approval_badge', 'membership_badge', 'email_status_badge', 'is_active', 'date_joined']
    list_filter = ['role', 'is_approved', 'email_verified', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'full_name']
    search_help_text = _('Search by username, email, or full name.')
    list_per_page = 25
    
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
    
    actions = ['approve_users', 'approve_and_verify_users', 'create_member_profiles', 'reject_users', 'verify_emails', 'mark_emails_unverified', 'resend_verification_emails']

    def approval_badge(self, obj):
        """Show the account review state in plain language for bureau members."""
        if obj.is_approved:
            return format_html(
                '<span style="background:#166534;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">APPROVED</span>'
            )
        if not obj.is_active:
            return format_html(
                '<span style="background:#6b7280;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">INACTIVE</span>'
            )
        return format_html(
            '<span style="background:#b91c1c;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">NEEDS REVIEW</span>'
        )
    approval_badge.short_description = _('Approval')
    approval_badge.admin_order_field = 'is_approved'

    def membership_badge(self, obj):
        """Show whether this login account is connected to an association member record."""
        if obj.is_superuser:
            return format_html(
                '<span style="background:#312e81;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">ADMIN LOGIN</span>'
            )
        if obj.is_staff:
            return format_html(
                '<span style="background:#1e3a8a;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">BUREAU LOGIN</span>'
            )
        try:
            member = obj.member_profile
        except Exception:
            if obj.is_approved:
                return format_html(
                    '<span style="background:#92400e;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">NO MEMBER RECORD</span>'
                )
            return format_html(
                '<span style="background:#6b7280;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">ACCOUNT ONLY</span>'
            )

        if member.is_active_member:
            return format_html(
                '<span style="background:#166534;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">ACTIVE MEMBER</span>'
            )
        return format_html(
            '<span style="background:#1d4ed8;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">MEMBER PENDING</span>'
        )
    membership_badge.short_description = _('Membership')

    def email_status_badge(self, obj):
        """Show email state without making bureau/staff accounts look like verified members."""
        if obj.is_superuser:
            return format_html(
                '<span style="background:#312e81;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">ADMIN ACCESS</span>'
            )
        if obj.is_staff:
            return format_html(
                '<span style="background:#1e3a8a;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">BUREAU ACCESS</span>'
            )
        if obj.email_verified:
            return format_html(
                '<span style="background:#166534;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">EMAIL VERIFIED</span>'
            )
        return format_html(
            '<span style="background:#b91c1c;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">EMAIL UNVERIFIED</span>'
        )
    email_status_badge.short_description = _('Email Status')
    email_status_badge.admin_order_field = 'email_verified'
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Override to use CKEditor 5 for bio TextField."""
        from django.db import models
        from django.forms import Textarea
        try:
            from django_ckeditor_5.widgets import CKEditor5Widget
            if isinstance(db_field, models.TextField) and db_field.name == 'bio':
                kwargs['widget'] = CKEditor5Widget(config_name='default')
        except ImportError:
            pass
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
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

    def approve_and_verify_users(self, request, queryset):
        """Approve accounts and mark their current email addresses as verified."""
        self.approve_users(request, queryset)
        self.verify_emails(request, queryset)
    approve_and_verify_users.short_description = _('Approve and verify selected users')

    def create_member_profiles(self, request, queryset):
        """
        Create governance member records for selected approved and verified users.
        """
        from apps.governance.models import Member

        created = 0
        skipped = 0
        for user in queryset:
            if not user.is_approved or not user.email_verified:
                skipped += 1
                continue
            if hasattr(user, 'member_profile'):
                skipped += 1
                continue

            Member.objects.create(
                user=user,
                member_type='student' if user.role == 'student' else 'active',
                membership_start_date=timezone.now().date(),
                is_active_member=False,
            )
            created += 1

        self.message_user(
            request,
            _('{} member profile(s) created. {} user(s) skipped because they were not approved, not email verified, or already had a member profile.').format(created, skipped),
        )
    create_member_profiles.short_description = _('Create member profiles for selected approved and verified users')
    
    def _send_approval_email(self, user):
        """Helper method to send approval email to a user."""
        if not user.email:
            return
        
        try:
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
            
            login_url = f"{site_url}/accounts/login/"
            context = {
                'user': user,
                'username': user.get_display_name(),
                'login_url': login_url,
            }

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

            send_branded_email(
                subject=_('Your ASCAI Lazio Account Has Been Approved'),
                text_body=email_text,
                template_name='accounts/email/account_approved.html',
                context=context,
                site_url=site_url,
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
                
                # Create new email confirmation
                emailconfirmation = EmailConfirmation.create(email_address)
                # EmailConfirmation.create() saves automatically, but let's verify
                if not emailconfirmation.pk:
                    emailconfirmation.save()
                logger.info(
                    f"Created EmailConfirmation for {user.email} - "
                    f"Key: {emailconfirmation.key[:20]}..., "
                    f"ID: {emailconfirmation.pk}, "
                    f"Created: {emailconfirmation.created}"
                )
                
                # Verify it exists in the database
                db_confirmation = EmailConfirmation.objects.filter(pk=emailconfirmation.pk).first()
                if db_confirmation:
                    logger.info(f"✓ EmailConfirmation verified in database with key: {db_confirmation.key[:20]}...")
                else:
                    logger.error(f"✗ EmailConfirmation NOT found in database after creation!")
                
                # Send the confirmation email using the adapter
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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        pending_count = User.objects.filter(is_approved=False, is_active=True).count()
        if pending_count:
            extra_context['notification_count'] = pending_count
            extra_context['notification_message'] = _('{} account(s) waiting for approval').format(pending_count)
        return super().changelist_view(request, extra_context)


@admin.register(UserDocument)
class UserDocumentAdmin(ModelAdmin):
    """Admin interface for user documents."""
    list_display = ['user', 'document_type', 'verification_badge', 'open_file', 'uploaded_at']
    list_filter = ['document_type', 'is_verified', 'uploaded_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'uploaded_at']
    autocomplete_fields = ['user']
    list_per_page = 25
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

    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background:#166534;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">VERIFIED</span>'
            )
        return format_html(
            '<span style="background:#b91c1c;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">CHECK DOCUMENT</span>'
        )
    verification_badge.short_description = _('Verification')
    verification_badge.admin_order_field = 'is_verified'

    def open_file(self, obj):
        if not obj.file:
            return '-'
        return format_html('<a href="{}" target="_blank" rel="noopener">Open document</a>', obj.file.url)
    open_file.short_description = _('File')
    
    def verify_documents(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, _('{} documents verified.').format(updated))
    verify_documents.short_description = _('Verify selected documents')
    
    def unverify_documents(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, _('{} documents unverified.').format(updated))
    unverify_documents.short_description = _('Unverify selected documents')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        pending_count = UserDocument.objects.filter(is_verified=False).count()
        if pending_count:
            extra_context['notification_count'] = pending_count
            extra_context['notification_message'] = _('{} document(s) waiting for verification').format(pending_count)
        return super().changelist_view(request, extra_context)
