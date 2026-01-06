# Production Setup Guide

This guide provides step-by-step instructions for setting up the ASCAI Lazio platform in production.

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- AWS S3 account (optional, for media storage)
- Email service account (Brevo, SendGrid, or SMTP)
- Domain name (optional)
- Deployment platform account (Railway, Render, DigitalOcean, etc.)

## Step 1: Environment Variables

Create a `.env` file or set environment variables in your deployment platform:

### Core Django Settings

```bash
# Required
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=<generate-a-secure-random-key>
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname
# OR individual settings:
# DB_NAME=ascai_lazio
# DB_USER=ascai_user
# DB_PASSWORD=secure_password
# DB_HOST=localhost
# DB_PORT=5432

# Default Language
DEFAULT_LANGUAGE=en
```

### Email Configuration (Choose ONE)

**Option 1: Brevo (Recommended)**
```bash
BREVO_API_KEY=your-brevo-api-key
```

**Option 2: SendGrid**
```bash
SENDGRID_API_KEY=your-sendgrid-api-key
```

**Option 3: SMTP**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

### Storage Configuration (Choose ONE)

**Option 1: AWS S3 (Recommended for Production)**
```bash
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=ascai-lazio-media
AWS_S3_REGION_NAME=us-east-1
# Optional: Custom domain
AWS_S3_CUSTOM_DOMAIN=cdn.your-domain.com
```

**Option 2: Railway Volume**
```bash
USE_S3=False
RAILWAY_VOLUME_MOUNT_PATH=/data
```

**Option 3: Local Storage (Not Recommended for Production)**
```bash
USE_S3=False
# Files will be lost on container restart
```

### Google OAuth (Optional)

```bash
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
# OR
GOOGLE_OAUTH2_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH2_CLIENT_SECRET=your-google-client-secret
```

### Data Population (Optional)

```bash
# Populate initial data on startup
POPULATE_DATA=true
# Clear existing data before populating
POPULATE_DATA_CLEAR=false
```

### Site Configuration

```bash
SITE_DOMAIN=your-domain.com
```

## Step 2: Generate Secret Key

Generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use an online generator: https://djecrety.ir/

## Step 3: Database Setup

### Create PostgreSQL Database

```bash
# On your server or database provider
createdb ascai_lazio
```

### Or use Database URL

If using a managed database service (Railway, Render, etc.), they will provide a DATABASE_URL.

## Step 4: AWS S3 Setup (If Using S3)

1. **Create S3 Bucket**
   - Go to AWS S3 Console
   - Create a new bucket (e.g., `ascai-lazio-media`)
   - Choose region (e.g., `us-east-1`)

2. **Configure Bucket Policy**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicReadGetObject",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::ascai-lazio-media/*"
       }
     ]
   }
   ```

3. **Create IAM User**
   - Go to IAM Console
   - Create new user with programmatic access
   - Attach policy: `AmazonS3FullAccess` (or create custom policy)
   - Save Access Key ID and Secret Access Key

4. **Set Environment Variables**
   ```bash
   USE_S3=True
   AWS_ACCESS_KEY_ID=<your-access-key>
   AWS_SECRET_ACCESS_KEY=<your-secret-key>
   AWS_STORAGE_BUCKET_NAME=ascai-lazio-media
   AWS_S3_REGION_NAME=us-east-1
   ```

## Step 5: Email Service Setup

### Brevo (Recommended)

1. **Sign up**: https://www.brevo.com/
2. **Get API Key**:
   - Go to Settings → API Keys
   - Create new API key
   - Copy the key
3. **Set Environment Variable**:
   ```bash
   BREVO_API_KEY=your-api-key
   ```

### SendGrid

1. **Sign up**: https://sendgrid.com/
2. **Get API Key**:
   - Go to Settings → API Keys
   - Create new API key
   - Copy the key
3. **Set Environment Variable**:
   ```bash
   SENDGRID_API_KEY=your-api-key
   ```

### Gmail SMTP

1. **Enable 2-Factor Authentication**
2. **Generate App Password**:
   - Go to Google Account → Security
   - Enable 2FA
   - Generate App Password
3. **Set Environment Variables**:
   ```bash
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

## Step 6: Google OAuth Setup (Optional)

1. **Create OAuth Credentials**:
   - Go to Google Cloud Console
   - Create new project or select existing
   - Enable Google+ API
   - Go to Credentials → Create Credentials → OAuth 2.0 Client ID
   - Set authorized redirect URIs:
     - `https://your-domain.com/accounts/google/login/callback/`
   - Save Client ID and Client Secret

2. **Set Environment Variables**:
   ```bash
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

3. **Configure in Django**:
   The `setup_google_oauth` command will automatically configure this.

## Step 7: Domain and SSL Setup

### Railway

1. **Add Custom Domain**:
   - Go to your service → Settings → Domains
   - Add your domain
   - Follow DNS configuration instructions

2. **SSL Certificate**:
   - Railway automatically provisions SSL certificates
   - Wait for certificate to be issued

### Render

1. **Add Custom Domain**:
   - Go to your service → Settings → Custom Domains
   - Add your domain
   - Follow DNS configuration instructions

2. **SSL Certificate**:
   - Render automatically provisions SSL certificates
   - Wait for certificate to be issued

### DigitalOcean

1. **Add Domain**:
   - Go to Networking → Domains
   - Add your domain
   - Configure DNS records

2. **SSL Certificate**:
   - Use Let's Encrypt or Cloudflare
   - Follow platform-specific instructions

## Step 8: Deployment Platform Setup

### Railway

1. **Create New Project**
2. **Add PostgreSQL Service**
3. **Add Web Service**:
   - Connect your repository
   - Set start command: `gunicorn config.wsgi:application`
   - Set environment variables
4. **Add Volume** (if not using S3):
   - Add volume service
   - Mount at `/data`
   - Set `RAILWAY_VOLUME_MOUNT_PATH=/data`

### Render

1. **Create New Web Service**
2. **Connect Repository**
3. **Add PostgreSQL Database**
4. **Configure Service**:
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start command: `gunicorn config.wsgi:application`
   - Set environment variables

### DigitalOcean

1. **Create App**
2. **Connect Repository**
3. **Add Database**
4. **Configure App**:
   - Set build and run commands
   - Set environment variables

## Step 9: Verify Configuration

Before deploying, verify your configuration:

```bash
# Check Django settings
python manage.py check --deploy

# Test email
python manage.py test_email

# Verify database connection
python manage.py dbshell
```

## Step 10: Initial Deployment

1. **Push to Repository**
2. **Deploy Service**
3. **Run Migrations** (if not automatic):
   ```bash
   python manage.py migrate
   ```
4. **Create Admin User**:
   ```bash
   python manage.py create_admin
   ```
5. **Populate Initial Data** (optional):
   ```bash
   python manage.py populate_all_initial_data
   ```

## Step 11: Post-Deployment Verification

1. **Health Check**:
   ```bash
   curl https://your-domain.com/health/
   ```

2. **Test Authentication**:
   - Visit login page
   - Test registration
   - Test password reset

3. **Test Email**:
   - Submit contact form
   - Verify email is sent

4. **Test File Uploads**:
   - Upload profile avatar
   - Verify file is accessible

5. **Run Test Commands**:
   ```bash
   python manage.py run_all_tests
   ```

## Troubleshooting

### Issue: Application Won't Start

- Check environment variables
- Verify database connection
- Check logs for errors
- Ensure all required services are running

### Issue: Static Files Not Loading

- Run `collectstatic` command
- Check STATIC_URL configuration
- Verify WhiteNoise/S3 configuration

### Issue: Email Not Sending

- Verify email backend configuration
- Check email service credentials
- Test with `test_email` command
- Check email service logs

### Issue: Database Connection Errors

- Verify DATABASE_URL or DB settings
- Check database is accessible
- Verify credentials
- Check firewall rules

## Next Steps

After successful setup:

1. Set up monitoring (Sentry, etc.)
2. Configure backups
3. Set up CI/CD pipeline
4. Document any custom configurations
5. Train administrators

## Support

For issues or questions:
- Check deployment platform documentation
- Review Django deployment checklist
- Check application logs
- Contact development team

