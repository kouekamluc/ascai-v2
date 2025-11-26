"""
Views for core app.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.db import connection
from apps.diaspora.models import News, Event
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class HomeView(TemplateView):
    """
    Home page view with latest news, events, and success stories.
    """
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get latest news (published only) - with error handling
        try:
            context['latest_news'] = News.objects.filter(
                is_published=True
            ).order_by('-published_at')[:6]
        except Exception as e:
            logger.error(f"Error fetching latest news: {str(e)}", exc_info=True)
            context['latest_news'] = []
        
        # Get upcoming events (first 6 for initial display) - with error handling
        try:
            context['upcoming_events'] = Event.objects.filter(
                is_published=True,
                start_datetime__gte=timezone.now()
            ).order_by('start_datetime')[:6]
        except Exception as e:
            logger.error(f"Error fetching upcoming events: {str(e)}", exc_info=True)
            context['upcoming_events'] = []
        
        # Success stories (from News with category 'success_story') - with error handling
        try:
            context['success_stories'] = News.objects.filter(
                is_published=True,
                category='success_story'
            ).order_by('-published_at')[:3]
        except Exception as e:
            logger.error(f"Error fetching success stories: {str(e)}", exc_info=True)
            context['success_stories'] = []
        
        return context


class HealthCheckView(TemplateView):
    """
    Simple healthcheck endpoint that doesn't require database queries.
    Used for deployment healthchecks.
    """
    def get(self, request, *args, **kwargs):
        # Ultra-simple check - just return 200 OK immediately
        # No database queries, no template rendering, just HTTP 200
        return HttpResponse("OK", status=200, content_type="text/plain")


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

