#!/usr/bin/env python
"""
Script to verify production setup before deployment.
Checks all required environment variables and configurations.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.conf import settings
from django.core.management import call_command


def check_environment_variables():
    """Check required environment variables."""
    print("=" * 60)
    print("Checking Environment Variables...")
    print("=" * 60)
    
    required_vars = {
        'SECRET_KEY': 'Django secret key',
        'DEBUG': 'Debug mode (should be False)',
        'ALLOWED_HOSTS': 'Allowed hosts',
        'DATABASE_URL': 'Database connection string (or DB_* variables)',
    }
    
    optional_vars = {
        'BREVO_API_KEY': 'Brevo email API key',
        'SENDGRID_API_KEY': 'SendGrid email API key',
        'AWS_ACCESS_KEY_ID': 'AWS S3 access key',
        'AWS_SECRET_ACCESS_KEY': 'AWS S3 secret key',
        'AWS_STORAGE_BUCKET_NAME': 'AWS S3 bucket name',
        'GOOGLE_CLIENT_ID': 'Google OAuth client ID',
        'GOOGLE_CLIENT_SECRET': 'Google OAuth client secret',
    }
    
    missing_required = []
    missing_optional = []
    
    for var, description in required_vars.items():
        value = getattr(settings, var, None) or os.environ.get(var)
        if not value:
            missing_required.append((var, description))
            print(f"✗ {var}: {description} - MISSING")
        else:
            if var == 'SECRET_KEY' and value == 'django-insecure-change-me-in-production':
                print(f"⚠ {var}: Using default value - CHANGE THIS!")
            elif var == 'DEBUG' and value == 'True':
                print(f"⚠ {var}: Should be False in production!")
            else:
                print(f"✓ {var}: Set")
    
    for var, description in optional_vars.items():
        value = getattr(settings, var, None) or os.environ.get(var)
        if not value:
            missing_optional.append((var, description))
            print(f"ℹ {var}: {description} - Not set (optional)")
        else:
            print(f"✓ {var}: Set")
    
    return len(missing_required) == 0, missing_required, missing_optional


def check_database():
    """Check database connection."""
    print("\n" + "=" * 60)
    print("Checking Database...")
    print("=" * 60)
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        return False


def check_email():
    """Check email configuration."""
    print("\n" + "=" * 60)
    print("Checking Email Configuration...")
    print("=" * 60)
    
    email_backend = getattr(settings, 'EMAIL_BACKEND', None)
    if not email_backend:
        print("✗ EMAIL_BACKEND not configured")
        return False
    
    print(f"✓ Email backend: {email_backend}")
    
    # Check if it's console backend (not recommended for production)
    if 'console' in email_backend.lower():
        print("⚠ Using console email backend - emails won't be sent!")
        return False
    
    # Check for API keys or SMTP settings
    has_brevo = bool(getattr(settings, 'BREVO_API_KEY', None))
    has_sendgrid = bool(getattr(settings, 'SENDGRID_API_KEY', None))
    has_smtp = bool(getattr(settings, 'EMAIL_HOST', None))
    
    if has_brevo:
        print("✓ Brevo API key configured")
    elif has_sendgrid:
        print("✓ SendGrid API key configured")
    elif has_smtp:
        print("✓ SMTP settings configured")
    else:
        print("⚠ No email credentials found")
    
    return True


def check_storage():
    """Check storage configuration."""
    print("\n" + "=" * 60)
    print("Checking Storage Configuration...")
    print("=" * 60)
    
    use_s3 = getattr(settings, 'USE_S3', False)
    
    if use_s3:
        print("✓ Using AWS S3 for storage")
        has_key = bool(getattr(settings, 'AWS_ACCESS_KEY_ID', None))
        has_secret = bool(getattr(settings, 'AWS_SECRET_ACCESS_KEY', None))
        has_bucket = bool(getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None))
        
        if has_key and has_secret and has_bucket:
            print("✓ S3 credentials configured")
            return True
        else:
            print("✗ S3 credentials incomplete")
            return False
    else:
        print("⚠ Using local storage (files will be lost on container restart)")
        print("  Consider using S3 or a persistent volume")
        return True


def check_django_settings():
    """Run Django system check."""
    print("\n" + "=" * 60)
    print("Running Django System Check...")
    print("=" * 60)
    
    try:
        call_command('check', '--deploy', verbosity=1)
        print("✓ Django system check passed")
        return True
    except SystemExit:
        print("✗ Django system check failed")
        return False
    except Exception as e:
        print(f"✗ Django system check error: {str(e)}")
        return False


def main():
    """Main verification function."""
    print("\n" + "=" * 60)
    print("Production Setup Verification")
    print("=" * 60 + "\n")
    
    results = {
        'env_vars': False,
        'database': False,
        'email': False,
        'storage': False,
        'django_check': False,
    }
    
    # Check environment variables
    env_ok, missing_required, missing_optional = check_environment_variables()
    results['env_vars'] = env_ok
    
    # Check database
    results['database'] = check_database()
    
    # Check email
    results['email'] = check_email()
    
    # Check storage
    results['storage'] = check_storage()
    
    # Check Django settings
    results['django_check'] = check_django_settings()
    
    # Summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check.replace('_', ' ').title()}: {status}")
    
    if missing_required:
        print("\n⚠ Missing Required Variables:")
        for var, desc in missing_required:
            print(f"  - {var}: {desc}")
    
    if all_passed:
        print("\n✓ All checks passed! Ready for deployment.")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above before deploying.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

