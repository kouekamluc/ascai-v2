"""
Custom admin site configuration for ASCAI Lazio.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

admin.site.site_header = _('ASCAI Lazio Administration')
admin.site.site_title = _('ASCAI Lazio Admin')
admin.site.index_title = _('Welcome to ASCAI Lazio Administration')










