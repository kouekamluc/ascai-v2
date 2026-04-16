"""
Shared helpers for branded transactional emails.
"""
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.templatetags.static import static

EMAIL_LOGO_PATH = "images/web-app-manifest-512x512.png"


def get_site_url(request=None):
    """Return a fully qualified site URL for email links and assets."""
    if request and hasattr(request, "build_absolute_uri"):
        try:
            return request.build_absolute_uri("/").rstrip("/")
        except Exception:
            pass

    try:
        site = Site.objects.get_current()
        domain = site.domain.strip()
        if domain.startswith(("http://", "https://")):
            return domain.rstrip("/")
        if domain:
            return f"https://{domain}"
    except Exception:
        pass

    configured = getattr(settings, "SITE_URL", "").strip()
    if configured.startswith(("http://", "https://")):
        return configured.rstrip("/")
    if configured and configured != "/":
        return f"https://{configured.lstrip('/')}".rstrip("/")

    return "http://localhost:8000" if settings.DEBUG else "https://ascai.org"


def build_absolute_static_url(path, site_url=None):
    """Build an absolute URL for a static asset."""
    static_url = static(path)
    if static_url.startswith(("http://", "https://")):
        return static_url

    base_url = (site_url or get_site_url()).rstrip("/")
    if not static_url.startswith("/"):
        static_url = f"/{static_url}"
    return f"{base_url}{static_url}"


def get_email_branding_context(request=None, site_url=None):
    """Common template context used by all branded email templates."""
    resolved_site_url = (site_url or get_site_url(request=request)).rstrip("/")
    return {
        "site_url": resolved_site_url,
        "logo_url": build_absolute_static_url(EMAIL_LOGO_PATH, resolved_site_url),
        "organization_name": "ASCAI Lazio",
        "organization_tagline": "Association of Cameroonian Students and Academics in Lazio",
    }


def send_branded_email(
    *,
    subject,
    text_body,
    recipient_list,
    template_name=None,
    context=None,
    from_email=None,
    fail_silently=False,
    request=None,
    site_url=None,
):
    """Send an email with a branded HTML alternative when a template is provided."""
    html_message = None
    if template_name:
        html_context = get_email_branding_context(request=request, site_url=site_url)
        if context:
            html_context.update(context)
        html_message = render_to_string(template_name, html_context)

    return send_mail(
        subject=subject,
        message=text_body.strip(),
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        html_message=html_message,
        fail_silently=fail_silently,
    )
