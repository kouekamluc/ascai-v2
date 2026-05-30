"""
Admin configuration for scholarships app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from config.admin import BaseAdmin, ModelAdmin
from .models import Scholarship, SavedScholarship, ScholarshipSyncRun


@admin.register(Scholarship)
class ScholarshipAdmin(BaseAdmin):
    """Admin interface for Scholarship model."""
    list_display = ['title', 'provider', 'amount', 'currency', 'level', 'region', 'is_disco_lazio', 'source_name', 'status', 'application_deadline', 'source_last_seen_at']
    list_filter = ['status', 'is_disco_lazio', 'level', 'region', 'currency', 'source_name', 'created_at']
    search_fields = ['title', 'provider', 'description', 'source_name', 'source_url']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'provider', 'description', 'is_disco_lazio')
        }),
        (_('Classification'), {
            'fields': ('level', 'region')
        }),
        (_('Funding Information'), {
            'fields': ('amount', 'currency')
        }),
        (_('Application Details'), {
            'fields': ('eligibility_criteria', 'application_deadline', 'application_url', 'requirements_document')
        }),
        (_('Source Tracking'), {
            'fields': ('source_name', 'source_url', 'source_excerpt', 'source_last_seen_at', 'source_imported_at', 'source_hash'),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'source_last_seen_at', 'source_imported_at', 'source_hash']


@admin.register(SavedScholarship)
class SavedScholarshipAdmin(ModelAdmin):
    """Admin interface for SavedScholarship model."""
    list_display = ['user', 'scholarship', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'scholarship__title']
    raw_id_fields = ['user', 'scholarship']


@admin.register(ScholarshipSyncRun)
class ScholarshipSyncRunAdmin(ModelAdmin):
    list_display = ['status', 'started_at', 'finished_at', 'source_count', 'created_count', 'updated_count', 'skipped_count', 'dry_run']
    list_filter = ['status', 'dry_run', 'started_at']
    search_fields = ['error_log']
    readonly_fields = ['status', 'started_at', 'finished_at', 'source_count', 'created_count', 'updated_count', 'skipped_count', 'error_log', 'dry_run']
