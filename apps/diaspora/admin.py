"""
Admin configuration for diaspora app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import News, Event


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Admin interface for News model."""
    list_display = ['title', 'category', 'author', 'is_published', 'published_at', 'language', 'created_at']
    list_filter = ['category', 'is_published', 'language', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'content', 'author', 'category', 'language', 'image')
        }),
        (_('Publication'), {
            'fields': ('is_published', 'published_at')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Event model."""
    list_display = ['title', 'location', 'start_datetime', 'end_datetime', 'organizer', 'is_published', 'registration_required']
    list_filter = ['is_published', 'registration_required', 'language', 'start_datetime']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_datetime'
    
    fieldsets = (
        (_('Event Details'), {
            'fields': ('title', 'slug', 'description', 'location', 'image', 'language')
        }),
        (_('Schedule'), {
            'fields': ('start_datetime', 'end_datetime')
        }),
        (_('Organization'), {
            'fields': ('organizer', 'is_published', 'registration_required', 'max_participants')
        }),
        (_('Date'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']

