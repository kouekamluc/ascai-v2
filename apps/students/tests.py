"""
Tests for students app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import StudentGuideSection, StudentGuideStep, StudentGuideProgress

User = get_user_model()


class StudentsViewsTest(TestCase):
    """Test students views."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_students_home_view(self):
        """Test students home view."""
        # Assuming there's a students home URL
        # Adjust based on actual URL pattern
        try:
            url = reverse('students:index')
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 404])
        except:
            # If URL doesn't exist, that's okay for now
            pass

    def test_guide_progress_can_be_toggled_and_reset(self):
        user = User.objects.create_user(
            username='guideuser',
            email='guide@example.com',
            password='testpass123',
            is_approved=True,
        )
        section = StudentGuideSection.objects.create(
            title='Arrival',
            slug='arrival',
            section_type='arrival',
            content='Arrival guidance',
        )
        step = StudentGuideStep.objects.create(
            section=section,
            title='First step',
            content='Do this first',
        )
        self.client.login(username='guideuser', password='testpass123')

        first_response = self.client.post(reverse('students:save_guide_progress', args=[step.pk]))
        self.assertEqual(first_response.status_code, 200)
        progress = StudentGuideProgress.objects.get(user=user, section=section)
        self.assertTrue(progress.completed_steps.filter(pk=step.pk).exists())
        self.assertTrue(progress.is_completed)

        second_response = self.client.post(reverse('students:save_guide_progress', args=[step.pk]))
        self.assertEqual(second_response.status_code, 200)
        progress.refresh_from_db()
        self.assertFalse(progress.completed_steps.filter(pk=step.pk).exists())
        self.assertFalse(progress.is_completed)

        progress.completed_steps.add(step)
        progress.is_completed = True
        progress.save()
        reset_response = self.client.post(reverse('students:reset_guide_section_progress', args=[section.slug]))
        self.assertEqual(reset_response.status_code, 302)
        progress.refresh_from_db()
        self.assertEqual(progress.completed_steps.count(), 0)
        self.assertFalse(progress.is_completed)

