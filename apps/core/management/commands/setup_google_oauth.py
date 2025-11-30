"""
Management command to set up Google OAuth SocialApplication.
This creates or updates the Google SocialApplication record in the database.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = 'Set up Google OAuth SocialApplication from environment variables'

    def handle(self, *args, **options):
        # Support both GOOGLE_CLIENT_ID and GOOGLE_OAUTH2_CLIENT_ID for flexibility
        client_id = config('GOOGLE_OAUTH2_CLIENT_ID', default=config('GOOGLE_CLIENT_ID', default=''))
        client_secret = config('GOOGLE_OAUTH2_CLIENT_SECRET', default=config('GOOGLE_CLIENT_SECRET', default=''))
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.WARNING(
                    'Google OAuth credentials not found in environment variables.\n'
                    'Please set either:\n'
                    '  - GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET, OR\n'
                    '  - GOOGLE_OAUTH2_CLIENT_ID and GOOGLE_OAUTH2_CLIENT_SECRET\n'
                    'The Google login button will not appear until credentials are set.'
                )
            )
            return
        
        # Get the current site
        try:
            site = Site.objects.get_current()
        except Site.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('No Site object found. Please run migrations first.')
            )
            return
        
        # Delete all existing Google SocialApplications to prevent MultipleObjectsReturned errors
        existing_count = SocialApp.objects.filter(provider='google').count()
        if existing_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Found {existing_count} existing Google SocialApplication(s). Deleting to prevent conflicts...'
                )
            )
            SocialApp.objects.filter(provider='google').delete()
            self.stdout.write(
                self.style.SUCCESS(f'✓ Deleted {existing_count} existing Google SocialApplication(s)')
            )
        
        # Create a new Google SocialApplication
        social_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=client_secret,
            key='',
        )
        
        # Add the site to the social app
        social_app.sites.add(site)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Google OAuth SocialApplication created successfully!\n'
                f'   Client ID: {client_id[:20]}...\n'
                f'   Site: {site.domain}\n'
                f'   Total Google apps after cleanup: 1'
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Google login button should now be visible on login and signup pages!'
            )
        )

