"""
Tests for diaspora app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import News, Event

User = get_user_model()


class NewsModelTest(TestCase):
    """Test News model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_news(self):
        """Test creating a news article."""
        news = News.objects.create(
            title='Test News',
            content='Test content',
            author=self.user,
            category='general',
            is_published=True
        )
        self.assertEqual(news.title, 'Test News')
        self.assertTrue(news.is_published)
        self.assertIsNotNone(news.slug)
    
    def test_news_str(self):
        """Test news string representation."""
        news = News.objects.create(
            title='Test News',
            content='Test content',
            author=self.user
        )
        self.assertEqual(str(news), 'Test News')
    
    def test_news_auto_slug(self):
        """Test news auto-generates slug."""
        news = News.objects.create(
            title='Test News Article',
            content='Test content',
            author=self.user
        )
        self.assertIsNotNone(news.slug)
        self.assertIn('test-news-article', news.slug)


class EventModelTest(TestCase):
    """Test Event model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_event(self):
        """Test creating an event."""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=2),
            location='Test Location',
            is_published=True
        )
        self.assertEqual(event.title, 'Test Event')
        self.assertTrue(event.is_published)
    
    def test_event_str(self):
        """Test event string representation."""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=2),
            location='Test Location'
        )
        self.assertEqual(str(event), 'Test Event')


class DiasporaViewsTest(TestCase):
    """Test diaspora views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.news = News.objects.create(
            title='Test News',
            content='Test content',
            author=self.user,
            is_published=True,
            slug='test-news'
        )
        self.event = Event.objects.create(
            title='Test Event',
            description='Test description',
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=2),
            location='Test Location',
            is_published=True,
            slug='test-event'
        )
    
    def test_news_list_view(self):
        """Test news list view."""
        url = reverse('diaspora:news_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_news_detail_view(self):
        """Test news detail view."""
        url = reverse('diaspora:news_detail', kwargs={'slug': self.news.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_event_list_view(self):
        """Test event list view."""
        url = reverse('diaspora:event_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_event_detail_view(self):
        """Test event detail view."""
        url = reverse('diaspora:event_detail', kwargs={'slug': self.event.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

