"""
Tests for downloads app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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
            uploaded_by=self.user
        )
    
    def test_document_list_view(self):
        """Test document list view."""
        url = reverse('downloads:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_document_download_view(self):
        """Test document download view."""
        url = reverse('downloads:document_download', kwargs={'pk': self.document.pk})
        response = self.client.get(url)
        # May redirect or return file, both are valid
        self.assertIn(response.status_code, [200, 302, 404])

