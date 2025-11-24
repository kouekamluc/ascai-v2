"""
URL configuration for gallery app.
"""
from django.urls import path
from .views import GalleryListView, AlbumDetailView

app_name = 'gallery'

urlpatterns = [
    path('', GalleryListView.as_view(), name='index'),
    path('<int:pk>/', AlbumDetailView.as_view(), name='album_detail'),
]

