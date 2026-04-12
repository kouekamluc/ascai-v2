from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("governance", "0005_alter_executiveposition_position"),
    ]

    operations = [
        migrations.AlterField(
            model_name="membershipstatus",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", _("Pending")),
                    ("active", _("Active")),
                    ("inactive", _("Inactive")),
                    ("suspended", _("Suspended")),
                    ("expelled", _("Expelled")),
                ],
                default="active",
                max_length=20,
                verbose_name="Status",
            ),
        ),
    ]
