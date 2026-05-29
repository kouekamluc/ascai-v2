"""
Admin configuration for site-wide core content.
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from config.admin import BaseAdmin

from .models import AssociationSettings, Collaborator, CommunityService, ConversionEvent, ServicePartner


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
    search_help_text = _("Search by collaborator name or website.")
    list_editable = ["is_featured", "is_active", "display_order"]
    readonly_fields = ["logo_preview_large", "created_at", "updated_at"]
    list_per_page = 20

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


@admin.register(AssociationSettings)
class AssociationSettingsAdmin(BaseAdmin):
    fieldsets = (
        (_("Brand"), {
            "fields": ("site_name", "tagline", "public_email"),
        }),
        (_("Public Location"), {
            "fields": ("public_location", "map_embed_url", "map_link_url"),
            "description": _("Control the location and map shown on the public contact page."),
        }),
        (_("Social Media Links"), {
            "fields": (
                "facebook_url",
                "instagram_url",
                "linkedin_url",
                "tiktok_url",
                "youtube_url",
            ),
            "description": _("Paste the full public URLs to your association social accounts."),
        }),
    )
    readonly_fields = ["updated_at"]
    list_per_page = 1

    def has_add_permission(self, request):
        return not AssociationSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = AssociationSettings.objects.first()
        if obj:
            return redirect(reverse("admin:core_associationsettings_change", args=[obj.pk]))
        return redirect(reverse("admin:core_associationsettings_add"))


@admin.register(ServicePartner)
class ServicePartnerAdmin(BaseAdmin):
    list_display = [
        "name",
        "category",
        "verification_status",
        "annual_listing_fee",
        "is_featured",
        "is_active",
        "display_order",
    ]
    list_filter = ["category", "verification_status", "is_featured", "is_active"]
    search_fields = ["name", "short_description", "contact_name", "cities_served"]
    search_help_text = _("Search service providers by name, contact, or city coverage.")
    list_editable = ["verification_status", "is_featured", "is_active", "display_order"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 25
    fieldsets = (
        (_("Partner Details"), {
            "fields": (
                "name",
                "category",
                "short_description",
                "cities_served",
            ),
        }),
        (_("Contacts"), {
            "fields": (
                "contact_name",
                "contact_email",
                "phone_number",
                "whatsapp_number",
                "website_url",
            ),
        }),
        (_("Verification and Revenue"), {
            "fields": (
                "verification_status",
                "annual_listing_fee",
                "is_featured",
                "is_active",
                "display_order",
            ),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(CommunityService)
class CommunityServiceAdmin(BaseAdmin):
    list_display = [
        "title",
        "category",
        "access_level",
        "revenue_stream",
        "partner",
        "is_featured",
        "is_active",
        "display_order",
    ]
    list_filter = ["category", "access_level", "delivery_mode", "revenue_stream", "is_featured", "is_active"]
    search_fields = ["title", "summary", "audience", "association_benefit"]
    search_help_text = _("Search services by title, audience, or service summary.")
    list_editable = ["is_featured", "is_active", "display_order"]
    autocomplete_fields = ["partner"]
    readonly_fields = ["created_at", "updated_at"]
    list_per_page = 25
    fieldsets = (
        (_("Service Details"), {
            "fields": (
                "title",
                "category",
                "audience",
                "summary",
                "association_benefit",
            ),
        }),
        (_("Access and Delivery"), {
            "fields": (
                "access_level",
                "delivery_mode",
                "revenue_stream",
                "partner",
            ),
        }),
        (_("Visibility"), {
            "fields": ("is_featured", "is_active", "display_order"),
        }),
        (_("Timestamps"), {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


@admin.register(ConversionEvent)
class ConversionEventAdmin(BaseAdmin):
    list_display = ["event_type", "user", "source_path", "ip_address", "created_at"]
    list_filter = ["event_type", "created_at"]
    search_fields = ["source_path", "user__username", "user__email", "ip_address", "user_agent"]
    readonly_fields = ["event_type", "user", "source_path", "session_key", "ip_address", "user_agent", "created_at"]
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
