"""
Admin configuration for scholarships app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from .models import Scholarship, SavedScholarship


@admin.register(Scholarship)
class ScholarshipAdmin(ModelAdmin):
    """Admin interface for Scholarship model."""
    list_display = ['title', 'provider', 'amount', 'currency', 'level', 'region', 'is_disco_lazio', 'status', 'application_deadline', 'created_at']
    list_filter = ['status', 'is_disco_lazio', 'level', 'region', 'currency', 'created_at']
    search_fields = ['title', 'provider', 'description']
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
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SavedScholarship)
class SavedScholarshipAdmin(ModelAdmin):
    """Admin interface for SavedScholarship model."""
    list_display = ['user', 'scholarship', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'scholarship__title']
    raw_id_fields = ['user', 'scholarship']

