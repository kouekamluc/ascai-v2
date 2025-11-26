"""
Admin configuration for downloads app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document."""
    list_display = ['title', 'category', 'file_type', 'download_count', 'is_active', 'uploaded_by', 'uploaded_at']
    list_filter = ['category', 'is_active', 'file_type', 'uploaded_at']
    search_fields = ['title', 'description']
    raw_id_fields = ['uploaded_by']
    
    fieldsets = (
        (_('Document Information'), {
            'fields': ('title', 'description', 'category', 'file', 'file_type')
        }),
        (_('Status'), {
            'fields': ('is_active', 'download_count')
        }),
        (_('Upload Information'), {
            'fields': ('uploaded_by', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['file_type', 'download_count', 'uploaded_at']
    
    def save_model(self, request, obj, form, change):
        """Automatically set uploaded_by to current user if not set."""
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

