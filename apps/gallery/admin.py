"""
Admin configuration for gallery app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import GalleryAlbum, GalleryImage, GalleryVideo


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
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """Admin interface for GalleryImage."""
    list_display = ['album', 'caption', 'order', 'uploaded_at']
    list_filter = ['uploaded_at', 'album']
    search_fields = ['caption', 'album__title']
    raw_id_fields = ['album']


@admin.register(GalleryVideo)
class GalleryVideoAdmin(admin.ModelAdmin):
    """Admin interface for GalleryVideo."""
    list_display = ['title', 'video_type', 'event', 'created_by', 'created_at']
    list_filter = ['video_type', 'created_at', 'event']
    search_fields = ['title', 'description']
    raw_id_fields = ['event', 'created_by']
    fields = ['title', 'description', 'video_type', 'video_id', 'thumbnail', 'event', 'order', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

