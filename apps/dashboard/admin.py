"""
Admin configuration for dashboard app.
"""
from datetime import datetime

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from config.admin import BaseAdmin, ModelAdmin, TabularInline
from .models import (
    SupportTicket, TicketReply, CommunityGroup, GroupDiscussion, GroupAnnouncement, GroupFile,
    UserStorySubmission, StoryImage, EventRegistration, EventWaitlistEntry, SavedDocument,
    StudentQuestion, OrientationSession, BureauMessage, BureauMessageReply
)
from .services import send_bureau_message_notification


class TicketReplyInline(TabularInline):
    """Inline admin for ticket replies."""
    model = TicketReply
    extra = 0
    readonly_fields = ['author', 'created_at']
    fields = ['author', 'message', 'is_admin_reply', 'created_at']
    
    def get_formset(self, request, obj=None, **kwargs):
        """Override formset to handle author field for new instances."""
        formset = super().get_formset(request, obj, **kwargs)
        user = request.user
        
        class TicketReplyFormset(formset):
            def save_new(self, form, commit=True):
                """Set author and is_admin_reply for new replies."""
                instance = super().save_new(form, commit=False)
                instance.author = user
                instance.is_admin_reply = True
                if commit:
                    instance.save()
                return instance
        
        return TicketReplyFormset


class BureauMessageReplyInline(TabularInline):
    """Read-only replies shown on bureau direct messages."""
    model = BureauMessageReply
    extra = 0
    fields = ['author', 'body', 'created_at']
    readonly_fields = ['author', 'body', 'created_at']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BureauMessage)
class BureauMessageAdmin(BaseAdmin):
    """Admin interface for direct bureau-to-user messages."""
    list_display = ['recipient', 'subject', 'sender', 'read_badge', 'email_status_badge', 'allow_reply', 'reply_count', 'created_at']
    list_filter = ['is_read', 'email_delivery_status', 'allow_reply', 'created_at']
    search_fields = ['subject', 'body', 'recipient__username', 'recipient__email', 'recipient__full_name']
    autocomplete_fields = ['recipient', 'sender']
    readonly_fields = [
        'is_read', 'read_at', 'email_sent_at', 'email_delivery_status',
        'email_delivery_error', 'created_at', 'updated_at'
    ]
    list_display_links = ['recipient', 'subject']
    inlines = [BureauMessageReplyInline]
    actions = ['resend_email_notifications', 'mark_unread', 'mark_read']
    fieldsets = (
        (_('Message'), {
            'fields': ('sender', 'recipient', 'subject', 'body', 'allow_reply')
        }),
        (_('Delivery & Read Status'), {
            'fields': ('is_read', 'read_at', 'email_sent_at', 'email_delivery_status', 'email_delivery_error')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def read_badge(self, obj):
        from django.utils.html import format_html
        if obj.is_read:
            return format_html(
                '<span style="background:#166534;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">READ</span>'
            )
        return format_html(
            '<span style="background:#b45309;color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">UNREAD</span>'
        )
    read_badge.short_description = _('Read Status')
    read_badge.admin_order_field = 'is_read'

    def reply_count(self, obj):
        return obj.replies.count()
    reply_count.short_description = _('Replies')

    def email_status_badge(self, obj):
        from django.utils.html import format_html
        colors = {
            'sent': '#166534',
            'failed': '#b91c1c',
            'skipped': '#6b7280',
            'pending': '#b45309',
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:700;">{}</span>',
            colors.get(obj.email_delivery_status, '#374151'),
            obj.get_email_delivery_status_display().upper(),
        )
    email_status_badge.short_description = _('Email')
    email_status_badge.admin_order_field = 'email_delivery_status'

    def save_model(self, request, obj, form, change):
        if not obj.sender_id:
            obj.sender = request.user
        super().save_model(request, obj, form, change)

    def mark_unread(self, request, queryset):
        updated = queryset.update(is_read=False, read_at=None)
        self.message_user(request, _('{} message(s) marked unread.').format(updated))
    mark_unread.short_description = _('Mark selected messages unread')

    def mark_read(self, request, queryset):
        updated = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, _('{} message(s) marked read.').format(updated))
    mark_read.short_description = _('Mark selected messages read')

    def resend_email_notifications(self, request, queryset):
        sent = 0
        failed = 0
        for message in queryset.select_related('recipient', 'sender'):
            try:
                sent += send_bureau_message_notification(message, request=request)
            except Exception:
                failed += 1
        if failed:
            self.message_user(
                request,
                _('{} email notification(s) sent, {} failed. Open failed records to see the delivery error.').format(sent, failed),
                level='ERROR',
            )
        else:
            self.message_user(request, _('{} email notification(s) sent.').format(sent))
    resend_email_notifications.short_description = _('Resend email notification for selected messages')


@admin.register(BureauMessageReply)
class BureauMessageReplyAdmin(ModelAdmin):
    """Admin interface for bureau message replies."""
    list_display = ['message', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['message__subject', 'author__username', 'body']
    readonly_fields = ['message', 'author', 'body', 'created_at']


@admin.register(SupportTicket)
class SupportTicketAdmin(BaseAdmin):
    list_display = ['user', 'subject', 'status_badge', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'message', 'user__username', 'user__email']
    readonly_fields = ['user', 'created_at', 'updated_at']
    inlines = [TicketReplyInline]
    list_display_links = ['user', 'subject']
    actions = ['mark_pending', 'mark_resolved', 'mark_closed']
    fieldsets = (
        (_('Ticket Information'), {
            'fields': ('user', 'subject', 'message', 'status')
        }),
        (_('Admin Response'), {
            'fields': ('admin_response', 'resolved_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with a badge indicator for open/pending tickets."""
        from django.utils.html import format_html
        if obj.status in ['open', 'pending']:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">ACTION NEEDED</span> '
                '<span>{}</span>',
                obj.get_status_display()
            )
        elif obj.status == 'resolved':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">RESOLVED</span> '
                '<span>{}</span>',
                obj.get_status_display()
            )
        return obj.get_status_display()
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'resolved':
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)

    def mark_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, _('{} ticket(s) marked pending.').format(updated))
    mark_pending.short_description = _('Mark selected tickets as pending')

    def mark_resolved(self, request, queryset):
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, _('{} ticket(s) marked resolved.').format(updated))
    mark_resolved.short_description = _('Mark selected tickets as resolved')

    def mark_closed(self, request, queryset):
        updated = queryset.update(status='closed', resolved_at=timezone.now())
        self.message_user(request, _('{} ticket(s) closed.').format(updated))
    mark_closed.short_description = _('Close selected tickets')
    
    def save_formset(self, request, form, formset, change):
        """Handle formset saving - author is set in formset's save_new method."""
        formset.save()
        # Delete removed instances
        for obj in formset.deleted_objects:
            obj.delete()
    
    def changelist_view(self, request, extra_context=None):
        """Add notification count to changelist context."""
        extra_context = extra_context or {}
        open_count = SupportTicket.objects.filter(status__in=['open', 'pending']).count()
        if open_count > 0:
            extra_context['notification_count'] = open_count
            extra_context['notification_message'] = _('{} open support ticket(s)').format(open_count)
        return super().changelist_view(request, extra_context)


@admin.register(TicketReply)
class TicketReplyAdmin(BaseAdmin):
    list_display = ['ticket', 'author', 'is_admin_reply', 'created_at']
    list_filter = ['is_admin_reply', 'created_at']
    search_fields = ['message', 'ticket__subject', 'author__username']
    readonly_fields = ['ticket', 'author', 'created_at']
    
    def save_model(self, request, obj, form, change):
        """Set is_admin_reply to True and author to current user for admin replies."""
        if not change:  # New reply
            obj.author = request.user
            obj.is_admin_reply = True
        super().save_model(request, obj, form, change)


@admin.register(CommunityGroup)
class CommunityGroupAdmin(BaseAdmin):
    list_display = ['name', 'category', 'is_public', 'featured', 'created_by', 'created_at', 'member_count', 'activity_count']
    list_filter = ['category', 'is_public', 'featured', 'created_at']
    search_fields = ['name', 'description', 'tags']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['members']
    readonly_fields = ['created_at', 'updated_at', 'member_count', 'activity_count', 'last_activity']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'category', 'description', 'cover_image')
        }),
        (_('Settings'), {
            'fields': ('is_public', 'featured', 'tags', 'rules')
        }),
        (_('Members'), {
            'fields': ('members', 'created_by')
        }),
        (_('Statistics'), {
            'fields': ('member_count', 'activity_count', 'last_activity')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def member_count(self, obj):
        return obj.member_count
    member_count.short_description = _('Members')
    
    def activity_count(self, obj):
        return obj.activity_count
    activity_count.short_description = _('Activity')


@admin.register(GroupDiscussion)
class GroupDiscussionAdmin(BaseAdmin):
    list_display = ['title', 'group', 'author', 'created_at']
    list_filter = ['group', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GroupAnnouncement)
class GroupAnnouncementAdmin(BaseAdmin):
    list_display = ['title', 'group', 'author', 'is_pinned', 'created_at']
    list_filter = ['group', 'is_pinned', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']


@admin.register(GroupFile)
class GroupFileAdmin(ModelAdmin):
    list_display = ['title', 'group', 'uploaded_by', 'uploaded_at']
    list_filter = ['group', 'uploaded_at']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at']


@admin.register(StoryImage)
class StoryImageAdmin(ModelAdmin):
    list_display = ['caption', 'uploaded_at']
    search_fields = ['caption']
    readonly_fields = ['uploaded_at']


@admin.register(UserStorySubmission)
class UserStorySubmissionAdmin(BaseAdmin):
    list_display = ['title', 'user', 'submission_type', 'status', 'featured', 'is_anonymous', 'submitted_at', 'published_date']
    list_filter = ['status', 'submission_type', 'featured', 'is_anonymous', 'submitted_at']
    search_fields = ['title', 'story', 'user__username', 'tags', 'location']
    readonly_fields = ['user', 'submitted_at', 'reviewed_at', 'published_date']
    filter_horizontal = ['images']
    fieldsets = (
        (_('Story Information'), {
            'fields': ('user', 'title', 'story', 'submission_type', 'cover_image', 'is_anonymous', 'tags', 'location')
        }),
        (_('Media'), {
            'fields': ('images', 'documents')
        }),
        (_('Review & Publication'), {
            'fields': ('status', 'featured', 'admin_notes', 'reviewed_at', 'published_date')
        }),
        (_('Timestamps'), {
            'fields': ('submitted_at',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            from django.utils import timezone
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    actions = ['approve_stories', 'decline_stories']
    
    def approve_stories(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='published', reviewed_at=timezone.now())
        self.message_user(request, _('{} stories approved.').format(updated))
    approve_stories.short_description = _('Approve selected stories')
    
    def decline_stories(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='declined', reviewed_at=timezone.now())
        self.message_user(request, _('{} stories declined.').format(updated))
    decline_stories.short_description = _('Decline selected stories')


@admin.register(EventRegistration)
class EventRegistrationAdmin(ModelAdmin):
    list_display = ['user', 'event', 'registration_code', 'attended', 'registered_at']
    list_filter = ['attended', 'registered_at', 'event']
    search_fields = ['user__username', 'event__title', 'registration_code']
    readonly_fields = ['registration_code', 'registered_at']
    actions = ['mark_attended', 'mark_not_attended']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'event')

    def mark_attended(self, request, queryset):
        updated = queryset.update(attended=True)
        self.message_user(request, _('{} registration(s) marked attended.').format(updated))
    mark_attended.short_description = _('Mark selected registrations attended')

    def mark_not_attended(self, request, queryset):
        updated = queryset.update(attended=False)
        self.message_user(request, _('{} registration(s) marked not attended.').format(updated))
    mark_not_attended.short_description = _('Mark selected registrations not attended')


@admin.register(EventWaitlistEntry)
class EventWaitlistEntryAdmin(ModelAdmin):
    list_display = ['user', 'event', 'status', 'event_capacity', 'joined_at', 'promoted_at']
    list_filter = ['status', 'joined_at', 'promoted_at', 'event']
    search_fields = ['user__username', 'user__email', 'event__title', 'notes']
    readonly_fields = ['joined_at', 'promoted_at']
    list_display_links = ['user', 'event']
    actions = ['promote_to_registration', 'mark_cancelled']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'event')

    def event_capacity(self, obj):
        capacity = obj.event.capacity
        if not capacity:
            return _('Unlimited')
        return _('{} left').format(obj.event.spots_remaining())
    event_capacity.short_description = _('Capacity')

    def promote_to_registration(self, request, queryset):
        promoted = 0
        skipped = 0
        for entry in queryset.select_related('user', 'event').filter(status='waiting').order_by('joined_at'):
            if entry.event.is_full():
                skipped += 1
                continue
            EventRegistration.objects.get_or_create(user=entry.user, event=entry.event)
            entry.status = 'promoted'
            entry.promoted_at = timezone.now()
            entry.save(update_fields=['status', 'promoted_at'])
            promoted += 1
        message = _('{} waitlist entry/entries promoted to registration.').format(promoted)
        if skipped:
            message = '{} {}'.format(message, _('{} skipped because the event is full.').format(skipped))
        self.message_user(request, message)
    promote_to_registration.short_description = _('Promote selected waiting users to registration')

    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, _('{} waitlist entry/entries cancelled.').format(updated))
    mark_cancelled.short_description = _('Cancel selected waitlist entries')


@admin.register(SavedDocument)
class SavedDocumentAdmin(ModelAdmin):
    list_display = ['user', 'document', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'document__title']
    readonly_fields = ['saved_at']


@admin.register(StudentQuestion)
class StudentQuestionAdmin(BaseAdmin):
    list_display = ['subject', 'user', 'category', 'resolution_badge', 'created_at']
    list_filter = ['is_resolved', 'category', 'created_at']
    search_fields = ['subject', 'question', 'user__username']
    readonly_fields = ['user', 'created_at', 'resolved_at']
    list_display_links = ['subject', 'user']
    actions = ['mark_resolved', 'mark_unresolved']
    fieldsets = (
        (_('Question'), {
            'fields': ('user', 'subject', 'question', 'category')
        }),
        (_('Response'), {
            'fields': ('admin_response', 'is_resolved', 'resolved_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def resolution_badge(self, obj):
        """Display resolution status with a badge indicator."""
        from django.utils.html import format_html
        if not obj.is_resolved:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">UNRESOLVED</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">RESOLVED</span>'
            )
    resolution_badge.short_description = _('Status')
    resolution_badge.admin_order_field = 'is_resolved'
    
    def save_model(self, request, obj, form, change):
        if change and 'is_resolved' in form.changed_data and obj.is_resolved:
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)

    def mark_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now())
        self.message_user(request, _('{} student question(s) marked resolved.').format(updated))
    mark_resolved.short_description = _('Mark selected questions resolved')

    def mark_unresolved(self, request, queryset):
        updated = queryset.update(is_resolved=False, resolved_at=None)
        self.message_user(request, _('{} student question(s) reopened.').format(updated))
    mark_unresolved.short_description = _('Reopen selected questions')
    
    def changelist_view(self, request, extra_context=None):
        """Add notification count to changelist context."""
        extra_context = extra_context or {}
        unresolved_count = StudentQuestion.objects.filter(is_resolved=False).count()
        if unresolved_count > 0:
            extra_context['notification_count'] = unresolved_count
            extra_context['notification_message'] = _('{} unresolved student question(s)').format(unresolved_count)
        return super().changelist_view(request, extra_context)


@admin.register(OrientationSession)
class OrientationSessionAdmin(ModelAdmin):
    list_display = ['user', 'preferred_date', 'preferred_time', 'confirmation_badge', 'created_at']
    list_filter = ['is_confirmed', 'created_at']
    search_fields = ['user__username', 'topics']
    readonly_fields = ['user', 'created_at']
    autocomplete_fields = ['user']
    list_display_links = ['user', 'preferred_date']
    actions = ['confirm_for_preferred_slot', 'mark_unconfirmed']
    fieldsets = (
        (_('Session Request'), {
            'fields': ('user', 'preferred_date', 'preferred_time', 'topics')
        }),
        (_('Confirmation'), {
            'fields': ('is_confirmed', 'confirmed_date', 'notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def confirmation_badge(self, obj):
        """Display confirmation status with a badge indicator."""
        from django.utils.html import format_html
        if not obj.is_confirmed:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">NEW BOOKING</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">CONFIRMED</span>'
            )
    confirmation_badge.short_description = _('Status')
    confirmation_badge.admin_order_field = 'is_confirmed'

    def save_model(self, request, obj, form, change):
        if obj.is_confirmed and not obj.confirmed_date:
            obj.confirmed_date = timezone.now()
        elif not obj.is_confirmed:
            obj.confirmed_date = None
        super().save_model(request, obj, form, change)

    def confirm_for_preferred_slot(self, request, queryset):
        confirmed = 0
        for session in queryset:
            preferred_dt = datetime.combine(session.preferred_date, session.preferred_time)
            if timezone.is_naive(preferred_dt):
                preferred_dt = timezone.make_aware(preferred_dt, timezone.get_current_timezone())
            session.is_confirmed = True
            session.confirmed_date = preferred_dt
            session.save(update_fields=['is_confirmed', 'confirmed_date'])
            confirmed += 1
        self.message_user(request, _('{} orientation session(s) confirmed.').format(confirmed))
    confirm_for_preferred_slot.short_description = _('Confirm selected sessions for preferred slot')

    def mark_unconfirmed(self, request, queryset):
        updated = queryset.update(is_confirmed=False, confirmed_date=None)
        self.message_user(request, _('{} orientation session(s) marked unconfirmed.').format(updated))
    mark_unconfirmed.short_description = _('Mark selected sessions unconfirmed')
    
    def changelist_view(self, request, extra_context=None):
        """Add notification count to changelist context."""
        extra_context = extra_context or {}
        unconfirmed_count = OrientationSession.objects.filter(is_confirmed=False).count()
        if unconfirmed_count > 0:
            extra_context['notification_count'] = unconfirmed_count
            extra_context['notification_message'] = _('{} unconfirmed orientation session(s)').format(unconfirmed_count)
        return super().changelist_view(request, extra_context)
