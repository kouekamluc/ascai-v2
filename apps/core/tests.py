"""
Tests for core app.
"""
import os
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import translation

from apps.core.models import AssociationSettings, Collaborator, ServicePartner
from apps.core.templatetags.i18n_utils import translate_current_url

User = get_user_model()


class CoreViewsTest(TestCase):
    """Test core views."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_home_view(self):
        """Test home view."""
        url = reverse('core:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_health_check_view(self):
        """Test health check view."""
        url = reverse('health')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Health check returns a response (content type may vary)
        self.assertIsNotNone(response.content)

    def test_home_view_includes_featured_collaborators(self):
        """Featured collaborators should be available on the public home page."""
        Collaborator.objects.create(
            name='Partner Org',
            category='partner',
            is_featured=True,
            is_active=True,
        )
        Collaborator.objects.create(
            name='Hidden Org',
            category='collaborator',
            is_featured=False,
            is_active=True,
        )

        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Partner Org')
        self.assertNotContains(response, 'Hidden Org')

    def test_home_view_uses_authenticated_user_avatar_in_navbar(self):
        user = User.objects.create_user(
            username='avataruser',
            email='avatar@example.com',
            password='testpass123',
            is_approved=True,
        )
        user.avatar = 'profiles/avataruser.jpg'
        user.save(update_fields=['avatar'])

        self.client.force_login(user)
        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/media/profiles/avataruser.jpg')

    def test_premium_services_view_renders_fallback_content(self):
        response = self.client.get(reverse('core:premium_services'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Premium services')
        self.assertContains(response, 'Verified remittance partner referrals')

    def test_premium_services_view_can_render_real_partners(self):
        ServicePartner.objects.create(
            name='Trusted Transfers',
            category='money_transfer',
            short_description='Money transfer service for Cameroon.',
            verification_status='verified',
            is_featured=True,
            is_active=True,
        )

        response = self.client.get(reverse('core:premium_services'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trusted Transfers')

    def test_sponsorship_view_renders_student_and_sponsor_value(self):
        response = self.client.get(reverse('core:sponsorship'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sponsor the bridge')
        self.assertContains(response, 'Student Success Sponsor')

    def test_sponsorship_view_renders_real_impact_numbers(self):
        from datetime import date, time
        from apps.dashboard.models import OrientationSession

        user = User.objects.create_user(
            username='impactmember',
            email='impact@example.com',
            password='testpass123',
            is_approved=True,
        )
        OrientationSession.objects.create(
            user=user,
            preferred_date=date.today(),
            preferred_time=time(10, 0),
            topics='Residence permit and university enrollment',
        )

        response = self.client.get(reverse('core:sponsorship'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Active members')
        self.assertContains(response, 'Orientation requests')
        self.assertContains(response, '>1<', html=False)

    def test_sponsor_one_pager_pdf_downloads(self):
        response = self.client.get(reverse('core:sponsor_one_pager'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_conversion_tracking_records_sponsor_interest(self):
        from apps.core.models import ConversionEvent

        response = self.client.get(reverse('core:track_conversion', args=['sponsor_interest']))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('contact:index'))
        self.assertTrue(
            ConversionEvent.objects.filter(event_type='sponsor_interest').exists()
        )

    def test_home_view_promotes_student_success_and_sponsorship(self):
        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Student success pathway')
        self.assertContains(response, 'Built for adoption')
        self.assertContains(response, 'Every stakeholder gets a reason to come back.')
        self.assertContains(response, 'View Sponsor Plan')


class CoreContextProcessorsTest(TestCase):
    """Test core context processors."""
    
    def test_language_preference_processor(self):
        """Test language preference context processor."""
        from apps.core.context_processors import language_preference
        request = type('Request', (), {
            'user': type('User', (), {'language_preference': 'fr', 'is_authenticated': True})()
        })()
        context = language_preference(request)
        self.assertIn('user_language', context)
        self.assertEqual(context['user_language'], 'fr')

    def test_public_collaborators_processor(self):
        """Featured collaborators should be returned by the context processor."""
        from apps.core.context_processors import public_collaborators

        Collaborator.objects.create(name='Visible Partner', is_featured=True, is_active=True)
        Collaborator.objects.create(name='Inactive Partner', is_featured=True, is_active=False)

        context = public_collaborators(None)

        self.assertEqual(len(context['public_collaborators']), 1)
        self.assertEqual(context['public_collaborators'][0].name, 'Visible Partner')

    def test_association_settings_processor(self):
        """Association settings should always be available."""
        from apps.core.context_processors import association_settings

        context = association_settings(None)

        self.assertIn('association_settings', context)
        self.assertIsInstance(context['association_settings'], AssociationSettings)


class UserPreferredLocaleMiddlewareTest(TestCase):
    """Test saved language preferences are applied consistently."""

    def test_authenticated_user_preference_sets_request_language_and_cookie(self):
        user = User.objects.create_user(
            username='frenchmember',
            email='french@example.com',
            password='testpass123',
            language_preference='fr',
        )

        self.client.force_login(user)
        response = self.client.get(reverse('core:home'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/fr/'))
        self.assertEqual(
            response.cookies[settings.LANGUAGE_COOKIE_NAME].value,
            'fr',
        )

    def test_url_language_prefix_overrides_saved_preference(self):
        user = User.objects.create_user(
            username='italianmember',
            email='italian@example.com',
            password='testpass123',
            language_preference='fr',
        )

        self.client.force_login(user)
        response = self.client.get('/it/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.LANGUAGE_CODE, 'it')
        self.assertEqual(
            response.cookies[settings.LANGUAGE_COOKIE_NAME].value,
            'it',
        )

    def test_set_language_post_updates_cookie_for_anonymous_user(self):
        response = self.client.post(
            reverse('set_language'),
            {'language': 'fr', 'next': '/'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertEqual(
            response.cookies[settings.LANGUAGE_COOKIE_NAME].value,
            'fr',
        )
        self.assertEqual(
            self.client.cookies[settings.LANGUAGE_COOKIE_NAME].value,
            'fr',
        )

    def test_set_language_post_persists_authenticated_user_preference(self):
        user = User.objects.create_user(
            username='switcher',
            email='switcher@example.com',
            password='testpass123',
            language_preference='en',
        )

        self.client.force_login(user)
        response = self.client.post(
            reverse('set_language'),
            {'language': 'it', 'next': '/premium-services/'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/premium-services/')
        self.assertEqual(
            response.cookies[settings.LANGUAGE_COOKIE_NAME].value,
            'it',
        )

        user.refresh_from_db()
        self.assertEqual(user.language_preference, 'it')

        follow_up = self.client.get('/premium-services/')
        self.assertEqual(follow_up.status_code, 302)
        self.assertEqual(follow_up.url, '/it/premium-services/')

    def test_admin_route_is_not_forced_under_language_prefix(self):
        user = User.objects.create_user(
            username='adminswitch',
            email='adminswitch@example.com',
            password='testpass123',
            language_preference='fr',
        )

        self.client.force_login(user)
        response = self.client.get('/admin/', follow=False)

        self.assertIn(response.status_code, [200, 302, 403])
        self.assertFalse(response.get('Location', '').startswith('/fr/admin/'))


class TranslationCatalogSmokeTest(TestCase):
    """Guard key production pages against untranslated catalog regressions."""

    def test_key_public_and_dashboard_strings_have_fr_and_it_translations(self):
        strings = [
            'Student Guide',
            'Sponsor the bridge between Cameroonian talent and Italian opportunity.',
            'My ASCAI Membership',
            'My Membership Dues',
            'Trusted providers for practical needs',
            (
                'ASCAI lists only active providers that have been reviewed by the '
                'association, including money transfer, documents, housing, '
                'logistics, and other community services.'
            ),
        ]

        for language in ['fr', 'it']:
            with translation.override(language):
                for value in strings:
                    translated = translation.gettext(value)
                    self.assertNotEqual(
                        translated,
                        value,
                        msg=f'{language}: {value}',
                    )


class TranslateCurrentUrlTemplateTagTest(TestCase):
    """Ensure translated redirect targets stay stable across languages."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_translate_current_url_adds_non_default_prefix(self):
        request = self.factory.get('/premium-services/')
        with translation.override('en'):
            translated_url = translate_current_url({'request': request}, 'fr')

        self.assertEqual(translated_url, '/fr/premium-services/')

    def test_translate_current_url_removes_prefix_for_default_language(self):
        request = self.factory.get('/fr/premium-services/')
        with translation.override('fr'):
            translated_url = translate_current_url({'request': request}, 'en')

        self.assertEqual(translated_url, '/premium-services/')

    def test_translate_current_url_preserves_query_string(self):
        request = self.factory.get('/downloads/?type=forms&page=2')
        with translation.override('en'):
            translated_url = translate_current_url({'request': request}, 'it')

        self.assertEqual(translated_url, '/it/downloads/?type=forms&page=2')


class CoreEmailUtilsTest(TestCase):
    """Test branded email helpers."""

    def test_email_branding_context_has_absolute_logo_url(self):
        from apps.core.email_utils import get_email_branding_context

        context = get_email_branding_context(site_url='https://ascai.test')

        self.assertEqual(context['site_url'], 'https://ascai.test')
        self.assertTrue(context['logo_url'].startswith('https://ascai.test/'))
        self.assertIn('web-app-manifest-512x512.png', context['logo_url'])


class SetupGoogleOAuthCommandTest(TestCase):
    """Test Google OAuth setup command startup behavior."""

    def test_command_skips_when_socialaccount_is_not_installed(self):
        previous_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        previous_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        os.environ['GOOGLE_CLIENT_ID'] = 'test-client-id'
        os.environ['GOOGLE_CLIENT_SECRET'] = 'test-client-secret'
        output = StringIO()

        try:
            call_command('setup_google_oauth', stdout=output)
        finally:
            if previous_client_id is None:
                os.environ.pop('GOOGLE_CLIENT_ID', None)
            else:
                os.environ['GOOGLE_CLIENT_ID'] = previous_client_id

            if previous_client_secret is None:
                os.environ.pop('GOOGLE_CLIENT_SECRET', None)
            else:
                os.environ['GOOGLE_CLIENT_SECRET'] = previous_client_secret

        self.assertIn('Google OAuth setup skipped', output.getvalue())

