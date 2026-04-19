"""
Views for core app.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.db import connection
from apps.diaspora.models import News, Event
from apps.downloads.models import Document
from apps.core.models import CommunityService, ServicePartner
from apps.governance.services import get_member_resource_access
from apps.core.membership_content import (
    MEMBER_RESOURCE_COLLECTIONS,
    MEMBERSHIP_BENEFIT_PILLARS,
)
from apps.core.service_catalog import (
    DEFAULT_COMMUNITY_SERVICES,
    DEFAULT_PARTNER_OPPORTUNITIES,
    DEFAULT_REVENUE_CHANNELS,
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def get_premium_service_context():
    """Return services and partner opportunities, using DB content when available."""
    try:
        services = list(
            CommunityService.objects.filter(is_active=True, is_featured=True)
            .select_related("partner")
            .order_by("display_order", "title")
        )
        partners = list(
            ServicePartner.objects.filter(is_active=True, is_featured=True)
            .order_by("display_order", "name")
        )
    except Exception as e:
        logger.error("Error loading premium service content: %s", str(e), exc_info=True)
        services = []
        partners = []

    if services:
        service_cards = [
            {
                "title": service.title,
                "category": service.get_category_display(),
                "audience": service.audience,
                "summary": service.summary,
                "access": service.get_access_level_display(),
                "delivery": service.get_delivery_mode_display(),
                "revenue": service.get_revenue_stream_display(),
                "association_benefit": service.association_benefit,
                "partner_name": service.partner.name if service.partner else "",
            }
            for service in services
        ]
    else:
        service_cards = DEFAULT_COMMUNITY_SERVICES

    if partners:
        partner_cards = [
            {
                "title": partner.name,
                "summary": partner.short_description,
                "listing_fee_eur": f"{partner.annual_listing_fee:.0f}",
                "value": (
                    f"{partner.get_category_display()} visibility"
                    + (f" in {partner.cities_served}" if partner.cities_served else "")
                ),
                "verification_status": partner.get_verification_status_display(),
            }
            for partner in partners
        ]
    else:
        partner_cards = DEFAULT_PARTNER_OPPORTUNITIES

    return {
        "community_service_cards": service_cards,
        "partner_opportunity_cards": partner_cards,
        "revenue_channel_cards": DEFAULT_REVENUE_CHANNELS,
        "service_partner_listing_fee": "20",
    }


class ExecutiveBoardPublicContextMixin:
    """Adds executive_board and executive_positions from governance data."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from apps.governance.utils import get_current_public_executive_board
            board, positions = get_current_public_executive_board()
            context['executive_board'] = board
            context['executive_positions'] = positions
        except Exception as e:
            logger.error(
                'Error fetching executive board for public page: %s',
                str(e),
                exc_info=True,
            )
            context['executive_board'] = None
            context['executive_positions'] = []
        return context


class HomeView(ExecutiveBoardPublicContextMixin, TemplateView):
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

        context['membership_access'] = get_member_resource_access(self.request.user)
        context['membership_benefits'] = MEMBERSHIP_BENEFIT_PILLARS
        context['member_resource_collections'] = MEMBER_RESOURCE_COLLECTIONS
        context.update(get_premium_service_context())

        try:
            context['premium_resource_count'] = Document.objects.filter(
                is_active=True,
                is_reserved=True,
            ).count()
        except Exception as e:
            logger.error(f"Error fetching premium resource count: {str(e)}", exc_info=True)
            context['premium_resource_count'] = 0
        
        return context


class LeadershipView(ExecutiveBoardPublicContextMixin, TemplateView):
    """Public page listing current executive board members."""
    template_name = 'core/leadership.html'


class PremiumServicesView(TemplateView):
    """Public page for monetisable premium services and partner offers."""
    template_name = 'core/premium_services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['membership_access'] = get_member_resource_access(self.request.user)
        context.update(get_premium_service_context())
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


def serve_media_file(request, path):
    """
    Serve media files in production when S3 is not enabled.
    This view handles file serving when DEBUG=False.
    """
    from django.conf import settings
    from django.http import Http404, FileResponse
    import os
    from pathlib import Path
    
    # Only serve media files if S3 is not enabled
    if getattr(settings, 'USE_S3', False):
        raise Http404("Media files are served from S3")
    
    # Get the full file path
    media_root = settings.MEDIA_ROOT
    if isinstance(media_root, str):
        media_root = Path(media_root)
    elif hasattr(media_root, 'path'):
        media_root = Path(media_root.path)
    else:
        media_root = Path(media_root)
    
    file_path = media_root / path
    
    # Security: Ensure the file is within MEDIA_ROOT
    try:
        file_path = file_path.resolve()
        media_root_resolved = media_root.resolve()
        if not str(file_path).startswith(str(media_root_resolved)):
            raise Http404("Invalid file path")
    except (ValueError, OSError):
        raise Http404("Invalid file path")
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"Media file not found: {file_path}")
        raise Http404("File not found")
    
    # Determine content type
    import mimetypes
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # Serve the file
    try:
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type
        )
        # Set appropriate headers
        response['Content-Disposition'] = f'inline; filename="{file_path.name}"'
        return response
    except IOError:
        logger.error(f"Error reading media file: {file_path}")
        raise Http404("Error reading file")


def serve_static_file(request, path):
    """
    Serve static files in production when S3 is not enabled.
    This view handles static file serving when DEBUG=False.
    WhiteNoise should handle this, but this provides a reliable fallback.
    """
    from django.conf import settings
    from django.http import Http404, FileResponse
    from pathlib import Path
    
    # Only serve static files if S3 is not enabled
    if getattr(settings, 'USE_S3', False):
        raise Http404("Static files are served from S3")
    
    # Get the full file path
    static_root = settings.STATIC_ROOT
    if isinstance(static_root, str):
        static_root = Path(static_root)
    elif hasattr(static_root, 'path'):
        static_root = Path(static_root.path)
    else:
        static_root = Path(static_root)
    
    file_path = static_root / path
    
    # Security: Ensure the file is within STATIC_ROOT
    try:
        file_path = file_path.resolve()
        static_root_resolved = static_root.resolve()
        if not str(file_path).startswith(str(static_root_resolved)):
            raise Http404("Invalid file path")
    except (ValueError, OSError):
        raise Http404("Invalid file path")
    
    # Check if file exists
    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"Static file not found: {file_path}")
        raise Http404("File not found")
    
    # Determine content type
    import mimetypes
    content_type, _ = mimetypes.guess_type(str(file_path))
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # Serve the file with cache headers
    try:
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type
        )
        # Set cache headers for static files
        response['Cache-Control'] = 'public, max-age=31536000'
        return response
    except IOError:
        logger.error(f"Error reading static file: {file_path}")
        raise Http404("Error reading file")


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
