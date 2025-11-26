"""
URL configuration for downloads app.
"""
from django.urls import path
from .views import DownloadListView, document_download, increment_download_count

app_name = 'downloads'

urlpatterns = [
    path('', DownloadListView.as_view(), name='index'),
    path('<int:pk>/download/', document_download, name='document_download'),
    path('<int:pk>/increment-count/', increment_download_count, name='increment_count'),
]

