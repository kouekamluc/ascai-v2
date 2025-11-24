"""
URL configuration for diaspora app.
"""
from django.urls import path
from .views import (
    DiasporaIndexView, NewsListView, NewsDetailView,
    EventListView, EventDetailView,
    TestimonialListView,
    SuccessStoryListView, SuccessStoryDetailView,
    LifeInItalyListView, LifeInItalyDetailView
)

app_name = 'diaspora'

urlpatterns = [
    path('', DiasporaIndexView.as_view(), name='index'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('events/', EventListView.as_view(), name='event_list'),
    path('events/<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    path('testimonials/', TestimonialListView.as_view(), name='testimonial_list'),
    path('success-stories/', SuccessStoryListView.as_view(), name='success_story_list'),
    path('success-stories/<slug:slug>/', SuccessStoryDetailView.as_view(), name='success_story_detail'),
    path('life-in-italy/', LifeInItalyListView.as_view(), name='life_in_italy_list'),
    path('life-in-italy/<slug:slug>/', LifeInItalyDetailView.as_view(), name='life_in_italy_detail'),
]

