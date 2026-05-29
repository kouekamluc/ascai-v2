"""
Tests for diaspora app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import override
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import News, Event
from apps.dashboard.models import EventRegistration, EventWaitlistEntry, UserStorySubmission

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

    def test_duplicate_news_titles_get_unique_slugs(self):
        """Duplicate news titles should not collide on the slug field."""
        first = News.objects.create(
            title='Shared Title',
            content='First',
            author=self.user
        )
        second = News.objects.create(
            title='Shared Title',
            content='Second',
            author=self.user
        )

        self.assertNotEqual(first.slug, second.slug)


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

    def test_duplicate_event_titles_get_unique_slugs(self):
        """Duplicate event titles should not collide on the slug field."""
        start = timezone.now() + timedelta(days=1)
        first = Event.objects.create(
            title='Shared Event',
            description='First description',
            start_datetime=start,
            end_datetime=start + timedelta(hours=2),
            location='Rome'
        )
        second = Event.objects.create(
            title='Shared Event',
            description='Second description',
            start_datetime=start + timedelta(days=1),
            end_datetime=start + timedelta(days=1, hours=2),
            location='Milan'
        )

        self.assertNotEqual(first.slug, second.slug)


class DiasporaViewsTest(TestCase):
    """Test diaspora views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_approved=True
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

    def test_event_detail_view_renders_registration_flow(self):
        """Registration-required event pages should render without reverse errors."""
        event = Event.objects.create(
            title='Registration Event',
            description='Test description',
            start_datetime=timezone.now() + timedelta(days=3),
            end_datetime=timezone.now() + timedelta(days=3, hours=2),
            location='Rome',
            is_published=True,
            registration_required=True,
            capacity=5,
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('diaspora:event_detail', kwargs={'slug': event.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('diaspora:event_register', kwargs={'slug': event.slug}))

    def test_event_register_and_unregister_flow(self):
        """Users can register and later cancel from the diaspora flow."""
        event = Event.objects.create(
            title='Flow Event',
            description='Test description',
            start_datetime=timezone.now() + timedelta(days=4),
            end_datetime=timezone.now() + timedelta(days=4, hours=2),
            location='Rome',
            is_published=True,
            registration_required=True,
            capacity=5,
        )

        self.client.force_login(self.user)

        register_response = self.client.post(
            reverse('diaspora:event_register', kwargs={'slug': event.slug}),
            follow=True,
        )
        self.assertEqual(register_response.status_code, 200)
        self.assertTrue(EventRegistration.objects.filter(event=event, user=self.user).exists())

        unregister_response = self.client.post(
            reverse('diaspora:event_unregister', kwargs={'slug': event.slug}),
            follow=True,
        )
        self.assertEqual(unregister_response.status_code, 200)
        self.assertFalse(EventRegistration.objects.filter(event=event, user=self.user).exists())

    def test_full_event_waitlist_join_and_leave_flow(self):
        event = Event.objects.create(
            title='Waitlist Event',
            description='Test description',
            start_datetime=timezone.now() + timedelta(days=4),
            end_datetime=timezone.now() + timedelta(days=4, hours=2),
            location='Rome',
            is_published=True,
            registration_required=True,
            capacity=1,
            waitlist_enabled=True,
        )
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123',
            is_approved=True,
        )
        EventRegistration.objects.create(event=event, user=other_user)
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('diaspora:event_join_waitlist', kwargs={'slug': event.slug}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            EventWaitlistEntry.objects.filter(
                event=event,
                user=self.user,
                status='waiting',
            ).exists()
        )
        self.assertContains(response, 'You are on the waitlist')

        response = self.client.post(
            reverse('diaspora:event_leave_waitlist', kwargs={'slug': event.slug}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            EventWaitlistEntry.objects.filter(
                event=event,
                user=self.user,
                status='waiting',
            ).exists()
        )

    def test_waitlist_user_is_promoted_when_registration_is_cancelled(self):
        event = Event.objects.create(
            title='Promotion Event',
            description='Test description',
            start_datetime=timezone.now() + timedelta(days=4),
            end_datetime=timezone.now() + timedelta(days=4, hours=2),
            location='Rome',
            is_published=True,
            registration_required=True,
            capacity=1,
            waitlist_enabled=True,
        )
        registered_user = User.objects.create_user(
            username='registereduser',
            email='registered@example.com',
            password='testpass123',
            is_approved=True,
        )
        EventRegistration.objects.create(event=event, user=registered_user)
        EventWaitlistEntry.objects.create(event=event, user=self.user)

        self.client.force_login(registered_user)
        response = self.client.post(
            reverse('diaspora:event_unregister', kwargs={'slug': event.slug}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(EventRegistration.objects.filter(event=event, user=self.user).exists())
        self.assertTrue(
            EventWaitlistEntry.objects.filter(
                event=event,
                user=self.user,
                status='promoted',
            ).exists()
        )

    def test_story_submission_detail_with_tags_renders(self):
        """Tagged story details should render without template method calls."""
        submission = UserStorySubmission.objects.create(
            user=self.user,
            title='Tagged Story',
            story='Story content',
            tags='rome, student, community',
        )

        self.client.force_login(self.user)
        response = self.client.get(
            reverse('diaspora:story_submission_detail', kwargs={'pk': submission.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'rome')
        self.assertContains(response, 'student')

    def test_event_detail_page_translates_to_french(self):
        """The public event flow should render translated French copy."""
        event = Event.objects.create(
            title='French Event',
            description='Test description',
            start_datetime=timezone.now() + timedelta(days=5),
            end_datetime=timezone.now() + timedelta(days=5, hours=2),
            location='Rome',
            is_published=True,
            registration_required=True,
            capacity=5,
        )

        self.client.force_login(self.user)
        with override('fr'):
            response = self.client.get(
                reverse('diaspora:event_detail', kwargs={'slug': event.slug}),
                HTTP_ACCEPT_LANGUAGE='fr',
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'S inscrire a l evenement')

