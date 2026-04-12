from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AssociationSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("site_name", models.CharField(default="ASCAI Lazio", max_length=200, verbose_name="Site Name")),
                ("tagline", models.CharField(blank=True, max_length=255, verbose_name="Tagline")),
                ("public_email", models.EmailField(blank=True, max_length=254, verbose_name="Public Email")),
                ("facebook_url", models.URLField(blank=True, verbose_name="Facebook URL")),
                ("instagram_url", models.URLField(blank=True, verbose_name="Instagram URL")),
                ("linkedin_url", models.URLField(blank=True, verbose_name="LinkedIn URL")),
                ("tiktok_url", models.URLField(blank=True, verbose_name="TikTok URL")),
                ("youtube_url", models.URLField(blank=True, verbose_name="YouTube URL")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Association Settings",
                "verbose_name_plural": "Association Settings",
            },
        ),
    ]
