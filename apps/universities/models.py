"""
Models for universities app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class University(models.Model):
    """
    University model for Lazio region universities.
    """
    CITY_CHOICES = [
        ('rome', _('Rome')),
        ('cassino', _('Cassino')),
        ('viterbo', _('Viterbo')),
        ('latina', _('Latina')),
        ('frosinone', _('Frosinone')),
        ('rieti', _('Rieti')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('University Name'))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    city = models.CharField(max_length=50, choices=CITY_CHOICES, verbose_name=_('City'))
    address = models.TextField(verbose_name=_('Address'))
    website = models.URLField(blank=True, null=True, verbose_name=_('Website'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Phone'))
    description = models.TextField(verbose_name=_('Description'))
    tuition_range_min = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Minimum Tuition (EUR)')
    )
    tuition_range_max = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Maximum Tuition (EUR)')
    )
    languages = models.JSONField(
        default=list,
        verbose_name=_('Languages of Instruction'),
        help_text=_('List of languages offered (e.g., ["Italian", "English"])')
    )
    degree_types = models.JSONField(
        default=list,
        verbose_name=_('Degree Types'),
        help_text=_('List of degree types (e.g., ["Bachelor", "Master", "PhD"])')
    )
    fields_of_study = models.JSONField(
        default=list,
        verbose_name=_('Fields of Study'),
        help_text=_('List of fields (e.g., ["Engineering", "Medicine", "Law"])')
    )
    logo = models.ImageField(
        upload_to='universities/logos/',
        blank=True,
        null=True,
        verbose_name=_('Logo')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('University')
        verbose_name_plural = _('Universities')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('universities:detail', kwargs={'slug': self.slug})


class UniversityProgram(models.Model):
    """
    University program/degree model.
    """
    DEGREE_CHOICES = [
        ('bachelor', _('Bachelor')),
        ('master', _('Master')),
        ('phd', _('PhD')),
        ('other', _('Other')),
    ]
    
    LANGUAGE_CHOICES = [
        ('italian', _('Italian')),
        ('english', _('English')),
        ('french', _('French')),
        ('bilingual', _('Bilingual')),
    ]
    
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='programs',
        verbose_name=_('University')
    )
    name = models.CharField(max_length=200, verbose_name=_('Program Name'))
    degree_type = models.CharField(
        max_length=20,
        choices=DEGREE_CHOICES,
        verbose_name=_('Degree Type')
    )
    field = models.CharField(max_length=100, verbose_name=_('Field of Study'))
    duration_years = models.PositiveIntegerField(verbose_name=_('Duration (Years)'))
    language = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        verbose_name=_('Language of Instruction')
    )
    tuition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Tuition (EUR)')
    )
    description = models.TextField(verbose_name=_('Description'))
    requirements = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Requirements')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Program')
        verbose_name_plural = _('Programs')
        ordering = ['university', 'name']
    
    def __str__(self):
        return f"{self.university.name} - {self.name}"


class SavedUniversity(models.Model):
    """
    Student saved universities (favorites).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_universities',
        verbose_name=_('User')
    )
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        verbose_name=_('University')
    )
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Saved At'))
    
    class Meta:
        verbose_name = _('Saved University')
        verbose_name_plural = _('Saved Universities')
        unique_together = ['user', 'university']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.university.name}"

