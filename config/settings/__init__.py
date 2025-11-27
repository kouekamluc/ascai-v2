from django.core.exceptions import ImproperlyConfigured
import os
from decouple import config

# Determine which settings module to use based on environment
ENVIRONMENT = os.environ.get('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'test':
    from .test import *
else:
    from .development import *












