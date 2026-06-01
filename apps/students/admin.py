"""
Admin configuration for students app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from config.admin import BaseAdmin, ModelAdmin
from .models import (
    StudentProfile, ResourceCategory, ResourceLink,
    StudentGuideSection, StudentGuideStep, StudentGuideProgress
)


@admin.register(StudentProfile)
class StudentProfileAdmin(BaseAdmin):
    """Admin queue for users who selected the student role."""
    list_display = ['user', 'account_status', 'onboarding_status', 'city', 'university', 'created_at']
    list_filter = ['onboarding_status', 'user__is_approved', 'user__email_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__full_name', 'user__field_of_study']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_in_progress', 'mark_completed']
    fieldsets = (
        (_('Student Account'), {
            'fields': ('user', 'onboarding_status', 'notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def account_status(self, obj):
        if obj.user.is_approved and obj.user.email_verified:
            return _('Verified and approved')
        if obj.user.email_verified:
            return _('Email verified')
        if obj.user.is_approved:
            return _('Account approved')
        return _('Pending')
    account_status.short_description = _('Account Status')

    def city(self, obj):
        return obj.user.get_city_in_lazio_display() if obj.user.city_in_lazio else '-'
    city.short_description = _('City')

    def university(self, obj):
        return obj.user.university or '-'
    university.short_description = _('University')

    def mark_in_progress(self, request, queryset):
        updated = queryset.update(onboarding_status='in_progress')
        self.message_user(request, _('{} student profile(s) marked in progress.').format(updated))
    mark_in_progress.short_description = _('Mark selected student profiles in progress')

    def mark_completed(self, request, queryset):
        updated = queryset.update(onboarding_status='completed')
        self.message_user(request, _('{} student profile(s) marked completed.').format(updated))
    mark_completed.short_description = _('Mark selected student profiles completed')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        pending_count = StudentProfile.objects.filter(onboarding_status='pending').count()
        if pending_count:
            extra_context['notification_count'] = pending_count
            extra_context['notification_message'] = _('{} student profile(s) pending onboarding review').format(pending_count)
        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'user__university')


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
