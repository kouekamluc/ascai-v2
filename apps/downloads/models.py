"""
Models for downloads app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

User = get_user_model()


class Document(models.Model):
    """Document model for downloadable files."""
    CATEGORY_CHOICES = [
        ('reddito', _('Reddìto Forms')),
        ('enrollment', _('Enrollment Documents')),
        ('visa', _('Visa-Related Documents')),
        ('guidelines', _('ASCAI Lazio Guidelines')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    file = models.FileField(upload_to='documents/', verbose_name=_('File'))
    thumbnail = models.ImageField(
        upload_to='documents/thumbnails/',
        blank=True,
        null=True,
        verbose_name=_('Thumbnail'),
        help_text=_('Thumbnail image for document preview')
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name=_('Category')
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Tags'),
        help_text=_('Comma-separated tags (e.g., "form, visa, application")')
    )
    download_count = models.PositiveIntegerField(default=0, verbose_name=_('Download Count'))
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('File Size (bytes)'),
        help_text=_('Automatically calculated from file')
    )
    preview_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Preview URL'),
        help_text=_('URL for document preview (e.g., Google Docs viewer)')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_reserved = models.BooleanField(
        default=False,
        verbose_name=_('Reserved Area Only'),
        help_text=_('If checked, this document is only accessible to authenticated users in the reserved area.')
    )
    download_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Download Limit'),
        help_text=_('Maximum number of downloads allowed (leave blank for unlimited)')
    )
    expiry_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Expiry Date'),
        help_text=_('Date after which document is no longer available')
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name=_('Uploaded By')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_type = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_('File Type'),
        help_text=_('Automatically detected from file extension.')
    )
    
    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if self.file:
            extension = self.file.name.split('.')[-1].lower()
            self.file_type = extension
            # Calculate file size
            try:
                self.file_size = self.file.size
            except (AttributeError, OSError):
                pass
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('downloads:document_download', kwargs={'pk': self.pk})
    
    def get_detail_url(self):
        """Get detail page URL."""
        return reverse('downloads:document_detail', kwargs={'pk': self.pk})
    
    def increment_download_count(self):
        """Increment download count."""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def is_expired(self):
        """Check if document has expired."""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        return timezone.now() > self.expiry_date
    
    def can_be_downloaded(self):
        """Check if document can be downloaded."""
        if not self.is_active:
            return False
        if self.is_expired():
            return False
        if self.download_limit and self.download_count >= self.download_limit:
            return False
        return True
    
    def get_file_size_display(self):
        """Get human-readable file size."""
        if not self.file_size:
            return _('Unknown')
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_related_documents(self, limit=5):
        """Get related documents (same category or tags)."""
        from django.db.models import Q
        queryset = Document.objects.filter(
            is_active=True
        ).exclude(pk=self.pk)
        
        # Filter by same category
        if self.category:
            queryset = queryset.filter(category=self.category)
        
        # Filter by tags if available
        if self.tags:
            tag_list = [tag.strip() for tag in self.tags.split(',')]
            tag_query = Q()
            for tag in tag_list:
                tag_query |= Q(tags__icontains=tag)
            queryset = queryset.filter(tag_query)
        
        return queryset[:limit]

