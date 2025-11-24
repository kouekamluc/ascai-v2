"""
Views for gallery app.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import GalleryAlbum, GalleryImage


class GalleryListView(ListView):
    """List view for gallery albums."""
    model = GalleryAlbum
    template_name = 'gallery/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12


class AlbumDetailView(DetailView):
    """Detail view for gallery album with images."""
    model = GalleryAlbum
    template_name = 'gallery/album_detail.html'
    context_object_name = 'album'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        return context

