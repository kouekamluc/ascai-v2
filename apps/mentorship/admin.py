"""
Admin configuration for mentorship app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import MentorProfile, MentorshipRequest, MentorshipMessage, MentorRating


@admin.register(MentorProfile)
class MentorProfileAdmin(ModelAdmin):
    """Admin interface for MentorProfile."""
    list_display = ['user', 'specialization', 'is_approved', 'availability_status', 'rating', 'students_helped']
    list_filter = ['is_approved', 'availability_status']
    search_fields = ['user__username', 'specialization', 'bio']
    raw_id_fields = ['user']
    actions = ['approve_mentors']
    
    def approve_mentors(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} mentor(s) approved.')
    approve_mentors.short_description = _('Approve selected mentors')


@admin.register(MentorshipRequest)
class MentorshipRequestAdmin(ModelAdmin):
    """Admin interface for MentorshipRequest."""
    list_display = ['student', 'mentor', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['student__username', 'mentor__user__username', 'subject']
    raw_id_fields = ['student', 'mentor']


@admin.register(MentorshipMessage)
class MentorshipMessageAdmin(ModelAdmin):
    """Admin interface for MentorshipMessage."""
    list_display = ['request', 'sender', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__username']
    raw_id_fields = ['request', 'sender']


@admin.register(MentorRating)
class MentorRatingAdmin(ModelAdmin):
    """Admin interface for MentorRating."""
    list_display = ['mentor', 'student', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['mentor__user__username', 'student__username', 'comment']
    raw_id_fields = ['request', 'student', 'mentor']

















