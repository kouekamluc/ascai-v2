# Railway Production Email Fix - Quick Setup Guide

## ✅ What Was Fixed Automatically

The following code changes have been made to fix email confirmation issues:

1. ✅ **Email URLs now use absolute URLs** - Fixed in `apps/accounts/adapters.py`
   - Email confirmation links now work correctly in production
   - Uses `request.build_absolute_uri()` for proper domain handling

2. ✅ **Enhanced email logging** - Added to `apps/accounts/adapters.py`
   - Logs when emails are sent successfully
   - Logs errors if email sending fails
   - Helps debug email issues in production

3. ✅ **Styled redirect page** - Created `templates/account/email_confirmed.html`
   - Beautiful styled success page after email confirmation
   - Matches ASCAI Lazio design system

4. ✅ **Management command** - Created `update_site_domain.py`
   - Helps ensure Site domain matches your Railway domain
   - Run after deployment to verify email links

## 🚀 Railway Setup Steps

### Step 1: Add Email Environment Variables

Go to Railway → Your Service → **Variables** tab and add/verify these:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

**⚠️ For Gmail:** 
- You MUST use an App Password (not regular password)
- Get it from: https://myaccount.google.com/apppasswords
- **Remove ALL SPACES** from the password when pasting into Railway
- Example: Google shows `abcd efgh ijkl mnop` → Use `abcdefghijklmnop`

### Step 2: Verify Domain Variables

Make sure these are set (get your domain from Railway → Settings → Domains):

```bash
ALLOWED_HOSTS=your-app-name.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app
```

### Step 3: Deploy and Test

1. **Deploy your changes** (push to main branch or trigger deployment)

2. **Update Site domain** (after first deployment):
   ```bash
   railway run python manage.py update_site_domain --domain your-app-name.up.railway.app
   ```
   Replace `your-app-name.up.railway.app` with your actual Railway domain.

3. **Test email sending**:
   ```bash
   railway run python manage.py test_email your-email@example.com
   ```

4. **Test full registration flow**:
   - Go to your production site
   - Register a new user
   - Check email for confirmation link
   - Click the link
   - Verify you see the styled success page

## 📋 Complete Variable Checklist

Copy and verify all these in Railway → Variables:

```bash
# Core
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key

# Domain (replace with your actual Railway domain)
ALLOWED_HOSTS=your-app-name.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app

# Email (replace with your actual email credentials)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

## 🔍 Troubleshooting

### Emails not being sent?

1. **Check Railway logs:**
   - Go to Railway → Deployments → Latest → Logs
   - Look for "Sending email confirmation" or error messages

2. **Verify Gmail App Password:**
   - Make sure you're using App Password (not regular password)
   - Verify NO SPACES in the password
   - Check 2-Step Verification is enabled

3. **Test email command:**
   ```bash
   railway run python manage.py test_email your-email@example.com
   ```

### Email links not working?

1. **Update Site domain:**
   ```bash
   railway run python manage.py update_site_domain --domain your-app-name.up.railway.app
   ```

2. **Check ALLOWED_HOSTS:**
   - Verify it includes your Railway domain
   - Should match the domain you generated in Railway

### Redirect page not styled?

- The styled page should appear automatically after email confirmation
- If you see an unstyled page, check Railway logs for errors
- Verify the template exists: `templates/account/email_confirmed.html`

## 📚 Full Documentation

For detailed instructions, see:
- **[PRODUCTION_EMAIL_SETUP.md](PRODUCTION_EMAIL_SETUP.md)** - Complete setup guide
- **[GMAIL_SETUP_GUIDE.md](GMAIL_SETUP_GUIDE.md)** - Gmail configuration details
- **[RAILWAY_DEPLOYMENT_CHECKLIST.md](RAILWAY_DEPLOYMENT_CHECKLIST.md)** - Full deployment guide

## ✅ Verification

After setup, verify:

- [ ] All email variables set in Railway
- [ ] Gmail App Password has NO SPACES
- [ ] Test email command works
- [ ] User registration sends confirmation email
- [ ] Confirmation link works
- [ ] Styled success page appears after confirmation

---

**Ready to deploy!** 🚀







