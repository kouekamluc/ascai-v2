"""
Admin configuration for universities app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import University, UniversityProgram, SavedUniversity


class UniversityProgramInline(admin.TabularInline):
    """Inline admin for university programs."""
    model = UniversityProgram
    extra = 1
    fields = ['name', 'degree_type', 'field', 'duration_years', 'language', 'tuition']


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    """Admin interface for University model."""
    list_display = ['name', 'city', 'website', 'created_at']
    list_filter = ['city', 'created_at']
    search_fields = ['name', 'city', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [UniversityProgramInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'city', 'address', 'description', 'logo')
        }),
        (_('Contact Information'), {
            'fields': ('website', 'email', 'phone')
        }),
        (_('Academic Information'), {
            'fields': ('languages', 'degree_types', 'fields_of_study')
        }),
        (_('Tuition'), {
            'fields': ('tuition_range_min', 'tuition_range_max')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UniversityProgram)
class UniversityProgramAdmin(admin.ModelAdmin):
    """Admin interface for UniversityProgram model."""
    list_display = ['name', 'university', 'degree_type', 'field', 'language', 'tuition']
    list_filter = ['degree_type', 'language', 'university']
    search_fields = ['name', 'field', 'university__name']
    raw_id_fields = ['university']


@admin.register(SavedUniversity)
class SavedUniversityAdmin(admin.ModelAdmin):
    """Admin interface for SavedUniversity model."""
    list_display = ['user', 'university', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'university__name']
    raw_id_fields = ['user', 'university']

