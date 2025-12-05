"""
Tests for scholarships app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from .models import Scholarship, SavedScholarship

User = get_user_model()


class ScholarshipModelTest(TestCase):
    """Test Scholarship model."""
    
    def test_create_scholarship(self):
        """Test creating a scholarship."""
        scholarship = Scholarship.objects.create(
            title='Test Scholarship',
            provider='Test Provider',
            description='Test description',
            amount=Decimal('1000.00'),
            currency='EUR',
            eligibility_criteria='Test criteria',
            status='active',
            slug='test-scholarship'
        )
        self.assertEqual(scholarship.title, 'Test Scholarship')
        self.assertEqual(scholarship.status, 'active')
        self.assertEqual(scholarship.amount, Decimal('1000.00'))
    
    def test_scholarship_str(self):
        """Test scholarship string representation."""
        scholarship = Scholarship.objects.create(
            title='Test Scholarship',
            provider='Test Provider',
            description='Test description',
            eligibility_criteria='Test criteria',
            status='active',
            slug='test-scholarship'
        )
        self.assertEqual(str(scholarship), 'Test Scholarship')
    
    def test_scholarship_auto_slug(self):
        """Test scholarship auto-generates slug."""
        scholarship = Scholarship.objects.create(
            title='Test Scholarship Title',
            provider='Test Provider',
            description='Test description',
            eligibility_criteria='Test criteria',
            status='active'
        )
        self.assertIsNotNone(scholarship.slug)


class SavedScholarshipModelTest(TestCase):
    """Test SavedScholarship model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.scholarship = Scholarship.objects.create(
            title='Test Scholarship',
            provider='Test Provider',
            description='Test description',
            eligibility_criteria='Test criteria',
            status='active',
            slug='test-scholarship'
        )
    
    def test_create_saved_scholarship(self):
        """Test creating a saved scholarship."""
        saved = SavedScholarship.objects.create(
            user=self.user,
            scholarship=self.scholarship
        )
        self.assertEqual(saved.user, self.user)
        self.assertEqual(saved.scholarship, self.scholarship)


class ScholarshipsViewsTest(TestCase):
    """Test scholarships views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.scholarship = Scholarship.objects.create(
            title='Test Scholarship',
            provider='Test Provider',
            description='Test description',
            eligibility_criteria='Test criteria',
            status='active',
            slug='test-scholarship'
        )
    
    def test_scholarship_list_view(self):
        """Test scholarship list view."""
        url = reverse('scholarships:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_scholarship_detail_view(self):
        """Test scholarship detail view."""
        url = reverse('scholarships:detail', kwargs={'slug': self.scholarship.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

