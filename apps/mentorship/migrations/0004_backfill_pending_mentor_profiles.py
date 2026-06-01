from django.db import migrations
from django.db.models import Q


def backfill_mentor_profiles(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    MentorProfile = apps.get_model("mentorship", "MentorProfile")

    existing_user_ids = set(MentorProfile.objects.values_list("user_id", flat=True))
    users = (
        User.objects.filter(is_superuser=False, is_staff=False, role="mentor")
        .filter(Q(email_verified=True) | Q(is_approved=True))
        .exclude(id__in=existing_user_ids)
    )

    MentorProfile.objects.bulk_create(
        [
            MentorProfile(
                user_id=user.id,
                specialization="Pending setup",
                years_experience=0,
                bio="Pending mentor profile completion.",
                availability_status="unavailable",
                is_approved=False,
            )
            for user in users
        ],
        ignore_conflicts=True,
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_user_language_preference"),
        ("mentorship", "0003_mentorspecialization_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_mentor_profiles, noop_reverse),
    ]
