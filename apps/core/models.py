"""
Core models for site-wide content.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class Collaborator(models.Model):
    """Public-facing collaborator or partner logo shown across the site."""

    CATEGORY_CHOICES = [
        ("collaborator", _("Collaborator")),
        ("partner", _("Partner")),
        ("supporter", _("Supporter")),
        ("institution", _("Institution")),
    ]

    name = models.CharField(max_length=200, verbose_name=_("Name"))
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="collaborator",
        verbose_name=_("Category"),
    )
    logo = models.ImageField(
        upload_to="collaborators/",
        blank=True,
        null=True,
        verbose_name=_("Logo"),
        help_text=_("Recommended: transparent PNG or SVG-friendly image."),
    )
    website_url = models.URLField(
        blank=True,
        verbose_name=_("Website URL"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Short Description"),
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
    )
    is_featured = models.BooleanField(
        default=True,
        verbose_name=_("Featured on Site"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = _("Collaborator")
        verbose_name_plural = _("Collaborators")

    def __str__(self):
        return self.name


class AssociationSettings(models.Model):
    """Singleton-style site settings editable from Django admin."""

    site_name = models.CharField(
        max_length=200,
        default="ASCAI Lazio",
        verbose_name=_("Site Name"),
    )
    tagline = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Tagline"),
    )
    public_email = models.EmailField(
        blank=True,
        verbose_name=_("Public Email"),
    )
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook URL"))
    instagram_url = models.URLField(blank=True, verbose_name=_("Instagram URL"))
    linkedin_url = models.URLField(blank=True, verbose_name=_("LinkedIn URL"))
    tiktok_url = models.URLField(blank=True, verbose_name=_("TikTok URL"))
    youtube_url = models.URLField(blank=True, verbose_name=_("YouTube URL"))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Association Settings")
        verbose_name_plural = _("Association Settings")

    def __str__(self):
        return self.site_name or _("Association Settings")

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _created = cls.objects.get_or_create(
            pk=1,
            defaults={
                "site_name": "ASCAI Lazio",
                "tagline": _("Association of Cameroonian Students and Academics in Lazio"),
            },
        )
        return obj


class ServicePartner(models.Model):
    """Verified service providers who want visibility through ASCAI."""

    CATEGORY_CHOICES = [
        ("money_transfer", _("Money Transfer")),
        ("documents_translation", _("Documents and Translation")),
        ("legal_admin", _("Legal and Administrative Help")),
        ("housing_settlement", _("Housing and Settlement")),
        ("travel_logistics", _("Travel and Logistics")),
        ("business_services", _("Business Services")),
        ("health_wellbeing", _("Health and Wellbeing")),
        ("other", _("Other")),
    ]

    VERIFICATION_CHOICES = [
        ("pending", _("Pending")),
        ("verified", _("Verified")),
        ("needs_review", _("Needs Review")),
        ("suspended", _("Suspended")),
    ]

    name = models.CharField(max_length=200, verbose_name=_("Partner Name"))
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="other",
        verbose_name=_("Category"),
    )
    short_description = models.TextField(verbose_name=_("Short Description"))
    contact_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Contact Name"),
    )
    contact_email = models.EmailField(blank=True, verbose_name=_("Contact Email"))
    phone_number = models.CharField(max_length=50, blank=True, verbose_name=_("Phone Number"))
    whatsapp_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("WhatsApp Number"),
    )
    website_url = models.URLField(blank=True, verbose_name=_("Website URL"))
    cities_served = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Cities Served"),
        help_text=_("Examples: Rome, Latina, online"),
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default="pending",
        verbose_name=_("Verification Status"),
    )
    annual_listing_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=Decimal("20.00"),
        verbose_name=_("Annual Listing Fee"),
        help_text=_("Annual fee charged to service providers for verified visibility."),
    )
    is_featured = models.BooleanField(default=True, verbose_name=_("Featured"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = _("Service Partner")
        verbose_name_plural = _("Service Partners")

    def __str__(self):
        return self.name

    @property
    def is_verified(self):
        return self.verification_status == "verified"


class CommunityService(models.Model):
    """Association-run or partner-linked services that create member value and revenue."""

    CATEGORY_CHOICES = [
        ("consular_support", _("Consular Support")),
        ("documentation", _("Documentation")),
        ("arrival_support", _("Arrival and Settlement")),
        ("money_transfer", _("Money Transfer")),
        ("career_business", _("Career and Business")),
        ("family_life", _("Family and Community Life")),
        ("other", _("Other")),
    ]

    ACCESS_LEVEL_CHOICES = [
        ("public", _("Public")),
        ("member", _("Members")),
        ("member_referral", _("Members with Verified Referrals")),
    ]

    DELIVERY_MODE_CHOICES = [
        ("resource_pack", _("Resource Pack")),
        ("workshop", _("Workshop")),
        ("clinic", _("Clinic")),
        ("partner_referral", _("Partner Referral")),
        ("appointment_prep", _("Appointment Preparation")),
    ]

    REVENUE_STREAM_CHOICES = [
        ("included_in_dues", _("Included in Dues")),
        ("partner_listing_fee", _("Partner Listing Fee")),
        ("paid_clinic", _("Paid Clinic")),
        ("event_revenue", _("Event Revenue")),
        ("sponsorship", _("Sponsorship")),
    ]

    title = models.CharField(max_length=200, verbose_name=_("Title"))
    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="other",
        verbose_name=_("Category"),
    )
    audience = models.CharField(max_length=200, blank=True, verbose_name=_("Audience"))
    summary = models.TextField(verbose_name=_("Summary"))
    association_benefit = models.TextField(
        blank=True,
        verbose_name=_("Association Benefit"),
        help_text=_("How this service can strengthen ASCAI's value or revenue."),
    )
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default="member",
        verbose_name=_("Access Level"),
    )
    delivery_mode = models.CharField(
        max_length=20,
        choices=DELIVERY_MODE_CHOICES,
        default="resource_pack",
        verbose_name=_("Delivery Mode"),
    )
    revenue_stream = models.CharField(
        max_length=25,
        choices=REVENUE_STREAM_CHOICES,
        default="included_in_dues",
        verbose_name=_("Revenue Stream"),
    )
    partner = models.ForeignKey(
        ServicePartner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
        verbose_name=_("Linked Partner"),
    )
    is_featured = models.BooleanField(default=True, verbose_name=_("Featured"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_("Display Order"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "title"]
        verbose_name = _("Community Service")
        verbose_name_plural = _("Community Services")

    def __str__(self):
        return self.title


class ConversionEvent(models.Model):
    """Lightweight conversion tracking for sponsor and student intent."""

    EVENT_CHOICES = [
        ("sponsor_interest", _("Sponsor Interest")),
        ("orientation_request", _("Orientation Request")),
        ("one_pager_download", _("Sponsor One-Pager Download")),
    ]

    event_type = models.CharField(
        max_length=40,
        choices=EVENT_CHOICES,
        verbose_name=_("Event Type"),
    )
    source_path = models.CharField(max_length=255, blank=True, verbose_name=_("Source Path"))
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversion_events",
        verbose_name=_("User"),
    )
    session_key = models.CharField(max_length=80, blank=True, verbose_name=_("Session Key"))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_("IP Address"))
    user_agent = models.TextField(blank=True, verbose_name=_("User Agent"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Conversion Event")
        verbose_name_plural = _("Conversion Events")

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.created_at:%Y-%m-%d}"
