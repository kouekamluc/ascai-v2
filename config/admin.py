"""
Custom admin site configuration for ASCAI Lazio.
"""
from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.forms import Textarea
from unfold.admin import ModelAdmin, TabularInline, StackedInline

# Try to import WYSIWYG widget - fallback to Textarea if not available
# Note: WYSIWYG widget availability depends on django-unfold version
# In some versions, the widget may not be directly importable
WysiwygWidget = None
try:
    # Try different possible import paths for WYSIWYG widget
    from unfold.widgets import WysiwygWidget
except (ImportError, AttributeError):
    try:
        from unfold.contrib.forms.widgets import WysiwygWidget
    except (ImportError, AttributeError):
        try:
            from unfold.contrib.forms.widgets import TrixWidget as WysiwygWidget
        except (ImportError, AttributeError):
            # WYSIWYG not available in this version - will use Textarea fallback
            WysiwygWidget = None


class BaseAdmin(ModelAdmin):
    """
    Base admin class with automatic WYSIWYG editor for all TextField fields.
    
    This class automatically replaces all TextField widgets with Unfold's
    WYSIWYG editor (Trix) when available, allowing admins to format content
    with Bold, Italic, Lists, and other formatting options.
    
    If WYSIWYG widget is not available, falls back to standard Textarea.
    
    Usage:
        from config.admin import BaseAdmin
        
        @admin.register(Post)
        class PostAdmin(BaseAdmin):
            list_display = ['title', 'author', 'created_at']
    """
    # Set formfield_overrides based on widget availability
    # Use WYSIWYG widget if available, otherwise fallback to Textarea
    formfield_overrides = {
        models.TextField: {
            'widget': WysiwygWidget if WysiwygWidget is not None else Textarea(attrs={'rows': 10, 'cols': 80}),
        },
    }


def dashboard_callback(request, context):
    """
    Dashboard callback function for Django Unfold admin index page.
    
    This function provides dynamic statistics and data to the admin dashboard,
    giving association administrators immediate insights upon login.
    
    Args:
        request: The HTTP request object
        context: The template context dictionary (modified in-place)
    
    Returns:
        dict: Additional context data to merge with the admin index context
    """
    from apps.accounts.models import User
    from apps.diaspora.models import News, Event, SuccessStory
    from apps.community.models import ForumPost, ForumThread
    from apps.mentorship.models import MentorshipRequest
    from apps.universities.models import University
    from apps.scholarships.models import Scholarship
    from apps.downloads.models import Document
    from apps.dashboard.models import SupportTicket
    
    # Calculate statistics
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'staff_users': User.objects.filter(is_staff=True).count(),
        'recent_users': User.objects.filter(
            date_joined__gte=timezone.now() - timezone.timedelta(days=30)
        ).count(),
    }
    
    # Content statistics
    content_stats = {
        'total_news': News.objects.count(),
        'published_news': News.objects.filter(is_published=True).count(),
        'draft_news': News.objects.filter(is_published=False).count(),
        'total_events': Event.objects.count(),
        'upcoming_events': Event.objects.filter(
            start_datetime__gte=timezone.now(),
            is_published=True
        ).count(),
        'total_stories': SuccessStory.objects.count(),
        'published_stories': SuccessStory.objects.filter(is_published=True).count(),
    }
    
    # Community statistics
    community_stats = {
        'total_forum_posts': ForumPost.objects.count(),
        'total_forum_threads': ForumThread.objects.count(),
        'recent_posts': ForumPost.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count(),
    }
    
    # Resource statistics
    resource_stats = {
        'total_universities': University.objects.count(),
        'total_scholarships': Scholarship.objects.count(),
        'active_scholarships': Scholarship.objects.filter(status='active').count(),
        'total_documents': Document.objects.count(),
    }
    
    # Support statistics
    support_stats = {
        'open_tickets': SupportTicket.objects.filter(
            status__in=['open', 'pending']
        ).count(),
        'total_tickets': SupportTicket.objects.count(),
    }
    
    # Mentorship statistics
    mentorship_stats = {
        'pending_requests': MentorshipRequest.objects.filter(
            status='pending'
        ).count(),
        'active_mentorships': MentorshipRequest.objects.filter(
            status='accepted'
        ).count(),
    }
    
    # Recent activity (last 5 items)
    recent_news = News.objects.order_by('-created_at')[:5]
    recent_events = Event.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')[:5]
    recent_tickets = SupportTicket.objects.filter(
        status__in=['open', 'pending']
    ).order_by('-created_at')[:5]
    
    # Add all statistics to context
    context.update({
        'dashboard_stats': stats,
        'content_stats': content_stats,
        'community_stats': community_stats,
        'resource_stats': resource_stats,
        'support_stats': support_stats,
        'mentorship_stats': mentorship_stats,
        'recent_news': recent_news,
        'recent_events': recent_events,
        'recent_tickets': recent_tickets,
    })
    
    return context


# Configure the default admin site (Unfold will automatically style it)
# These use gettext_lazy so they will be translated based on the current language
admin.site.site_header = _('ASCAI Lazio Administration')
admin.site.site_title = _('ASCAI Lazio Admin')
admin.site.index_title = _('Welcome to ASCAI Lazio Administration')

# Make admin_site available for direct imports (alias to admin.site for compatibility)
admin_site = admin.site

# Export Unfold admin classes for use in app admin.py files
# This allows apps to use: from config.admin import BaseAdmin, ModelAdmin, TabularInline, StackedInline
__all__ = ['admin_site', 'BaseAdmin', 'ModelAdmin', 'TabularInline', 'StackedInline', 'dashboard_callback']



















