"""
Models for gallery app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from apps.diaspora.models import Event

User = get_user_model()


class GalleryAlbum(models.Model):
    """Gallery album model."""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    cover_image = models.ImageField(
        upload_to='gallery/albums/',
        blank=True,
        null=True,
        verbose_name=_('Cover Image')
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='albums',
        verbose_name=_('Related Event')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_albums',
        verbose_name=_('Created By')
    )
    
    class Meta:
        verbose_name = _('Gallery Album')
        verbose_name_plural = _('Gallery Albums')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('gallery:album_detail', kwargs={'pk': self.pk})


class GalleryImage(models.Model):
    """Gallery image model."""
    album = models.ForeignKey(
        GalleryAlbum,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Album')
    )
    image = models.ImageField(upload_to='gallery/images/', verbose_name=_('Image'))
    caption = models.CharField(max_length=200, blank=True, verbose_name=_('Caption'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Gallery Image')
        verbose_name_plural = _('Gallery Images')
        ordering = ['order', 'uploaded_at']
    
    def __str__(self):
        return f"Image in {self.album.title}"


class GalleryVideo(models.Model):
    """Gallery video model for YouTube/Vimeo embeds."""
    VIDEO_TYPE_CHOICES = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    video_type = models.CharField(
        max_length=10,
        choices=VIDEO_TYPE_CHOICES,
        default='youtube',
        verbose_name=_('Video Type')
    )
    video_id = models.CharField(
        max_length=100,
        verbose_name=_('Video ID'),
        help_text=_('For YouTube: enter the video ID (e.g., dQw4w9WgXcQ). For Vimeo: enter the video ID from the URL.')
    )
    thumbnail = models.ImageField(
        upload_to='gallery/videos/',
        blank=True,
        null=True,
        verbose_name=_('Thumbnail')
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='videos',
        verbose_name=_('Related Event')
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_videos',
        verbose_name=_('Created By')
    )
    
    class Meta:
        verbose_name = _('Gallery Video')
        verbose_name_plural = _('Gallery Videos')
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_embed_url(self):
        """Get the embed URL for the video."""
        if self.video_type == 'youtube':
            return f"https://www.youtube.com/embed/{self.video_id}"
        elif self.video_type == 'vimeo':
            return f"https://player.vimeo.com/video/{self.video_id}"
        return None
    
    def get_thumbnail_url(self):
        """Get thumbnail URL from video service if not uploaded."""
        if self.thumbnail:
            return self.thumbnail.url
        if self.video_type == 'youtube':
            return f"https://img.youtube.com/vi/{self.video_id}/maxresdefault.jpg"
        elif self.video_type == 'vimeo':
            # Vimeo requires API call for thumbnail, so we'll use a placeholder
            return None
        return None
