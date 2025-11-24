"""
Views for core app.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from apps.diaspora.models import News, Event
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class HomeView(TemplateView):
    """
    Home page view with latest news, events, and success stories.
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get latest news (published only)
        context['latest_news'] = News.objects.filter(
            is_published=True
        ).order_by('-published_at')[:6]
        
        # Get upcoming events (first 6 for initial display)
        context['upcoming_events'] = Event.objects.filter(
            is_published=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:6]
        
        # Success stories (from News with category 'success_story')
        context['success_stories'] = News.objects.filter(
            is_published=True,
            category='success_story'
        ).order_by('-published_at')[:3]
        
        return context


class EventsPartialView(TemplateView):
    """
    HTMX partial view for events container.
    """
    template_name = 'core/partials/events_partial.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_events'] = Event.objects.filter(
            is_published=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:6]
        return context


class EventsLoadMoreView(TemplateView):
    """
    HTMX view for loading more events (infinite scroll).
    """
    template_name = 'core/partials/events_item.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get offset from request
        try:
            offset = int(self.request.GET.get('offset', 6))
        except (ValueError, TypeError):
            offset = 6
        
        limit = 6
        
        # Get total count
        total_count = Event.objects.filter(
            is_published=True,
            start_datetime__gte=timezone.now()
        ).count()
        
        # Get next batch of events
        events = Event.objects.filter(
            is_published=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[offset:offset + limit]
        
        context['events'] = events
        context['has_more'] = offset + limit < total_count
        context['next_offset'] = offset + limit
        
        return context

