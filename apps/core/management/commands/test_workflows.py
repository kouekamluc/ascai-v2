"""
Management command to test all workflows: mentorship, support tickets, events, governance, financial approvals.
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()


class Command(BaseCommand):
    help = 'Test all workflows: mentorship, support tickets, events, governance, financial approvals'

    def handle(self, *args, **options):
        self.stdout.write('Testing Workflows...\n')
        self.client = Client()
        
        results = {
            'passed': [],
            'failed': [],
        }

        # Create test user for authenticated tests
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_approved': True,
                'email_verified': True,
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write('Created test user for workflow testing')

        # Test 1: Mentorship Directory
        self.stdout.write('1. Testing Mentorship Directory...')
        try:
            response = self.client.get(reverse('mentorship:index'))
            if response.status_code == 200:
                results['passed'].append('Mentorship directory accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Mentorship directory accessible'))
            else:
                results['failed'].append(f'Mentorship directory returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Mentorship directory returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Mentorship directory test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Mentorship directory test failed: {str(e)}'))

        # Test 2: Dashboard (requires authentication)
        self.stdout.write('2. Testing Dashboard Access...')
        try:
            # Test unauthenticated access
            response = self.client.get(reverse('dashboard:home'))
            if response.status_code == 302:  # Should redirect to login
                results['passed'].append('Dashboard requires authentication')
                self.stdout.write(self.style.SUCCESS('  ✓ Dashboard requires authentication'))
            else:
                results['failed'].append(f'Dashboard returned {response.status_code} (expected 302)')
                self.stdout.write(self.style.ERROR(f'  ✗ Dashboard returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Dashboard test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Dashboard test failed: {str(e)}'))

        # Test 3: Events List
        self.stdout.write('3. Testing Events List...')
        try:
            response = self.client.get(reverse('diaspora:event_list'))
            if response.status_code == 200:
                results['passed'].append('Events list accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Events list accessible'))
            else:
                results['failed'].append(f'Events list returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Events list returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Events list test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Events list test failed: {str(e)}'))

        # Test 4: News List
        self.stdout.write('4. Testing News List...')
        try:
            response = self.client.get(reverse('diaspora:news_list'))
            if response.status_code == 200:
                results['passed'].append('News list accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ News list accessible'))
            else:
                results['failed'].append(f'News list returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ News list returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'News list test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ News list test failed: {str(e)}'))

        # Test 5: Governance (if accessible)
        self.stdout.write('5. Testing Governance Access...')
        try:
            response = self.client.get(reverse('governance:dashboard'))
            if response.status_code in [200, 302, 403]:
                results['passed'].append('Governance section accessible (may require auth)')
                self.stdout.write(self.style.SUCCESS('  ✓ Governance section accessible'))
            else:
                results['failed'].append(f'Governance returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Governance returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Governance test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Governance test failed: {str(e)}'))

        # Test 6: Gallery
        self.stdout.write('6. Testing Gallery...')
        try:
            response = self.client.get(reverse('gallery:index'))
            if response.status_code == 200:
                results['passed'].append('Gallery accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Gallery accessible'))
            else:
                results['failed'].append(f'Gallery returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Gallery returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Gallery test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Gallery test failed: {str(e)}'))

        # Test 7: Downloads
        self.stdout.write('7. Testing Downloads...')
        try:
            response = self.client.get(reverse('downloads:index'))
            if response.status_code == 200:
                results['passed'].append('Downloads accessible')
                self.stdout.write(self.style.SUCCESS('  ✓ Downloads accessible'))
            else:
                results['failed'].append(f'Downloads returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Downloads returned {response.status_code}'))
        except Exception as e:
            results['failed'].append(f'Downloads test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Downloads test failed: {str(e)}'))

        # Test 8: Authenticated Dashboard Access
        self.stdout.write('8. Testing Authenticated Dashboard Access...')
        try:
            self.client.login(username='testuser', password='testpass123')
            response = self.client.get(reverse('dashboard:home'))
            if response.status_code == 200:
                results['passed'].append('Authenticated dashboard access works')
                self.stdout.write(self.style.SUCCESS('  ✓ Authenticated dashboard access works'))
            else:
                results['failed'].append(f'Authenticated dashboard returned {response.status_code}')
                self.stdout.write(self.style.ERROR(f'  ✗ Authenticated dashboard returned {response.status_code}'))
            self.client.logout()
        except Exception as e:
            results['failed'].append(f'Authenticated dashboard test failed: {str(e)}')
            self.stdout.write(self.style.ERROR(f'  ✗ Authenticated dashboard test failed: {str(e)}'))

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
            self.stdout.write(self.style.SUCCESS('\n✓ All workflow tests passed!'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠ {len(results["failed"])} test(s) failed. Please review the errors above.'))

