"""
Models for diaspora app - News, Events, Success Stories.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


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
            self.slug = slugify(self.title)
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
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(verbose_name=_('Description'))
    location = models.CharField(max_length=200, verbose_name=_('Location'))
    start_datetime = models.DateTimeField(verbose_name=_('Start Date & Time'))
    end_datetime = models.DateTimeField(verbose_name=_('End Date & Time'))
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
    max_participants = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Max Participants')
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_('Language')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')
        ordering = ['start_datetime']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('diaspora:event_detail', kwargs={'slug': self.slug})


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
            self.slug = slugify(self.title)
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
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('diaspora:life_in_italy_detail', kwargs={'slug': self.slug})
