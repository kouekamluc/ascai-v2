"""
URL configuration for diaspora app.
"""
from django.urls import path
from .views import DiasporaIndexView, NewsListView, NewsDetailView, EventListView, EventDetailView

app_name = 'diaspora'

urlpatterns = [
    path('', DiasporaIndexView.as_view(), name='index'),
    path('news/', NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', NewsDetailView.as_view(), name='news_detail'),
    path('events/', EventListView.as_view(), name='event_list'),
    path('events/<slug:slug>/', EventDetailView.as_view(), name='event_detail'),
]

