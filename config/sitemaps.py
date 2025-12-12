"""
Sitemap configuration for ASCAI Lazio website.
Generates XML sitemaps for search engine optimization.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

# Import models
from apps.diaspora.models import News, Event, SuccessStory
from apps.universities.models import University
from apps.scholarships.models import Scholarship
from apps.gallery.models import GalleryAlbum
from apps.community.models import ForumThread, ForumCategory


class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages and main sections.
    """
    changefreq = 'weekly'

    def items(self):
        """
        Return list of URL names for static pages.
        """
        return [
            ('core:home', 1.0),  # Home page has highest priority
            ('diaspora:index', 0.8),
            ('community:index', 0.8),
            ('universities:index', 0.8),
            ('scholarships:index', 0.8),
            ('gallery:index', 0.8),
            ('downloads:index', 0.8),
            ('contact:index', 0.8),
            ('mentorship:index', 0.8),
        ]

    def location(self, item):
        """
        Return the URL path for each static page.
        """
        url_name, _ = item
        return reverse(url_name)

    def priority(self, item):
        """
        Return priority for each static page.
        """
        _, priority = item
        return priority

    def lastmod(self, item):
        """
        Return None for static pages (no modification date).
        """
        return None


class NewsSitemap(Sitemap):
    """
    Sitemap for news articles.
    """
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        """
        Return published news articles.
        """
        return News.objects.filter(is_published=True).order_by('-published_at', '-created_at')

    def lastmod(self, obj):
        """
        Return the last modification date of the news article.
        """
        return obj.updated_at or obj.published_at or obj.created_at

    def location(self, obj):
        """
        Return the URL path for the news article.
        """
        return reverse('diaspora:news_detail', kwargs={'slug': obj.slug})


class EventSitemap(Sitemap):
    """
    Sitemap for events.
    """
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        """
        Return published events.
        """
        return Event.objects.filter(is_published=True).order_by('-start_datetime')

    def lastmod(self, obj):
        """
        Return the creation date of the event.
        """
        return obj.created_at

    def location(self, obj):
        """
        Return the URL path for the event.
        """
        return reverse('diaspora:event_detail', kwargs={'slug': obj.slug})


class UniversitySitemap(Sitemap):
    """
    Sitemap for universities.
    """
    changefreq = 'monthly'
    priority = 0.64

    def items(self):
        """
        Return all universities.
        """
        return University.objects.all().order_by('name')

    def lastmod(self, obj):
        """
        Return the last update date of the university.
        """
        return obj.updated_at or obj.created_at

    def location(self, obj):
        """
        Return the URL path for the university.
        """
        return reverse('universities:detail', kwargs={'slug': obj.slug})


class ScholarshipSitemap(Sitemap):
    """
    Sitemap for scholarships.
    """
    changefreq = 'monthly'
    priority = 0.64

    def items(self):
        """
        Return active scholarships.
        """
        return Scholarship.objects.filter(status='active').order_by('-created_at')

    def lastmod(self, obj):
        """
        Return the last update date of the scholarship.
        """
        return obj.updated_at or obj.created_at

    def location(self, obj):
        """
        Return the URL path for the scholarship.
        """
        return reverse('scholarships:detail', kwargs={'slug': obj.slug})


class GalleryAlbumSitemap(Sitemap):
    """
    Sitemap for gallery albums.
    """
    changefreq = 'monthly'
    priority = 0.64

    def items(self):
        """
        Return all gallery albums.
        """
        return GalleryAlbum.objects.all().order_by('-created_at')

    def lastmod(self, obj):
        """
        Return the creation date of the album.
        """
        return obj.created_at

    def location(self, obj):
        """
        Return the URL path for the gallery album.
        """
        return reverse('gallery:album_detail', kwargs={'pk': obj.pk})


class SuccessStorySitemap(Sitemap):
    """
    Sitemap for success stories.
    """
    changefreq = 'monthly'
    priority = 0.64

    def items(self):
        """
        Return published success stories.
        """
        return SuccessStory.objects.filter(is_published=True).order_by('-created_at')

    def lastmod(self, obj):
        """
        Return the last update date of the success story.
        """
        return obj.updated_at or obj.created_at

    def location(self, obj):
        """
        Return the URL path for the success story.
        """
        return reverse('diaspora:success_story_detail', kwargs={'slug': obj.slug})


class AccountPagesSitemap(Sitemap):
    """
    Sitemap for account-related pages (login, signup, password reset).
    """
    changefreq = 'monthly'

    def items(self):
        """
        Return list of account URL names with priorities.
        """
        return [
            ('account_login', 0.8),
            ('account_signup', 0.8),
            ('account_reset_password', 0.64),
        ]

    def location(self, item):
        """
        Return the URL path for each account page.
        """
        url_name, _ = item
        return reverse(url_name)

    def priority(self, item):
        """
        Return priority for each account page.
        """
        _, priority = item
        return priority


class ScholarshipPagesSitemap(Sitemap):
    """
    Sitemap for scholarship section pages (including special pages like disco-lazio).
    """
    changefreq = 'monthly'
    priority = 0.64

    def items(self):
        """
        Return list of scholarship URL names.
        """
        return [
            'scholarships:disco_lazio',
        ]

    def location(self, item):
        """
        Return the URL path for each scholarship page.
        """
        return reverse(item)


class DiasporaPagesSitemap(Sitemap):
    """
    Sitemap for diaspora section pages.
    """
    changefreq = 'weekly'
    priority = 0.64

    def items(self):
        """
        Return list of diaspora URL names.
        """
        return [
            'diaspora:news_list',
            'diaspora:event_list',
            'diaspora:testimonial_list',
            'diaspora:success_story_list',
            'diaspora:life_in_italy_list',
        ]

    def location(self, item):
        """
        Return the URL path for each diaspora page.
        """
        return reverse(item)


# Dictionary mapping sitemap names to sitemap classes
sitemaps = {
    'static': StaticViewSitemap,
    'news': NewsSitemap,
    'events': EventSitemap,
    'universities': UniversitySitemap,
    'scholarships': ScholarshipSitemap,
    'scholarship_pages': ScholarshipPagesSitemap,
    'gallery': GalleryAlbumSitemap,
    'success_stories': SuccessStorySitemap,
    'accounts': AccountPagesSitemap,
    'diaspora_pages': DiasporaPagesSitemap,
}

