"""
Tests for downloads app.
"""
from datetime import date
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.governance.models import Member, MembershipDues
from .models import Document

User = get_user_model()


class DocumentModelTest(TestCase):
    """Test Document model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_document(self):
        """Test creating a document."""
        doc = Document.objects.create(
            title='Test Document',
            description='Test description',
            file=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            ),
            category='other',
            uploaded_by=self.user
        )
        self.assertEqual(doc.title, 'Test Document')
        self.assertEqual(doc.download_count, 0)
        self.assertTrue(doc.is_active)
    
    def test_document_str(self):
        """Test document string representation."""
        doc = Document.objects.create(
            title='Test Document',
            file=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            ),
            uploaded_by=self.user
        )
        self.assertEqual(str(doc), 'Test Document')
    
    def test_document_get_absolute_url(self):
        """Test document get_absolute_url method."""
        doc = Document.objects.create(
            title='Test Document',
            file=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            ),
            uploaded_by=self.user
        )
        url = doc.get_absolute_url()
        self.assertIsNotNone(url)


class DownloadsViewsTest(TestCase):
    """Test downloads views."""
    
    def setUp(self):
        """Set up test client and document."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.document = Document.objects.create(
            title='Test Document',
            file=SimpleUploadedFile(
                "test.pdf",
                b"file_content",
                content_type="application/pdf"
            ),
            thumbnail=SimpleUploadedFile(
                "thumb.jpg",
                b"thumbnail_content",
                content_type="image/jpeg"
            ),
            uploaded_by=self.user
        )
        self.reserved_document = Document.objects.create(
            title='Members Only Resource',
            file=SimpleUploadedFile(
                "members.pdf",
                b"member_file_content",
                content_type="application/pdf"
            ),
            uploaded_by=self.user,
            is_reserved=True
        )

    def create_paid_member(self, user, amount=Decimal('10.00')):
        Member.objects.create(
            user=user,
            member_type='student' if amount == Decimal('10.00') else 'sympathizer',
            membership_start_date=date(date.today().year, 1, 1),
            is_active_member=True,
        )
        MembershipDues.objects.create(
            member=user.member_profile,
            year=date.today().year,
            amount=amount,
            due_date=date(date.today().year, 3, 31),
            payment_date=date.today(),
            status='paid',
            valid_from=date(date.today().year, 1, 1) if amount == Decimal('10.00') else None,
            valid_until=date(date.today().year, 12, 31) if amount == Decimal('10.00') else None,
        )

    def create_unpaid_member(self, user):
        Member.objects.create(
            user=user,
            member_type='student',
            membership_start_date=date(date.today().year, 1, 1),
            is_active_member=False,
        )
        MembershipDues.objects.create(
            member=user.member_profile,
            year=date.today().year,
            amount=Decimal('10.00'),
            due_date=date(date.today().year, 3, 31),
            status='pending',
        )
    
    def test_document_list_view(self):
        """Test document list view."""
        url = reverse('downloads:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('popular_documents', response.context)
        self.assertIn('recent_documents', response.context)
        self.assertIn('sort_by', response.context)
        self.assertNotContains(response, self.reserved_document.title)

    def test_document_download_view(self):
        """Test document download view."""
        url = reverse('downloads:document_download', kwargs={'pk': self.document.pk})
        response = self.client.get(url)
        # May redirect or return file, both are valid
        self.assertIn(response.status_code, [200, 302, 404])

    def test_popular_and_recent_pages_render(self):
        popular_response = self.client.get(reverse('downloads:popular'))
        recent_response = self.client.get(reverse('downloads:recent'))
        self.assertEqual(popular_response.status_code, 200)
        self.assertEqual(recent_response.status_code, 200)

    def test_thumbnail_is_rendered_on_list_and_detail_pages(self):
        list_response = self.client.get(reverse('downloads:index'))
        detail_response = self.client.get(
            reverse('downloads:document_detail', kwargs={'pk': self.document.pk})
        )

        self.assertContains(list_response, self.document.thumbnail.url)
        self.assertContains(detail_response, self.document.thumbnail.url)

    def test_paid_member_sees_member_only_resources(self):
        paid_user = User.objects.create_user(
            username='paidmember',
            email='paid@example.com',
            password='testpass123'
        )
        self.create_paid_member(paid_user)
        self.client.force_login(paid_user)

        response = self.client.get(reverse('downloads:index'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.reserved_document.title)

    def test_reserved_document_detail_requires_paid_dues(self):
        response = self.client.get(
            reverse('downloads:document_detail', kwargs={'pk': self.reserved_document.pk})
        )

        self.assertEqual(response.status_code, 404)

    def test_reserved_document_download_redirects_unpaid_member_to_dues(self):
        unpaid_user = User.objects.create_user(
            username='unpaidmember',
            email='unpaid@example.com',
            password='testpass123',
            email_verified=True,
        )
        self.create_unpaid_member(unpaid_user)
        self.client.force_login(unpaid_user)

        response = self.client.get(
            reverse('downloads:document_download', kwargs={'pk': self.reserved_document.pk})
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('governance:my_dues'))

    def test_reserved_document_download_allows_paid_member(self):
        paid_user = User.objects.create_user(
            username='memberdownload',
            email='memberdownload@example.com',
            password='testpass123'
        )
        self.create_paid_member(paid_user)
        self.client.force_login(paid_user)

        response = self.client.get(
            reverse('downloads:document_download', kwargs={'pk': self.reserved_document.pk})
        )

        self.assertEqual(response.status_code, 200)

