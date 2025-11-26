# Railway.app Deployment Checklist for ASCAI Lazio Platform

This checklist covers all the steps and configurations needed to successfully deploy your Django application on Railway.

## Prerequisites

- [ ] Railway account created (sign up at https://railway.app)
- [ ] GitHub repository connected to Railway
- [ ] Railway CLI installed (optional, for local testing)

---

## Step 1: Create New Project on Railway

- [ ] Log in to Railway dashboard
- [ ] Click "New Project"
- [ ] Select "Deploy from GitHub repo"
- [ ] Choose your repository (`ascai-v2` or your repo name)
- [ ] Railway will automatically detect the Dockerfile

---

## Step 2: Add PostgreSQL Database

- [ ] In your Railway project, click "+ New"
- [ ] Select "Database" → "Add PostgreSQL"
- [ ] Railway will automatically create a PostgreSQL service
- [ ] **Important**: Railway automatically injects `DATABASE_URL` environment variable
- [ ] Note the database service name for reference

---

## Step 3: Configure Environment Variables

Go to your service → **Variables** tab and add the following:

### Required Core Settings

- [ ] **`DJANGO_ENV`** = `production`
  - *Tells Django to use production settings*

- [ ] **`DJANGO_SETTINGS_MODULE`** = `config.settings.production`
  - *Explicitly sets the settings module (optional, but recommended)*

- [ ] **`DEBUG`** = `False`
  - *MUST be False in production for security*

- [ ] **`SECRET_KEY`** = `[Generate a secure key]`
  - *Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`*
  - *Or use: https://djecrety.ir/ (online generator)*
  - *⚠️ Keep this secret and never commit it to git*

### Hosts & Security

- [ ] **`ALLOWED_HOSTS`** = `your-app-name.up.railway.app,your-custom-domain.com`
  - *Replace `your-app-name` with your actual Railway app name*
  - *Add your custom domain if you have one (comma-separated)*
  - *Example: `ascai-lazio.up.railway.app,ascailazio.org,www.ascailazio.org`*
  - *Note: `healthcheck.railway.app` and `.railway.app` are automatically added by the application*

- [ ] **`CSRF_TRUSTED_ORIGINS`** = `https://your-app-name.up.railway.app,https://your-custom-domain.com`
  - *Same domains as ALLOWED_HOSTS but with `https://` prefix*
  - *Example: `https://ascai-lazio.up.railway.app,https://ascailazio.org`*

### Database Configuration

- [ ] **`DATABASE_URL`** = *[Automatically set by Railway when you add PostgreSQL]*
  - *Railway automatically provides this - you don't need to set it manually*
  - *If not automatically set, copy from PostgreSQL service → Variables → `DATABASE_URL`*

### Static & Media Storage

**Option A: Use WhiteNoise (Recommended for starting)**

- [ ] **`USE_S3`** = `False`
  - *Uses WhiteNoise for static files (included in deployment)*

**Option B: Use AWS S3 (For production with high traffic)**

- [ ] **`USE_S3`** = `True`
- [ ] **`AWS_ACCESS_KEY_ID`** = `[Your AWS Access Key]`
- [ ] **`AWS_SECRET_ACCESS_KEY`** = `[Your AWS Secret Key]`
- [ ] **`AWS_STORAGE_BUCKET_NAME`** = `[Your S3 Bucket Name]`
- [ ] **`AWS_S3_REGION_NAME`** = `us-east-1` *(or your preferred region)*
- [ ] **`AWS_S3_CUSTOM_DOMAIN`** = `[Optional: Your CDN domain]`

### Email Configuration

- [ ] **`EMAIL_BACKEND`** = `django.core.mail.backends.smtp.EmailBackend`
- [ ] **`EMAIL_HOST`** = `smtp.gmail.com` *(or your SMTP server)*
- [ ] **`EMAIL_PORT`** = `587`
- [ ] **`EMAIL_USE_TLS`** = `True`
- [ ] **`EMAIL_HOST_USER`** = `your-email@gmail.com`
- [ ] **`EMAIL_HOST_PASSWORD`** = `[App Password or SMTP password]`
  - *For Gmail: Use App Password (not regular password)*
  - *Generate at: https://myaccount.google.com/apppasswords*
- [ ] **`DEFAULT_FROM_EMAIL`** = `ASCAI Lazio <noreply@ascailazio.org>`
- [ ] **`CONTACT_EMAIL`** = `info@ascailazio.org`

### Localization

- [ ] **`DEFAULT_LANGUAGE`** = `en`
  - *Options: `en` (English) or `fr` (French)*

### Optional Settings

- [ ] **`DJANGO_LOG_LEVEL`** = `INFO` *(default: INFO)*
  - *Options: DEBUG, INFO, WARNING, ERROR, CRITICAL*

- [ ] **`SITE_DOMAIN`** = `your-app-name.up.railway.app`
  - *Used by Django-Allauth for email links*

---

## Step 4: Configure Service Settings

In your Railway service settings:

- [ ] **Build Command**: *(Auto-detected from Dockerfile - no action needed)*
- [ ] **Start Command**: *(Auto-detected - should be `./scripts/entrypoint.sh`)*
- [ ] **Healthcheck Path**: `/health/` *(Already configured in railway.json)*
- [ ] **Healthcheck Timeout**: `300` seconds *(Already configured)*

---

## Step 5: Deploy and Verify

- [ ] Click "Deploy" or push to your main branch (auto-deploys)
- [ ] Wait for build to complete (check Build logs)
- [ ] Wait for deployment to complete (check Deploy logs)
- [ ] Verify healthcheck passes (should see "✓" in logs)
- [ ] Check that migrations ran successfully
- [ ] Check that static files were collected

---

## Step 6: Post-Deployment Setup

### Create Superuser

- [ ] Go to Railway service → **Deployments** → Click on latest deployment
- [ ] Open **Shell** or use Railway CLI: `railway run python manage.py createsuperuser`
- [ ] Follow prompts to create admin account

### Verify Application

- [ ] Visit your Railway URL: `https://your-app-name.up.railway.app`
- [ ] Test home page loads correctly
- [ ] Test admin panel: `https://your-app-name.up.railway.app/admin/`
- [ ] Log in with superuser credentials
- [ ] Verify database connection works
- [ ] Test user registration flow
- [ ] Check static files are loading (CSS, images)

---

## Step 7: Custom Domain (Optional)

If you have a custom domain:

- [ ] Go to Railway service → **Settings** → **Domains**
- [ ] Click "Generate Domain" or "Add Custom Domain"
- [ ] For custom domain:
  - [ ] Add your domain (e.g., `ascailazio.org`)
  - [ ] Update DNS records as instructed by Railway
  - [ ] Wait for DNS propagation (can take up to 48 hours)
- [ ] Update `ALLOWED_HOSTS` to include custom domain
- [ ] Update `CSRF_TRUSTED_ORIGINS` to include custom domain
- [ ] Redeploy after DNS is configured

---

## Step 8: Monitoring & Maintenance

- [ ] Set up Railway monitoring/alerts (if available)
- [ ] Bookmark Railway dashboard for easy access
- [ ] Set up backup strategy for PostgreSQL database
- [ ] Document your deployment process
- [ ] Set up log aggregation (optional)

---

## Troubleshooting Checklist

If deployment fails:

- [ ] Check **Build logs** for errors
- [ ] Check **Deploy logs** for runtime errors
- [ ] Verify all required environment variables are set
- [ ] Verify `SECRET_KEY` is set and not the default value
- [ ] Verify `DEBUG=False` is set
- [ ] Verify `ALLOWED_HOSTS` includes your Railway domain
- [ ] Check database connection (verify `DATABASE_URL` is set)
- [ ] Verify migrations completed successfully
- [ ] Check if static files collection succeeded
- [ ] Review healthcheck logs (should see `/health/` endpoint responding)

---

## Quick Reference: Minimum Required Variables

For a basic deployment, you MUST set these at minimum:

```
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=[your-generated-secret-key]
ALLOWED_HOSTS=your-app-name.up.railway.app
```

Everything else has defaults or is auto-configured by Railway.

---

## Environment Variable Template

Copy this template and fill in your values:

```bash
# Core
DJANGO_ENV=production
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=your-secret-key-here

# Hosts
ALLOWED_HOSTS=your-app.up.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app.up.railway.app

# Database (auto-set by Railway)
# DATABASE_URL is automatically provided

# Storage
USE_S3=False

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org

# Localization
DEFAULT_LANGUAGE=en
```

---

## Notes

- Railway automatically provides `PORT` environment variable (don't set it manually)
- Railway automatically provides `DATABASE_URL` when PostgreSQL is added
- Railway may provide `RAILWAY_PUBLIC_DOMAIN` automatically
- Static files are collected automatically during deployment via `entrypoint.sh`
- Migrations run automatically during deployment via `entrypoint.sh`
- Healthcheck is configured to use `/health/` endpoint with 300s timeout

---

## Support Resources

- Railway Documentation: https://docs.railway.app
- Railway Status: https://status.railway.app
- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/

---

**Last Updated**: Based on current project configuration
**Project**: ASCAI Lazio Platform
**Django Version**: 5.2
**Database**: PostgreSQL (via Railway)

