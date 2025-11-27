"""
Production settings for ASCAI Lazio project.
"""
from .base import *
from decouple import config
from django.core.exceptions import ImproperlyConfigured

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

DEBUG = config('DEBUG', default=False, cast=bool)

# Validate required settings in production
if DEBUG:
    raise ImproperlyConfigured(
        "DEBUG must be False in production. Set DEBUG=False in your environment variables."
    )

# Validate SECRET_KEY
if SECRET_KEY == 'django-insecure-change-me-in-production':
    raise ImproperlyConfigured(
        "SECRET_KEY must be set in production. Generate one and set it in your environment variables."
    )

# Get ALLOWED_HOSTS from environment, with fallback to Railway's public domain
allowed_hosts_str = config('ALLOWED_HOSTS', default='')
if not allowed_hosts_str:
    # Try Railway's public domain as fallback
    railway_domain = config('RAILWAY_PUBLIC_DOMAIN', default=None)
    if railway_domain:
        allowed_hosts_str = railway_domain

ALLOWED_HOSTS = [s.strip() for s in allowed_hosts_str.split(',')] if allowed_hosts_str else []

# Automatically add Railway's internal domains for healthchecks
# Django supports leading dot notation for subdomain matching: .railway.app matches *.railway.app
railway_internal_domains = [
    'healthcheck.railway.app',
    '.railway.app',  # Matches all Railway subdomains (e.g., *.railway.app, *.up.railway.app)
    '.up.railway.app',  # Explicitly match *.up.railway.app subdomains
]

# Add Railway internal domains if not already present
for domain in railway_internal_domains:
    if domain not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(domain)

# Log ALLOWED_HOSTS for debugging (without exposing sensitive info)
import logging
logger = logging.getLogger(__name__)
logger.info(f"ALLOWED_HOSTS configured: {len(ALLOWED_HOSTS)} host(s)")

if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS must be set in production. Set it as a comma-separated list of domains, "
        "or ensure RAILWAY_PUBLIC_DOMAIN is available."
    )

# Database
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL and dj_database_url:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Validate individual database settings
    db_name = config('DB_NAME', default=None)
    db_user = config('DB_USER', default=None)
    db_password = config('DB_PASSWORD', default=None)
    db_host = config('DB_HOST', default=None)
    
    if not all([db_name, db_user, db_password, db_host]):
        raise ImproperlyConfigured(
            "Database configuration is incomplete. Either set DATABASE_URL or provide "
            "DB_NAME, DB_USER, DB_PASSWORD, and DB_HOST environment variables."
        )
    
    DATABASES = {
        'default': {
            'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': config('DB_PORT', default='5432'),
            'CONN_MAX_AGE': 600,
        }
    }

# Security settings
# Railway uses a proxy, so we need to trust the X-Forwarded-Proto header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default=True, cast=bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default=True, cast=bool)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',')] if v else []
)

# Validate CSRF_TRUSTED_ORIGINS matches ALLOWED_HOSTS
if not CSRF_TRUSTED_ORIGINS:
    # Auto-populate from ALLOWED_HOSTS if not set
    CSRF_TRUSTED_ORIGINS = [f'https://{host}' for host in ALLOWED_HOSTS]

# Static files (use S3 or WhiteNoise)
if not USE_S3:
    # Use CompressedStaticFilesStorage instead of CompressedManifestStaticFilesStorage
    # This doesn't require a manifest file and is more reliable
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    
    # WhiteNoise configuration
    # In production, serve from STATIC_ROOT only (files collected via collectstatic)
    # This is more efficient and reliable than using finders
    # WhiteNoise automatically uses STATIC_ROOT, so no need to set WHITENOISE_ROOT
    WHITENOISE_USE_FINDERS = False  # Serve from STATIC_ROOT only - requires collectstatic
    WHITENOISE_AUTOREFRESH = False  # Disable auto-refresh in production for performance
    
    logger.info("Using WhiteNoise for static file storage (S3 disabled)")
else:
    # Validate AWS S3 configuration in production
    # Note: Basic validation already happens in base.py, but we add logging here
    try:
        # Check if AWS variables are defined (they should be if USE_S3 is True)
        if not all([hasattr(globals(), 'AWS_ACCESS_KEY_ID'), 
                   hasattr(globals(), 'AWS_SECRET_ACCESS_KEY'),
                   hasattr(globals(), 'AWS_STORAGE_BUCKET_NAME')]):
            logger.warning(
                "AWS S3 is enabled but AWS configuration variables are not properly set. "
                "This should not happen if base.py validation worked correctly."
            )
        else:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError
            
            # Test AWS credentials by attempting to create a client
            # This will fail gracefully if credentials are invalid
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_S3_REGION_NAME
            )
            
            # Try to head the bucket to verify access
            try:
                s3_client.head_bucket(Bucket=AWS_STORAGE_BUCKET_NAME)
                logger.info(
                    f"AWS S3 configured successfully: bucket '{AWS_STORAGE_BUCKET_NAME}' "
                    f"in region '{AWS_S3_REGION_NAME}'"
                )
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                if error_code == '404':
                    logger.error(
                        f"AWS S3 bucket '{AWS_STORAGE_BUCKET_NAME}' not found. "
                        "Please verify the bucket name and region."
                    )
                elif error_code == '403':
                    logger.error(
                        f"AWS S3 access denied for bucket '{AWS_STORAGE_BUCKET_NAME}'. "
                        "Please verify IAM permissions."
                    )
                else:
                    logger.warning(
                        f"AWS S3 bucket verification failed: {error_code}. "
                        "S3 may still work, but please verify configuration."
                    )
            except Exception as e:
                logger.warning(
                    f"AWS S3 bucket verification failed: {str(e)}. "
                    "S3 may still work, but please verify configuration."
                )
            
    except NoCredentialsError:
        logger.error(
            "AWS credentials not found. S3 is enabled but credentials are invalid. "
            "Falling back to local storage."
        )
    except ImportError:
        logger.warning(
            "boto3 not installed. S3 functionality may not work properly. "
            "Install with: pip install boto3"
        )
    except Exception as e:
        logger.warning(
            f"AWS S3 configuration check failed: {str(e)}. "
            "S3 may still work, but please verify configuration."
        )

# Email Configuration
# Note: Email settings are inherited from base.py via 'from .base import *'
# They read from environment variables. We explicitly show them here for clarity.
# The validation below ensures they are set correctly for production.
#
# These settings come from base.py but are shown here for reference:
# EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
# EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
# EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
# DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='ASCAI Lazio <noreply@ascailazio.org>')
# CONTACT_EMAIL = config('CONTACT_EMAIL', default='info@ascailazio.org')
#
# Required environment variables for production:
# - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend (MUST be set, not console!)
# - EMAIL_HOST=smtp.gmail.com (or your SMTP provider)
# - EMAIL_PORT=587
# - EMAIL_USE_TLS=True
# - EMAIL_HOST_USER=your-email@example.com
# - EMAIL_HOST_PASSWORD=your-password-or-app-password
# - DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
# - CONTACT_EMAIL=info@ascailazio.org

# Email Configuration Validation and Enforcement
# Ensure email backend is properly configured for production
if EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    logger.error(
        "ERROR: Console email backend is configured in production! "
        "Emails will not be sent. Please set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend "
        "and configure SMTP settings in your environment variables."
    )
elif EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        logger.error(
            "ERROR: SMTP email backend is configured but EMAIL_HOST_USER or "
            "EMAIL_HOST_PASSWORD is missing. Emails will not be sent. "
            "Please configure email settings in your environment variables."
        )
    else:
        logger.info(
            f"Email backend configured: {EMAIL_BACKEND} "
            f"(Host: {EMAIL_HOST}, Port: {EMAIL_PORT}, User: {EMAIL_HOST_USER})"
        )
        # Note: Email connection test removed from startup to prevent blocking
        # Email connection will be tested when actually sending emails
        # If emails fail, check logs for detailed error messages
else:
    logger.warning(
        f"Email backend is set to {EMAIL_BACKEND}. "
        "Make sure this is the correct backend for production."
    )

# Note: Site domain should be updated after deployment using:
# python manage.py update_site_domain --domain your-app-name.up.railway.app
# This ensures email confirmation URLs use the correct domain.
# The adapter will use request.build_absolute_uri() which works with ALLOWED_HOSTS.

# Logging - Enhanced for production debugging
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
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps.accounts.adapters': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

