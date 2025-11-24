"""
Views for gallery app.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from .models import GalleryAlbum, GalleryImage, GalleryVideo


class GalleryListView(ListView):
    """List view for gallery albums and videos."""
    model = GalleryAlbum
    template_name = 'gallery/album_list.html'
    context_object_name = 'albums'
    paginate_by = 12
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = GalleryVideo.objects.all()[:6]  # Show latest 6 videos
        return context


class AlbumDetailView(DetailView):
    """Detail view for gallery album with images."""
    model = GalleryAlbum
    template_name = 'gallery/album_detail.html'
    context_object_name = 'album'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['images'] = self.object.images.all()
        return context


class VideoListView(ListView):
    """List view for gallery videos."""
    model = GalleryVideo
    template_name = 'gallery/video_list.html'
    context_object_name = 'videos'
    paginate_by = 12


def image_lightbox(request, image_id):
    """HTMX endpoint for image lightbox modal."""
    image = get_object_or_404(GalleryImage, id=image_id)
    return render(request, 'gallery/partials/image_lightbox.html', {
        'image': image
    })

