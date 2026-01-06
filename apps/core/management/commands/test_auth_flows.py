"""
Management command to test authentication flows.
This command simulates and tests various authentication scenarios.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Test authentication flows: registration, approval, email verification, OAuth, password reset'

    def handle(self, *args, **options):
        self.stdout.write('Testing Authentication Flows...\n')
        self.client = Client()
        
        results = {
            'passed': [],
            'failed': [],
        }

        # Test 1: User Registration
        self.stdout.write('1. Testing User Registration...')
        try:
            response = self.client.get(reverse('account_signup'))
            if response.status_code == 200:
                results['passed'].append('User registration page accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Registration page accessible'))
            else:
                results['failed'].append(f'Registration page returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Registration page returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Registration test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Registration test failed: {str(e)}'))

        # Test 2: Login Page
        self.stdout.write('2. Testing Login Page...')
        try:
            response = self.client.get(reverse('account_login'))
            if response.status_code == 200:
                results['passed'].append('Login page accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Login page accessible'))
            else:
                results['failed'].append(f'Login page returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Login page returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Login test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Login test failed: {str(e)}'))

        # Test 3: Password Reset
        self.stdout.write('3. Testing Password Reset...')
        try:
            response = self.client.get(reverse('account_reset_password'))
            if response.status_code == 200:
                results['passed'].append('Password reset page accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Password reset page accessible'))
            else:
                results['failed'].append(f'Password reset page returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Password reset page returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Password reset test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Password reset test failed: {str(e)}'))

        # Test 4: Email Verification
        self.stdout.write('4. Testing Email Verification...')
        try:
            response = self.client.get(reverse('account_email_verification_sent'))
            if response.status_code == 200:
                results['passed'].append('Email verification sent page accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Email verification sent page accessible'))
            else:
                results['failed'].append(f'Email verification page returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Email verification page returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Email verification test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Email verification test failed: {str(e)}'))

        # Test 5: Google OAuth (if configured)
        self.stdout.write('5. Testing Google OAuth...')
        try:
            from allauth.socialaccount.models import SocialApp
            if SocialApp.objects.filter(provider='google').exists():
                results['passed'].append('Google OAuth configured')
                self.stdout.write(self.style.SUCCESS('  ✓ Google OAuth is configured'))
            else:
                results['failed'].append('Google OAuth not configured')
                self.stdout.write(self.style.WARNING('  ⚠ Google OAuth not configured (this is optional)'))
        except Exception as e:
            results['failed'].append(f'Google OAuth test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Google OAuth test failed: {str(e)}'))

        # Test 6: Admin Approval Workflow
        self.stdout.write('6. Testing Admin Approval Workflow...')
        try:
            # Check if User model has is_approved field
            if hasattr(User, 'is_approved'):
                results['passed'].append('Admin approval field exists')
                self.stdout.write(self.style.SUCCESS('  ✓ Admin approval field exists'))
                
                # Check if there's a backend that checks approval
                from django.conf import settings
                if 'apps.accounts.backends.ApprovalRequiredBackend' in settings.AUTHENTICATION_BACKENDS:
                    results['passed'].append('Approval backend configured')
                    self.stdout.write(self.style.SUCCESS('  ✓ Approval backend configured'))
                else:
                    results['failed'].append('Approval backend not in AUTHENTICATION_BACKENDS')
                    self.stdout.write(self.style.ERROR('  ✗ Approval backend not configured'))
            else:
                results['failed'].append('is_approved field not found')
                self.stdout.write(self.style.ERROR('  ✗ is_approved field not found'))
        except Exception as e:
            results['failed'].append(f'Admin approval test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Admin approval test failed: {str(e)}'))

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
            self.stdout.write(self.style.SUCCESS('\n✓ All authentication flow tests passed!'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠ {len(results["failed"])} test(s) failed. Please review the errors above.'))

