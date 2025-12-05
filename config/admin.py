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

# Import CKEditor 5 widget for rich text editing
CKEditor5Widget = None
try:
    from django_ckeditor_5.widgets import CKEditor5Widget
except (ImportError, AttributeError):
    # CKEditor 5 not available - will use Textarea fallback
    CKEditor5Widget = None


class BaseAdmin(ModelAdmin):
    """
    Base admin class with automatic CKEditor 5 WYSIWYG editor for all TextField fields.
    
    This class automatically replaces all TextField widgets with CKEditor 5,
    providing a powerful rich text editor with formatting options including:
    - Headings, Bold, Italic, Underline
    - Lists (Bulleted and Numbered)
    - Links, Images, Tables
    - Code blocks, Block quotes
    - Font colors and styles
    - And much more (configurable in CKEDITOR_5_CONFIGS)
    
    CKEditor 5 configuration is defined in settings.py under CKEDITOR_5_CONFIGS.
    The 'default' config is used for all fields, but you can specify a different
    config name per field if needed.
    
    If CKEditor 5 is not available, falls back to standard Textarea.
    
    Usage:
        from config.admin import BaseAdmin
        
        @admin.register(Post)
        class PostAdmin(BaseAdmin):
            list_display = ['title', 'author', 'created_at']
            
        # For advanced usage with custom config:
        class AdvancedPostAdmin(BaseAdmin):
            def formfield_for_dbfield(self, db_field, request, **kwargs):
                formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
                if isinstance(db_field, models.TextField) and db_field.name == 'content':
                    formfield.widget.config_name = 'extends'
                return formfield
    """
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Override to use CKEditor 5 widget for all TextField fields.
        """
        if isinstance(db_field, models.TextField):
            if CKEditor5Widget is not None:
                kwargs['widget'] = CKEditor5Widget(config_name='default')
            else:
                kwargs.setdefault('widget', Textarea(attrs={'rows': 10, 'cols': 80}))
        
        return super().formfield_for_dbfield(db_field, request, **kwargs)


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
    
    # Notification counts - items that need admin attention
    from apps.contact.models import ContactSubmission
    from apps.dashboard.models import OrientationSession, StudentQuestion
    
    notification_counts = {
        'new_contact_submissions': ContactSubmission.objects.filter(
            status='new'
        ).count(),
        'pending_mentorship_requests': MentorshipRequest.objects.filter(
            status='pending'
        ).count(),
        'unconfirmed_orientation_sessions': OrientationSession.objects.filter(
            is_confirmed=False
        ).count(),
        'open_support_tickets': SupportTicket.objects.filter(
            status__in=['open', 'pending']
        ).count(),
        'unresolved_student_questions': StudentQuestion.objects.filter(
            is_resolved=False
        ).count(),
    }
    
    # Total notifications count
    total_notifications = sum(notification_counts.values())
    
    # Recent activity (last 5 items)
    recent_news = News.objects.order_by('-created_at')[:5]
    recent_events = Event.objects.filter(
        start_datetime__gte=timezone.now()
    ).order_by('start_datetime')[:5]
    recent_tickets = SupportTicket.objects.filter(
        status__in=['open', 'pending']
    ).order_by('-created_at')[:5]
    
    # Recent enquiries that need attention
    recent_contact_submissions = ContactSubmission.objects.filter(
        status='new'
    ).order_by('-created_at')[:5]
    recent_mentorship_requests = MentorshipRequest.objects.filter(
        status='pending'
    ).order_by('-created_at')[:5]
    recent_orientation_sessions = OrientationSession.objects.filter(
        is_confirmed=False
    ).order_by('-created_at')[:5]
    
    # Add all statistics to context
    context.update({
        'dashboard_stats': stats,
        'content_stats': content_stats,
        'community_stats': community_stats,
        'resource_stats': resource_stats,
        'support_stats': support_stats,
        'mentorship_stats': mentorship_stats,
        'notification_counts': notification_counts,
        'total_notifications': total_notifications,
        'recent_news': recent_news,
        'recent_events': recent_events,
        'recent_tickets': recent_tickets,
        'recent_contact_submissions': recent_contact_submissions,
        'recent_mentorship_requests': recent_mentorship_requests,
        'recent_orientation_sessions': recent_orientation_sessions,
    })
    
    return context


def get_notification_counts():
    """
    Get notification counts for admin sidebar badges.
    
    Returns:
        dict: Dictionary with notification counts for each category
    """
    try:
        from apps.contact.models import ContactSubmission
        from apps.mentorship.models import MentorshipRequest
        from apps.dashboard.models import OrientationSession, StudentQuestion, SupportTicket
        
        counts = {
            'contact': ContactSubmission.objects.filter(status='new').count(),
            'mentorship': MentorshipRequest.objects.filter(status='pending').count(),
            'orientation': OrientationSession.objects.filter(is_confirmed=False).count(),
            'tickets': SupportTicket.objects.filter(status__in=['open', 'pending']).count(),
            'questions': StudentQuestion.objects.filter(is_resolved=False).count(),
        }
        counts['total'] = sum(counts.values())
        return counts
    except Exception:
        # Return zeros if models aren't available (e.g., during migrations)
        return {
            'contact': 0,
            'mentorship': 0,
            'orientation': 0,
            'tickets': 0,
            'questions': 0,
            'total': 0,
        }


def get_notification_navigation(request):
    """
    Get navigation items with notification badge counts.
    
    This function dynamically generates the full navigation with current
    notification counts displayed in the titles.
    
    Args:
        request: The HTTP request object
    
    Returns:
        list: Complete navigation items with badge counts in titles
    """
    counts = get_notification_counts()
    
    # Helper to format title with count badge
    def format_with_badge(title, count):
        if count > 0:
            return f"{title} 🔴 {count}"
        return title
    
    # Return full navigation with notification counts
    return [
        {
            "title": format_with_badge(_("Notifications & Enquiries"), counts['total']),
            "icon": "notifications_active",
            "items": [
                {
                    "title": format_with_badge(_("Contact Messages"), counts['contact']),
                    "icon": "mail",
                    "link": "/admin/contact/contactsubmission/",
                },
                {
                    "title": format_with_badge(_("Mentorship Requests"), counts['mentorship']),
                    "icon": "school",
                    "link": "/admin/mentorship/mentorshiprequest/",
                },
                {
                    "title": format_with_badge(_("Orientation Sessions"), counts['orientation']),
                    "icon": "event_note",
                    "link": "/admin/dashboard/orientationsession/",
                },
                {
                    "title": format_with_badge(_("Support Tickets"), counts['tickets']),
                    "icon": "confirmation_number",
                    "link": "/admin/dashboard/supportticket/",
                },
                {
                    "title": format_with_badge(_("Student Questions"), counts['questions']),
                    "icon": "help",
                    "link": "/admin/dashboard/studentquestion/",
                },
            ],
        },
        {
            "title": _("Content Management"),
            "icon": "article",
            "items": [
                {
                    "title": _("News & Announcements"),
                    "icon": "newspaper",
                    "link": "/admin/diaspora/news/",
                },
                {
                    "title": _("Events"),
                    "icon": "event",
                    "link": "/admin/diaspora/event/",
                },
                {
                    "title": _("Success Stories"),
                    "icon": "star",
                    "link": "/admin/diaspora/successstory/",
                },
                {
                    "title": _("Life in Italy"),
                    "icon": "info",
                    "link": "/admin/diaspora/lifeinitaly/",
                },
                {
                    "title": _("Testimonials"),
                    "icon": "rate_review",
                    "link": "/admin/diaspora/testimonial/",
                },
                {
                    "title": _("Forum Categories"),
                    "icon": "category",
                    "link": "/admin/community/forumcategory/",
                },
                {
                    "title": _("Forum Threads"),
                    "icon": "forum",
                    "link": "/admin/community/forumthread/",
                },
                {
                    "title": _("Forum Posts"),
                    "icon": "comment",
                    "link": "/admin/community/forumpost/",
                },
            ],
        },
        {
            "title": _("User Management"),
            "icon": "people",
            "items": [
                {
                    "title": _("Users"),
                    "icon": "person",
                    "link": "/admin/accounts/user/",
                },
                {
                    "title": _("User Documents"),
                    "icon": "description",
                    "link": "/admin/accounts/userdocument/",
                },
                {
                    "title": _("Mentors"),
                    "icon": "school",
                    "link": "/admin/mentorship/mentorprofile/",
                },
                {
                    "title": _("Mentorship Requests"),
                    "icon": "handshake",
                    "link": "/admin/mentorship/mentorshiprequest/",
                },
                {
                    "title": _("Mentorship Messages"),
                    "icon": "message",
                    "link": "/admin/mentorship/mentorshipmessage/",
                },
                {
                    "title": _("Mentor Ratings"),
                    "icon": "star_rate",
                    "link": "/admin/mentorship/mentorrating/",
                },
            ],
        },
        {
            "title": _("Resources & Education"),
            "icon": "folder",
            "items": [
                {
                    "title": _("Universities"),
                    "icon": "account_balance",
                    "link": "/admin/universities/university/",
                },
                {
                    "title": _("University Programs"),
                    "icon": "menu_book",
                    "link": "/admin/universities/universityprogram/",
                },
                {
                    "title": _("Scholarships"),
                    "icon": "card_giftcard",
                    "link": "/admin/scholarships/scholarship/",
                },
                {
                    "title": _("Documents"),
                    "icon": "description",
                    "link": "/admin/downloads/document/",
                },
                {
                    "title": _("Gallery Albums"),
                    "icon": "photo_album",
                    "link": "/admin/gallery/galleryalbum/",
                },
                {
                    "title": _("Gallery Images"),
                    "icon": "photo_library",
                    "link": "/admin/gallery/galleryimage/",
                },
                {
                    "title": _("Gallery Videos"),
                    "icon": "video_library",
                    "link": "/admin/gallery/galleryvideo/",
                },
            ],
        },
        {
            "title": _("Support & Community"),
            "icon": "support_agent",
            "items": [
                {
                    "title": _("Ticket Replies"),
                    "icon": "reply",
                    "link": "/admin/dashboard/ticketreply/",
                },
                {
                    "title": _("Community Groups"),
                    "icon": "groups",
                    "link": "/admin/dashboard/communitygroup/",
                },
                {
                    "title": _("Group Discussions"),
                    "icon": "forum",
                    "link": "/admin/dashboard/groupdiscussion/",
                },
                {
                    "title": _("Group Announcements"),
                    "icon": "campaign",
                    "link": "/admin/dashboard/groupannouncement/",
                },
                {
                    "title": _("User Stories"),
                    "icon": "article",
                    "link": "/admin/dashboard/userstorysubmission/",
                },
            ],
        },
        {
            "title": _("Governance"),
            "icon": "gavel",
            "items": [
                {
                    "title": _("Members"),
                    "icon": "people",
                    "link": "/admin/governance/member/",
                },
                {
                    "title": _("Membership Status"),
                    "icon": "badge",
                    "link": "/admin/governance/membershipstatus/",
                },
                {
                    "title": _("Executive Board"),
                    "icon": "groups",
                    "link": "/admin/governance/executiveboard/",
                },
                {
                    "title": _("Executive Positions"),
                    "icon": "work",
                    "link": "/admin/governance/executiveposition/",
                },
                {
                    "title": _("Board Meetings"),
                    "icon": "meeting_room",
                    "link": "/admin/governance/boardmeeting/",
                },
                {
                    "title": _("General Assembly"),
                    "icon": "people_outline",
                    "link": "/admin/governance/generalassembly/",
                },
                {
                    "title": _("Elections"),
                    "icon": "how_to_vote",
                    "link": "/admin/governance/election/",
                },
                {
                    "title": _("Financial Transactions"),
                    "icon": "account_balance_wallet",
                    "link": "/admin/governance/financialtransaction/",
                },
                {
                    "title": _("Membership Dues"),
                    "icon": "payment",
                    "link": "/admin/governance/membershipdues/",
                },
                {
                    "title": _("Financial Reports"),
                    "icon": "assessment",
                    "link": "/admin/governance/financialreport/",
                },
            ],
        },
        {
            "title": _("Administration"),
            "icon": "settings",
            "items": [
                {
                    "title": _("Event Registrations"),
                    "icon": "event_available",
                    "link": "/admin/dashboard/eventregistration/",
                },
                {
                    "title": _("Saved Documents"),
                    "icon": "bookmark",
                    "link": "/admin/dashboard/saveddocument/",
                },
            ],
        },
    ]


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



















