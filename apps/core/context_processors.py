"""
Context processors for core app.
"""
from django.conf import settings
from django.contrib.sites.models import Site


def language_preference(request):
    """Add language preference to context."""
    if hasattr(request, 'user') and request.user.is_authenticated:
        return {'user_language': request.user.language_preference}
    return {'user_language': 'en'}


def site_url(request):
    """Add site URL to context for absolute URLs in templates."""
    try:
        site = Site.objects.get_current()
        site_domain = site.domain
        # Use https in production, http in development
        protocol = 'https' if not settings.DEBUG else 'http'
        site_url = f"{protocol}://{site_domain}" if not site_domain.startswith('http') else site_domain
    except Exception:
        # Fallback: try to get from request if available
        if request and hasattr(request, 'build_absolute_uri'):
            try:
                site_url = request.build_absolute_uri('/').rstrip('/')
            except Exception:
                # Final fallback
                if settings.DEBUG:
                    site_url = 'http://localhost:8000'
                else:
                    site_url = 'https://ascai.org'
        else:
            # Fallback to production URL or localhost
            if settings.DEBUG:
                site_url = 'http://localhost:8000'
            else:
                site_url = 'https://ascai.org'
    
    return {'site_url': site_url}


def public_collaborators(request):
    """Expose featured collaborators for public site sections."""
    try:
        from apps.core.models import Collaborator

        collaborators = list(
            Collaborator.objects.filter(is_active=True, is_featured=True).order_by("display_order", "name")[:12]
        )
    except Exception:
        collaborators = []

    return {"public_collaborators": collaborators}


def association_settings(request):
    """Expose singleton website settings for public templates and admin-aware pages."""
    try:
        from apps.core.models import AssociationSettings

        settings_obj = AssociationSettings.load()
    except Exception:
        settings_obj = None

    return {"association_settings": settings_obj}
