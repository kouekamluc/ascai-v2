# Google OAuth Redirect URI Mismatch Fix Guide

## Error Message
```
Error 400: redirect_uri_mismatch
You can't sign in because this app sent an invalid request.
```

## What This Error Means

This error occurs when the redirect URI that your Django application sends to Google doesn't match any of the authorized redirect URIs configured in your Google Cloud Console OAuth credentials.

## How Django-allauth Constructs the Redirect URI

Django-allauth automatically constructs the redirect URI using:
- **Protocol**: `https` in production, `http` in development
- **Domain**: From Django's `Site` model (stored in database)
- **Path**: `/accounts/google/login/callback/`

**Format**: `{protocol}://{site.domain}/accounts/google/login/callback/`

**Example**: `https://ascai.org/accounts/google/login/callback/`

## Step-by-Step Fix

### Step 1: Check Your Current Site Domain

Run this command in your production environment:

```bash
railway run python manage.py shell
```

Then in the shell:
```python
from django.contrib.sites.models import Site
site = Site.objects.get_current()
print(f"Current Site domain: {site.domain}")
print(f"Redirect URI would be: https://{site.domain}/accounts/google/login/callback/")
```

### Step 2: Update Site Domain (If Needed)

If your Site domain doesn't match your production domain, update it:

```bash
# For Railway
railway run python manage.py update_site_domain --domain your-production-domain.com

# For local testing
python manage.py update_site_domain --domain localhost:8000
```

**Common production domains:**
- `ascai.org` (if using custom domain)
- `your-app.up.railway.app` (if using Railway default domain)
- `www.ascai.org` (if using www subdomain)

### Step 3: Get the Exact Redirect URI

After updating the Site domain, run the setup command to see the exact redirect URI:

```bash
railway run python manage.py setup_google_oauth
```

This will display the exact redirect URI you need to configure in Google Cloud Console.

### Step 4: Configure Google Cloud Console

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Select your project

2. **Navigate to OAuth Credentials**
   - Go to: **APIs & Services** → **Credentials**
   - Find your OAuth 2.0 Client ID (the one matching your `GOOGLE_CLIENT_ID`)
   - Click on it to edit

3. **Add Authorized Redirect URI**
   - Scroll down to **"Authorized redirect URIs"**
   - Click **"ADD URI"**
   - Enter the **exact** redirect URI from Step 3:
     ```
     https://your-production-domain.com/accounts/google/login/callback/
     ```
   - **Important**: 
     - Must start with `https://` (not `http://`) for production
     - Must end with `/accounts/google/login/callback/` (trailing slash is important)
     - Must match your Site domain exactly

4. **Save Changes**
   - Click **"SAVE"** at the bottom
   - Wait a few seconds for changes to propagate

### Step 5: Test the Fix

1. **Clear browser cache** (or use incognito mode)
2. **Try logging in with Google** again
3. The error should be resolved

## Common Issues and Solutions

### Issue 1: Site Domain is Wrong

**Symptom**: Redirect URI shows wrong domain (e.g., `localhost:8000` in production)

**Solution**: 
```bash
railway run python manage.py update_site_domain --domain your-production-domain.com
```

### Issue 2: Multiple Domains (www vs non-www)

**Symptom**: Site works on `ascai.org` but not `www.ascai.org` (or vice versa)

**Solution**: Add **both** redirect URIs to Google Cloud Console:
- `https://ascai.org/accounts/google/login/callback/`
- `https://www.ascai.org/accounts/google/login/callback/`

Or, redirect one to the other and only configure the canonical domain.

### Issue 3: Trailing Slash Mismatch

**Symptom**: URI looks correct but still getting error

**Solution**: Ensure the redirect URI in Google Cloud Console **exactly** matches:
- Must have trailing slash: `/accounts/google/login/callback/`
- Not: `/accounts/google/login/callback` (missing trailing slash)

### Issue 4: HTTP vs HTTPS

**Symptom**: Using `http://` in production

**Solution**: 
- Production must use `https://`
- Development can use `http://localhost:8000`
- Add both if testing locally and in production

### Issue 5: Domain Changed After Deployment

**Symptom**: Worked before, stopped working after domain change

**Solution**: 
1. Update Site domain: `python manage.py update_site_domain --domain new-domain.com`
2. Add new redirect URI to Google Cloud Console
3. Optionally remove old redirect URI if no longer needed

## Verification Checklist

- [ ] Site domain matches production domain
- [ ] Redirect URI in Google Cloud Console matches exactly (including trailing slash)
- [ ] Using `https://` for production redirect URI
- [ ] Saved changes in Google Cloud Console
- [ ] Waited a few seconds for changes to propagate
- [ ] Cleared browser cache or using incognito mode
- [ ] Tested login with Google

## Quick Reference Commands

```bash
# Check current Site domain
railway run python manage.py shell -c "from django.contrib.sites.models import Site; print(Site.objects.get_current().domain)"

# Update Site domain
railway run python manage.py update_site_domain --domain your-domain.com

# Setup Google OAuth (shows redirect URI)
railway run python manage.py setup_google_oauth

# Verify redirect URI format
# Should be: https://your-domain.com/accounts/google/login/callback/
```

## Still Having Issues?

1. **Double-check the redirect URI**:
   - Run `python manage.py setup_google_oauth` to see the exact URI
   - Compare it character-by-character with what's in Google Cloud Console

2. **Check Google Cloud Console**:
   - Ensure you're editing the correct OAuth Client ID
   - Verify the redirect URI is saved (refresh the page)
   - Check if there are multiple OAuth clients (use the one matching your `GOOGLE_CLIENT_ID`)

3. **Check Site domain**:
   - Verify it matches your actual production domain
   - If using Railway, check your Railway domain in Settings → Domains

4. **Wait for propagation**:
   - Google changes can take a few minutes to propagate
   - Try again after 2-3 minutes

5. **Check logs**:
   - Look for any errors in your application logs
   - Check Railway logs: `railway logs`

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Django-allauth Documentation](https://docs.allauth.org/)
- [Google Cloud Console](https://console.cloud.google.com/)
