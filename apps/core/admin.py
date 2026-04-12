"""
Admin configuration for site-wide core content.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from config.admin import BaseAdmin

from .models import Collaborator


@admin.register(Collaborator)
class CollaboratorAdmin(BaseAdmin):
    list_display = [
        "logo_preview",
        "name",
        "category",
        "is_featured",
        "is_active",
        "display_order",
        "website_url",
    ]
    list_filter = ["category", "is_featured", "is_active"]
    search_fields = ["name", "description", "website_url"]
    list_editable = ["is_featured", "is_active", "display_order"]
    readonly_fields = ["logo_preview_large", "created_at", "updated_at"]

    fieldsets = (
        (_("Collaborator Details"), {
            "fields": ("name", "category", "description", "website_url"),
        }),
        (_("Branding"), {
            "fields": ("logo", "logo_preview_large"),
        }),
        (_("Visibility"), {
            "fields": ("is_featured", "is_active", "display_order"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def logo_preview(self, obj):
        if not obj.logo:
            return "-"
        return format_html(
            '<img src="{}" alt="{}" style="height: 38px; width: 38px; '
            'object-fit: contain; border-radius: 10px; background: white; padding: 4px; border: 1px solid #e5e7eb;">',
            obj.logo.url,
            obj.name,
        )

    logo_preview.short_description = _("Logo")

    def logo_preview_large(self, obj):
        if not obj.pk or not obj.logo:
            return _("Upload a logo to preview it here.")
        return format_html(
            '<img src="{}" alt="{}" style="max-height: 96px; max-width: 220px; '
            'object-fit: contain; border-radius: 18px; background: white; padding: 12px; border: 1px solid #e5e7eb;">',
            obj.logo.url,
            obj.name,
        )

    logo_preview_large.short_description = _("Logo Preview")
