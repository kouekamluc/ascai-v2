"""
URL configuration for core app.
"""
from django.urls import path
from .views import (
    HomeView,
    LeadershipView,
    PremiumServicesView,
    EventsPartialView,
    EventsLoadMoreView,
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('leadership/', LeadershipView.as_view(), name='leadership'),
    path('premium-services/', PremiumServicesView.as_view(), name='premium_services'),
    path('events/partial/', EventsPartialView.as_view(), name='events_partial'),
    path('events/load-more/', EventsLoadMoreView.as_view(), name='events_load_more'),
]
