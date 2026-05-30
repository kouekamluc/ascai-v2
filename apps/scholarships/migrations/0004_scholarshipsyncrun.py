from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scholarships', '0003_scholarship_source_metadata'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScholarshipSyncRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('running', 'Running'), ('success', 'Success'), ('partial', 'Partial Success'), ('failed', 'Failed'), ('dry_run', 'Dry Run')], default='running', max_length=20, verbose_name='Status')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='Started At')),
                ('finished_at', models.DateTimeField(blank=True, null=True, verbose_name='Finished At')),
                ('created_count', models.PositiveIntegerField(default=0, verbose_name='Created Count')),
                ('updated_count', models.PositiveIntegerField(default=0, verbose_name='Updated Count')),
                ('skipped_count', models.PositiveIntegerField(default=0, verbose_name='Skipped Count')),
                ('source_count', models.PositiveIntegerField(default=0, verbose_name='Source Count')),
                ('error_log', models.TextField(blank=True, verbose_name='Error Log')),
                ('dry_run', models.BooleanField(default=False, verbose_name='Dry Run')),
            ],
            options={
                'verbose_name': 'Scholarship Sync Run',
                'verbose_name_plural': 'Scholarship Sync Runs',
                'ordering': ['-started_at'],
            },
        ),
    ]
