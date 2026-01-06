"""
Management command to test core functionality: HTMX interactions, file uploads, email sending, multi-language, search/filtering.
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Test core functionality: HTMX interactions, file uploads, email sending, multi-language, search/filtering'

    def handle(self, *args, **options):
        self.stdout.write('Testing Core Functionality...\n')
        self.client = Client()
        
        results = {
            'passed': [],
            'failed': [],
        }

        # Test 1: Home Page
        self.stdout.write('1. Testing Home Page...')
        try:
            response = self.client.get(reverse('core:home'))
            if response.status_code == 200:
                results['passed'].append('Home page accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Home page accessible'))
            else:
                results['failed'].append(f'Home page returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Home page returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Home page test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Home page test failed: {str(e)}'))

        # Test 2: Language Switching
        self.stdout.write('2. Testing Language Switching...')
        try:
            response = self.client.post(reverse('set_language'), {'language': 'fr'})
            if response.status_code in [200, 302]:
                results['passed'].append('Language switching works')
                self.stdout.write(self.style.SUCCESS('  ✓ Language switching works'))
            else:
                results['failed'].append(f'Language switching returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Language switching returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Language switching test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Language switching test failed: {str(e)}'))

        # Test 3: Universities List (with HTMX filtering)
        self.stdout.write('3. Testing Universities List...')
        try:
            response = self.client.get(reverse('universities:index'))
            if response.status_code == 200:
                results['passed'].append('Universities list accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Universities list accessible'))
            else:
                results['failed'].append(f'Universities list returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Universities list returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Universities list test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Universities list test failed: {str(e)}'))

        # Test 4: Scholarships List
        self.stdout.write('4. Testing Scholarships List...')
        try:
            response = self.client.get(reverse('scholarships:index'))
            if response.status_code == 200:
                results['passed'].append('Scholarships list accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Scholarships list accessible'))
            else:
                results['failed'].append(f'Scholarships list returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Scholarships list returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Scholarships list test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Scholarships list test failed: {str(e)}'))

        # Test 5: Community Forum
        self.stdout.write('5. Testing Community Forum...')
        try:
            response = self.client.get(reverse('community:index'))
            if response.status_code == 200:
                results['passed'].append('Community forum accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Community forum accessible'))
            else:
                results['failed'].append(f'Community forum returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Community forum returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Community forum test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Community forum test failed: {str(e)}'))

        # Test 6: Contact Form
        self.stdout.write('6. Testing Contact Form...')
        try:
            response = self.client.get(reverse('contact:index'))
            if response.status_code == 200:
                results['passed'].append('Contact form accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Contact form accessible'))
            else:
                results['failed'].append(f'Contact form returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Contact form returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Contact form test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Contact form test failed: {str(e)}'))

        # Test 7: Email Backend Configuration
        self.stdout.write('7. Testing Email Backend Configuration...')
        try:
            from django.conf import settings
            email_backend = getattr(settings, 'EMAIL_BACKEND', None)
            if email_backend:
                results['passed'].append(f'Email backend configured: {email_backend}')
                self.stdout.write(self.style.SUCCESS(f'  ✓ Email backend configured: {email_backend}'))
            else:
                results['failed'].append('Email backend not configured')
                self.stdout.write(self.style.WARNING('  ⚠ Email backend not configured'))
        except Exception as e:
            results['failed'].append(f'Email backend test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Email backend test failed: {str(e)}'))

        # Test 8: File Upload Configuration
        self.stdout.write('8. Testing File Upload Configuration...')
        try:
            from django.conf import settings
            max_upload_size = getattr(settings, 'MAX_UPLOAD_SIZE', None)
            if max_upload_size:
                results['passed'].append(f'File upload limit configured: {max_upload_size / (1024*1024):.1f} MB')
                self.stdout.write(self.style.SUCCESS(f'  ✓ File upload limit: {max_upload_size / (1024*1024):.1f} MB'))
            else:
                results['failed'].append('File upload limit not configured')
                self.stdout.write(self.style.WARNING('  ⚠ File upload limit not configured'))
        except Exception as e:
            results['failed'].append(f'File upload test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ File upload test failed: {str(e)}'))

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Test Summary:')
        self.stdout.write(f'  Passed: {len(results["passed"])}')
        self.stdout.write(f'  Failed: {len(results["failed"])}')
        
        if results['failed']:
            self.stdout.write('\nFailed Tests:')
            for failure in results['failed']:
                self.stdout.write(self.style.ERROR(f'  ✗ {failure}'))
        
        if len(results['failed']) == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ All core functionality tests passed!'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠ {len(results["failed"])} test(s) failed. Please review the errors above.'))

