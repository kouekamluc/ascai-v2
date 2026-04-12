"""
Tests for accounts app.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import User, UserDocument

User = get_user_model()


class UserModelTest(TestCase):
    """Test User model."""
    
    def test_create_user(self):
        """Test creating a user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_approved)
        self.assertEqual(user.role, 'student')
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_user_role_choices(self):
        """Test user role field."""
        user = User.objects.create_user(
            username='mentor',
            email='mentor@example.com',
            password='testpass123'
        )
        user.role = 'mentor'
        user.save()
        self.assertEqual(user.role, 'mentor')
    
    def test_user_language_preference(self):
        """Test user language preference."""
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123'
        )
        user.language_preference = 'fr'
        user.save()
        self.assertEqual(user.language_preference, 'fr')
    
    def test_user_full_name(self):
        """Test user full name field."""
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123',
            full_name='John Doe'
        )
        self.assertEqual(user.full_name, 'John Doe')
    
    def test_user_city_in_lazio(self):
        """Test user city in Lazio field."""
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='testpass123',
            city_in_lazio='rome'
        )
        self.assertEqual(user.city_in_lazio, 'rome')
    
    def test_user_str(self):
        """Test user string representation."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(str(user), 'testuser')


class UserDocumentModelTest(TestCase):
    """Test UserDocument model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_document(self):
        """Test creating a user document."""
        doc = UserDocument.objects.create(
            user=self.user,
            document_type='id_card',
            file=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.assertEqual(doc.user, self.user)
        self.assertEqual(doc.document_type, 'id_card')
        self.assertFalse(doc.is_verified)
    
    def test_user_document_str(self):
        """Test user document string representation."""
        doc = UserDocument.objects.create(
            user=self.user,
            document_type='id_card',
            file=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            )
        )
        self.assertIn('testuser', str(doc))


class AccountsViewsTest(TestCase):
    """Test accounts views."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_approved=True
        )
    
    def test_signup_flow_creates_approved_user(self):
        """The public signup flow should create an immediately approved user."""
        response = self.client.post(
            reverse('account_signup'),
            {
                'username': 'newmember',
                'email': 'newmember@example.com',
                'password1': 'testpass12345',
                'password2': 'testpass12345',
                'phone': '+390000000',
                'role': 'student',
                'language_preference': 'en',
            },
        )
        self.assertEqual(response.status_code, 302)
        created_user = User.objects.get(username='newmember')
        self.assertTrue(created_user.is_approved)
        self.assertTrue(created_user.is_active)

    def test_login_flow_redirects_approved_user_to_dashboard(self):
        """Approved users should enter through the dashboard route."""
        response = self.client.post(
            reverse('account_login'),
            {'login': 'testuser', 'password': 'testpass123'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.url)
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires login."""
        url = reverse('accounts:profile')
        response = self.client.get(url)
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_profile_view_authenticated(self):
        """Test profile view for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('accounts:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AccountsURLsTest(TestCase):
    """Test accounts URLs."""
    
    def test_profile_url(self):
        """Test profile URL resolves."""
        url = reverse('accounts:profile')
        self.assertEqual(url, '/accounts/profile/')

    def test_allauth_login_url_resolves(self):
        self.assertEqual(reverse('account_login'), '/accounts/login/')

