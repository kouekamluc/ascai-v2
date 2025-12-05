"""
Tests for contact app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from .models import ContactSubmission


class ContactSubmissionModelTest(TestCase):
    """Test ContactSubmission model."""
    
    def test_create_contact_submission(self):
        """Test creating a contact submission."""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message'
        )
        self.assertEqual(submission.name, 'John Doe')
        self.assertEqual(submission.email, 'john@example.com')
        self.assertEqual(submission.status, 'new')
    
    def test_contact_submission_str(self):
        """Test contact submission string representation."""
        submission = ContactSubmission.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test Subject',
            message='Test message'
        )
        self.assertIn('John Doe', str(submission))
        self.assertIn('Test Subject', str(submission))


class ContactViewsTest(TestCase):
    """Test contact views."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_contact_view_get(self):
        """Test contact view GET request."""
        url = reverse('contact:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_contact_view_post_valid(self):
        """Test contact form submission."""
        url = reverse('contact:index')
        response = self.client.post(url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        })
        # Should redirect or return success
        self.assertIn(response.status_code, [200, 302])
        # Check that submission was created
        self.assertTrue(ContactSubmission.objects.filter(email='john@example.com').exists())

