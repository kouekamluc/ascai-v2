"""
Admin configuration for contact app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(ModelAdmin):
    """Admin interface for ContactSubmission."""
    list_display = ['name', 'email', 'subject', 'status_badge', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    list_display_links = ['name', 'email']
    
    fieldsets = (
        (_('Contact Information'), {
            'fields': ('name', 'email', 'phone')
        }),
        (_('Message'), {
            'fields': ('subject', 'message')
        }),
        (_('Status'), {
            'fields': ('status', 'created_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display status with a badge indicator for new submissions."""
        if obj.status == 'new':
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">NEW</span> '
                '<span>{}</span>',
                obj.get_status_display()
            )
        elif obj.status == 'read':
            return format_html(
                '<span style="background-color: #ffc107; color: #000; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">READ</span> '
                '<span>{}</span>',
                obj.get_status_display()
            )
        return obj.get_status_display()
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'
    
    def get_queryset(self, request):
        """Annotate queryset to highlight new submissions."""
        return super().get_queryset(request)
    
    def changelist_view(self, request, extra_context=None):
        """Add notification count to changelist context."""
        extra_context = extra_context or {}
        new_count = ContactSubmission.objects.filter(status='new').count()
        if new_count > 0:
            extra_context['notification_count'] = new_count
            extra_context['notification_message'] = _('{} new contact submission(s)').format(new_count)
        return super().changelist_view(request, extra_context)



















