"""
Models for diaspora app - News, Events, Success Stories.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


def _generate_unique_slug(model_class, value, instance_pk=None, fallback='item', max_length=200):
    """Generate a unique slug for a model instance."""
    base_slug = slugify(value) or fallback
    base_slug = base_slug[:max_length]
    slug = base_slug
    counter = 1

    queryset = model_class.objects.all()
    if instance_pk:
        queryset = queryset.exclude(pk=instance_pk)

    while queryset.filter(slug=slug).exists():
        suffix = f"-{counter}"
        slug = f"{base_slug[:max_length - len(suffix)]}{suffix}"
        counter += 1

    return slug


class News(models.Model):
    """
    News article model for diaspora news and announcements.
    """
    CATEGORY_CHOICES = [
        ('general', _('General')),
        ('academic', _('Academic')),
        ('cultural', _('Cultural')),
        ('integration', _('Integration')),
        ('success_story', _('Success Story')),
        ('announcement', _('Announcement')),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
        ('it', _('Italiano')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField(verbose_name=_('Content'))
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='news_articles',
        verbose_name=_('Author')
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name=_('Category')
    )
    image = models.ImageField(
        upload_to='news/',
        blank=True,
        null=True,
        verbose_name=_('Featured Image')
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Published At')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Is Published'),
        help_text=_('Only published news will be visible to users.')
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Language')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('News')
        verbose_name_plural = _('News')
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(News, self.title, self.pk, fallback='news')
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('diaspora:news_detail', kwargs={'slug': self.slug})


class Event(models.Model):
    """
    Event model for diaspora events and activities.
    """
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
        ('it', _('Italiano')),
    ]
    
    EVENT_TYPE_CHOICES = [
        ('cultural', _('Cultural')),
        ('educational', _('Educational')),
        ('social', _('Social')),
        ('networking', _('Networking')),
        ('sports', _('Sports')),
        ('workshop', _('Workshop')),
        ('seminar', _('Seminar')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(verbose_name=_('Description'))
    location = models.CharField(max_length=200, verbose_name=_('Location'))
    location_map = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Location Map URL'),
        help_text=_('Google Maps or other map service URL')
    )
    start_datetime = models.DateTimeField(verbose_name=_('Start Date & Time'))
    end_datetime = models.DateTimeField(verbose_name=_('End Date & Time'))
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='other',
        verbose_name=_('Event Type')
    )
    image = models.ImageField(
        upload_to='events/',
        blank=True,
        null=True,
        verbose_name=_('Event Image')
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='organized_events',
        verbose_name=_('Organizer')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Is Published')
    )
    registration_required = models.BooleanField(
        default=False,
        verbose_name=_('Registration Required')
    )
    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Registration Deadline'),
        help_text=_('Deadline for event registration')
    )
    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Max Participants')
    )
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Capacity'),
        help_text=_('Total capacity for the event (same as max_participants if not specified)')
    )
    waitlist_enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enable Waitlist'),
        help_text=_('Allow users to join waitlist when event is full')
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Language')
    )
    related_resources = models.ManyToManyField(
        'downloads.Document',
        blank=True,
        related_name='events',
        verbose_name=_('Related Resources'),
        help_text=_('Documents related to this event')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ['start_datetime']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(Event, self.title, self.pk, fallback='event')
        # Set capacity to max_participants if not specified
        if not self.capacity and self.max_participants:
            self.capacity = self.max_participants
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('diaspora:event_detail', kwargs={'slug': self.slug})
    
    def get_registered_count(self):
        """Get the number of registered participants."""
        return self.registrations.count()
    
    def is_full(self):
        """Check if event is at capacity."""
        if not self.capacity:
            return False
        return self.get_registered_count() >= self.capacity
    
    def spots_remaining(self):
        """Get number of spots remaining."""
        if not self.capacity:
            return None
        remaining = self.capacity - self.get_registered_count()
        return max(0, remaining)


class Testimonial(models.Model):
    """
    Testimonial model for testimonials from Cameroonians in Lazio.
    """
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
        ('it', _('Italiano')),
    ]
    
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Title/Position'),
        help_text=_('e.g., "Student at Sapienza University" or "Software Engineer"')
    )
    testimonial = models.TextField(verbose_name=_('Testimonial'))
    image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        verbose_name=_('Photo')
    )
    location = models.CharField(
        max_length=200,
        default='Lazio, Italy',
        verbose_name=_('Location')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Featured'),
        help_text=_('Featured testimonials appear on the main diaspora page.')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Is Published')
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Language')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Testimonial')
        verbose_name_plural = _('Testimonials')
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.title or 'Testimonial'}"


class SuccessStory(models.Model):
    """
    Success story model with images for diaspora success stories.
    """
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
        ('it', _('Italiano')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    person_name = models.CharField(max_length=200, verbose_name=_('Person Name'))
    person_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Person Title/Position')
    )
    story = models.TextField(verbose_name=_('Success Story'))
    featured_image = models.ImageField(
        upload_to='success_stories/',
        blank=True,
        null=True,
        verbose_name=_('Featured Image')
    )
    additional_images = models.ManyToManyField(
        'SuccessStoryImage',
        blank=True,
        related_name='success_stories',
        verbose_name=_('Additional Images')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Featured'),
        help_text=_('Featured stories appear on the main diaspora page.')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Is Published')
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Language')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Success Story')
        verbose_name_plural = _('Success Stories')
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(
                SuccessStory,
                self.title,
                self.pk,
                fallback='success-story',
            )
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('diaspora:success_story_detail', kwargs={'slug': self.slug})


class SuccessStoryImage(models.Model):
    """
    Additional images for success stories.
    """
    image = models.ImageField(
        upload_to='success_stories/additional/',
        verbose_name=_('Image')
    )
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Caption')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Success Story Image')
        verbose_name_plural = _('Success Story Images')
    
    def __str__(self):
        return self.caption or f"Image {self.id}"


class LifeInItaly(models.Model):
    """
    Information about life in Italy (bureaucracy, health, documents).
    """
    CATEGORY_CHOICES = [
        ('bureaucracy', _('Bureaucracy')),
        ('health', _('Healthcare')),
        ('documents', _('Documents & Permits')),
        ('housing', _('Housing')),
        ('work', _('Work & Employment')),
        ('education', _('Education')),
        ('transportation', _('Transportation')),
        ('other', _('Other')),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('Français')),
        ('it', _('Italiano')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name=_('Category')
    )
    content = models.TextField(verbose_name=_('Content'))
    image = models.ImageField(
        upload_to='life_in_italy/',
        blank=True,
        null=True,
        verbose_name=_('Image')
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_('Featured'),
        help_text=_('Featured articles appear on the main diaspora page.')
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_('Is Published')
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Language')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Life in Italy')
        verbose_name_plural = _('Life in Italy Articles')
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug(
                LifeInItaly,
                self.title,
                self.pk,
                fallback='life-in-italy',
            )
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('diaspora:life_in_italy_detail', kwargs={'slug': self.slug})
