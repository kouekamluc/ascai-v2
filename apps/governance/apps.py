"""
App configuration for governance app.
"""
from django.apps import AppConfig


class GovernanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.governance'
    verbose_name = 'ASCAI Governance'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.governance.signals  # noqa

