"""
URL configuration for gallery app.
"""
from django.urls import path
from .views import GalleryListView, AlbumDetailView, VideoListView, image_lightbox

app_name = 'gallery'

urlpatterns = [
    path('', GalleryListView.as_view(), name='index'),
    path('<int:pk>/', AlbumDetailView.as_view(), name='album_detail'),
    path('videos/', VideoListView.as_view(), name='video_list'),
    path('image/<int:image_id>/lightbox/', image_lightbox, name='image_lightbox'),
]

