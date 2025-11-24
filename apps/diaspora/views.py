"""
Views for diaspora app.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import News, Event


class DiasporaIndexView(TemplateView):
    """Main diaspora page."""
    template_name = 'diaspora/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_news'] = News.objects.filter(is_published=True)[:5]
        context['upcoming_events'] = Event.objects.filter(
            is_published=True,
            start_datetime__gte=timezone.now()
        )[:5]
        return context


class NewsListView(ListView):
    """List view for news articles."""
    model = News
    template_name = 'diaspora/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = News.objects.filter(is_published=True)
        category = self.request.GET.get('category')
        language = self.request.GET.get('language')
        
        if category:
            queryset = queryset.filter(category=category)
        if language:
            queryset = queryset.filter(language=language)
        
        return queryset.order_by('-published_at', '-created_at')


class NewsDetailView(DetailView):
    """Detail view for news articles."""
    model = News
    template_name = 'diaspora/news_detail.html'
    context_object_name = 'news'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return News.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_news'] = News.objects.filter(
            category=self.object.category,
            is_published=True
        ).exclude(pk=self.object.pk)[:3]
        return context


class EventListView(ListView):
    """List view for events."""
    model = Event
    template_name = 'diaspora/event_list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Event.objects.filter(is_published=True)
        
        # Filter by date
        date_filter = self.request.GET.get('date_filter', 'upcoming')
        if date_filter == 'past':
            queryset = queryset.filter(end_datetime__lt=timezone.now())
        else:  # upcoming
            queryset = queryset.filter(start_datetime__gte=timezone.now())
        
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        return queryset.order_by('start_datetime')


class EventDetailView(DetailView):
    """Detail view for events."""
    model = Event
    template_name = 'diaspora/event_detail.html'
    context_object_name = 'event'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Event.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_past'] = self.object.end_datetime < timezone.now()
        context['related_events'] = Event.objects.filter(
            is_published=True
        ).exclude(pk=self.object.pk)[:3]
        return context

