"""
Admin configuration for diaspora app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from config.admin import BaseAdmin, ModelAdmin
from .models import News, Event, Testimonial, SuccessStory, SuccessStoryImage, LifeInItaly


@admin.register(News)
class NewsAdmin(BaseAdmin):
    """
    Admin interface for News model.
    
    Uses BaseAdmin which automatically provides WYSIWYG editor (Trix)
    for the 'content' TextField, allowing rich text formatting.
    """
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
class EventAdmin(BaseAdmin):
    """
    Admin interface for Event model.
    
    Uses BaseAdmin which automatically provides WYSIWYG editor (Trix)
    for the 'description' TextField, allowing rich text formatting.
    """
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


@admin.register(Testimonial)
class TestimonialAdmin(BaseAdmin):
    """
    Admin interface for Testimonial model.
    
    Uses BaseAdmin which automatically provides WYSIWYG editor (Trix)
    for the 'testimonial' TextField, allowing rich text formatting.
    """
    list_display = ['name', 'title', 'location', 'is_featured', 'is_published', 'language', 'created_at']
    list_filter = ['is_featured', 'is_published', 'language', 'created_at']
    search_fields = ['name', 'title', 'testimonial']
    list_editable = ['is_featured', 'is_published']
    
    fieldsets = (
        (_('Personal Information'), {
            'fields': ('name', 'title', 'location', 'image')
        }),
        (_('Content'), {
            'fields': ('testimonial', 'language')
        }),
        (_('Publication'), {
            'fields': ('is_featured', 'is_published')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']




@admin.register(SuccessStoryImage)
class SuccessStoryImageAdmin(ModelAdmin):
    """Admin interface for SuccessStoryImage model."""
    list_display = ['caption', 'created_at']
    search_fields = ['caption']


@admin.register(SuccessStory)
class SuccessStoryAdmin(BaseAdmin):
    """
    Admin interface for SuccessStory model.
    
    Uses BaseAdmin which automatically provides WYSIWYG editor (Trix)
    for the 'story' TextField, allowing rich text formatting.
    """
    list_display = ['title', 'person_name', 'is_featured', 'is_published', 'language', 'created_at']
    list_filter = ['is_featured', 'is_published', 'language', 'created_at']
    search_fields = ['title', 'person_name', 'person_title', 'story']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured', 'is_published']
    filter_horizontal = ['additional_images']
    
    fieldsets = (
        (_('Story Information'), {
            'fields': ('title', 'slug', 'person_name', 'person_title', 'language')
        }),
        (_('Content'), {
            'fields': ('story', 'featured_image')
        }),
        (_('Additional Images'), {
            'fields': ('additional_images',),
            'classes': ('collapse',)
        }),
        (_('Publication'), {
            'fields': ('is_featured', 'is_published')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LifeInItaly)
class LifeInItalyAdmin(BaseAdmin):
    """
    Admin interface for LifeInItaly model.
    
    Uses BaseAdmin which automatically provides WYSIWYG editor (Trix)
    for the 'content' TextField, allowing rich text formatting.
    """
    list_display = ['title', 'category', 'is_featured', 'is_published', 'language', 'created_at']
    list_filter = ['category', 'is_featured', 'is_published', 'language', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_featured', 'is_published']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'category', 'content', 'image', 'language')
        }),
        (_('Publication'), {
            'fields': ('is_featured', 'is_published')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

