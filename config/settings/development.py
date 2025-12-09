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

# Override SECRET_KEY to use _config (which reads from .env.example as fallback)
# This ensures SECRET_KEY can be read from .env.example if .env doesn't exist
SECRET_KEY = _config('SECRET_KEY', default='django-insecure-change-me-in-production')

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

# Disable WhiteNoise middleware in development
# Django's staticfiles app handles static file serving automatically in DEBUG mode
# WhiteNoise should only be used in production
if 'whitenoise.middleware.WhiteNoiseMiddleware' in MIDDLEWARE:
    MIDDLEWARE = [m for m in MIDDLEWARE if m != 'whitenoise.middleware.WhiteNoiseMiddleware']

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

# Email Configuration
# Note: Base email settings are inherited from base.py
# Default to console backend for development, but allow override via .env
# To send real emails, set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend in .env
EMAIL_BACKEND = _config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Override email settings (inherited from base.py, but redefined here for clarity)
# These will be used if you set EMAIL_BACKEND to SMTP in .env for testing
EMAIL_HOST = _config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = _config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = _config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = _config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = _config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = _config('DEFAULT_FROM_EMAIL', default='ASCAI Associazione <info@ascai.org>')
SERVER_EMAIL = _config('SERVER_EMAIL', default='info@ascai.org')
CONTACT_EMAIL = _config('CONTACT_EMAIL', default='info@ascai.org')

# Debug toolbar (optional - install with: pip install django-debug-toolbar)
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1', 'localhost']
    except ImportError:
        pass  # debug_toolbar not installed, skip it

# Logging configuration for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',  # Set to 'DEBUG' to see SQL queries
            'propagate': False,
        },
    },
}

