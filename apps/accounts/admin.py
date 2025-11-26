"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserDocument


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.
    """
    list_display = ['username', 'email', 'full_name', 'role', 'is_approved', 'is_active', 'date_joined']
    list_filter = ['role', 'is_approved', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'full_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('ASCAI Lazio Information'), {
            'fields': ('role', 'phone', 'bio', 'avatar', 'language_preference', 'is_approved')
        }),
        (_('Extended Profile'), {
            'fields': (
                'full_name', 'city_in_lazio', 'university', 'field_of_study',
                'profession', 'occupation', 'arrival_year', 'date_of_birth',
                'email_verified', 'notification_preferences'
            )
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('ASCAI Lazio Information'), {
            'fields': ('role', 'phone', 'language_preference', 'is_approved')
        }),
    )
    
    actions = ['approve_users', 'reject_users']
    
    def save_model(self, request, obj, form, change):
        """Override save to auto-approve superusers and staff."""
        # Superusers must always be staff and active
        if obj.is_superuser:
            obj.is_staff = True
            obj.is_active = True
            obj.is_approved = True
        elif obj.is_staff:
            obj.is_active = True
            obj.is_approved = True
        super().save_model(request, obj, form, change)
    
    def approve_users(self, request, queryset):
        """Approve selected users and activate them."""
        updated = queryset.update(is_approved=True, is_active=True)
        self.message_user(request, f'{updated} user(s) approved and activated successfully.')
    approve_users.short_description = _('Approve selected users')
    
    def reject_users(self, request, queryset):
        """Reject selected users."""
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} user(s) rejected.')
    reject_users.short_description = _('Reject selected users')


@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    """Admin interface for user documents."""
    list_display = ['user', 'document_type', 'is_verified', 'uploaded_at']
    list_filter = ['document_type', 'is_verified', 'uploaded_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'uploaded_at']
    fieldsets = (
        (_('Document Information'), {
            'fields': ('user', 'document_type', 'file', 'is_verified', 'notes')
        }),
        (_('Timestamps'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_documents', 'unverify_documents']
    
    def verify_documents(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, _('{} documents verified.').format(updated))
    verify_documents.short_description = _('Verify selected documents')
    
    def unverify_documents(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, _('{} documents unverified.').format(updated))
    unverify_documents.short_description = _('Unverify selected documents')

