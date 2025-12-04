"""
Custom admin site configuration for ASCAI Lazio.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# Configure the default admin site (Unfold will automatically style it)
admin.site.site_header = _('ASCAI Lazio Administration')
admin.site.site_title = _('ASCAI Lazio Admin')
admin.site.index_title = _('Welcome to ASCAI Lazio Administration')

# Make admin_site available for direct imports (alias to admin.site for compatibility)
admin_site = admin.site



















