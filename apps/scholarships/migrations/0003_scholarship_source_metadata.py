from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("scholarships", "0002_scholarship_level_scholarship_region"),
    ]

    operations = [
        migrations.AddField(
            model_name="scholarship",
            name="source_excerpt",
            field=models.TextField(blank=True, help_text="Short imported summary from the source page.", verbose_name="Source Excerpt"),
        ),
        migrations.AddField(
            model_name="scholarship",
            name="source_hash",
            field=models.CharField(blank=True, help_text="Internal fingerprint used to detect source changes.", max_length=64, verbose_name="Source Hash"),
        ),
        migrations.AddField(
            model_name="scholarship",
            name="source_imported_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Source Imported At"),
        ),
        migrations.AddField(
            model_name="scholarship",
            name="source_last_seen_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Source Last Seen At"),
        ),
        migrations.AddField(
            model_name="scholarship",
            name="source_name",
            field=models.CharField(blank=True, help_text="Official source this scholarship was imported from.", max_length=200, verbose_name="Source Name"),
        ),
        migrations.AddField(
            model_name="scholarship",
            name="source_url",
            field=models.URLField(blank=True, help_text="Official page where students should verify the latest information.", verbose_name="Source URL"),
        ),
    ]
