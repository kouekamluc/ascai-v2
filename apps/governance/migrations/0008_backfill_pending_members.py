from django.db import migrations
from django.db.models import Q


def create_pending_members_for_verified_accounts(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Member = apps.get_model("governance", "Member")

    existing_user_ids = set(Member.objects.values_list("user_id", flat=True))
    users = (
        User.objects.filter(is_superuser=False, is_staff=False, role__in=["student", "mentor"])
        .filter(Q(email_verified=True) | Q(is_approved=True))
        .exclude(id__in=existing_user_ids)
    )

    members = []
    for user in users:
        members.append(
            Member(
                user_id=user.id,
                member_type="student" if user.role == "student" else "active",
                is_active_member=False,
            )
        )

    Member.objects.bulk_create(members, ignore_conflicts=True)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_user_language_preference"),
        ("governance", "0007_extraordinaryassemblyrequest"),
    ]

    operations = [
        migrations.RunPython(create_pending_members_for_verified_accounts, noop_reverse),
    ]
