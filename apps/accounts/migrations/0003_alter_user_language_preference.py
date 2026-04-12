from django.db import migrations, models
from django.utils.translation import gettext_lazy as _


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_arrival_year_user_city_in_lazio_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="language_preference",
            field=models.CharField(
                choices=[
                    ("en", _("English")),
                    ("fr", _("French")),
                    ("it", _("Italian")),
                ],
                default="en",
                max_length=2,
                verbose_name="Language Preference",
            ),
        ),
    ]
