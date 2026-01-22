"""
Models for students app - Resources and New Student Guide.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class ResourceCategory(models.Model):
    """
    Category model for organizing resources.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Name')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_('Slug')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Icon class name (e.g., "folder", "document", "link")'),
        verbose_name=_('Icon')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Resource Category')
        verbose_name_plural = _('Resource Categories')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ResourceLink(models.Model):
    """
    External resource link model.
    """
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    url = models.URLField(
        verbose_name=_('URL')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )
    category = models.ForeignKey(
        ResourceCategory,
        on_delete=models.CASCADE,
        related_name='resource_links',
        verbose_name=_('Category')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Featured'),
        help_text=_('Featured resources appear prominently on the resources page.')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Resource Link')
        verbose_name_plural = _('Resource Links')
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title


class StudentGuideSection(models.Model):
    """
    Main sections of the new student guide.
    """
    SECTION_CHOICES = [
        ('welcome', _('Welcome to ASCAI Lazio')),
        ('before_arrival', _('Before Arrival')),
        ('arrival', _('Arrival & First Steps')),
        ('enrollment', _('University Enrollment')),
        ('living', _('Living in Lazio')),
        ('membership', _('ASCAI Membership')),
        ('resources', _('Resources & Support')),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name=_('Slug')
    )
    section_type = models.CharField(
        max_length=50,
        choices=SECTION_CHOICES,
        verbose_name=_('Section Type')
    )
    content = models.TextField(
        verbose_name=_('Content'),
        help_text=_('Main content for this section.')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Icon class name (e.g., "home", "school", "info")'),
        verbose_name=_('Icon')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Guide Section')
        verbose_name_plural = _('Guide Sections')
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('students:guide_section_detail', kwargs={'slug': self.slug})


class StudentGuideStep(models.Model):
    """
    Step-by-step guide items within each section.
    """
    section = models.ForeignKey(
        StudentGuideSection,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name=_('Section')
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title')
    )
    content = models.TextField(
        verbose_name=_('Content')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Order')
    )
    image = models.ImageField(
        upload_to='guide_images/%Y/%m/',
        blank=True,
        null=True,
        verbose_name=_('Image')
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text=_('Optional video URL (YouTube, Vimeo, etc.)'),
        verbose_name=_('Video URL')
    )
    related_resources = models.ManyToManyField(
        'downloads.Document',
        blank=True,
        related_name='guide_steps',
        verbose_name=_('Related Resources')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated At')
    )
    
    class Meta:
        verbose_name = _('Guide Step')
        verbose_name_plural = _('Guide Steps')
        ordering = ['order', 'title']
    
    def __str__(self):
        return f"{self.section.title} - {self.title}"


class StudentGuideProgress(models.Model):
    """
    Track user progress through the new student guide.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='guide_progress',
        verbose_name=_('User')
    )
    section = models.ForeignKey(
        StudentGuideSection,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name=_('Section')
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name=_('Completed')
    )
    completed_steps = models.ManyToManyField(
        StudentGuideStep,
        blank=True,
        related_name='completed_by_users',
        verbose_name=_('Completed Steps')
    )
    last_accessed = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Accessed')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created At')
    )
    
    class Meta:
        verbose_name = _('Guide Progress')
        verbose_name_plural = _('Guide Progress')
        unique_together = ['user', 'section']
        ordering = ['-last_accessed']
    
    def __str__(self):
        status = _('Completed') if self.is_completed else _('In Progress')
        return f"{self.user.username} - {self.section.title} ({status})"
    
    def get_completion_percentage(self):
        """Calculate completion percentage for this section."""
        total_steps = self.section.steps.count()
        if total_steps == 0:
            return 100 if self.is_completed else 0
        completed_count = self.completed_steps.count()
        return int((completed_count / total_steps) * 100)
