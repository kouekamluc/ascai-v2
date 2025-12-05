"""
Tests for mentorship app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import MentorProfile, MentorshipRequest, MentorshipMessage, MentorRating

User = get_user_model()


class MentorProfileModelTest(TestCase):
    """Test MentorProfile model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='mentor',
            email='mentor@example.com',
            password='testpass123',
            role='mentor'
        )
    
    def test_create_mentor_profile(self):
        """Test creating a mentor profile."""
        profile = MentorProfile.objects.create(
            user=self.user,
            specialization='Computer Science',
            years_experience=5,
            bio='Test bio',
            availability_status='available'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.specialization, 'Computer Science')
        self.assertEqual(profile.rating, Decimal('0.00'))
    
    def test_mentor_profile_str(self):
        """Test mentor profile string representation."""
        profile = MentorProfile.objects.create(
            user=self.user,
            specialization='Computer Science',
            years_experience=5,
            bio='Test bio'
        )
        self.assertIn('mentor', str(profile).lower())


class MentorshipRequestModelTest(TestCase):
    """Test MentorshipRequest model."""
    
    def setUp(self):
        """Set up test users."""
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
            role='student'
        )
        self.mentor_user = User.objects.create_user(
            username='mentor',
            email='mentor@example.com',
            password='testpass123',
            role='mentor'
        )
        self.mentor_profile = MentorProfile.objects.create(
            user=self.mentor_user,
            specialization='Computer Science',
            years_experience=5,
            bio='Test bio'
        )
    
    def test_create_mentorship_request(self):
        """Test creating a mentorship request."""
        request = MentorshipRequest.objects.create(
            student=self.student,
            mentor=self.mentor_profile,
            subject='Test Subject',
            message='Test message'
        )
        self.assertEqual(request.student, self.student)
        self.assertEqual(request.mentor, self.mentor_profile)
        self.assertEqual(request.status, 'pending')
    
    def test_mentorship_request_str(self):
        """Test mentorship request string representation."""
        request = MentorshipRequest.objects.create(
            student=self.student,
            mentor=self.mentor_profile,
            subject='Test Subject',
            message='Test message'
        )
        # The __str__ method returns "Request from {student} to {mentor}"
        self.assertIn('student', str(request).lower())
        self.assertIn('mentor', str(request).lower())


class MentorRatingModelTest(TestCase):
    """Test MentorRating model."""
    
    def setUp(self):
        """Set up test data."""
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123'
        )
        self.mentor_user = User.objects.create_user(
            username='mentor',
            email='mentor@example.com',
            password='testpass123'
        )
        self.mentor_profile = MentorProfile.objects.create(
            user=self.mentor_user,
            specialization='Computer Science',
            years_experience=5,
            bio='Test bio'
        )
        self.mentorship_request = MentorshipRequest.objects.create(
            student=self.student,
            mentor=self.mentor_profile,
            subject='Test Subject',
            message='Test message',
            status='completed'
        )
    
    def test_create_mentor_rating(self):
        """Test creating a mentor rating."""
        rating = MentorRating.objects.create(
            request=self.mentorship_request,
            mentor=self.mentor_profile,
            student=self.student,
            rating=5,
            comment='Great mentor!'
        )
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.comment, 'Great mentor!')


class MentorshipViewsTest(TestCase):
    """Test mentorship views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.mentor_user = User.objects.create_user(
            username='mentor',
            email='mentor@example.com',
            password='testpass123',
            role='mentor'
        )
        self.mentor_profile = MentorProfile.objects.create(
            user=self.mentor_user,
            specialization='Computer Science',
            years_experience=5,
            bio='Test bio',
            is_approved=True
        )
    
    def test_mentor_list_view(self):
        """Test mentor list view."""
        url = reverse('mentorship:mentor_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_mentor_detail_view(self):
        """Test mentor detail view."""
        url = reverse('mentorship:mentor_detail', kwargs={'pk': self.mentor_profile.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

