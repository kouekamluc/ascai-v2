# Google OAuth Redirect URI Mismatch - Quick Fix

## The Problem
You're seeing: **Error 400: redirect_uri_mismatch**

This means the redirect URI your app is sending doesn't match what's configured in Google Cloud Console.

## Quick Fix (3 Steps)

### Step 1: Check Your Redirect URI
```bash
railway run python manage.py verify_google_oauth
```

This will show you the exact redirect URI your app is using.

### Step 2: Update Site Domain (If Wrong)
If the domain shown doesn't match your production domain:
```bash
railway run python manage.py update_site_domain --domain your-production-domain.com
```

**Common domains:**
- `ascai.org` (custom domain)
- `your-app.up.railway.app` (Railway default)

### Step 3: Add Redirect URI to Google Cloud Console

1. Go to: https://console.cloud.google.com/
2. Select your project
3. Navigate to: **APIs & Services** → **Credentials**
4. Click your OAuth 2.0 Client ID
5. Under **"Authorized redirect URIs"**, click **"ADD URI"**
6. Paste the exact URI from Step 1 (must match exactly, including trailing slash)
7. Click **"SAVE"**

**Example redirect URI:**
```
https://ascai.org/accounts/google/login/callback/
```

## Verify It Works

1. Wait 1-2 minutes for Google changes to propagate
2. Clear browser cache or use incognito mode
3. Try logging in with Google again

## Still Not Working?

Run the verification command again and check:
- ✅ Site domain matches your production domain
- ✅ Redirect URI uses `https://` (not `http://`)
- ✅ Redirect URI ends with `/accounts/google/login/callback/` (trailing slash)
- ✅ Same URI is in Google Cloud Console (character-for-character match)

## Full Documentation

See `GOOGLE_OAUTH_REDIRECT_URI_FIX.md` for detailed troubleshooting.
