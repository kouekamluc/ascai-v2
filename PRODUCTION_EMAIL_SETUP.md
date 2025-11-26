# Production Email Setup Instructions for Railway

This guide provides step-by-step instructions to configure email confirmation in production on Railway.

## ✅ What Has Been Fixed Automatically

The following issues have been resolved in the code:

1. **Email confirmation URLs now use absolute URLs** - Fixed in `apps/accounts/adapters.py`
2. **Email sending with proper logging** - Enhanced error handling and logging
3. **Styled redirect page after email confirmation** - Created `templates/account/email_confirmed.html`
4. **Site domain auto-update** - Production settings automatically update Site domain

## 📋 Railway Environment Variables Setup

### Step 1: Go to Railway Dashboard

1. Log in to [Railway](https://railway.app)
2. Select your project
3. Click on your service (the Django app, not the database)
4. Go to the **"Variables"** tab

### Step 2: Add/Verify Required Email Variables

Add or verify these environment variables:

```bash
# Email Backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# SMTP Server (Gmail example - adjust if using different provider)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Email Credentials
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password

# Email Addresses
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

### Step 3: Get Gmail App Password (If Using Gmail)

**⚠️ IMPORTANT:** For Gmail, you MUST use an App Password, not your regular password!

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Sign in with your Gmail account
3. Make sure 2-Step Verification is enabled (required for App Passwords)
4. Create a new App Password:
   - Select "Mail" or "Other (Custom name)"
   - Enter name: "ASCAI Lazio Django"
   - Click "Generate"
5. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)
6. **⚠️ REMOVE ALL SPACES** when pasting into Railway:
   - Google shows: `abcd efgh ijkl mnop`
   - Use in Railway: `abcdefghijklmnop` (no spaces!)

### Step 4: Verify Domain Configuration

Make sure these are set correctly:

```bash
# Your Railway domain (get from Railway → Settings → Domains)
ALLOWED_HOSTS=your-app-name.up.railway.app

# CSRF trusted origins (same domain with https://)
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app
```

**To find your Railway domain:**
1. Go to Railway → Your Service → **Settings** tab
2. Scroll to **"Networking"** or **"Domains"** section
3. Copy the generated domain (e.g., `ascai-lazio.up.railway.app`)

### Step 5: Update Site Domain (After First Deployment)

After your first deployment, run this command to ensure email links use the correct domain:

**Option A: Using Railway Shell**
1. Go to Railway → Your Service → **Deployments**
2. Click on the latest deployment
3. Click **"Shell"** or use Railway CLI: `railway run python manage.py update_site_domain`

**Option B: Using Railway CLI**
```bash
railway run python manage.py update_site_domain --domain your-app-name.up.railway.app
```

**Option C: Automatic (Already Configured)**
The production settings will automatically update the Site domain on startup, but running the command manually ensures it's set correctly.

## 🧪 Testing Email Configuration

### Test 1: Verify Email Settings

After setting environment variables, test email sending:

**Using Railway Shell:**
```bash
railway run python manage.py test_email your-test-email@example.com
```

Replace `your-test-email@example.com` with your actual email address.

### Test 2: Test User Registration Flow

1. Go to your production site: `https://your-app-name.up.railway.app`
2. Click "Register" or "Sign Up"
3. Fill in the registration form
4. Submit the form
5. **Check your email inbox** (and spam folder) for the confirmation email
6. Click the confirmation link in the email
7. Verify you see the **styled success page** (not an unstyled redirect)

### Test 3: Check Railway Logs

1. Go to Railway → Your Service → **Deployments** → Latest deployment
2. Open the **"Logs"** tab
3. Look for email-related log messages:
   - `Sending email confirmation to...`
   - `Email confirmation sent successfully to...`
   - Any error messages if emails fail

## 🔍 Troubleshooting

### Issue: "Email not received"

**Check 1: Verify Environment Variables**
- Go to Railway → Variables tab
- Verify all email variables are set correctly
- Check `EMAIL_HOST_PASSWORD` has NO SPACES (for Gmail App Passwords)

**Check 2: Check Railway Logs**
- Look for error messages in deployment logs
- Look for "Failed to send email confirmation" errors
- Check for authentication errors

**Check 3: Test Email Sending**
```bash
railway run python manage.py test_email your-email@example.com
```

**Check 4: Verify Gmail App Password**
- Make sure you're using an App Password (not regular password)
- Verify 2-Step Verification is enabled
- Check the password has NO SPACES

### Issue: "Email links don't work / redirect not styled"

**Check 1: Verify Site Domain**
```bash
railway run python manage.py update_site_domain --domain your-app-name.up.railway.app
```

**Check 2: Verify ALLOWED_HOSTS**
- Make sure `ALLOWED_HOSTS` includes your Railway domain
- Check Railway → Variables → `ALLOWED_HOSTS`

**Check 3: Check Email Link**
- Open the confirmation email
- Check the link starts with `https://your-app-name.up.railway.app`
- If it starts with `http://` or a different domain, the Site domain needs updating

### Issue: "Authentication failed" in logs

**For Gmail:**
- Verify you're using an App Password (not regular password)
- Make sure the password has NO SPACES
- Verify 2-Step Verification is enabled
- Try generating a new App Password

**For Other Providers:**
- Verify SMTP credentials are correct
- Check SMTP host and port settings
- Verify firewall/network allows outbound SMTP connections

## 📝 Quick Reference: All Required Variables

Copy this template and fill in your values:

```bash
# Core Django Settings
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here

# Domain Configuration
ALLOWED_HOSTS=your-app-name.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org

# Database (auto-set by Railway)
# DATABASE_URL is automatically provided

# Storage
USE_S3=False
```

## ✅ Verification Checklist

After setup, verify:

- [ ] All email environment variables are set in Railway
- [ ] `EMAIL_HOST_PASSWORD` has NO SPACES (for Gmail)
- [ ] `ALLOWED_HOSTS` includes your Railway domain
- [ ] `CSRF_TRUSTED_ORIGINS` includes your Railway domain with `https://`
- [ ] Test email command works: `railway run python manage.py test_email your-email@example.com`
- [ ] User registration sends confirmation email
- [ ] Confirmation email link works and shows styled success page
- [ ] Railway logs show successful email sending

## 🚀 After Setup

Once everything is configured:

1. **Test the full flow:**
   - Register a new user
   - Check email for confirmation link
   - Click the link
   - Verify styled success page appears

2. **Monitor logs:**
   - Check Railway logs regularly for email errors
   - Set up alerts if available

3. **Update Site domain if needed:**
   - If you change your domain, run: `railway run python manage.py update_site_domain --domain new-domain.com`

## 📚 Additional Resources

- [Gmail Setup Guide](GMAIL_SETUP_GUIDE.md) - Detailed Gmail configuration
- [Email Quick Reference](EMAIL_QUICK_REFERENCE.md) - Quick email config reference
- [Railway Deployment Checklist](RAILWAY_DEPLOYMENT_CHECKLIST.md) - Full deployment guide

---

**Last Updated:** Based on current codebase with email confirmation fixes
**Status:** Ready for production deployment

