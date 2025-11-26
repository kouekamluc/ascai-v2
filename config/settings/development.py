"""
Development settings for ASCAI Lazio project.
"""
from .base import *
from decouple import config, Config, RepositoryEnv
import os

# Try to load from .env.example as fallback if .env doesn't exist
def get_config():
    """Get config with fallback to .env.example"""
    env_file = '.env'
    env_example = '.env.example'
    
    # Try .env first
    if os.path.exists(env_file):
        return Config(RepositoryEnv(env_file))
    # Fallback to .env.example
    elif os.path.exists(env_example):
        return Config(RepositoryEnv(env_example))
    # Default config (reads from environment variables)
    else:
        return config

# Use the config function
_config = get_config()

DEBUG = _config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = _config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',')])

# Database
# Support DATABASE_URL (for Railway, Heroku, etc.) or individual settings
try:
    import dj_database_url
    DATABASE_URL = _config('DATABASE_URL', default=None)
    if DATABASE_URL:
        DATABASES = {
            'default': dj_database_url.parse(DATABASE_URL)
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': _config('DB_ENGINE', default='django.db.backends.postgresql'),
                'NAME': _config('DB_NAME', default='ASCAI-V2'),
                'USER': _config('DB_USER', default='postgres'),
                'PASSWORD': _config('DB_PASSWORD', default=''),
                'HOST': _config('DB_HOST', default='localhost'),
                'PORT': _config('DB_PORT', default='5432'),
            }
        }
except ImportError:
    # Fallback if dj_database_url is not installed
    DATABASES = {
        'default': {
            'ENGINE': _config('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': _config('DB_NAME', default='ASCAI-V2'),
            'USER': _config('DB_USER', default='postgres'),
            'PASSWORD': _config('DB_PASSWORD', default=''),
            'HOST': _config('DB_HOST', default='localhost'),
            'PORT': _config('DB_PORT', default='5432'),
        }
    }

# Static files (using local storage in development)
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files (using local storage in development)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Security settings (relaxed for development)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False

CSRF_TRUSTED_ORIGINS = _config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:8000,http://127.0.0.1:8000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# Email backend (console for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar (optional)
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1']
    except ImportError:
        pass  # debug_toolbar not installed, skip it

