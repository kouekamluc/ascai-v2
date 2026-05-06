from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0003_servicepartner_communityservice"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConversionEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("sponsor_interest", "Sponsor Interest"),
                            ("orientation_request", "Orientation Request"),
                            ("one_pager_download", "Sponsor One-Pager Download"),
                        ],
                        max_length=40,
                        verbose_name="Event Type",
                    ),
                ),
                ("source_path", models.CharField(blank=True, max_length=255, verbose_name="Source Path")),
                ("session_key", models.CharField(blank=True, max_length=80, verbose_name="Session Key")),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True, verbose_name="IP Address")),
                ("user_agent", models.TextField(blank=True, verbose_name="User Agent")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="conversion_events",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Conversion Event",
                "verbose_name_plural": "Conversion Events",
                "ordering": ["-created_at"],
            },
        ),
    ]
