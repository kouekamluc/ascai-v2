from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('governance', '0006_alter_membershipstatus_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraordinaryAssemblyRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField(blank=True, help_text='Optional reason or proposed agenda for the extraordinary assembly.', verbose_name='Reason')),
                ('status', models.CharField(choices=[('active', 'Active'), ('withdrawn', 'Withdrawn'), ('converted', 'Converted to Assembly')], default='active', max_length=20, verbose_name='Status')),
                ('requested_at', models.DateTimeField(auto_now_add=True, verbose_name='Requested At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extraordinary_assembly_requests', to='governance.member', verbose_name='Member')),
            ],
            options={
                'verbose_name': 'Extraordinary Assembly Request',
                'verbose_name_plural': 'Extraordinary Assembly Requests',
                'ordering': ['-requested_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='extraordinaryassemblyrequest',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'active')), fields=('member',), name='unique_active_extraordinary_request_per_member'),
        ),
    ]
