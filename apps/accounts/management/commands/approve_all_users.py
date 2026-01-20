"""
Management command to approve all existing users.
This is a one-time fix for users created before auto-approval was enabled.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Approve all existing users who are not yet approved'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be approved without actually approving',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all users who are not approved (excluding superusers who are already approved)
        unapproved_users = User.objects.filter(is_approved=False, is_superuser=False)
        count = unapproved_users.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✓ All users are already approved!')
            )
            return
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would approve {count} user(s):'
                )
            )
            for user in unapproved_users[:10]:  # Show first 10
                self.stdout.write(f'  - {user.username} ({user.email})')
            if count > 10:
                self.stdout.write(f'  ... and {count - 10} more')
        else:
            # Approve all users
            updated = unapproved_users.update(is_approved=True, is_active=True)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Successfully approved {updated} user(s)!'
                )
            )
