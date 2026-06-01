from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def backfill_student_profiles(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    StudentProfile = apps.get_model("students", "StudentProfile")

    existing_user_ids = set(StudentProfile.objects.values_list("user_id", flat=True))
    users = (
        User.objects.filter(is_superuser=False, is_staff=False, role="student")
        .exclude(id__in=existing_user_ids)
    )

    StudentProfile.objects.bulk_create(
        [StudentProfile(user_id=user.id) for user in users],
        ignore_conflicts=True,
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_user_language_preference"),
        ("students", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "onboarding_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending Review"),
                            ("in_progress", "In Progress"),
                            ("completed", "Completed"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="Onboarding Status",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Internal Notes")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Student Profile",
                "verbose_name_plural": "Student Profiles",
                "ordering": ["-created_at"],
            },
        ),
        migrations.RunPython(backfill_student_profiles, noop_reverse),
    ]
