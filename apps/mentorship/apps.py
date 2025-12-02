from django.apps import AppConfig


class MentorshipConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mentorship'
    verbose_name = 'Mentorship'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.mentorship.signals  # noqa

















