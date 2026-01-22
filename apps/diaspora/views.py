"""
Views for diaspora app.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from .models import News, Event, Testimonial, SuccessStory, LifeInItaly
from .forms import StorySubmissionForm
from apps.dashboard.models import UserStorySubmission, StoryImage, EventRegistration


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
        
        # Add absolute image URL for meta tags
        if self.object.image:
            context['image_url'] = self.request.build_absolute_uri(self.object.image.url)
        else:
            context['image_url'] = None
        
        return context


class EventListView(ListView):
    """Enhanced list view for events with filtering and calendar toggle."""
    model = Event
    template_name = 'diaspora/event_list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_template_names(self):
        """Return different template for HTMX pagination requests."""
        view_type = self.request.GET.get('view', 'list')
        if view_type == 'calendar':
            return ['diaspora/events/calendar.html']
        if self.request.headers.get('HX-Request') and self.request.GET.get('page'):
            return ['diaspora/partials/event_list_partial.html']
        return [self.template_name]
    
    def get_queryset(self):
        queryset = Event.objects.filter(is_published=True)
        
        # Filter by event type
        event_type = self.request.GET.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        # Filter by date
        date_filter = self.request.GET.get('date_filter', 'upcoming')
        if date_filter == 'past':
            queryset = queryset.filter(end_datetime__lt=timezone.now())
        else:  # upcoming
            queryset = queryset.filter(start_datetime__gte=timezone.now())
        
        # Filter by location
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        language = self.request.GET.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        return queryset.order_by('start_datetime')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_type'] = self.request.GET.get('view', 'list')
        context['filter_event_type'] = self.request.GET.get('event_type', '')
        context['filter_date'] = self.request.GET.get('date_filter', 'upcoming')
        context['filter_location'] = self.request.GET.get('location', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['featured_events'] = Event.objects.filter(
            is_published=True,
            start_datetime__gte=timezone.now()
        ).order_by('start_datetime')[:6]
        return context


class EventDetailView(DetailView):
    """Enhanced detail view for events with registration info."""
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
        
        # Registration info
        if self.object.registration_required:
            context['registered_count'] = self.object.get_registered_count()
            context['spots_remaining'] = self.object.spots_remaining()
            context['is_full'] = self.object.is_full()
            context['can_register'] = (
                not context['is_past'] and
                not context['is_full'] and
                (not self.object.registration_deadline or self.object.registration_deadline > timezone.now())
            )
            
            # Check if user is registered
            if self.request.user.is_authenticated:
                context['is_registered'] = EventRegistration.objects.filter(
                    event=self.object,
                    user=self.request.user
                ).exists()
            else:
                context['is_registered'] = False
        
        # Add absolute image URL for meta tags
        if self.object.image:
            context['image_url'] = self.request.build_absolute_uri(self.object.image.url)
        else:
            context['image_url'] = None
        
        return context


class EventCalendarView(TemplateView):
    """Full calendar view for events."""
    template_name = 'diaspora/events/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get events for the calendar
        context['events'] = Event.objects.filter(
            is_published=True
        ).order_by('start_datetime')
        return context


class MyEventsView(LoginRequiredMixin, ListView):
    """User's registered events."""
    model = EventRegistration
    template_name = 'diaspora/events/my_events.html'
    context_object_name = 'registrations'
    paginate_by = 12
    
    def get_queryset(self):
        return EventRegistration.objects.filter(
            user=self.request.user
        ).select_related('event').order_by('-registered_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Separate upcoming and past events
        context['upcoming_registrations'] = [
            reg for reg in self.get_queryset()
            if reg.event.start_datetime >= now
        ]
        context['past_registrations'] = [
            reg for reg in self.get_queryset()
            if reg.event.end_datetime < now
        ]
        
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


# Story Submission Views

class PublicStorySubmissionView(LoginRequiredMixin, CreateView):
    """Public multi-step story submission form."""
    model = UserStorySubmission
    form_class = StorySubmissionForm
    template_name = 'diaspora/stories/submit.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = 'pending'
        messages.success(self.request, _('Your story has been submitted successfully! It will be reviewed by our team.'))
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('diaspora:story_submission_success', kwargs={'pk': self.object.pk})


class StorySubmissionSuccessView(LoginRequiredMixin, DetailView):
    """Success page after story submission."""
    model = UserStorySubmission
    template_name = 'diaspora/stories/submit_success.html'
    context_object_name = 'submission'
    
    def get_queryset(self):
        return UserStorySubmission.objects.filter(user=self.request.user)


class MyStoriesView(LoginRequiredMixin, ListView):
    """User's story submissions."""
    model = UserStorySubmission
    template_name = 'diaspora/stories/my_stories.html'
    context_object_name = 'stories'
    paginate_by = 12
    
    def get_queryset(self):
        return UserStorySubmission.objects.filter(
            user=self.request.user
        ).order_by('-submitted_at')


class StorySubmissionDetailView(LoginRequiredMixin, DetailView):
    """View submission details and status."""
    model = UserStorySubmission
    template_name = 'diaspora/stories/submission_detail.html'
    context_object_name = 'submission'
    
    def get_queryset(self):
        return UserStorySubmission.objects.filter(user=self.request.user)

