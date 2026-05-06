"""
URL configuration for core app.
"""
from django.urls import path
from .views import (
    HomeView,
    LeadershipView,
    PremiumServicesView,
    SponsorshipView,
    EventsPartialView,
    EventsLoadMoreView,
    sponsor_one_pager_pdf,
    track_conversion,
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('leadership/', LeadershipView.as_view(), name='leadership'),
    path('premium-services/', PremiumServicesView.as_view(), name='premium_services'),
    path('impact-sponsorship/', SponsorshipView.as_view(), name='sponsorship'),
    path('impact-sponsorship/one-pager.pdf', sponsor_one_pager_pdf, name='sponsor_one_pager'),
    path('track/<str:event_type>/', track_conversion, name='track_conversion'),
    path('events/partial/', EventsPartialView.as_view(), name='events_partial'),
    path('events/load-more/', EventsLoadMoreView.as_view(), name='events_load_more'),
]
