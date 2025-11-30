"""
Base settings for ASCAI Lazio project.
"""
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Third party apps
    'django_extensions',
    'django_filters',
    'storages',
    'ckeditor',
    'ckeditor_uploader',
    
    # Django Allauth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Local apps
    'apps.accounts',
    'apps.core',
    'apps.students',
    'apps.diaspora',
    'apps.community',
    'apps.mentorship',
    'apps.universities',
    'apps.scholarships',
    'apps.gallery',
    'apps.downloads',
    'apps.contact',
    'apps.dashboard',
]

MIDDLEWARE = [
    'config.middleware.CustomSecurityMiddleware',  # Custom SecurityMiddleware with healthcheck exemption
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'apps.core.context_processors.language_preference',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = config('DEFAULT_LANGUAGE', default='en')
TIME_ZONE = 'Europe/Rome'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Media files
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# AWS S3 Configuration
# Handle USE_S3 with robust boolean conversion
# Railway environment variables are strings, so we need to handle "True", "true", "1", etc.
use_s3_raw = config('USE_S3', default='False').strip().lower()
USE_S3 = use_s3_raw in ('true', '1', 'yes', 'on')

# Log the S3 configuration status for debugging
import logging
logger = logging.getLogger(__name__)
logger.info(f"USE_S3 environment variable: '{config('USE_S3', default='False')}' → parsed as: {USE_S3}")

if USE_S3:
    # Read AWS configuration from environment variables
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='').strip()
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='').strip()
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='').strip()
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1').strip()
    AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='').strip()
    AWS_S3_SIGNATURE_VERSION = config('AWS_S3_SIGNATURE_VERSION', default='s3v4')
    AWS_S3_ADDRESSING_STYLE = config('AWS_S3_ADDRESSING_STYLE', default='virtual')
    
    # Validate S3 settings BEFORE using them to build domain
    # This prevents errors when building default_domain with empty bucket name
    # In Railway, gracefully fall back to local storage if credentials are missing
    # Use both logger and print to ensure messages appear (logging may not be configured yet)
    aws_key_status = 'SET' if AWS_ACCESS_KEY_ID else 'MISSING'
    aws_secret_status = 'SET' if AWS_SECRET_ACCESS_KEY else 'MISSING'
    aws_bucket_status = f'SET ({AWS_STORAGE_BUCKET_NAME})' if AWS_STORAGE_BUCKET_NAME else 'MISSING'
    
    print("=" * 60)
    print("AWS S3 CONFIGURATION CHECK (base.py)")
    print(f"  AWS_ACCESS_KEY_ID: {aws_key_status}")
    print(f"  AWS_SECRET_ACCESS_KEY: {aws_secret_status}")
    print(f"  AWS_STORAGE_BUCKET_NAME: {aws_bucket_status}")
    print(f"  AWS_S3_REGION_NAME: {AWS_S3_REGION_NAME}")
    print("=" * 60)
    
    logger.info(f"AWS S3 configuration check:")
    logger.info(f"  AWS_ACCESS_KEY_ID: {aws_key_status}")
    logger.info(f"  AWS_SECRET_ACCESS_KEY: {aws_secret_status}")
    logger.info(f"  AWS_STORAGE_BUCKET_NAME: {aws_bucket_status}")
    logger.info(f"  AWS_S3_REGION_NAME: {AWS_S3_REGION_NAME}")
    
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
        error_msg = (
            "❌ AWS S3 is enabled (USE_S3=True) but AWS credentials are missing or incomplete.\n"
            "Falling back to local file storage. Files will be lost on container restart.\n"
            f"  - AWS_ACCESS_KEY_ID: {aws_key_status}\n"
            f"  - AWS_SECRET_ACCESS_KEY: {aws_secret_status}\n"
            f"  - AWS_STORAGE_BUCKET_NAME: {aws_bucket_status}\n"
            f"  - AWS_S3_REGION_NAME: {AWS_S3_REGION_NAME}\n"
            "Please set these environment variables in Railway Variables."
        )
        print(error_msg)
        logger.error(error_msg)
        # Disable S3 and fall back to local storage
        USE_S3 = False
        # Clear AWS variables to prevent confusion
        AWS_ACCESS_KEY_ID = None
        AWS_SECRET_ACCESS_KEY = None
        AWS_STORAGE_BUCKET_NAME = None
        print("⚠️  USE_S3 set to False due to missing credentials. Using local storage.")
        logger.warning("USE_S3 set to False due to missing credentials. Using local storage.")
    else:
        print("✅ AWS S3 credentials validated successfully - S3 will be used for static/media files")
        logger.info("✅ AWS S3 credentials validated successfully")
        
        # Build default domain only after validation
        # Ensure region name is not empty (fallback to us-east-1 if somehow empty)
        if not AWS_S3_REGION_NAME:
            AWS_S3_REGION_NAME = 'us-east-1'
        
        default_domain = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
        
        # Handle custom domain - if provided, use it; otherwise use default
        custom_domain = config('AWS_S3_CUSTOM_DOMAIN', default='').strip()
        if custom_domain:
            AWS_S3_CUSTOM_DOMAIN = custom_domain
        else:
            AWS_S3_CUSTOM_DOMAIN = default_domain
        
        # AWS S3 configuration
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400',
        }
        # Set ACL to None - let bucket policy handle public access
        # Setting to 'public-read' causes "Access Denied" when bucket blocks public access
        AWS_DEFAULT_ACL = None
        AWS_S3_FILE_OVERWRITE = False
        AWS_QUERYSTRING_AUTH = False
        
        # Only set endpoint URL if explicitly provided (for S3-compatible services)
        # If empty, django-storages will use default AWS S3 endpoints
        # Don't set it to None, just leave it as empty string if not provided
        if not AWS_S3_ENDPOINT_URL:
            # Use default AWS endpoints - don't set the variable
            # django-storages will handle this automatically
            pass
        
        # Static files storage
        STATICFILES_STORAGE = 'config.storage_backends.StaticStorage'
        
        # Media files storage
        DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'
        
        # Also set STORAGES for Django 4.2+ compatibility (if not already set)
        # This ensures S3 takes precedence over any WhiteNoise settings
        if 'STORAGES' not in globals() or not isinstance(globals().get('STORAGES'), dict):
            STORAGES = {}
        STORAGES["staticfiles"] = {
            "BACKEND": "config.storage_backends.StaticStorage",
        }
        STORAGES["default"] = {
            "BACKEND": "config.storage_backends.MediaStorage",
        }
        
        # Build URLs with proper protocol
        STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
        
        logger.info(f"✅ S3 configured: Static files → {STATIC_URL}")
        logger.info(f"✅ S3 configured: Media files → {MEDIA_URL}")
        logger.info(f"✅ S3 storage backends set: STATICFILES_STORAGE = {STATICFILES_STORAGE}")
else:
    logger.info("ℹ️  S3 is disabled (USE_S3=False or not set). Using local file storage.")

# Email Configuration
# SendGrid API Key (preferred - bypasses SMTP blocking)
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')

# Use SendGrid API backend if API key is set, otherwise use SMTP
if SENDGRID_API_KEY:
    EMAIL_BACKEND = 'apps.core.email_backends.SendGridBackend'
else:
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# SMTP Configuration (fallback if SendGrid API not used)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)  # 10 second timeout to prevent blocking
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='ASCAI Lazio <noreply@ascailazio.org>')
CONTACT_EMAIL = config('CONTACT_EMAIL', default='info@ascailazio.org')

# CKEditor Configuration
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}

# Login/Logout URLs (using allauth)
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'dashboard:home'
LOGOUT_REDIRECT_URL = 'core:home'

# Django Allauth Configuration
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    # Custom backend with approval check (must be first)
    'apps.accounts.backends.ApprovalRequiredBackend',
    # Django default backend
    'django.contrib.auth.backends.ModelBackend',
    # Allauth backend
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Allauth Account Settings
# New settings format (django-allauth >= 0.57.0)
ACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomAccountAdapter'
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_SIGNUP_REDIRECT_URL = 'account_email_verification_sent'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'dashboard:home'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'account_login'
ACCOUNT_PASSWORD_MIN_LENGTH = 8
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/5m',  # 5 attempts per 5 minutes
}

# Session Configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# HTMX Configuration
HTMX_ENABLED = True

