"""
Delete stale accounts that never verified their email address.
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone


User = get_user_model()


class Command(BaseCommand):
    help = "Delete non-staff accounts that have not verified email after the configured grace period."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Delete unverified accounts older than this many days.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show accounts that would be deleted without deleting them.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]
        cutoff = timezone.now() - timedelta(days=days)

        stale_users = User.objects.filter(
            email_verified=False,
            date_joined__lt=cutoff,
            is_staff=False,
            is_superuser=False,
        )

        count = stale_users.count()
        if dry_run:
            self.stdout.write(f"DRY RUN: would delete {count} unverified account(s).")
            for user in stale_users.order_by("date_joined")[:25]:
                self.stdout.write(f"- {user.username} <{user.email}> joined {user.date_joined:%Y-%m-%d}")
            return

        deleted, details = stale_users.delete()
        user_count = details.get(f"{User._meta.app_label}.{User._meta.object_name}", 0)
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {user_count} unverified account(s) older than {days} day(s)."
            )
        )
