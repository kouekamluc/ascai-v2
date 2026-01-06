"""
Management command to run all test commands.
This provides a convenient way to test all functionality.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Run all test commands: auth flows, core functionality, workflows'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-auth',
            action='store_true',
            help='Skip authentication flow tests',
        )
        parser.add_argument(
            '--skip-core',
            action='store_true',
            help='Skip core functionality tests',
        )
        parser.add_argument(
            '--skip-workflows',
            action='store_true',
            help='Skip workflow tests',
        )

    def handle(self, *args, **options):
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('Running All Tests'))
        self.stdout.write('='*60 + '\n')

        tests_run = 0
        tests_failed = 0

        # 1. Test Authentication Flows
        if not options.get('skip_auth', False):
            self.stdout.write('\n1. Testing Authentication Flows...')
            try:
                call_command('test_auth_flows', verbosity=1)
                tests_run += 1
            except Exception as e:
                tests_failed += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Authentication tests failed: {str(e)}'))

        # 2. Test Core Functionality
        if not options.get('skip_core', False):
            self.stdout.write('\n2. Testing Core Functionality...')
            try:
                call_command('test_core_functionality', verbosity=1)
                tests_run += 1
            except Exception as e:
                tests_failed += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Core functionality tests failed: {str(e)}'))

        # 3. Test Workflows
        if not options.get('skip_workflows', False):
            self.stdout.write('\n3. Testing Workflows...')
            try:
                call_command('test_workflows', verbosity=1)
                tests_run += 1
            except Exception as e:
                tests_failed += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Workflow tests failed: {str(e)}'))

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Test Summary:')
        self.stdout.write(f'  Tests Run: {tests_run}')
        self.stdout.write(f'  Tests Failed: {tests_failed}')
        
        if tests_failed == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ All tests completed!'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠ {tests_failed} test suite(s) had issues. Please review the output above.'))

