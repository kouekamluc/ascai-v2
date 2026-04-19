"""
Minimal URL configuration for tests.

This avoids optional integrations such as the admin and editor routes while
still exercising the public pages and i18n behavior we care about in tests.
"""
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.views.i18n import set_language

from apps.accounts.views import (
    CustomConfirmEmailView,
    CustomEmailVerificationSentView,
    email_verification_required_view,
)
from apps.core.views import HealthCheckView


urlpatterns = [
    path('i18n/setlang/', set_language, name='set_language'),
    path('health/', HealthCheckView.as_view(), name='health'),
    path(
        'accounts/confirm-email/<str:key>/',
        CustomConfirmEmailView.as_view(),
        name='account_confirm_email',
    ),
    path(
        'accounts/confirm-email/',
        email_verification_required_view,
        name='account_email_verification_required',
    ),
    path(
        'accounts/email-verification-sent/',
        CustomEmailVerificationSentView.as_view(),
        name='account_email_verification_notice',
    ),
]

urlpatterns += i18n_patterns(
    path('', include('apps.core.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('community/', include('apps.community.urls')),
    path('diaspora/', include('apps.diaspora.urls')),
    path('mentorship/', include('apps.mentorship.urls')),
    path('universities/', include('apps.universities.urls')),
    path('scholarships/', include('apps.scholarships.urls')),
    path('gallery/', include('apps.gallery.urls')),
    path('downloads/', include('apps.downloads.urls')),
    path('contact/', include('apps.contact.urls')),
    path('students/', include('apps.students.urls')),
    path('governance/', include('apps.governance.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    prefix_default_language=False,
)
