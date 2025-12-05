"""
Tests for core app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

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

