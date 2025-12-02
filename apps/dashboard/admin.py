"""
Admin configuration for dashboard app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    SupportTicket, TicketReply, CommunityGroup, GroupDiscussion, GroupAnnouncement, GroupFile,
    UserStorySubmission, StoryImage, EventRegistration, SavedDocument,
    StudentQuestion, OrientationSession
)


class TicketReplyInline(admin.TabularInline):
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


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'message', 'user__username', 'user__email']
    readonly_fields = ['user', 'created_at', 'updated_at']
    inlines = [TicketReplyInline]
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
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'resolved':
            from django.utils import timezone
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        """Handle formset saving - author is set in formset's save_new method."""
        formset.save()
        # Delete removed instances
        for obj in formset.deleted_objects:
            obj.delete()


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
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
class CommunityGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_public', 'created_by', 'created_at', 'member_count']
    list_filter = ['category', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['members']
    readonly_fields = ['created_at']
    
    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = _('Members')


@admin.register(GroupDiscussion)
class GroupDiscussionAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'author', 'created_at']
    list_filter = ['group', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GroupAnnouncement)
class GroupAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'author', 'is_pinned', 'created_at']
    list_filter = ['group', 'is_pinned', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at']


@admin.register(GroupFile)
class GroupFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'uploaded_by', 'uploaded_at']
    list_filter = ['group', 'uploaded_at']
    search_fields = ['title', 'description']
    readonly_fields = ['uploaded_at']


@admin.register(StoryImage)
class StoryImageAdmin(admin.ModelAdmin):
    list_display = ['caption', 'uploaded_at']
    search_fields = ['caption']
    readonly_fields = ['uploaded_at']


@admin.register(UserStorySubmission)
class UserStorySubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'status', 'is_anonymous', 'submitted_at', 'reviewed_at']
    list_filter = ['status', 'is_anonymous', 'submitted_at']
    search_fields = ['title', 'story', 'user__username']
    readonly_fields = ['user', 'submitted_at', 'reviewed_at']
    filter_horizontal = ['images']
    fieldsets = (
        (_('Story Information'), {
            'fields': ('user', 'title', 'story', 'is_anonymous', 'images', 'documents')
        }),
        (_('Review'), {
            'fields': ('status', 'admin_notes', 'reviewed_at')
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
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registration_code', 'attended', 'registered_at']
    list_filter = ['attended', 'registered_at', 'event']
    search_fields = ['user__username', 'event__title', 'registration_code']
    readonly_fields = ['registration_code', 'registered_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'event')


@admin.register(SavedDocument)
class SavedDocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'document', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'document__title']
    readonly_fields = ['saved_at']


@admin.register(StudentQuestion)
class StudentQuestionAdmin(admin.ModelAdmin):
    list_display = ['subject', 'user', 'category', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'category', 'created_at']
    search_fields = ['subject', 'question', 'user__username']
    readonly_fields = ['user', 'created_at', 'resolved_at']
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
    
    def save_model(self, request, obj, form, change):
        if change and 'is_resolved' in form.changed_data and obj.is_resolved:
            from django.utils import timezone
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(OrientationSession)
class OrientationSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_date', 'preferred_time', 'is_confirmed', 'created_at']
    list_filter = ['is_confirmed', 'created_at']
    search_fields = ['user__username', 'topics']
    readonly_fields = ['user', 'created_at']
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
