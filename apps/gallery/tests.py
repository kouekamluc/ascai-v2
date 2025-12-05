"""
Tests for gallery app.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import GalleryAlbum, GalleryImage

User = get_user_model()


class GalleryAlbumModelTest(TestCase):
    """Test GalleryAlbum model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_album(self):
        """Test creating a gallery album."""
        album = GalleryAlbum.objects.create(
            title='Test Album',
            description='Test description',
            created_by=self.user
        )
        self.assertEqual(album.title, 'Test Album')
        self.assertEqual(album.created_by, self.user)
    
    def test_album_str(self):
        """Test album string representation."""
        album = GalleryAlbum.objects.create(
            title='Test Album',
            created_by=self.user
        )
        self.assertEqual(str(album), 'Test Album')


class GalleryImageModelTest(TestCase):
    """Test GalleryImage model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.album = GalleryAlbum.objects.create(
            title='Test Album',
            created_by=self.user
        )
    
    def test_create_image(self):
        """Test creating a gallery image."""
        image = GalleryImage.objects.create(
            album=self.album,
            image=SimpleUploadedFile(
                "test.jpg",
                b"file_content",
                content_type="image/jpeg"
            )
        )
        self.assertEqual(image.album, self.album)
        self.assertIsNotNone(image.image)


class GalleryViewsTest(TestCase):
    """Test gallery views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.album = GalleryAlbum.objects.create(
            title='Test Album',
            created_by=self.user
        )
    
    def test_gallery_list_view(self):
        """Test gallery list view."""
        url = reverse('gallery:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_album_detail_view(self):
        """Test album detail view."""
        url = reverse('gallery:album_detail', kwargs={'pk': self.album.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

