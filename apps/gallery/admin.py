"""
Admin configuration for gallery app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import GalleryAlbum, GalleryImage


class GalleryImageInline(admin.TabularInline):
    """Inline admin for gallery images."""
    model = GalleryImage
    extra = 3
    fields = ['image', 'caption', 'order']


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    """Admin interface for GalleryAlbum."""
    list_display = ['title', 'event', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description']
    raw_id_fields = ['event', 'created_by']
    inlines = [GalleryImageInline]


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """Admin interface for GalleryImage."""
    list_display = ['album', 'caption', 'order', 'uploaded_at']
    list_filter = ['uploaded_at', 'album']
    search_fields = ['caption', 'album__title']
    raw_id_fields = ['album']

