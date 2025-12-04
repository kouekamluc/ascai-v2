"""
Admin configuration for contact app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(ModelAdmin):
    """Admin interface for ContactSubmission."""
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']
    
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



















