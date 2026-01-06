"""
Comprehensive management command to populate all initial data.
This command calls all other population commands in the correct order.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Populate all initial data: forum categories, news, events, universities, scholarships'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )
        parser.add_argument(
            '--skip-universities',
            action='store_true',
            help='Skip populating universities',
        )
        parser.add_argument(
            '--skip-scholarships',
            action='store_true',
            help='Skip populating scholarships',
        )
        parser.add_argument(
            '--skip-forum',
            action='store_true',
            help='Skip populating forum categories',
        )
        parser.add_argument(
            '--skip-content',
            action='store_true',
            help='Skip populating news and events',
        )

    def handle(self, *args, **options):
        clear = options.get('clear', False)
        self.stdout.write('='*60)
        self.stdout.write(self.style.SUCCESS('Populating All Initial Data'))
        self.stdout.write('='*60 + '\n')

        commands_run = 0
        commands_failed = 0

        # 1. Populate Forum Categories
        if not options.get('skip_forum', False):
            self.stdout.write('\n1. Populating Forum Categories...')
            try:
                call_command('populate_forum_categories', clear=clear, verbosity=0)
                commands_run += 1
                self.stdout.write(self.style.SUCCESS('  ✓ Forum categories populated'))
            except Exception as e:
                commands_failed += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Failed: {str(e)}'))

        # 2. Populate News and Events
        if not options.get('skip_content', False):
            self.stdout.write('\n2. Populating News and Events...')
            try:
                call_command('populate_initial_content', clear=clear, verbosity=0)
                commands_run += 1
                self.stdout.write(self.style.SUCCESS('  ✓ News and events populated'))
            except Exception as e:
                commands_failed += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Failed: {str(e)}'))

        # 3. Populate Universities
        if not options.get('skip_universities', False):
            self.stdout.write('\n3. Populating Universities...')
            try:
                call_command('populate_universities', clear=clear, verbosity=0)
                commands_run += 1
                self.stdout.write(self.style.SUCCESS('  ✓ Universities populated'))
            except Exception as e:
                commands_failed += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Failed: {str(e)}'))

        # 4. Populate Scholarships
        if not options.get('skip_scholarships', False):
            self.stdout.write('\n4. Populating Scholarships...')
            try:
                call_command('populate_scholarships', clear=clear, verbosity=0)
                commands_run += 1
                self.stdout.write(self.style.SUCCESS('  ✓ Scholarships populated'))
            except Exception as e:
                commands_failed += 1
                self.stdout.write(self.style.ERROR(f'  ✗ Failed: {str(e)}'))

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write('Population Summary:')
        self.stdout.write(f'  Commands Run: {commands_run}')
        self.stdout.write(f'  Commands Failed: {commands_failed}')
        
        if commands_failed == 0:
            self.stdout.write(self.style.SUCCESS('\n✓ All data population completed successfully!'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠ {commands_failed} command(s) failed. Please review the errors above.'))

