"""
Custom admin site configuration for ASCAI Lazio.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.sites import UnfoldAdminSite

# Create custom admin site instance using Unfold
admin_site = UnfoldAdminSite()

# Configure the admin site
admin_site.site_header = _('ASCAI Lazio Administration')
admin_site.site_title = _('ASCAI Lazio Admin')
admin_site.index_title = _('Welcome to ASCAI Lazio Administration')

# Replace the default admin.site with our custom Unfold admin site
# This ensures all @admin.register decorators work with Unfold
admin.site = admin_site

# Make admin_site available for direct imports if needed
__all__ = ['admin_site']



















