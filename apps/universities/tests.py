"""
Tests for universities app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import University, UniversityProgram, SavedUniversity

User = get_user_model()


class UniversityModelTest(TestCase):
    """Test University model."""
    
    def test_create_university(self):
        """Test creating a university."""
        university = University.objects.create(
            name='Test University',
            city='rome',
            address='123 Test St',
            description='Test description',
            slug='test-university'
        )
        self.assertEqual(university.name, 'Test University')
        self.assertEqual(university.city, 'rome')
    
    def test_university_str(self):
        """Test university string representation."""
        university = University.objects.create(
            name='Test University',
            city='rome',
            address='123 Test St',
            description='Test description',
            slug='test-university'
        )
        self.assertEqual(str(university), 'Test University')
    
    def test_university_auto_slug(self):
        """Test university auto-generates slug."""
        university = University.objects.create(
            name='Test University Name',
            city='rome',
            address='123 Test St',
            description='Test description'
        )
        self.assertIsNotNone(university.slug)


class UniversityProgramModelTest(TestCase):
    """Test UniversityProgram model."""
    
    def setUp(self):
        """Set up test university."""
        self.university = University.objects.create(
            name='Test University',
            city='rome',
            address='123 Test St',
            description='Test description',
            slug='test-university'
        )
    
    def test_create_program(self):
        """Test creating a university program."""
        program = UniversityProgram.objects.create(
            university=self.university,
            name='Computer Science',
            degree_type='Bachelor',
            duration_years=3
        )
        self.assertEqual(program.university, self.university)
        self.assertEqual(program.name, 'Computer Science')


class SavedUniversityModelTest(TestCase):
    """Test SavedUniversity model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.university = University.objects.create(
            name='Test University',
            city='rome',
            address='123 Test St',
            description='Test description',
            slug='test-university'
        )
    
    def test_create_saved_university(self):
        """Test creating a saved university."""
        saved = SavedUniversity.objects.create(
            user=self.user,
            university=self.university
        )
        self.assertEqual(saved.user, self.user)
        self.assertEqual(saved.university, self.university)


class UniversitiesViewsTest(TestCase):
    """Test universities views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.university = University.objects.create(
            name='Test University',
            city='rome',
            address='123 Test St',
            description='Test description',
            slug='test-university'
        )
    
    def test_university_list_view(self):
        """Test university list view."""
        url = reverse('universities:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_university_detail_view(self):
        """Test university detail view."""
        url = reverse('universities:detail', kwargs={'slug': self.university.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

