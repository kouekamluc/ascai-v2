"""
Tests for mentorship app.
"""
from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import MentorProfile, MentorshipRequest, MentorshipMessage, MentorRating
from .services import create_request, accept_request, reject_request, complete_request

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
        profile = self.user.mentor_profile
        profile.specialization = 'Computer Science'
        profile.years_experience = 5
        profile.bio = 'Test bio'
        profile.availability_status = 'available'
        profile.save()
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.specialization, 'Computer Science')
        self.assertEqual(profile.rating, Decimal('0.00'))
    
    def test_mentor_profile_str(self):
        """Test mentor profile string representation."""
        profile = self.user.mentor_profile
        profile.specialization = 'Computer Science'
        profile.years_experience = 5
        profile.bio = 'Test bio'
        profile.save()
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
        self.mentor_profile = self.mentor_user.mentor_profile
        self.mentor_profile.specialization = 'Computer Science'
        self.mentor_profile.years_experience = 5
        self.mentor_profile.bio = 'Test bio'
        self.mentor_profile.save()
    
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

    def test_new_request_email_includes_logo(self):
        MentorshipRequest.objects.create(
            student=self.student,
            mentor=self.mentor_profile,
            subject='Email Branding',
            message='Please help me settle in Rome.',
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].alternatives)
        html_body = mail.outbox[0].alternatives[0][0]
        self.assertIn('<img src="', html_body)
        self.assertIn('web-app-manifest-512x512.png', html_body)


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
        self.mentor_profile = self.mentor_user.mentor_profile
        self.mentor_profile.specialization = 'Computer Science'
        self.mentor_profile.years_experience = 5
        self.mentor_profile.bio = 'Test bio'
        self.mentor_profile.is_approved = True
        self.mentor_profile.save()
    
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


class MentorshipWorkflowServiceTest(TestCase):
    """Regression coverage for the shared mentorship workflow service."""

    def setUp(self):
        self.student = User.objects.create_user(
            username='student_service',
            email='student_service@example.com',
            password='testpass123',
            role='student',
        )
        self.mentor_user = User.objects.create_user(
            username='mentor_service',
            email='mentor_service@example.com',
            password='testpass123',
            role='mentor',
        )
        self.mentor_profile = self.mentor_user.mentor_profile
        self.mentor_profile.specialization = 'Engineering'
        self.mentor_profile.years_experience = 6
        self.mentor_profile.bio = 'Experienced mentor'
        self.mentor_profile.is_approved = True
        self.mentor_profile.save()

    def test_shared_service_runs_full_request_lifecycle(self):
        mentorship_request = create_request(
            student=self.student,
            mentor=self.mentor_profile,
            subject='Need guidance',
            message='I would like help with settling in Rome.',
        )
        self.assertEqual(mentorship_request.status, 'pending')

        accept_request(mentorship_request=mentorship_request, actor=self.mentor_user)
        mentorship_request.refresh_from_db()
        self.assertEqual(mentorship_request.status, 'accepted')

        complete_request(mentorship_request=mentorship_request, actor=self.mentor_user)
        mentorship_request.refresh_from_db()
        self.mentor_profile.refresh_from_db()
        self.assertEqual(mentorship_request.status, 'completed')
        self.assertEqual(self.mentor_profile.students_helped, 1)

    def test_duplicate_active_request_is_blocked(self):
        create_request(
            student=self.student,
            mentor=self.mentor_profile,
            subject='First request',
            message='First message',
        )

        with self.assertRaisesMessage(ValidationError, 'active request'):
            create_request(
                student=self.student,
                mentor=self.mentor_profile,
                subject='Second request',
                message='Second message',
            )


class DashboardMentorshipWorkflowTest(TestCase):
    """Ensure dashboard actions use the same mentorship lifecycle rules."""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='student_dash',
            email='student_dash@example.com',
            password='testpass123',
            role='student',
            is_approved=True,
        )
        self.mentor_user = User.objects.create_user(
            username='mentor_dash',
            email='mentor_dash@example.com',
            password='testpass123',
            role='mentor',
            is_approved=True,
        )
        self.mentor_profile = self.mentor_user.mentor_profile
        self.mentor_profile.specialization = 'Law'
        self.mentor_profile.years_experience = 4
        self.mentor_profile.bio = 'Mentor bio'
        self.mentor_profile.is_approved = True
        self.mentor_profile.save()
        self.request = MentorshipRequest.objects.create(
            student=self.student,
            mentor=self.mentor_profile,
            subject='Dashboard test',
            message='Please help',
        )

    def test_dashboard_accept_and_complete_actions_update_request(self):
        self.client.login(username='mentor_dash', password='testpass123')
        accept_url = reverse(
            'dashboard:mentorship_accept_request',
            kwargs={'request_id': self.request.pk},
        )
        complete_url = reverse(
            'dashboard:mentorship_complete_request',
            kwargs={'request_id': self.request.pk},
        )

        accept_response = self.client.post(accept_url)
        self.assertEqual(accept_response.status_code, 302)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'accepted')

        complete_response = self.client.post(complete_url)
        self.assertEqual(complete_response.status_code, 302)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'completed')

