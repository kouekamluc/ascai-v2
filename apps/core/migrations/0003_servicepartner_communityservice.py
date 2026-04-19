from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_associationsettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="ServicePartner",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Partner Name")),
                ("category", models.CharField(choices=[("money_transfer", "Money Transfer"), ("documents_translation", "Documents and Translation"), ("legal_admin", "Legal and Administrative Help"), ("housing_settlement", "Housing and Settlement"), ("travel_logistics", "Travel and Logistics"), ("business_services", "Business Services"), ("health_wellbeing", "Health and Wellbeing"), ("other", "Other")], default="other", max_length=30, verbose_name="Category")),
                ("short_description", models.TextField(verbose_name="Short Description")),
                ("contact_name", models.CharField(blank=True, max_length=200, verbose_name="Contact Name")),
                ("contact_email", models.EmailField(blank=True, max_length=254, verbose_name="Contact Email")),
                ("phone_number", models.CharField(blank=True, max_length=50, verbose_name="Phone Number")),
                ("whatsapp_number", models.CharField(blank=True, max_length=50, verbose_name="WhatsApp Number")),
                ("website_url", models.URLField(blank=True, verbose_name="Website URL")),
                ("cities_served", models.CharField(blank=True, help_text="Examples: Rome, Latina, online", max_length=255, verbose_name="Cities Served")),
                ("verification_status", models.CharField(choices=[("pending", "Pending"), ("verified", "Verified"), ("needs_review", "Needs Review"), ("suspended", "Suspended")], default="pending", max_length=20, verbose_name="Verification Status")),
                ("annual_listing_fee", models.DecimalField(decimal_places=2, default=Decimal("20.00"), help_text="Annual fee charged to service providers for verified visibility.", max_digits=6, verbose_name="Annual Listing Fee")),
                ("is_featured", models.BooleanField(default=True, verbose_name="Featured")),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
                ("display_order", models.PositiveIntegerField(default=0, verbose_name="Display Order")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Service Partner",
                "verbose_name_plural": "Service Partners",
                "ordering": ["display_order", "name"],
            },
        ),
        migrations.CreateModel(
            name="CommunityService",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="Title")),
                ("category", models.CharField(choices=[("consular_support", "Consular Support"), ("documentation", "Documentation"), ("arrival_support", "Arrival and Settlement"), ("money_transfer", "Money Transfer"), ("career_business", "Career and Business"), ("family_life", "Family and Community Life"), ("other", "Other")], default="other", max_length=30, verbose_name="Category")),
                ("audience", models.CharField(blank=True, max_length=200, verbose_name="Audience")),
                ("summary", models.TextField(verbose_name="Summary")),
                ("association_benefit", models.TextField(blank=True, help_text="How this service can strengthen ASCAI's value or revenue.", verbose_name="Association Benefit")),
                ("access_level", models.CharField(choices=[("public", "Public"), ("member", "Members"), ("member_referral", "Members with Verified Referrals")], default="member", max_length=20, verbose_name="Access Level")),
                ("delivery_mode", models.CharField(choices=[("resource_pack", "Resource Pack"), ("workshop", "Workshop"), ("clinic", "Clinic"), ("partner_referral", "Partner Referral"), ("appointment_prep", "Appointment Preparation")], default="resource_pack", max_length=20, verbose_name="Delivery Mode")),
                ("revenue_stream", models.CharField(choices=[("included_in_dues", "Included in Dues"), ("partner_listing_fee", "Partner Listing Fee"), ("paid_clinic", "Paid Clinic"), ("event_revenue", "Event Revenue"), ("sponsorship", "Sponsorship")], default="included_in_dues", max_length=25, verbose_name="Revenue Stream")),
                ("is_featured", models.BooleanField(default=True, verbose_name="Featured")),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
                ("display_order", models.PositiveIntegerField(default=0, verbose_name="Display Order")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("partner", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="services", to="core.servicepartner", verbose_name="Linked Partner")),
            ],
            options={
                "verbose_name": "Community Service",
                "verbose_name_plural": "Community Services",
                "ordering": ["display_order", "title"],
            },
        ),
    ]
