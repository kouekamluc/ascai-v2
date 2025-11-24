"""
Models for scholarships app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

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

