"""
URL configuration for ASCAI Lazio project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from config import admin as custom_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/setlang/', set_language, name='set_language'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# Language-prefixed URLs
urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('accounts/', include('allauth.urls')),  # Django allauth URLs - must be before accounts.urls
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

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

