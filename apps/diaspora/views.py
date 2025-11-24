"""
Views for diaspora app.
"""
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from .models import News, Event, Testimonial, SuccessStory, LifeInItaly


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
        context['featured_testimonials'] = Testimonial.objects.filter(
            is_published=True,
            is_featured=True
        )[:3]
        context['featured_success_stories'] = SuccessStory.objects.filter(
            is_published=True,
            is_featured=True
        )[:3]
        context['featured_life_in_italy'] = LifeInItaly.objects.filter(
            is_published=True,
            is_featured=True
        )[:3]
        return context


class NewsListView(ListView):
    """List view for news articles with HTMX pagination."""
    model = News
    template_name = 'diaspora/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 12
    
    def get_template_names(self):
        """Return different template for HTMX pagination requests."""
        if self.request.headers.get('HX-Request') and self.request.GET.get('page'):
            return ['diaspora/partials/news_list_partial.html']
        return [self.template_name]
    
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
    """List view for events with HTMX pagination."""
    model = Event
    template_name = 'diaspora/event_list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_template_names(self):
        """Return different template for HTMX pagination requests."""
        if self.request.headers.get('HX-Request') and self.request.GET.get('page'):
            return ['diaspora/partials/event_list_partial.html']
        return [self.template_name]
    
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


class TestimonialListView(ListView):
    """List view for testimonials."""
    model = Testimonial
    template_name = 'diaspora/testimonial_list.html'
    context_object_name = 'testimonials'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Testimonial.objects.filter(is_published=True)
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(language=language)
        return queryset.order_by('-is_featured', '-created_at')


class SuccessStoryListView(ListView):
    """List view for success stories."""
    model = SuccessStory
    template_name = 'diaspora/success_story_list.html'
    context_object_name = 'success_stories'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = SuccessStory.objects.filter(is_published=True)
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(language=language)
        return queryset.order_by('-is_featured', '-created_at')


class SuccessStoryDetailView(DetailView):
    """Detail view for success stories."""
    model = SuccessStory
    template_name = 'diaspora/success_story_detail.html'
    context_object_name = 'story'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return SuccessStory.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_stories'] = SuccessStory.objects.filter(
            is_published=True
        ).exclude(pk=self.object.pk)[:3]
        return context


class LifeInItalyListView(ListView):
    """List view for life in Italy articles."""
    model = LifeInItaly
    template_name = 'diaspora/life_in_italy_list.html'
    context_object_name = 'articles'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = LifeInItaly.objects.filter(is_published=True)
        category = self.request.GET.get('category')
        language = self.request.GET.get('language')
        
        if category:
            queryset = queryset.filter(category=category)
        if language:
            queryset = queryset.filter(language=language)
        
        return queryset.order_by('-is_featured', '-created_at')


class LifeInItalyDetailView(DetailView):
    """Detail view for life in Italy articles."""
    model = LifeInItaly
    template_name = 'diaspora/life_in_italy_detail.html'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return LifeInItaly.objects.filter(is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_articles'] = LifeInItaly.objects.filter(
            category=self.object.category,
            is_published=True
        ).exclude(pk=self.object.pk)[:3]
        return context

