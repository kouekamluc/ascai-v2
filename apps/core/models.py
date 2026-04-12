"""
Core models for site-wide content.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


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
