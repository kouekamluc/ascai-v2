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
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name=_('Category')
    )
    download_count = models.PositiveIntegerField(default=0, verbose_name=_('Download Count'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))
    is_reserved = models.BooleanField(
        default=False,
        verbose_name=_('Reserved Area Only'),
        help_text=_('If checked, this document is only accessible to authenticated users in the reserved area.')
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name=_('Uploaded By')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
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
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('downloads:document_download', kwargs={'pk': self.pk})
    
    def increment_download_count(self):
        """Increment download count."""
        self.download_count += 1
        self.save(update_fields=['download_count'])

