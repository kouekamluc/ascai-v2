from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Collaborator",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Name")),
                ("category", models.CharField(choices=[("collaborator", "Collaborator"), ("partner", "Partner"), ("supporter", "Supporter"), ("institution", "Institution")], default="collaborator", max_length=20, verbose_name="Category")),
                ("logo", models.ImageField(blank=True, help_text="Recommended: transparent PNG or SVG-friendly image.", null=True, upload_to="collaborators/", verbose_name="Logo")),
                ("website_url", models.URLField(blank=True, verbose_name="Website URL")),
                ("description", models.TextField(blank=True, verbose_name="Short Description")),
                ("display_order", models.PositiveIntegerField(default=0, verbose_name="Display Order")),
                ("is_featured", models.BooleanField(default=True, verbose_name="Featured on Site")),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Collaborator",
                "verbose_name_plural": "Collaborators",
                "ordering": ["display_order", "name"],
            },
        ),
    ]
