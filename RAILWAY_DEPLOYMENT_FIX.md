# Railway Deployment Healthcheck Fix

## Problem
After adding email environment variables, Railway deployment fails with healthcheck errors. The app builds successfully but the healthcheck endpoint `/health/` returns "service unavailable".

## Root Cause
The production settings were testing SMTP connection on startup, which could block or cause issues if:
1. Email credentials are incorrect
2. Network issues during startup
3. SMTP server is temporarily unavailable

## Solution Applied
✅ **Removed blocking SMTP connection test from startup** - Email connection will be tested when actually sending emails, not during app startup.

## What You Need to Check

### 1. Verify Environment Variables in Railway

Go to Railway → Your Service → **Variables** tab and verify these are set correctly:

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

### 2. Common Issues to Check

#### Issue: Quotes in Environment Variables
❌ **Wrong:**
```
EMAIL_HOST_USER="kouekamkamgouluc@gmail.com"
```

✅ **Correct:**
```
EMAIL_HOST_USER=kouekamkamgouluc@gmail.com
```

**Fix:** Remove all quotes from environment variable values in Railway.

#### Issue: Spaces in Password
❌ **Wrong:**
```
EMAIL_HOST_PASSWORD=xswh kmxt kehs lifj
```

✅ **Correct:**
```
EMAIL_HOST_PASSWORD=xswhkmxtkehslifj
```

**Fix:** Make sure App Password has NO spaces.

#### Issue: Incomplete Email Address
❌ **Wrong:**
```
EMAIL_HOST_USER=kouekamkamgouluc@gmail
```

✅ **Correct:**
```
EMAIL_HOST_USER=kouekamkamgouluc@gmail.com
```

**Fix:** Make sure email address is complete with `.com` extension.

#### Issue: Missing Required Variables
Make sure ALL of these are set:
- `EMAIL_BACKEND`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `DEFAULT_FROM_EMAIL`

### 3. Check Railway Logs

After deploying, check Railway logs for errors:

1. Go to Railway → Your Service → **Deployments**
2. Click on the latest deployment
3. Check **"Logs"** tab
4. Look for:
   - Email configuration messages
   - Django startup errors
   - Any exceptions or tracebacks

### 4. Test After Deployment

Once the app is running, test email sending:

```bash
# In Railway Shell
railway run python manage.py test_email kouekamkamgouluc@gmail.com
```

## Quick Fix Checklist

- [ ] All email environment variables are set in Railway
- [ ] No quotes around variable values
- [ ] No spaces in App Password
- [ ] Email address is complete (`@gmail.com`)
- [ ] All required variables are present
- [ ] Check Railway logs for specific errors
- [ ] Redeploy after fixing variables

## If Still Failing

1. **Check Railway Logs** - Look for specific error messages
2. **Verify Variables** - Double-check all environment variables
3. **Test Locally** - Make sure email works locally first
4. **Check Database** - Ensure database connection is working
5. **Review Deployment Logs** - Check for other startup errors

## Next Steps

After the fix is deployed:
1. The app should start successfully
2. Healthcheck should pass
3. Email will be tested when actually sending (not on startup)
4. Check logs for email configuration status

