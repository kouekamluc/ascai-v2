"""
Admin configuration for mentorship app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from config.admin import BaseAdmin, ModelAdmin
from .models import (
    MentorSpecialization, MentorProfile, MentorshipRequest,
    MentorshipMessage, MentorRating, MentorshipSession
)


@admin.register(MentorSpecialization)
class MentorSpecializationAdmin(ModelAdmin):
    """Admin interface for MentorSpecialization."""
    list_display = ['name', 'icon', 'order', 'mentor_count']
    list_filter = ['order']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    
    def mentor_count(self, obj):
        return obj.mentors.count()
    mentor_count.short_description = _('Mentors')


@admin.register(MentorProfile)
class MentorProfileAdmin(BaseAdmin):
    """Admin interface for MentorProfile."""
    list_display = ['user', 'specialization', 'approval_status_badge', 'is_approved', 'availability_status', 'rating', 'students_helped', 'success_rate', 'created_at']
    list_filter = ['is_approved', 'availability_status', 'created_at', 'specializations']
    search_fields = ['user__username', 'user__email', 'specialization', 'bio']
    raw_id_fields = ['user']
    filter_horizontal = ['specializations']
    actions = ['approve_mentors', 'reject_mentors']
    list_editable = ['is_approved']  # Allow quick approval from list view
    list_display_links = ['user', 'specialization']  # Make these clickable
    ordering = ['-created_at']  # Show newest first (unapproved will be at top)
    date_hierarchy = 'created_at'
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'specialization', 'specializations', 'years_experience', 'bio', 'profile_image')
        }),
        (_('Availability'), {
            'fields': ('availability_status', 'availability_calendar', 'response_time')
        }),
        (_('Statistics'), {
            'fields': ('rating', 'students_helped', 'success_rate')
        }),
        (_('Approval'), {
            'fields': ('is_approved',)
        }),
    )
    
    def approval_status_badge(self, obj):
        """Display approval status with a badge indicator."""
        from django.utils.html import format_html
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">✓ APPROVED</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">⚠ PENDING</span>'
            )
    approval_status_badge.short_description = _('Approval Status')
    approval_status_badge.admin_order_field = 'is_approved'
    
    def approve_mentors(self, request, queryset):
        """Approve selected mentors."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} mentor(s) approved successfully.')
    approve_mentors.short_description = _('Approve selected mentors')
    
    def reject_mentors(self, request, queryset):
        """Reject (unapprove) selected mentors."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} mentor(s) rejected.')
    reject_mentors.short_description = _('Reject selected mentors')
    
    def changelist_view(self, request, extra_context=None):
        """Add notification count for pending mentors."""
        extra_context = extra_context or {}
        pending_count = MentorProfile.objects.filter(is_approved=False).count()
        if pending_count > 0:
            extra_context['notification_count'] = pending_count
            extra_context['notification_message'] = _('⚠ {} mentor profile(s) pending approval').format(pending_count)
        return super().changelist_view(request, extra_context)
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(BaseAdmin):
    """Admin interface for MentorshipRequest."""
    list_display = ['student', 'mentor', 'subject', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__username', 'mentor__user__username', 'subject']
    raw_id_fields = ['student', 'mentor']
    list_display_links = ['student', 'subject']
    
    def status_badge(self, obj):
        """Display status with a badge indicator for pending requests."""
        from django.utils.html import format_html
        if obj.status == 'pending':
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">PENDING</span> '
                '<span>{}</span>',
                obj.get_status_display()
            )
        elif obj.status == 'accepted':
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">ACCEPTED</span> '
                '<span>{}</span>',
                obj.get_status_display()
            )
        return obj.get_status_display()
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'
    
    def changelist_view(self, request, extra_context=None):
        """Add notification count to changelist context."""
        extra_context = extra_context or {}
        pending_count = MentorshipRequest.objects.filter(status='pending').count()
        if pending_count > 0:
            extra_context['notification_count'] = pending_count
            extra_context['notification_message'] = _('{} pending mentorship request(s)').format(pending_count)
        return super().changelist_view(request, extra_context)


@admin.register(MentorshipMessage)
class MentorshipMessageAdmin(BaseAdmin):
    """Admin interface for MentorshipMessage."""
    list_display = ['request', 'sender', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__username']
    raw_id_fields = ['request', 'sender']


@admin.register(MentorRating)
class MentorRatingAdmin(BaseAdmin):
    """Admin interface for MentorRating."""
    list_display = ['mentor', 'student', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['mentor__user__username', 'student__username', 'comment']
    raw_id_fields = ['request', 'student', 'mentor']


@admin.register(MentorshipSession)
class MentorshipSessionAdmin(ModelAdmin):
    """Admin interface for MentorshipSession."""
    list_display = ['request', 'scheduled_at', 'duration', 'location', 'is_completed', 'rating', 'created_at']
    list_filter = ['is_completed', 'scheduled_at', 'created_at']
    search_fields = ['request__student__username', 'request__mentor__user__username', 'location', 'notes']
    raw_id_fields = ['request']
    date_hierarchy = 'scheduled_at'
    ordering = ['-scheduled_at']

















