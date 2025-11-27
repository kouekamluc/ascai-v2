"""
Management command to check migration state and provide guidance on fixing conflicts.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
import sys


class Command(BaseCommand):
    help = 'Check migration state and detect potential conflicts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix migration conflicts automatically',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed migration information',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking migration state...\n'))
        
        # Check database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.stdout.write(self.style.SUCCESS('✓ Database connection successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection failed: {e}'))
            sys.exit(1)
        
        # Check migration state
        self.stdout.write('\nChecking applied migrations...')
        try:
            # Get unapplied migrations
            from io import StringIO
            output = StringIO()
            call_command('showmigrations', '--plan', stdout=output)
            output.seek(0)
            migration_output = output.read()
            
            unapplied = [line for line in migration_output.split('\n') if '[ ]' in line]
            applied = [line for line in migration_output.split('\n') if '[X]' in line]
            
            if unapplied:
                self.stdout.write(self.style.WARNING(f'\n⚠ Found {len(unapplied)} unapplied migration(s):'))
                for migration in unapplied[:10]:  # Show first 10
                    self.stdout.write(f'  - {migration.strip()}')
                if len(unapplied) > 10:
                    self.stdout.write(f'  ... and {len(unapplied) - 10} more')
            else:
                self.stdout.write(self.style.SUCCESS(f'\n✓ All migrations are applied ({len(applied)} total)'))
            
            # Check for potential conflicts
            self.stdout.write('\nChecking for potential conflicts...')
            try:
                # Try to run migrate in dry-run mode to detect conflicts
                from io import StringIO
                error_output = StringIO()
                try:
                    call_command('migrate', '--plan', stdout=StringIO(), stderr=error_output)
                except Exception as e:
                    error_str = str(e)
                    if 'duplicate key value violates unique constraint' in error_str or 'pg_type_typname_nsp_index' in error_str:
                        self.stdout.write(self.style.ERROR('\n✗ Migration conflict detected!'))
                        self.stdout.write(self.style.WARNING('\nThis usually indicates a partial migration state.'))
                        self.stdout.write('\nPossible solutions:')
                        self.stdout.write('1. Check if PostgreSQL types already exist in the database')
                        self.stdout.write('2. Manually mark conflicting migrations as applied if types exist')
                        self.stdout.write('3. Reset the database if in development (WARNING: data loss)')
                        self.stdout.write('4. Contact database administrator for assistance')
                        
                        if options['fix']:
                            self.stdout.write(self.style.WARNING('\nAttempting automatic fix...'))
                            # This would require more sophisticated logic
                            self.stdout.write('Automatic fix not yet implemented. Manual intervention required.')
                    else:
                        self.stdout.write(self.style.ERROR(f'\n✗ Migration error: {e}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'\n⚠ Could not check for conflicts: {e}'))
            
            if options['verbose']:
                self.stdout.write('\n' + '='*50)
                self.stdout.write('Full migration plan:')
                self.stdout.write('='*50)
                self.stdout.write(migration_output)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n✗ Error checking migrations: {e}'))
            sys.exit(1)
        
        self.stdout.write(self.style.SUCCESS('\n✓ Migration check completed'))





