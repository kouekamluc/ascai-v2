"""
Tests for core app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.core.models import AssociationSettings, Collaborator

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

