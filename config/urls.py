"""
URL configuration for ASCAI Lazio project.
"""
from pathlib import Path
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from config import admin as custom_admin
from apps.core.views import HealthCheckView
from apps.accounts.views import CustomConfirmEmailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # Healthcheck endpoint (outside i18n_patterns for reliability)
    path('health/', HealthCheckView.as_view(), name='health'),
]

# Language-prefixed URLs
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    # Override allauth's email confirmation view with our styled version
    # This must come before allauth URLs to take precedence
    path('accounts/confirm-email/<str:key>/', CustomConfirmEmailView.as_view(), name='account_confirm_email'),
    path('accounts/', include('allauth.urls')),  # Django allauth URLs
    path('accounts/', include('apps.accounts.urls')),  # Custom accounts URLs (profile, etc.)
    path('dashboard/', include('apps.dashboard.urls')),
    path('students/', include('apps.students.urls')),
    path('diaspora/', include('apps.diaspora.urls')),
    path('community/', include('apps.community.urls')),
    path('mentorship/', include('apps.mentorship.urls')),
    path('universities/', include('apps.universities.urls')),
    path('scholarships/', include('apps.scholarships.urls')),
    path('gallery/', include('apps.gallery.urls')),
    path('downloads/', include('apps.downloads.urls')),
    path('contact/', include('apps.contact.urls')),
    prefix_default_language=False,
)

# Serve media files when running locally (DEBUG=True) or whenever S3 is disabled.
# This ensures profile avatars & other uploads remain accessible on platforms
# like Railway where we're relying on the app server to serve media.
# Note: In production without S3, files stored in MEDIA_ROOT will be lost on container restart.
# For persistent storage, enable S3 or use a persistent volume.
USE_S3 = getattr(settings, 'USE_S3', False)
if settings.DEBUG or not USE_S3:
    # Ensure MEDIA_ROOT directory exists
    media_root = settings.MEDIA_ROOT
    if isinstance(media_root, str):
        media_root = Path(media_root)
    elif hasattr(media_root, 'path'):
        media_root = Path(media_root.path)
    else:
        media_root = Path(media_root)
    
    # Create media directory if it doesn't exist
    media_root.mkdir(parents=True, exist_ok=True)
    
    # In production (DEBUG=False), use a view to serve media files
    # In development (DEBUG=True), use Django's static() helper
    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    else:
        # Use a view to serve media files in production
        from apps.core.views import serve_media_file
        # Remove leading slash from MEDIA_URL for pattern matching
        media_url_pattern = settings.MEDIA_URL.lstrip('/')
        urlpatterns += [
            path(f'{media_url_pattern}<path:path>', serve_media_file, name='serve_media'),
        ]

    # Serve static files
    # In development (DEBUG=True), Django's staticfiles app automatically serves static files
    # We also add explicit static() helper to ensure collected static files are served
    # In production (DEBUG=False), use WhiteNoise middleware with fallback URL pattern
    if settings.DEBUG:
        # In DEBUG mode, serve static files from STATIC_ROOT (collected files)
        # Django's staticfiles app will also serve from STATICFILES_DIRS automatically
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    else:
        # In production, add fallback static file serving view
        # WhiteNoise middleware should handle most requests, but this provides a reliable fallback
        # This ensures Django admin static files load even if WhiteNoise misses a request
        from apps.core.views import serve_static_file
        static_url_pattern = settings.STATIC_URL.lstrip('/')
        urlpatterns += [
            path(f'{static_url_pattern}<path:path>', serve_static_file, name='serve_static'),
        ]
        # Note: When USE_S3=False, WhiteNoise middleware also handles static files
        # The URL pattern above is a fallback in case WhiteNoise doesn't catch a request
    
    # Django Debug Toolbar URLs (only in development)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass  # debug_toolbar not installed, skip it

