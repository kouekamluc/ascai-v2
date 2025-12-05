"""
User models for ASCAI Lazio platform.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('mentor', _('Mentor')),
        ('student', _('Student')),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
        ('it', _('Italiano')),
    ]
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_('Phone Number')
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name=_('Role')
    )
    
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_('Approved'),
        help_text=_('Designates whether this user has been approved by an admin.')
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Bio'),
        help_text=_('A short biography about yourself.')
    )
    
    avatar = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name=_('Avatar')
    )
    
    language_preference = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Language Preference')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    # Extended profile fields
    full_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Full Name'),
        help_text=_('Your full name')
    )
    
    CITY_CHOICES = [
        ('rome', _('Rome')),
        ('latina', _('Latina')),
        ('frosinone', _('Frosinone')),
        ('rieti', _('Rieti')),
        ('viterbo', _('Viterbo')),
    ]
    
    city_in_lazio = models.CharField(
        max_length=50,
        choices=CITY_CHOICES,
        blank=True,
        null=True,
        verbose_name=_('City in Lazio')
    )
    
    university = models.ForeignKey(
        'universities.University',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        verbose_name=_('University')
    )
    
    field_of_study = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Field of Study / Profession')
    )
    
    profession = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_('Profession')
    )
    
    OCCUPATION_CHOICES = [
        ('student', _('Student')),
        ('worker', _('Worker')),
        ('job_seeker', _('Job Seeker')),
        ('researcher', _('Researcher')),
    ]
    
    occupation = models.CharField(
        max_length=20,
        choices=OCCUPATION_CHOICES,
        blank=True,
        null=True,
        verbose_name=_('Occupation')
    )
    
    arrival_year = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        verbose_name=_('Arrival Year in Italy')
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date of Birth')
    )
    
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email Verified')
    )
    
    notification_preferences = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Notification Preferences'),
        help_text=_('User notification settings')
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_mentor(self):
        return self.role == 'mentor'
    
    @property
    def is_student(self):
        return self.role == 'student'
    
    def get_display_name(self):
        """Return full name if available, otherwise username."""
        return self.full_name or self.username
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure superusers always have is_staff=True.
        This is required for Django admin access.
        """
        # Superusers must always be staff to access admin
        if self.is_superuser:
            self.is_staff = True
            self.is_active = True
            self.is_approved = True
        
        super().save(*args, **kwargs)


class UserDocument(models.Model):
    """
    Model for user-uploaded documents (ID card, student card, residence permit, etc.)
    """
    DOCUMENT_TYPE_CHOICES = [
        ('id_card', _('ID Card')),
        ('student_card', _('Student Card')),
        ('residence_permit', _('Residence Permit')),
        ('other', _('Other')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name=_('User')
    )
    
    document_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        verbose_name=_('Document Type')
    )
    
    file = models.FileField(
        upload_to='user_documents/%Y/%m/',
        verbose_name=_('File')
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Uploaded At')
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name=_('Verified'),
        help_text=_('Whether this document has been verified by an admin.')
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Notes'),
        help_text=_('Admin notes about this document.')
    )
    
    class Meta:
        verbose_name = _('User Document')
        verbose_name_plural = _('User Documents')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_document_type_display()}"

