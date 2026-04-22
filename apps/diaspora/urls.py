"""
URL configuration for diaspora app.
"""
from django.urls import path
from .views import (
    DiasporaIndexView, NewsListView, NewsDetailView,
    EventListView, EventDetailView, EventCalendarView, MyEventsView,
    TestimonialListView,
    SuccessStoryListView, SuccessStoryDetailView,
    LifeInItalyListView, LifeInItalyDetailView,
    event_register, event_unregister,
    PublicStorySubmissionView, StorySubmissionSuccessView,
    MyStoriesView, StorySubmissionDetailView
)

app_name = 'diaspora'

urlpatterns = [
    path('', DiasporaIndexView.as_view(), name='index'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('events/', EventListView.as_view(), name='event_list'),
    path('events/calendar/', EventCalendarView.as_view(), name='event_calendar'),
    path('events/my-events/', MyEventsView.as_view(), name='my_events'),
    path('events/<slug:slug>/register/', event_register, name='event_register'),
    path('events/<slug:slug>/unregister/', event_unregister, name='event_unregister'),
    path('events/<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
    path('testimonials/', TestimonialListView.as_view(), name='testimonial_list'),
    path('success-stories/', SuccessStoryListView.as_view(), name='success_story_list'),
    path('success-stories/<slug:slug>/', SuccessStoryDetailView.as_view(), name='success_story_detail'),
    path('life-in-italy/', LifeInItalyListView.as_view(), name='life_in_italy_list'),
    path('life-in-italy/<slug:slug>/', LifeInItalyDetailView.as_view(), name='life_in_italy_detail'),
    # Story Submissions
    path('stories/submit/', PublicStorySubmissionView.as_view(), name='story_submit'),
    path('stories/submit/<int:pk>/success/', StorySubmissionSuccessView.as_view(), name='story_submission_success'),
    path('stories/my-stories/', MyStoriesView.as_view(), name='my_stories'),
    path('stories/<int:pk>/', StorySubmissionDetailView.as_view(), name='story_submission_detail'),
]
