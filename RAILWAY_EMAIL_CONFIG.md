# Railway Email Configuration - Exact Settings

This document provides the **exact environment variables** you need to set in Railway for production email.

## 🚀 Quick Setup for Railway

### Step 1: Go to Railway Dashboard

1. Log in to [Railway](https://railway.app)
2. Select your project
3. Click on your **Django service** (not the database)
4. Go to the **"Variables"** tab
5. Click **"New Variable"** for each setting below

### Step 2: Copy-Paste These Variables

Copy and paste these **exact** environment variables into Railway:

#### Option A: Gmail SMTP (What You're Using Locally)

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=kouekamkamgouluc@gmail.com
EMAIL_HOST_PASSWORD=xswhkmxtkehslifj
DEFAULT_FROM_EMAIL=ASCAI Lazio <kouekamkamgouluc@gmail.com>
CONTACT_EMAIL=info@ascailazio.org
```

**⚠️ IMPORTANT NOTES:**
- Use the **exact same App Password** that works locally (`xswhkmxtkehslifj`)
- **NO SPACES** in the password
- Make sure the email address is complete (`@gmail.com`, not `@gmail`)

#### Option B: SendGrid (Recommended for Production)

If you want to use SendGrid instead (more reliable for production):

1. Sign up at [SendGrid](https://sendgrid.com) (free tier: 100 emails/day)
2. Get your API key from SendGrid dashboard
3. Use these variables:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

**Note:** Replace `SG.your-sendgrid-api-key-here` with your actual SendGrid API key.

### Step 3: Required Django Settings

Make sure these are also set in Railway:

```bash
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=your-production-secret-key-here
```

### Step 4: Domain Configuration

Set your Railway domain (get it from Railway → Settings → Domains):

```bash
ALLOWED_HOSTS=your-app-name.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app
```

**To find your domain:**
1. Railway → Your Service → **Settings** tab
2. Look for **"Networking"** or **"Domains"** section
3. Copy the domain (e.g., `ascai-lazio-production.up.railway.app`)

## 📋 Complete Railway Variables Checklist

### Required Email Variables (Choose One Option)

**Option A: Gmail (Current Setup)**
- [ ] `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- [ ] `EMAIL_HOST=smtp.gmail.com`
- [ ] `EMAIL_PORT=587`
- [ ] `EMAIL_USE_TLS=True`
- [ ] `EMAIL_HOST_USER=kouekamkamgouluc@gmail.com`
- [ ] `EMAIL_HOST_PASSWORD=xswhkmxtkehslifj` (your App Password)
- [ ] `DEFAULT_FROM_EMAIL=ASCAI Lazio <kouekamkamgouluc@gmail.com>`
- [ ] `CONTACT_EMAIL=info@ascailazio.org`

**Option B: SendGrid (Recommended)**
- [ ] `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- [ ] `EMAIL_HOST=smtp.sendgrid.net`
- [ ] `EMAIL_PORT=587`
- [ ] `EMAIL_USE_TLS=True`
- [ ] `EMAIL_HOST_USER=apikey`
- [ ] `EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key`
- [ ] `DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>`
- [ ] `CONTACT_EMAIL=info@ascailazio.org`

### Required Django Variables
- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production`
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY=your-secret-key` (generate a new one for production!)
- [ ] `ALLOWED_HOSTS=your-app.up.railway.app`
- [ ] `CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app`

### Database (Usually Auto-Configured)
- Railway usually injects `DATABASE_URL` automatically
- If not, you'll need to set database variables

## 🧪 Testing After Deployment

### Test 1: Check Railway Logs

After deploying, check Railway logs for email configuration:

1. Go to Railway → Your Service → **Deployments**
2. Click on the latest deployment
3. Check **"Logs"** tab
4. Look for email configuration messages

### Test 2: Test Email Sending

Use Railway Shell to test:

1. Railway → Your Service → **Deployments** → Latest deployment
2. Click **"Shell"** or use Railway CLI
3. Run:
   ```bash
   python manage.py test_email your-email@gmail.com
   ```

### Test 3: Test User Registration

1. Go to your Railway app URL
2. Try registering a new user
3. Check if confirmation email is sent
4. Check Railway logs for email sending status

## ⚠️ Common Issues

### Issue: "Console email backend is active"
**Solution:** Make sure `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` is set (not console)

### Issue: "Authentication failed"
**Solution:** 
- For Gmail: Verify App Password has no spaces
- For SendGrid: Make sure `EMAIL_HOST_USER=apikey` (literal word "apikey")

### Issue: "Email not received"
**Solution:**
- Check spam folder
- Verify email address is correct
- Check Railway logs for errors
- Verify SMTP credentials are correct

## 🔒 Security Notes

1. **Never commit `.env` files** - Railway variables are secure
2. **Use different App Password** for production (don't reuse local one)
3. **Generate new SECRET_KEY** for production (don't use development key)
4. **Use SendGrid for production** if possible (more reliable than Gmail)

## 📚 Related Documentation

- `PRODUCTION_EMAIL_SETUP.md` - Detailed production setup guide
- `GMAIL_SETUP_GUIDE.md` - Gmail-specific setup
- `EMAIL_IMPLEMENTATION_GUIDE.md` - Complete email provider guide
- `RAILWAY_DEPLOYMENT_CHECKLIST.md` - Full Railway deployment checklist

