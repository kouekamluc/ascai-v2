"""
Admin configuration for students app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from config.admin import BaseAdmin, ModelAdmin
from .models import (
    ResourceCategory, ResourceLink,
    StudentGuideSection, StudentGuideStep, StudentGuideProgress
)


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(ModelAdmin):
    """Admin interface for ResourceCategory."""
    list_display = ['name', 'slug', 'icon', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(ResourceLink)
class ResourceLinkAdmin(ModelAdmin):
    """Admin interface for ResourceLink."""
    list_display = ['title', 'category', 'is_featured', 'order', 'created_at']
    list_filter = ['category', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'url']
    ordering = ['order', 'title']
    raw_id_fields = ['category']


class StudentGuideStepInline(admin.TabularInline):
    """Inline admin for StudentGuideStep."""
    model = StudentGuideStep
    extra = 1
    fields = ['title', 'order', 'image', 'video_url']
    ordering = ['order']


@admin.register(StudentGuideSection)
class StudentGuideSectionAdmin(BaseAdmin):
    """Admin interface for StudentGuideSection."""
    list_display = ['title', 'section_type', 'slug', 'order', 'is_active', 'created_at']
    list_filter = ['section_type', 'is_active', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'title']
    inlines = [StudentGuideStepInline]
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'section_type', 'icon', 'order', 'is_active')
        }),
        (_('Content'), {
            'fields': ('content',)
        }),
    )


@admin.register(StudentGuideStep)
class StudentGuideStepAdmin(BaseAdmin):
    """Admin interface for StudentGuideStep."""
    list_display = ['title', 'section', 'order', 'has_image', 'has_video', 'created_at']
    list_filter = ['section', 'section__section_type', 'created_at']
    search_fields = ['title', 'content', 'section__title']
    ordering = ['section', 'order', 'title']
    raw_id_fields = ['section']
    filter_horizontal = ['related_resources']
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = _('Has Image')
    
    def has_video(self, obj):
        return bool(obj.video_url)
    has_video.boolean = True
    has_video.short_description = _('Has Video')


@admin.register(StudentGuideProgress)
class StudentGuideProgressAdmin(ModelAdmin):
    """Admin interface for StudentGuideProgress."""
    list_display = ['user', 'section', 'is_completed', 'completion_percentage', 'last_accessed']
    list_filter = ['is_completed', 'section', 'created_at']
    search_fields = ['user__username', 'user__email', 'section__title']
    readonly_fields = ['created_at', 'last_accessed']
    raw_id_fields = ['user', 'section']
    filter_horizontal = ['completed_steps']
    
    def completion_percentage(self, obj):
        return f"{obj.get_completion_percentage()}%"
    completion_percentage.short_description = _('Completion %')
