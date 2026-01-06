"""
Template tags for static file utilities.
"""
from django import template
from django.conf import settings
from django.templatetags.static import static as django_static

register = template.Library()


@register.simple_tag
def absolute_static(path, site_url=None):
    """
    Returns an absolute URL for a static file.
    Handles both S3 (absolute URLs) and local storage (relative URLs).
    
    Usage:
        {% load static_utils %}
        <link rel="icon" href="{% absolute_static 'images/favicon.ico' %}">
    """
    static_url = django_static(path)
    
    # If static_url is already absolute (starts with http:// or https://), return as-is
    if static_url.startswith('http://') or static_url.startswith('https://'):
        return static_url
    
    # If static_url is relative, prepend site_url
    if site_url:
        # Ensure no double slashes
        if site_url.endswith('/') and static_url.startswith('/'):
            return f"{site_url.rstrip('/')}{static_url}"
        elif not site_url.endswith('/') and not static_url.startswith('/'):
            return f"{site_url}/{static_url}"
        else:
            return f"{site_url}{static_url}"
    
    # Fallback: try to get site_url from context
    # This will be handled by the context processor
    return static_url

