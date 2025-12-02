# Environment Setup Guide for Local Email Testing

## Quick Setup Steps

### Step 1: Create `.env` file

Create a `.env` file in your project root (same directory as `manage.py`). You can copy from `env.railway.example` or create a new one.

### Step 2: Configure Email Settings

For **local email testing**, add these settings to your `.env` file:

#### Option A: Console Backend (Default - Emails print to terminal)
```bash
# This is the default - emails will print to console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

#### Option B: Gmail SMTP (Send real emails)
```bash
# Switch to SMTP backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Gmail SMTP settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <your-email@gmail.com>
CONTACT_EMAIL=info@ascailazio.org
```

**To get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Enable 2-Factor Authentication if not already enabled
3. Generate an App Password for "Mail"
4. **IMPORTANT:** Remove ALL spaces from the password!
   - Google shows: `abcd efgh ijkl mnop`
   - Use: `abcdefghijklmnop`

### Step 3: Minimum Required Settings

At minimum, your `.env` file should have:

```bash
# Django Core
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Email (for testing)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <your-email@gmail.com>
```

### Step 4: Test Email Sending

After configuring your `.env` file, test it:

```bash
python manage.py test_email your-email@gmail.com
```

## Complete `.env` Template

Here's a complete template you can use:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
SECRET_KEY=django-insecure-change-me-use-random-string

# Hosts
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

# Database (adjust for your local setup)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ASCAI-V2
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Email Configuration - CHOOSE ONE:

# Option 1: Console (emails print to terminal)
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Option 2: Gmail SMTP (sends real emails)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password-no-spaces
DEFAULT_FROM_EMAIL=ASCAI Lazio <your-email@gmail.com>
CONTACT_EMAIL=info@ascailazio.org

# Localization
DEFAULT_LANGUAGE=en
```

## What to Do Next

1. **Create `.env` file** in project root
2. **Add email configuration** (choose console or SMTP)
3. **Get Gmail App Password** if using SMTP (see GMAIL_SETUP_GUIDE.md)
4. **Test with:** `python manage.py test_email your-email@gmail.com`

## Troubleshooting

### "EMAIL_HOST_USER is not set"
- Make sure you've added `EMAIL_HOST_USER=your-email@gmail.com` to `.env`

### "Authentication failed"
- For Gmail: Make sure you're using an App Password (not regular password)
- Remove ALL spaces from the App Password
- Verify 2FA is enabled on your Google account

### "Connection timeout"
- Check your internet connection
- Verify firewall isn't blocking port 587

## Files Reference

- `env.railway.example` - Production template for Railway
- `GMAIL_SETUP_GUIDE.md` - Detailed Gmail setup instructions
- `LOCAL_EMAIL_TESTING.md` - Local testing guide
- `EMAIL_IMPLEMENTATION_GUIDE.md` - Complete email provider guide












