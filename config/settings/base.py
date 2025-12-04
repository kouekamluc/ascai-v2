"""
Base settings for ASCAI Lazio project.
"""
import os
from pathlib import Path
from decouple import config
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# Application definition
INSTALLED_APPS = [
    # Django Unfold must be before django.contrib.admin
    'unfold',  # Modern Django admin theme
    'unfold.contrib.filters',  # Enhanced filters for Unfold
    'unfold.contrib.forms',  # WYSIWYG editor support (Trix editor)
    
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
    'allauth.socialaccount.providers.google',
    
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
    'apps.governance',
]

# Conditionally add anymail if available (for email service integration)
try:
    import anymail
    INSTALLED_APPS.append('anymail')
except ImportError:
    pass  # anymail not installed locally, but will be available in production

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
    ('it', 'Italiano'),
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
    # Only set AWS_S3_ENDPOINT_URL if explicitly provided (for S3-compatible services like DigitalOcean Spaces)
    # If empty, don't set it at all - django-storages will use default AWS S3 endpoints
    # Setting to empty string causes "ValueError: Invalid endpoint:" error
    # Setting to None might also cause issues, so we only set it if a value is provided
    aws_endpoint_raw = config('AWS_S3_ENDPOINT_URL', default='').strip()
    if aws_endpoint_raw:
        AWS_S3_ENDPOINT_URL = aws_endpoint_raw
    # If empty, AWS_S3_ENDPOINT_URL is not set - django-storages will use defaults automatically
    AWS_S3_SIGNATURE_VERSION = config('AWS_S3_SIGNATURE_VERSION', default='s3v4')
    AWS_S3_ADDRESSING_STYLE = config('AWS_S3_ADDRESSING_STYLE', default='virtual')
    
    # Validate S3 settings BEFORE using them to build domain
    # This prevents errors when building default_domain with empty bucket name
    # In Railway, gracefully fall back to local storage if credentials are missing
    aws_key_status = 'SET' if AWS_ACCESS_KEY_ID else 'MISSING'
    aws_secret_status = 'SET' if AWS_SECRET_ACCESS_KEY else 'MISSING'
    aws_bucket_status = f'SET ({AWS_STORAGE_BUCKET_NAME})' if AWS_STORAGE_BUCKET_NAME else 'MISSING'
    
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
        logger.error(error_msg)
        # Disable S3 and fall back to local storage
        USE_S3 = False
        # Clear AWS variables to prevent confusion
        AWS_ACCESS_KEY_ID = None
        AWS_SECRET_ACCESS_KEY = None
        AWS_STORAGE_BUCKET_NAME = None
        logger.warning("USE_S3 set to False due to missing credentials. Using local storage.")
    else:
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
        
        # AWS_S3_ENDPOINT_URL is only set above if explicitly provided
        # If not set, django-storages will use default AWS S3 endpoints automatically
        # This prevents "ValueError: Invalid endpoint:" errors from empty strings
        # Only set AWS_S3_ENDPOINT_URL in environment if using S3-compatible services (DigitalOcean Spaces, MinIO, etc.)
        
        # Static files storage - set immediately when S3 is enabled
        STATICFILES_STORAGE = 'config.storage_backends.StaticStorage'
        
        # Media files storage - set immediately when S3 is enabled
        DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'
        
        # Django 4.2+ STORAGES setting - set immediately when S3 is enabled
        # This ensures S3 is used from the start, no "fix" logic needed
        STORAGES = {
            "staticfiles": {
                "BACKEND": "config.storage_backends.StaticStorage",
            },
            "default": {
                "BACKEND": "config.storage_backends.MediaStorage",
            },
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
# Priority: Brevo > SendGrid > SMTP > Console

# Brevo (formerly Sendinblue) Configuration (RECOMMENDED)
# Brevo API is reliable and bypasses Railway SMTP blocking
BREVO_API_KEY = config('BREVO_API_KEY', default='')

# SendGrid API Key (fallback option)
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')

# Determine which email backend to use
if BREVO_API_KEY:
    # Use Brevo via django-anymail
    EMAIL_BACKEND = 'anymail.backends.brevo.EmailBackend'
    ANYMAIL = {
        "BREVO_API_KEY": BREVO_API_KEY,
        "BREVO_SEND_DEFAULTS": {
            # Optional: set default tags, metadata, etc.
        },
        "BREVO_API_URL": "https://api.brevo.com/v3",
    }
    logger.info("✅ Email backend: Brevo (via django-anymail)")
elif SENDGRID_API_KEY:
    # Fallback to SendGrid if Brevo not configured
    EMAIL_BACKEND = 'apps.core.email_backends.SendGridBackend'
    logger.info("✅ Email backend: SendGrid API")
else:
    # Fallback to SMTP or console
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
    logger.info(f"⚠️  Email backend: {EMAIL_BACKEND} (Brevo/SendGrid not configured)")

# SMTP Configuration (fallback if API backends not used)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)  # 10 second timeout to prevent blocking

# Email addresses
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

# Social Account Settings (Google OAuth)
# NOTE: Google OAuth is configured via SocialApp database entries (created by setup_google_oauth command)
# Do NOT configure 'APP' here to avoid MultipleObjectsReturned errors
# The setup_google_oauth management command creates the SocialApp entry from environment variables
SOCIALACCOUNT_ADAPTER = 'apps.accounts.adapters.CustomSocialAccountAdapter'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
        'VERIFIED_EMAIL': True,  # CRITICAL: Tell allauth that Google emails are already verified
        # 'APP' configuration removed - using database SocialApp entries instead
        # This prevents MultipleObjectsReturned errors when both are configured
    }
}
# Auto-approve social accounts (users still need admin approval via is_approved field)
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # Google already verifies emails
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_STORE_TOKENS = False  # Don't store OAuth tokens unless needed
# Auto-connect social accounts to existing users with matching verified email
# This prevents "account already exists" email errors and improves UX
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
# Allow social login via GET request (prevents redirect loops)
# This is safe because the actual OAuth flow still requires user consent
SOCIALACCOUNT_LOGIN_ON_GET = True

# Session Configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# HTMX Configuration
HTMX_ENABLED = True

# File Upload Configuration
# Set reasonable limits for file uploads to prevent abuse
# These limits apply to all file uploads (images, documents, etc.)
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB - files larger than this will be written to disk
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB - form data size limit
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000  # Maximum number of form fields

# Maximum file size for uploads (50 MB)
# This is enforced at the application level, not Django level
# Individual apps can set stricter limits if needed
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

# Allowed file extensions for uploads (security measure)
# This is a general list - individual apps may have more specific requirements
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.rtf', '.odt']
ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.webm', '.ogg', '.mov']
ALLOWED_FILE_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS + ALLOWED_DOCUMENT_EXTENSIONS + ALLOWED_VIDEO_EXTENSIONS

# CKEditor Upload Settings
# CKEditor uploads will use the same S3 storage as other media files
# The upload path 'uploads/' will be under 'media/uploads/' in S3
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_ALLOW_NONIMAGE_FILES = True  # Allow non-image files in CKEditor

# CKEditor Configuration with upload support
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        # Upload settings - CKEditor will use the configured storage backend (S3)
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': '/ckeditor/browse/',
        # Allow all file types in uploads
        'allowedContent': True,
    },
}

# Django Unfold Configuration
# Professional Association Management Portal theme
UNFOLD = {
    "SITE_TITLE": _("Association Management Portal"),
    "SITE_HEADER": _("ASCAI Lazio Administration"),
    "SITE_URL": "/",
    "SITE_SYMBOL": "admin_panel_settings",  # Material Icons symbol
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "ENVIRONMENT": "ASCAI Lazio",  # Environment badge
    "DASHBOARD_CALLBACK": "config.admin.dashboard_callback",  # Dynamic dashboard
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Content Management"),
                "icon": "article",
                "items": [
                    {
                        "title": _("News & Announcements"),
                        "icon": "newspaper",
                        "link": "admin:diaspora_news_changelist",
                    },
                    {
                        "title": _("Events"),
                        "icon": "event",
                        "link": "admin:diaspora_event_changelist",
                    },
                    {
                        "title": _("Success Stories"),
                        "icon": "star",
                        "link": "admin:diaspora_successstory_changelist",
                    },
                    {
                        "title": _("Life in Italy"),
                        "icon": "info",
                        "link": "admin:diaspora_lifeinitaly_changelist",
                    },
                    {
                        "title": _("Forum Posts"),
                        "icon": "forum",
                        "link": "admin:community_forumpost_changelist",
                    },
                ],
            },
            {
                "title": _("User Management"),
                "icon": "people",
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": "admin:accounts_user_changelist",
                    },
                    {
                        "title": _("Mentors"),
                        "icon": "school",
                        "link": "admin:mentorship_mentorprofile_changelist",
                    },
                    {
                        "title": _("Testimonials"),
                        "icon": "rate_review",
                        "link": "admin:diaspora_testimonial_changelist",
                    },
                ],
            },
            {
                "title": _("Resources"),
                "icon": "folder",
                "items": [
                    {
                        "title": _("Universities"),
                        "icon": "account_balance",
                        "link": "admin:universities_university_changelist",
                    },
                    {
                        "title": _("Scholarships"),
                        "icon": "card_giftcard",
                        "link": "admin:scholarships_scholarship_changelist",
                    },
                    {
                        "title": _("Documents"),
                        "icon": "description",
                        "link": "admin:downloads_document_changelist",
                    },
                    {
                        "title": _("Gallery"),
                        "icon": "photo_library",
                        "link": "admin:gallery_photo_changelist",
                    },
                ],
            },
            {
                "title": _("Settings"),
                "icon": "settings",
                "items": [
                    {
                        "title": _("Governance"),
                        "icon": "gavel",
                        "link": "admin:governance_member_changelist",
                    },
                    {
                        "title": _("Contact Messages"),
                        "icon": "mail",
                        "link": "admin:contact_contactmessage_changelist",
                    },
                ],
            },
        ],
    },
    "STYLES": [
        {
            "source": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        },
    ],
    "SCRIPTS": [],
    "COLORS": {
        "primary": {
            "50": "250 250 252",
            "100": "244 244 247",
            "200": "228 228 234",
            "300": "200 200 210",
            "400": "156 156 171",
            "500": "30 58 138",  # Navy Blue primary
            "600": "30 64 175",
            "700": "29 78 216",
            "800": "30 58 138",
            "900": "30 41 59",
            "950": "15 23 42",
        },
    },
    "EXTENSIONS": {
        "modeltranslation": {
            "flags": {
                "en": "🇬🇧",
                "fr": "🇫🇷",
                "it": "🇮🇹",
            },
        },
    },
}

