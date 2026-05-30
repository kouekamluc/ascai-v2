"""
Views for core app.
"""
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils.html import strip_tags
from apps.diaspora.models import News, Event, Testimonial, SuccessStory
from apps.downloads.models import Document
from apps.core.models import CommunityService, ConversionEvent, ServicePartner
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
User = get_user_model()


STUDENT_SUCCESS_PATHWAY = [
    {
        "step": _("Arrive"),
        "title": _("Settle faster in Lazio"),
        "summary": _("Residence, housing, university, health, and city-life guidance in one trusted student dashboard."),
    },
    {
        "step": _("Study"),
        "title": _("Find funding and academic options"),
        "summary": _("Scholarship discovery, university comparisons, deadlines, documents, and peer advice from students who already passed through the process."),
    },
    {
        "step": _("Belong"),
        "title": _("Meet mentors and community"),
        "summary": _("Practical mentorship, events, discussion groups, and a visible Cameroonian academic network across Rome and Lazio."),
    },
    {
        "step": _("Advance"),
        "title": _("Build a credible future"),
        "summary": _("Stories, leadership opportunities, referrals, and institutional visibility that help students grow beyond survival mode."),
    },
]


SPONSOR_IMPACT_METRICS = [
    {
        "label": _("Student retention"),
        "value": _("Orientation"),
        "summary": _("Help new arrivals understand the administrative steps that often decide whether they stay enrolled and stable."),
    },
    {
        "label": _("Integration"),
        "value": _("Community"),
        "summary": _("Support bridge-building between Cameroonian students, Italian institutions, local services, and diaspora families."),
    },
    {
        "label": _("Visibility"),
        "value": _("Reporting"),
        "summary": _("Give sponsors a clear, reportable view of activities, resource usage, events, and student support outcomes."),
    },
]


PLATFORM_AUDIENCE_CARDS = [
    {
        "audience": _("New students"),
        "promise": _("Know what to do next after arrival"),
        "summary": _("Orientation, residence guidance, scholarships, universities, documents, and trusted first contacts in one guided dashboard."),
        "cta": _("Start student journey"),
        "url_name": "account_signup",
    },
    {
        "audience": _("Members"),
        "promise": _("Turn membership into visible value"),
        "summary": _("Dues, elections, assemblies, member resources, bureau messages, events, and community groups are connected to one member space."),
        "cta": _("Join ASCAI"),
        "url_name": "account_signup",
    },
    {
        "audience": _("Mentors"),
        "promise": _("Help students without losing structure"),
        "summary": _("Mentor profiles, requests, messaging, and availability tools make support easier to offer and easier to track."),
        "cta": _("Become a mentor"),
        "url_name": "mentorship:index",
    },
    {
        "audience": _("Sponsors and partners"),
        "promise": _("Support outcomes people can measure"),
        "summary": _("Impact metrics, verified services, events, and sponsor-ready reporting make ASCAI easier to trust and fund."),
        "cta": _("See impact plan"),
        "url_name": "core:sponsorship",
    },
]


SPONSOR_PACKAGES = [
    {
        "name": _("Student Success Sponsor"),
        "audience": _("Universities, regional offices, foundations"),
        "summary": _("Fund orientation sessions, scholarship guidance, and practical student support for Cameroonian newcomers in Lazio."),
        "returns": _("Impact report, public recognition, event presence, and student-facing visibility."),
    },
    {
        "name": _("Institutional Bridge Partner"),
        "audience": _("Embassy, consular offices, integration services"),
        "summary": _("Use ASCAI as an organized channel for communication, verified resources, and community feedback."),
        "returns": _("Cleaner outreach, reduced misinformation, documented community needs, and trusted local coordination."),
    },
    {
        "name": _("Diaspora Innovation Partner"),
        "audience": _("Companies, service providers, banks, remittance operators"),
        "summary": _("Reach Cameroonian students and families through verified, ethical, needs-based offers."),
        "returns": _("Partner listing, targeted campaigns, feedback loops, and measurable referral opportunities."),
    },
]


INSTITUTIONAL_PROOF_POINTS = [
    _("A multilingual platform for English, French, and Italian audiences."),
    _("Authenticated student dashboards for resources, requests, documents, events, and mentorship."),
    _("Governance and dues features that show ASCAI is building an accountable association, not only a social page."),
    _("A sponsorship story that connects student success, integration, community safety, and diaspora diplomacy."),
]


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


def get_impact_metrics():
    """Aggregate sponsor-facing numbers from existing platform activity."""
    from apps.dashboard.models import EventRegistration, OrientationSession
    from apps.mentorship.models import MentorshipRequest
    from apps.scholarships.models import SavedScholarship

    try:
        metrics = {
            "active_members": User.objects.filter(is_active=True, is_approved=True).count(),
            "orientation_requests": OrientationSession.objects.count(),
            "mentorship_requests": MentorshipRequest.objects.count(),
            "scholarship_saves": SavedScholarship.objects.count(),
            "event_registrations": EventRegistration.objects.count(),
        }
    except Exception as e:
        logger.error("Error loading impact metrics: %s", str(e), exc_info=True)
        metrics = {
            "active_members": 0,
            "orientation_requests": 0,
            "mentorship_requests": 0,
            "scholarship_saves": 0,
            "event_registrations": 0,
        }

    return [
        {
            "key": "active_members",
            "label": _("Active members"),
            "value": metrics["active_members"],
            "summary": _("Approved members reachable through ASCAI channels."),
        },
        {
            "key": "orientation_requests",
            "label": _("Orientation requests"),
            "value": metrics["orientation_requests"],
            "summary": _("Students asking for practical settlement guidance."),
        },
        {
            "key": "mentorship_requests",
            "label": _("Mentorship requests"),
            "value": metrics["mentorship_requests"],
            "summary": _("Peer and mentor connections initiated through the platform."),
        },
        {
            "key": "scholarship_saves",
            "label": _("Scholarship saves"),
            "value": metrics["scholarship_saves"],
            "summary": _("Funding opportunities students marked for action."),
        },
        {
            "key": "event_registrations",
            "label": _("Event registrations"),
            "value": metrics["event_registrations"],
            "summary": _("Measurable participation in community activities."),
        },
    ]


def get_sponsor_testimonials():
    """Use real testimonial/story content when available, with honest fallback copy."""
    testimonials = []
    try:
        for item in Testimonial.objects.filter(is_published=True).order_by("-is_featured", "-created_at")[:3]:
            testimonials.append({
                "name": item.name,
                "role": item.title or item.location,
                "quote": item.testimonial,
            })
    except Exception as e:
        logger.error("Error loading testimonials: %s", str(e), exc_info=True)

    if testimonials:
        return testimonials

    return [
        {
            "name": _("New student in Lazio"),
            "role": _("Student support voice"),
            "quote": _("What students need most is a trusted first place to ask practical questions before small mistakes become expensive problems."),
        },
        {
            "name": _("Community collaborator"),
            "role": _("Institutional partner voice"),
            "quote": _("A structured student association makes outreach clearer, faster, and more accountable for everyone involved."),
        },
    ]


def get_event_case_studies():
    """Build sponsor-ready case-study cards from past published events."""
    try:
        events = (
            Event.objects.filter(is_published=True, start_datetime__lt=timezone.now())
            .prefetch_related("registrations")
            .order_by("-start_datetime")[:3]
        )
        case_studies = []
        for event in events:
            registered_count = event.registrations.count()
            attended_count = event.registrations.filter(attended=True).count()
            case_studies.append({
                "title": event.title,
                "date": event.start_datetime,
                "location": event.location,
                "registered_count": registered_count,
                "attended_count": attended_count,
                "summary": strip_tags(event.description)[:220],
            })
        if case_studies:
            return case_studies
    except Exception as e:
        logger.error("Error loading event case studies: %s", str(e), exc_info=True)

    return [
        {
            "title": _("Orientation and integration cycle"),
            "date": None,
            "location": _("Rome and Lazio"),
            "registered_count": 0,
            "attended_count": 0,
            "summary": _("Use each ASCAI event as a sponsor-ready case study: objective, audience, attendance, questions raised, follow-up resources, and next action."),
        }
    ]


def _record_conversion(request, event_type):
    """Persist a conversion event without disrupting the user's path."""
    try:
        session_key = request.session.session_key or ""
        if not session_key:
            request.session.save()
            session_key = request.session.session_key or ""
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        ip_address = forwarded_for.split(",")[0].strip() or request.META.get("REMOTE_ADDR")
        ConversionEvent.objects.create(
            event_type=event_type,
            source_path=request.META.get("HTTP_REFERER", "")[:255] or request.path[:255],
            user=request.user if request.user.is_authenticated else None,
            session_key=session_key,
            ip_address=ip_address,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
        )
    except Exception as e:
        logger.error("Error recording conversion event: %s", str(e), exc_info=True)


def track_conversion(request, event_type):
    """Track conversion intent and redirect to the relevant action."""
    target_map = {
        "sponsor_interest": reverse("contact:index"),
        "orientation_request": reverse("dashboard:orientation_booking"),
        "one_pager_download": reverse("core:sponsor_one_pager"),
    }
    if event_type not in target_map:
        return redirect("core:sponsorship")

    _record_conversion(request, event_type)
    return redirect(target_map[event_type])


def _escape_pdf_text(value):
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(lines):
    """Create a dependency-free, one-page PDF with sponsor summary text."""
    content = ["BT", "/F1 18 Tf", "72 760 Td", "22 TL"]
    first = True
    for line in lines:
        if not first:
            content.append("T*")
        first = False
        size = 18 if line.get("heading") else 10
        content.append(f"/F1 {size} Tf")
        content.append(f"({_escape_pdf_text(line['text'])}) Tj")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


def sponsor_one_pager_pdf(request):
    """Downloadable sponsor one-pager PDF with live impact metrics."""
    _record_conversion(request, "one_pager_download")
    metric_lines = [
        f"{metric['label']}: {metric['value']} - {metric['summary']}"
        for metric in get_impact_metrics()
    ]
    lines = [
        {"text": "ASCAI Lazio Sponsor One-Pager", "heading": True},
        {"text": "Trusted bridge for Cameroonian student success and Italian-Cameroonian cooperation."},
        {"text": "Why sponsor: student retention, integration, diaspora visibility, and measurable outreach."},
        {"text": "Current platform impact", "heading": True},
        *[{"text": line} for line in metric_lines],
        {"text": "Sponsor options", "heading": True},
        {"text": "Student Success Sponsor: fund orientation, scholarship guidance, mentorship, and resources."},
        {"text": "Institutional Bridge Partner: use ASCAI as a trusted communication and feedback channel."},
        {"text": "Diaspora Innovation Partner: support ethical verified services for students and families."},
        {"text": "Contact: info@ascai.org | ascai.org/impact-sponsorship/"},
    ]
    response = HttpResponse(_build_simple_pdf(lines), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="ascai-lazio-sponsor-one-pager.pdf"'
    return response


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
        context['student_success_pathway'] = STUDENT_SUCCESS_PATHWAY
        context['sponsor_impact_metrics'] = SPONSOR_IMPACT_METRICS
        context['platform_audience_cards'] = PLATFORM_AUDIENCE_CARDS
        context['impact_metric_cards'] = get_impact_metrics()
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


class SponsorshipView(TemplateView):
    """Public impact page for institutions, authorities, and sponsors."""
    template_name = 'core/sponsorship.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_success_pathway'] = STUDENT_SUCCESS_PATHWAY
        context['sponsor_impact_metrics'] = SPONSOR_IMPACT_METRICS
        context['impact_metric_cards'] = get_impact_metrics()
        context['sponsor_packages'] = SPONSOR_PACKAGES
        context['institutional_proof_points'] = INSTITUTIONAL_PROOF_POINTS
        context['membership_benefits'] = MEMBERSHIP_BENEFIT_PILLARS
        context['sponsor_testimonials'] = get_sponsor_testimonials()
        context['event_case_studies'] = get_event_case_studies()
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
