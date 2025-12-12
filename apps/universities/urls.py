"""
URL configuration for universities app.
"""
from django.urls import path
from .views import UniversityListView, UniversityDetailView, toggle_save_university

app_name = 'universities'

urlpatterns = [
    path('', UniversityListView.as_view(), name='index'),
    path('<slug:slug>/', UniversityDetailView.as_view(), name='detail'),
    path('<slug:slug>/toggle-save/', toggle_save_university, name='toggle_save'),
]


























