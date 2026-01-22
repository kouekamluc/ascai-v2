"""
Admin configuration for downloads app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from config.admin import BaseAdmin, ModelAdmin
from .models import Document


@admin.register(Document)
class DocumentAdmin(BaseAdmin):
    """Admin interface for Document."""
    list_display = ['title', 'category', 'file_type', 'file_size_display', 'download_count', 'is_active', 'is_reserved', 'uploaded_by', 'uploaded_at']
    list_filter = ['category', 'is_active', 'is_reserved', 'file_type', 'uploaded_at']
    search_fields = ['title', 'description', 'tags']
    raw_id_fields = ['uploaded_by']
    
    fieldsets = (
        (_('Document Information'), {
            'fields': ('title', 'description', 'category', 'tags', 'file', 'thumbnail', 'file_type', 'file_size', 'preview_url')
        }),
        (_('Status & Access'), {
            'fields': ('is_active', 'is_reserved', 'download_count', 'download_limit', 'expiry_date')
        }),
        (_('Upload Information'), {
            'fields': ('uploaded_by', 'uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['file_type', 'file_size', 'download_count', 'uploaded_at', 'updated_at']
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = _('File Size')
    
    def save_model(self, request, obj, form, change):
        """Automatically set uploaded_by to current user if not set."""
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

