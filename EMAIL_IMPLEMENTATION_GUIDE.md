# Email Implementation Guide for ASCAI Lazio

This guide will help you set up email functionality with real email providers for your Django application.

## Table of Contents
1. [Overview](#overview)
2. [Email Provider Options](#email-provider-options)
3. [SendGrid Setup](#sendgrid-setup)
4. [Mailgun Setup](#mailgun-setup)
5. [AWS SES Setup](#aws-ses-setup)
6. [Gmail SMTP Setup](#gmail-smtp-setup)
7. [Configuration](#configuration)
8. [Testing Email](#testing-email)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

Your Django application currently uses the console email backend for development. To send real emails in production, you need to configure a real email service provider.

**Current Email Configuration:**
- Development: Console backend (emails printed to terminal)
- Production: Needs to be configured with a real provider

**Email Features in Your App:**
- User registration email verification (django-allauth)
- Password reset emails
- Account approval notifications
- Contact form submissions

---

## Email Provider Options

### Comparison Table

| Provider | Free Tier | Best For | Setup Difficulty |
|----------|-----------|----------|------------------|
| **SendGrid** | 100 emails/day | Production apps | Easy |
| **Mailgun** | 5,000 emails/month | Production apps | Easy |
| **AWS SES** | 62,000 emails/month | AWS users | Medium |
| **Gmail SMTP** | Unlimited* | Personal/small projects | Easy |

*Gmail has daily sending limits (500 emails/day for free accounts)

### Recommendation
- **For Production**: SendGrid or Mailgun (easiest setup, reliable)
- **If using AWS**: AWS SES (cost-effective at scale)
- **For Testing/Development**: Gmail SMTP (quick setup)

---

## SendGrid Setup

### Step 1: Create SendGrid Account
1. Go to [https://sendgrid.com](https://sendgrid.com)
2. Sign up for a free account (100 emails/day free)
3. Verify your email address

### Step 2: Create API Key
1. Navigate to **Settings** → **API Keys**
2. Click **Create API Key**
3. Name it: `ASCAI Lazio Production`
4. Select **Full Access** or **Restricted Access** (Mail Send permissions)
5. Click **Create & View**
6. **Copy the API key immediately** (you won't see it again!)

### Step 3: Verify Sender Identity
1. Go to **Settings** → **Sender Authentication**
2. Choose **Single Sender Verification**
3. Fill in your details:
   - **From Email**: `noreply@ascailazio.org`
   - **From Name**: `ASCAI Lazio`
   - **Reply To**: `info@ascailazio.org`
4. Verify the email address sent to your inbox

### Step 4: Configure Django Settings

**Option A: Using SendGrid SMTP (Recommended)**
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # Literally the string 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key-here'  # Your actual API key
DEFAULT_FROM_EMAIL = 'ASCAI Lazio <noreply@ascailazio.org>'
```

**Option B: Using django-sendgrid-v5 (Alternative)**
```bash
pip install django-sendgrid-v5
```

Then in settings:
```python
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = "your-sendgrid-api-key-here"
DEFAULT_FROM_EMAIL = 'ASCAI Lazio <noreply@ascailazio.org>'
```

### Environment Variables for SendGrid
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your_actual_api_key_here
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

---

## Mailgun Setup

### Step 1: Create Mailgun Account
1. Go to [https://www.mailgun.com](https://www.mailgun.com)
2. Sign up for a free account (5,000 emails/month free)
3. Verify your email address

### Step 2: Add and Verify Domain
1. Navigate to **Sending** → **Domains**
2. Click **Add New Domain**
3. Enter your domain: `ascailazio.org`
4. Follow DNS verification instructions:
   - Add TXT records for domain verification
   - Add MX records (optional, for receiving)
   - Add CNAME records for tracking
5. Wait for verification (usually 24-48 hours)

**Note**: For testing, you can use Mailgun's sandbox domain (emails will have a warning banner)

### Step 3: Get SMTP Credentials
1. Go to **Sending** → **Domain Settings** → **SMTP credentials**
2. Click **Create SMTP User**
3. Username: `postmaster@ascailazio.org` (or your verified domain)
4. Password: Generate a strong password
5. **Save these credentials**

### Step 4: Configure Django Settings
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@ascailazio.org'  # Your SMTP username
EMAIL_HOST_PASSWORD = 'your-mailgun-smtp-password'  # Your SMTP password
DEFAULT_FROM_EMAIL = 'ASCAI Lazio <noreply@ascailazio.org>'
```

### Environment Variables for Mailgun
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@ascailazio.org
EMAIL_HOST_PASSWORD=your-mailgun-smtp-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

---

## AWS SES Setup

### Step 1: AWS Account Setup
1. Log in to [AWS Console](https://aws.amazon.com/console/)
2. Navigate to **Amazon SES** service
3. Select your region (e.g., `us-east-1`)

### Step 2: Verify Email Address or Domain
1. Go to **Verified identities** → **Create identity**
2. Choose **Email address** or **Domain**
3. For email: Enter `noreply@ascailazio.org` and verify via email
4. For domain: Follow DNS verification steps

### Step 3: Move Out of Sandbox (Important!)
- By default, SES is in "sandbox mode" (can only send to verified emails)
- To send to any email, request production access:
  1. Go to **Account dashboard**
  2. Click **Request production access**
  3. Fill out the form (use case, expected volume)
  4. Wait for approval (usually 24 hours)

### Step 4: Create SMTP Credentials
1. Go to **SMTP settings** → **Create SMTP credentials**
2. IAM User Name: `ascai-email-sender`
3. Click **Create**
4. **Download the credentials** (CSV file with username and password)

### Step 5: Configure Django Settings
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = f'email-smtp.{AWS_REGION}.amazonaws.com'  # e.g., email-smtp.us-east-1.amazonaws.com
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-aws-ses-smtp-username'  # From downloaded CSV
EMAIL_HOST_PASSWORD = 'your-aws-ses-smtp-password'  # From downloaded CSV
DEFAULT_FROM_EMAIL = 'ASCAI Lazio <noreply@ascailazio.org>'
```

### Environment Variables for AWS SES
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-aws-ses-smtp-username
EMAIL_HOST_PASSWORD=your-aws-ses-smtp-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

---

## Gmail SMTP Setup

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled

### Step 2: Generate App Password
1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Select **App**: Mail
3. Select **Device**: Other (Custom name)
4. Enter: `ASCAI Lazio Django`
5. Click **Generate**
6. **Copy the 16-character password** (spaces don't matter)

### Step 3: Configure Django Settings
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your-16-char-app-password'  # App password from Step 2
DEFAULT_FROM_EMAIL = 'ASCAI Lazio <your-email@gmail.com>'
```

### Environment Variables for Gmail
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <your-email@gmail.com>
CONTACT_EMAIL=info@ascailazio.org
```

### Limitations
- **Daily limit**: 500 emails/day for free Gmail accounts
- **Not recommended for production** with high email volume
- **Best for**: Testing, development, small projects

---

## Configuration

### Update Your Settings Files

#### 1. Update `config/settings/production.py`

Add email validation to ensure email is configured:

```python
# Email Configuration Validation
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(
            "SMTP email backend is configured but EMAIL_HOST_USER or "
            "EMAIL_HOST_PASSWORD is missing. Emails will not be sent."
        )
```

#### 2. Update Environment Variables

**For Railway:**
1. Go to your Railway project dashboard
2. Navigate to **Variables** tab
3. Add the email configuration variables based on your chosen provider
4. Make sure to set `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`

**For Local Development:**
Create a `.env` file in your project root:
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net  # or your provider's SMTP host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey  # or your SMTP username
EMAIL_HOST_PASSWORD=your-api-key-or-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

### Update `env.railway.example`

Update the example file with your chosen provider's settings.

---

## Testing Email

### Method 1: Django Shell Test

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

# Test email
send_mail(
    subject='Test Email from ASCAI Lazio',
    message='This is a test email to verify email configuration.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-email@example.com'],
    fail_silently=False,
)
```

### Method 2: Create a Management Command

Create `apps/core/management/commands/test_email.py`:

```python
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Send a test email to verify email configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test email to',
        )

    def handle(self, *args, **options):
        recipient = options['email']
        
        try:
            send_mail(
                subject='Test Email from ASCAI Lazio',
                message='This is a test email to verify email configuration is working correctly.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully sent test email to {recipient}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )
```

**Usage:**
```bash
python manage.py test_email your-email@example.com
```

### Method 3: Test User Registration Flow

1. Go to your registration page
2. Register a new user with a real email address
3. Check your email inbox (and spam folder) for verification email
4. Click the verification link

### Method 4: Test Password Reset

1. Go to password reset page
2. Enter your email address
3. Check your inbox for reset link

---

## Troubleshooting

### Common Issues

#### 1. "Authentication failed" Error
**Causes:**
- Wrong username/password
- For Gmail: Not using App Password (using regular password)
- For SendGrid: Not using `apikey` as username

**Solutions:**
- Double-check credentials
- For Gmail: Generate a new App Password
- For SendGrid: Ensure username is literally `apikey`

#### 2. "Connection refused" or "Connection timeout"
**Causes:**
- Wrong SMTP host or port
- Firewall blocking port 587
- Provider's SMTP server is down

**Solutions:**
- Verify SMTP host and port in provider's documentation
- Try port 465 with SSL instead of 587 with TLS
- Check provider's status page

#### 3. Emails Going to Spam
**Causes:**
- Unverified sender domain
- Missing SPF/DKIM records
- Poor email content

**Solutions:**
- Verify your domain with the email provider
- Add SPF and DKIM DNS records (provider will give you these)
- Use a professional "From" name and email
- Avoid spam trigger words in subject/content

#### 4. "Rate limit exceeded"
**Causes:**
- Exceeded provider's free tier limits
- Too many emails sent too quickly

**Solutions:**
- Check your provider's rate limits
- Implement email queuing (use Celery with django-celery-email)
- Upgrade to paid plan if needed

#### 5. Emails Not Sending in Production
**Causes:**
- Environment variables not set correctly
- Wrong settings module
- Email backend still set to console

**Solutions:**
- Verify environment variables in Railway/your hosting platform
- Check `DJANGO_SETTINGS_MODULE` is set to `config.settings.production`
- Ensure `EMAIL_BACKEND` is set to SMTP backend

### Debug Email Configuration

Add this to your settings temporarily to debug:

```python
# Debug email settings (remove after debugging)
import logging
logger = logging.getLogger(__name__)
logger.info(f"Email Backend: {EMAIL_BACKEND}")
logger.info(f"Email Host: {EMAIL_HOST}")
logger.info(f"Email Port: {EMAIL_PORT}")
logger.info(f"Email User: {EMAIL_HOST_USER}")
logger.info(f"From Email: {DEFAULT_FROM_EMAIL}")
# Don't log password!
```

---

## Best Practices

### 1. Use Environment Variables
✅ **DO**: Store email credentials in environment variables
❌ **DON'T**: Hardcode credentials in settings files

### 2. Use Separate Email Accounts
✅ **DO**: Use dedicated email accounts for sending (e.g., `noreply@ascailazio.org`)
❌ **DON'T**: Use personal email accounts for production

### 3. Verify Your Domain
✅ **DO**: Verify your domain with your email provider
✅ **DO**: Set up SPF, DKIM, and DMARC records
❌ **DON'T**: Skip domain verification (emails will go to spam)

### 4. Monitor Email Delivery
✅ **DO**: Set up email delivery monitoring
✅ **DO**: Check provider's dashboard for bounce/spam reports
✅ **DO**: Monitor email sending limits

### 5. Handle Email Failures Gracefully
✅ **DO**: Use `fail_silently=False` in development (to catch errors)
✅ **DO**: Use `fail_silently=True` in production (or implement retry logic)
✅ **DO**: Log email sending failures

### 6. Use Email Queuing for High Volume
For high-volume email sending, consider using:
- **django-celery-email**: Queue emails with Celery
- **django-post-office**: Database-backed email queue

### 7. Test Before Production
✅ **DO**: Test email sending in staging environment
✅ **DO**: Test with real email addresses
✅ **DO**: Check spam folders

### 8. Email Templates
✅ **DO**: Use HTML email templates for better appearance
✅ **DO**: Include plain text versions
✅ **DO**: Test email rendering in different email clients

---

## Quick Start Checklist

- [ ] Choose an email provider (SendGrid recommended for ease)
- [ ] Create account and verify email/domain
- [ ] Get SMTP credentials or API key
- [ ] Add environment variables to Railway/local `.env`
- [ ] Update `EMAIL_BACKEND` to SMTP backend
- [ ] Test email sending using management command
- [ ] Test user registration email flow
- [ ] Test password reset email flow
- [ ] Verify emails are not going to spam
- [ ] Monitor email delivery in provider dashboard

---

## Additional Resources

- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [Mailgun Documentation](https://documentation.mailgun.com/)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)

---

## Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Review your email provider's documentation
3. Check Django logs for error messages
4. Verify environment variables are set correctly
5. Test with a simple email first before testing full flows

---

**Last Updated**: 2024
**Project**: ASCAI Lazio Django Application

