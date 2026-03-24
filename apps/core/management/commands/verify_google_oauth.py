"""
Management command to verify Google OAuth configuration and redirect URI.
This helps diagnose redirect_uri_mismatch errors.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from decouple import config


class Command(BaseCommand):
    help = 'Verify Google OAuth configuration and display redirect URI for Google Cloud Console'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('Google OAuth Configuration Verification'))
        self.stdout.write('='*70 + '\n')
        
        # Check environment variables
        client_id = config('GOOGLE_OAUTH2_CLIENT_ID', default=config('GOOGLE_CLIENT_ID', default=''))
        client_secret = config('GOOGLE_OAUTH2_CLIENT_SECRET', default=config('GOOGLE_CLIENT_SECRET', default=''))
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Google OAuth credentials not found in environment variables.\n'
                    '   Please set either:\n'
                    '   - GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET, OR\n'
                    '   - GOOGLE_OAUTH2_CLIENT_ID and GOOGLE_OAUTH2_CLIENT_SECRET'
                )
            )
            return
        
        self.stdout.write(self.style.SUCCESS(f'✅ Google OAuth credentials found'))
        self.stdout.write(f'   Client ID: {client_id[:30]}...\n')
        
        # Check Site domain
        try:
            site = Site.objects.get_current()
            site_domain = site.domain
            self.stdout.write(self.style.SUCCESS(f'✅ Site domain configured: {site_domain}'))
        except Site.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    '❌ No Site object found. Please run migrations first.\n'
                    '   Run: python manage.py migrate'
                )
            )
            return
        
        # Check SocialApp
        try:
            social_app = SocialApp.objects.get(provider='google')
            self.stdout.write(self.style.SUCCESS(f'✅ Google SocialApp found in database'))
            
            # Check if client IDs match
            if social_app.client_id != client_id:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  WARNING: SocialApp Client ID does not match environment variable!\n'
                        f'   Database: {social_app.client_id[:30]}...\n'
                        f'   Environment: {client_id[:30]}...\n'
                        f'   Run: python manage.py setup_google_oauth'
                    )
                )
            else:
                self.stdout.write(self.style.SUCCESS('✅ SocialApp Client ID matches environment variable'))
            
            # Check sites
            app_sites = list(social_app.sites.all())
            if site in app_sites:
                self.stdout.write(self.style.SUCCESS(f'✅ Current Site is linked to SocialApp'))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  WARNING: Current Site ({site_domain}) is NOT linked to SocialApp!\n'
                        f'   Linked sites: {[s.domain for s in app_sites]}\n'
                        f'   Run: python manage.py setup_google_oauth'
                    )
                )
        except SocialApp.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Google SocialApp not found in database.\n'
                    '   Run: python manage.py setup_google_oauth'
                )
            )
            return
        except SocialApp.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Multiple Google SocialApps found in database!\n'
                    '   This will cause errors. Run: python manage.py setup_google_oauth\n'
                    '   (This will clean up duplicates)'
                )
            )
            return
        
        # Calculate redirect URI
        protocol = 'https' if not settings.DEBUG else 'http'
        redirect_uri = f"{protocol}://{site_domain}/accounts/google/login/callback/"
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('📋 Redirect URI Configuration'))
        self.stdout.write('='*70 + '\n')
        self.stdout.write(
            f'The redirect URI for this application is:\n'
            f'   {self.style.SUCCESS(redirect_uri)}\n'
        )
        self.stdout.write(
            self.style.WARNING(
                '⚠️  IMPORTANT: This URI MUST be added to Google Cloud Console:\n'
                '   1. Go to: https://console.cloud.google.com/\n'
                '   2. Select your project\n'
                '   3. Navigate to: APIs & Services → Credentials\n'
                '   4. Click on your OAuth 2.0 Client ID\n'
                '   5. Under "Authorized redirect URIs", add:\n'
                f'      {redirect_uri}\n'
                '   6. Click "SAVE"\n'
            )
        )
        
        # Check for common issues
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('🔍 Common Issues Check'))
        self.stdout.write('='*70 + '\n')
        
        issues_found = []
        
        # Check if domain looks like localhost in production
        if not settings.DEBUG and ('localhost' in site_domain or '127.0.0.1' in site_domain):
            issues_found.append(
                f'⚠️  Site domain ({site_domain}) looks like localhost in production mode.\n'
                f'   Update it: python manage.py update_site_domain --domain your-production-domain.com'
            )
        
        # Check if using http in production
        if not settings.DEBUG and protocol == 'http':
            issues_found.append(
                '⚠️  Using HTTP in production. Should use HTTPS.\n'
                '   Check your settings.DEBUG value.'
            )
        
        # Check if domain matches ALLOWED_HOSTS
        if site_domain not in settings.ALLOWED_HOSTS:
            # Check if any ALLOWED_HOST matches
            matches = [h for h in settings.ALLOWED_HOSTS if site_domain in h or h.replace('.', '') in site_domain]
            if not matches:
                issues_found.append(
                    f'⚠️  Site domain ({site_domain}) not in ALLOWED_HOSTS.\n'
                    f'   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}\n'
                    f'   Consider updating Site domain or adding it to ALLOWED_HOSTS.'
                )
        
        if issues_found:
            for issue in issues_found:
                self.stdout.write(self.style.WARNING(issue))
        else:
            self.stdout.write(self.style.SUCCESS('✅ No common issues detected'))
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(
            self.style.SUCCESS(
                '✅ Verification complete!\n'
                '   If you see "Error 400: redirect_uri_mismatch", ensure the redirect URI\n'
                '   above is added to Google Cloud Console.'
            )
        )
        self.stdout.write('='*70 + '\n')
