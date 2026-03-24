"""
Management command to diagnose Google OAuth redirect URI issues.
This helps identify why redirect_uri_mismatch errors occur.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from decouple import config
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Diagnose Google OAuth redirect URI mismatch issues'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('🔍 Google OAuth Redirect URI Diagnostic'))
        self.stdout.write('='*70 + '\n')
        
        # Get credentials
        client_id = config('GOOGLE_OAUTH2_CLIENT_ID', default=config('GOOGLE_CLIENT_ID', default=''))
        client_secret = config('GOOGLE_OAUTH2_CLIENT_SECRET', default=config('GOOGLE_CLIENT_SECRET', default=''))
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR('❌ Google OAuth credentials not found in environment variables.')
            )
            return
        
        # Get Site domain
        try:
            site = Site.objects.get_current()
            site_domain = site.domain
        except Site.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ No Site object found. Run: python manage.py migrate')
            )
            return
        
        # Get SocialApp
        try:
            social_app = SocialApp.objects.get(provider='google')
        except SocialApp.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('❌ Google SocialApp not found. Run: python manage.py setup_google_oauth')
            )
            return
        except SocialApp.MultipleObjectsReturned:
            self.stdout.write(
                self.style.ERROR('❌ Multiple Google SocialApps found. Run: python manage.py setup_google_oauth')
            )
            return
        
        # Calculate what Django is sending
        protocol = 'https' if not settings.DEBUG else 'http'
        redirect_uri = f"{protocol}://{site_domain}/accounts/google/login/callback/"
        
        self.stdout.write(self.style.SUCCESS('📋 Current Configuration:'))
        self.stdout.write(f'   Site Domain: {site_domain}')
        self.stdout.write(f'   Protocol: {protocol}')
        self.stdout.write(f'   Client ID: {client_id[:40]}...')
        self.stdout.write(f'   Redirect URI Django is sending:')
        self.stdout.write(self.style.WARNING(f'      {redirect_uri}'))
        
        # Check for common issues
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('🔍 Diagnostic Checks'))
        self.stdout.write('='*70 + '\n')
        
        issues = []
        fixes = []
        
        # Check 1: www vs non-www
        if 'www.' in site_domain:
            non_www = site_domain.replace('www.', '')
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Site domain includes "www": {site_domain}\n'
                    f'   You may need to add BOTH redirect URIs to Google Cloud Console:\n'
                    f'   1. {redirect_uri}\n'
                    f'   2. {protocol}://{non_www}/accounts/google/login/callback/'
                )
            )
            fixes.append(f'Add both www and non-www redirect URIs to Google Cloud Console')
        elif not site_domain.startswith('www.'):
            www_domain = f'www.{site_domain}'
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Site domain does NOT include "www": {site_domain}\n'
                    f'   If users access via www.{site_domain}, you may need to add:\n'
                    f'   {protocol}://{www_domain}/accounts/google/login/callback/'
                )
            )
            fixes.append(f'Consider adding www redirect URI if users access via www subdomain')
        
        # Check 2: HTTP in production
        if not settings.DEBUG and protocol == 'http':
            issues.append('Using HTTP in production (should be HTTPS)')
            fixes.append('Ensure DEBUG=False in production')
        
        # Check 3: localhost in production
        if not settings.DEBUG and ('localhost' in site_domain or '127.0.0.1' in site_domain):
            issues.append(f'Site domain is localhost in production: {site_domain}')
            fixes.append(f'Run: python manage.py update_site_domain --domain your-production-domain.com')
        
        # Check 4: Client ID mismatch
        if social_app.client_id != client_id:
            issues.append('SocialApp Client ID does not match environment variable')
            fixes.append('Run: python manage.py setup_google_oauth')
        
        # Check 5: Site not linked
        if site not in social_app.sites.all():
            issues.append('Current Site is not linked to SocialApp')
            fixes.append('Run: python manage.py setup_google_oauth')
        
        # Check 6: ALLOWED_HOSTS
        if site_domain not in settings.ALLOWED_HOSTS:
            # Check for partial matches
            matches = [h for h in settings.ALLOWED_HOSTS 
                      if site_domain in h or h.replace('.', '') in site_domain.replace('.', '')]
            if not matches:
                issues.append(f'Site domain ({site_domain}) not in ALLOWED_HOSTS')
                fixes.append(f'Add {site_domain} to ALLOWED_HOSTS or update Site domain')
        
        # Display issues
        if issues:
            self.stdout.write(self.style.ERROR('❌ Issues Found:'))
            for i, issue in enumerate(issues, 1):
                self.stdout.write(f'   {i}. {issue}')
        else:
            self.stdout.write(self.style.SUCCESS('✅ No configuration issues detected'))
        
        # Display fixes
        if fixes:
            self.stdout.write('\n' + self.style.SUCCESS('🔧 Recommended Fixes:'))
            for i, fix in enumerate(fixes, 1):
                self.stdout.write(f'   {i}. {fix}')
        
        # Final instructions
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('📝 Next Steps'))
        self.stdout.write('='*70 + '\n')
        self.stdout.write(
            '1. Copy the redirect URI above (the one Django is sending)\n'
            '2. Go to: https://console.cloud.google.com/\n'
            '3. Navigate to: APIs & Services → Credentials\n'
            '4. Find the OAuth 2.0 Client ID matching: ' + client_id[:40] + '...\n'
            '5. Click on it to edit\n'
            '6. Under "Authorized redirect URIs", verify the EXACT URI is there:\n'
        )
        self.stdout.write(self.style.WARNING(f'   {redirect_uri}'))
        self.stdout.write(
            '\n7. Check for these common mistakes:\n'
            '   - Missing trailing slash (/)\n'
            '   - Using http:// instead of https://\n'
            '   - Extra spaces or characters\n'
            '   - Wrong domain (www vs non-www)\n'
            '\n8. If the URI is there but still not working:\n'
            '   - Wait 2-3 minutes for Google changes to propagate\n'
            '   - Clear browser cache or use incognito mode\n'
            '   - Check if you edited the correct OAuth Client ID\n'
            '   - Verify the Client ID in Google Cloud Console matches your environment variable'
        )
        self.stdout.write('\n' + '='*70 + '\n')
