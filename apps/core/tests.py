"""
Tests for core app.
"""
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

