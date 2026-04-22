"""
Tests for community/forum app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import override
from .models import ForumCategory, ForumThread, ForumPost
from apps.dashboard.models import CommunityGroup

User = get_user_model()


class ForumCategoryModelTest(TestCase):
    """Test ForumCategory model."""
    
    def test_create_category(self):
        """Test creating a forum category."""
        category = ForumCategory.objects.create(
            name='General Discussion',
            description='General discussion forum',
            slug='general'
        )
        self.assertEqual(category.name, 'General Discussion')
        self.assertEqual(category.slug, 'general')
    
    def test_category_str(self):
        """Test category string representation."""
        category = ForumCategory.objects.create(
            name='Test Category',
            slug='test'
        )
        self.assertEqual(str(category), 'Test Category')


class ForumThreadModelTest(TestCase):
    """Test ForumThread model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = ForumCategory.objects.create(
            name='General',
            slug='general'
        )
    
    def test_create_thread(self):
        """Test creating a forum thread."""
        thread = ForumThread.objects.create(
            title='Test Thread',
            category=self.category,
            author=self.user,
            content='Test content'
        )
        self.assertEqual(thread.title, 'Test Thread')
        self.assertEqual(thread.author, self.user)
        self.assertEqual(thread.views_count, 0)
    
    def test_thread_auto_slug(self):
        """Test thread auto-generates slug."""
        thread = ForumThread.objects.create(
            title='Test Thread Title',
            category=self.category,
            author=self.user,
            content='Test content'
        )
        self.assertIsNotNone(thread.slug)
        self.assertIn('test-thread-title', thread.slug)
    
    def test_thread_str(self):
        """Test thread string representation."""
        thread = ForumThread.objects.create(
            title='Test Thread',
            category=self.category,
            author=self.user,
            content='Test content'
        )
        self.assertEqual(str(thread), 'Test Thread')


class ForumPostModelTest(TestCase):
    """Test ForumPost model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = ForumCategory.objects.create(
            name='General',
            slug='general'
        )
        self.thread = ForumThread.objects.create(
            title='Test Thread',
            category=self.category,
            author=self.user,
            content='Test content'
        )
    
    def test_create_post(self):
        """Test creating a forum post."""
        post = ForumPost.objects.create(
            thread=self.thread,
            author=self.user,
            content='Test reply'
        )
        self.assertEqual(post.thread, self.thread)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.content, 'Test reply')


class CommunityViewsTest(TestCase):
    """Test community views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = ForumCategory.objects.create(
            name='General',
            slug='general'
        )
    
    def test_forum_list_view(self):
        """Test forum list view."""
        url = reverse('community:thread_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_forum_index_view(self):
        """Test forum index view."""
        url = reverse('community:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_thread_reply_redirects_to_login(self):
        """Anonymous replies should redirect instead of crashing the thread page."""
        thread = ForumThread.objects.create(
            title='Protected Thread',
            category=self.category,
            author=self.user,
            content='Test content'
        )

        response = self.client.post(
            reverse('community:thread_detail', kwargs={'slug': thread.slug}),
            {'content': 'Anonymous reply'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_public_group_detail_with_tags_renders(self):
        """Public group pages should render tag pills without template errors."""
        group = CommunityGroup.objects.create(
            name='Students Hub',
            description='Community group description',
            category='students',
            is_public=True,
            tags='students, rome, support',
            created_by=self.user,
        )

        response = self.client.get(reverse('community:group_detail', kwargs={'slug': group.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'students')
        self.assertContains(response, 'support')

    def test_thread_detail_translates_to_italian(self):
        """Thread detail replies section should render translated Italian copy."""
        thread = ForumThread.objects.create(
            title='Translated Thread',
            category=self.category,
            author=self.user,
            content='Test content'
        )

        with override('it'):
            response = self.client.get(
                reverse('community:thread_detail', kwargs={'slug': thread.slug}),
                HTTP_ACCEPT_LANGUAGE='it',
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Risposte')

