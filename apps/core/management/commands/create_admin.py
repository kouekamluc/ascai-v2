"""
Management command to automatically create a Django admin superuser.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Creates a Django admin superuser automatically'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing user if it already exists',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        # Hardcoded credentials as specified
        username = 'kouekam'
        password = 'kklkinkklk'
        email = 'admin@ascailazio.org'
        update = options.get('update', False)

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                if update:
                    user = User.objects.get(username=username)
                    user.set_password(password)
                    user.email = email
                    user.is_superuser = True
                    user.is_staff = True
                    user.is_active = True
                    user.role = 'admin'
                    user.is_approved = True
                    user.email_verified = True
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Successfully updated admin user "{username}"'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ User "{username}" already exists. Use --update to update it.'
                        )
                    )
                    return
            else:
                # Create new superuser
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )
                user.is_superuser = True
                user.is_staff = True
                user.is_active = True
                user.role = 'admin'
                user.is_approved = True
                user.email_verified = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Successfully created admin user "{username}"'
                    )
                )

            # Display user information
            self.stdout.write('\nAdmin user details:')
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Is Superuser: {user.is_superuser}')
            self.stdout.write(f'  Is Staff: {user.is_staff}')
            self.stdout.write(f'  Is Active: {user.is_active}')
            self.stdout.write(f'  Role: {user.role}')
            self.stdout.write(f'  Is Approved: {user.is_approved}')

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error creating user: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Unexpected error: {e}')
            )

