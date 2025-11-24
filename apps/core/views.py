"""
Views for core app.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from apps.diaspora.models import News, Event
from django.utils.translation import gettext_lazy as _


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
        
        # Get upcoming events
        from django.utils import timezone
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

