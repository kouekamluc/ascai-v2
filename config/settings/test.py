"""
Test settings for ASCAI Lazio project.
"""
import importlib.util

from .base import *

DEBUG = False
ROOT_URLCONF = 'config.test_urls'


def _module_available(app_name):
    """Return True when the app's top-level module is installed."""
    module_name = app_name.split('.')[0]
    return importlib.util.find_spec(module_name) is not None


INSTALLED_APPS = [
    app for app in INSTALLED_APPS
    if app != 'django.contrib.admin' and not app.startswith('unfold') and (
        app.startswith('apps.')
        or app.startswith('django.')
        or _module_available(app)
    )
]

# Use SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Password hashers for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Disable S3 for tests (use local storage)
USE_S3 = False

# Static files settings for tests
STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
}

# Test-specific middleware (can remove some for speed)
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.middleware.UserPreferredLocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

if _module_available('allauth'):
    MIDDLEWARE.insert(5, 'allauth.account.middleware.AccountMiddleware')





















