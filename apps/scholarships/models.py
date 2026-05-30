"""
Models for scholarships app.
"""
from urllib.parse import urlparse

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()


class Scholarship(models.Model):
    """
    Scholarship model for funding opportunities.
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('deadline_passed', _('Deadline Passed')),
    ]
    
    CURRENCY_CHOICES = [
        ('EUR', _('EUR (€)')),
        ('USD', _('USD ($)')),
    ]
    
    LEVEL_CHOICES = [
        ('bachelor', _('Bachelor\'s Degree')),
        ('master', _('Master\'s Degree')),
        ('phd', _('PhD')),
        ('all', _('All Levels')),
    ]
    
    REGION_CHOICES = [
        ('lazio', _('Lazio')),
        ('all', _('All Regions')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    provider = models.CharField(max_length=200, verbose_name=_('Provider'))
    description = models.TextField(verbose_name=_('Description'))
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Amount')
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='EUR',
        verbose_name=_('Currency')
    )
    eligibility_criteria = models.TextField(verbose_name=_('Eligibility Criteria'))
    application_deadline = models.DateField(null=True, blank=True, verbose_name=_('Application Deadline'))
    application_url = models.URLField(blank=True, null=True, verbose_name=_('Application URL'))
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='all',
        verbose_name=_('Level'),
        help_text=_('Education level this scholarship is for')
    )
    region = models.CharField(
        max_length=20,
        choices=REGION_CHOICES,
        default='all',
        verbose_name=_('Region'),
        help_text=_('Region this scholarship applies to')
    )
    is_disco_lazio = models.BooleanField(
        default=False,
        verbose_name=_('DISCO Lazio Scholarship'),
        help_text=_('Mark this if this is a DISCO Lazio scholarship')
    )
    requirements_document = models.FileField(
        upload_to='scholarships/requirements/',
        blank=True,
        null=True,
        verbose_name=_('Requirements Document')
    )
    source_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Source Name'),
        help_text=_('Official source this scholarship was imported from.'),
    )
    source_url = models.URLField(
        blank=True,
        verbose_name=_('Source URL'),
        help_text=_('Official page where students should verify the latest information.'),
    )
    source_excerpt = models.TextField(
        blank=True,
        verbose_name=_('Source Excerpt'),
        help_text=_('Short imported summary from the source page.'),
    )
    source_last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Source Last Seen At'),
    )
    source_imported_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Source Imported At'),
    )
    source_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_('Source Hash'),
        help_text=_('Internal fingerprint used to detect source changes.'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Status')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Scholarship')
        verbose_name_plural = _('Scholarships')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('scholarships:detail', kwargs={'slug': self.slug})

    @property
    def is_imported(self):
        return bool(self.source_url)

    @property
    def source_freshness_label(self):
        if not self.source_last_seen_at:
            return _('Manual entry')
        delta = timezone.now() - self.source_last_seen_at
        if delta.days == 0:
            return _('Checked today')
        if delta.days == 1:
            return _('Checked yesterday')
        return _('Checked %(days)s days ago') % {'days': delta.days}

    @property
    def source_hostname(self):
        if not self.source_url:
            return ''
        return urlparse(self.source_url).hostname or ''

    @property
    def provider_logo_url(self):
        if not self.source_hostname:
            return ''
        return f'https://www.google.com/s2/favicons?domain={self.source_hostname}&sz=128'

    @property
    def provider_initials(self):
        source = self.source_name or self.provider or self.title
        words = [word for word in source.replace('-', ' ').split() if word]
        if not words:
            return 'AS'
        if len(words) == 1:
            return words[0][:2].upper()
        return ''.join(word[0] for word in words[:2]).upper()


class SavedScholarship(models.Model):
    """
    Student saved scholarships (favorites).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_scholarships',
        verbose_name=_('User')
    )
    scholarship = models.ForeignKey(
        Scholarship,
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        verbose_name=_('Scholarship')
    )
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Saved At'))
    
    class Meta:
        verbose_name = _('Saved Scholarship')
        verbose_name_plural = _('Saved Scholarships')
        unique_together = ['user', 'scholarship']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.scholarship.title}"


class ScholarshipSyncRun(models.Model):
    """
    Audit log for automated scholarship source synchronization.
    """
    STATUS_CHOICES = [
        ('running', _('Running')),
        ('success', _('Success')),
        ('partial', _('Partial Success')),
        ('failed', _('Failed')),
        ('dry_run', _('Dry Run')),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='running',
        verbose_name=_('Status')
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Started At'))
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Finished At'))
    created_count = models.PositiveIntegerField(default=0, verbose_name=_('Created Count'))
    updated_count = models.PositiveIntegerField(default=0, verbose_name=_('Updated Count'))
    skipped_count = models.PositiveIntegerField(default=0, verbose_name=_('Skipped Count'))
    source_count = models.PositiveIntegerField(default=0, verbose_name=_('Source Count'))
    error_log = models.TextField(blank=True, verbose_name=_('Error Log'))
    dry_run = models.BooleanField(default=False, verbose_name=_('Dry Run'))

    class Meta:
        verbose_name = _('Scholarship Sync Run')
        verbose_name_plural = _('Scholarship Sync Runs')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.get_status_display()} - {self.started_at:%Y-%m-%d %H:%M}"
