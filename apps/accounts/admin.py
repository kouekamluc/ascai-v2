"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    """
    list_display = ['username', 'email', 'role', 'is_approved', 'is_active', 'date_joined']
    list_filter = ['role', 'is_approved', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('ASCAI Lazio Information'), {
            'fields': ('role', 'phone', 'bio', 'avatar', 'language_preference', 'is_approved')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('ASCAI Lazio Information'), {
            'fields': ('role', 'phone', 'language_preference', 'is_approved')
        }),
    )
    
    actions = ['approve_users', 'reject_users']
    
    def approve_users(self, request, queryset):
        """Approve selected users."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} user(s) approved successfully.')
    approve_users.short_description = _('Approve selected users')
    
    def reject_users(self, request, queryset):
        """Reject selected users."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} user(s) rejected.')
    reject_users.short_description = _('Reject selected users')

