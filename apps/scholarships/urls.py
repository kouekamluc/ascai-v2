"""
URL configuration for scholarships app.
"""
from django.urls import path
from .views import (
    ScholarshipListView,
    ScholarshipDetailView,
    DiscoLazioView,
    toggle_save_scholarship
)

app_name = 'scholarships'

urlpatterns = [
    path('', ScholarshipListView.as_view(), name='index'),
    path('disco-lazio/', DiscoLazioView.as_view(), name='disco_lazio'),
    path('<slug:slug>/', ScholarshipDetailView.as_view(), name='detail'),
    path('<slug:slug>/toggle-save/', toggle_save_scholarship, name='toggle_save'),
]






