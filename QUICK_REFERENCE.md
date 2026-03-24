# Quick Reference Guide

Quick reference for common tasks and commands in the ASCAI Lazio platform.

## Management Commands

### Testing Commands

```bash
# Run all tests
python manage.py run_all_tests

# Run specific test suites
python manage.py test_auth_flows
python manage.py test_core_functionality
python manage.py test_workflows

# Run Django unit tests
python manage.py test --settings=config.settings.test
```

### Data Population Commands

```bash
# Populate all initial data
python manage.py populate_all_initial_data

# Populate specific data
python manage.py populate_forum_categories
python manage.py populate_initial_content
python manage.py populate_universities
python manage.py populate_scholarships

# Clear and repopulate
python manage.py populate_all_initial_data --clear
```

### Setup Commands

```bash
# Create admin user
python manage.py create_admin

# Update site domain
python manage.py update_site_domain

# Setup Google OAuth
python manage.py setup_google_oauth

# Verify Google OAuth configuration (shows redirect URI)
python manage.py verify_google_oauth

# Test email
python manage.py test_email
```

### Verification Commands

```bash
# Verify production setup
python scripts/verify_production_setup.py

# Django system check
python manage.py check --deploy

# Show migrations
python manage.py showmigrations
```

## Common Tasks

### Initial Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create admin user**
   ```bash
   python manage.py create_admin
   ```

4. **Populate initial data**
   ```bash
   python manage.py populate_all_initial_data
   ```

5. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

6. **Run server**
   ```bash
   python manage.py runserver
   ```

### Before Deployment

1. **Run all tests**
   ```bash
   python manage.py run_all_tests
   ```

2. **Verify production setup**
   ```bash
   python scripts/verify_production_setup.py
   ```

3. **Check Django settings**
   ```bash
   python manage.py check --deploy
   ```

4. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

### After Deployment

1. **Health check**
   ```bash
   curl https://your-domain.com/health/
   ```

2. **Test authentication**
   - Visit login page
   - Test registration
   - Test password reset

3. **Test email**
   ```bash
   python manage.py test_email
   ```

4. **Run tests**
   ```bash
   python manage.py run_all_tests
   ```

## Environment Variables

### Required

```bash
SECRET_KEY=<generate-secure-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=postgresql://...
```

### Email (Choose ONE)

```bash
# Brevo (Recommended)
BREVO_API_KEY=your-key

# SendGrid
SENDGRID_API_KEY=your-key

# SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

### Storage (Choose ONE)

```bash
# AWS S3
USE_S3=True
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1

# Railway Volume
USE_S3=False
RAILWAY_VOLUME_MOUNT_PATH=/data
```

### Optional

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your-id
GOOGLE_CLIENT_SECRET=your-secret

# Data Population
POPULATE_DATA=true
POPULATE_DATA_CLEAR=false

# Site Domain
SITE_DOMAIN=your-domain.com
```

## File Locations

### Management Commands
- `apps/core/management/commands/` - Core commands
- `apps/community/management/commands/` - Community commands
- `apps/diaspora/management/commands/` - Diaspora commands
- `apps/universities/management/commands/` - University commands
- `apps/scholarships/management/commands/` - Scholarship commands

### Documentation
- `README.md` - Main readme
- `PRODUCTION_SETUP_GUIDE.md` - Production setup
- `DEPLOYMENT_CHECKLIST.md` - Deployment checklist
- `DEPLOYMENT_TESTING_GUIDE.md` - Testing guide
- `IMPLEMENTATION_COMPLETE.md` - Implementation summary

### Scripts
- `scripts/entrypoint.sh` - Deployment entrypoint
- `scripts/verify_production_setup.py` - Production verification
- `scripts/predeploy.sh` - Pre-deployment script

## Troubleshooting

### Command Not Found
- Ensure virtual environment is activated
- Check command is in correct app's management/commands/
- Verify command class name matches filename

### Import Errors
- Check all dependencies installed
- Verify Python path
- Check for circular imports

### Database Errors
- Verify database connection
- Check migrations applied
- Verify database credentials

### Email Not Sending
- Check email backend configuration
- Verify email credentials
- Test with `test_email` command

### Static Files Not Loading
- Run `collectstatic` command
- Check STATIC_URL configuration
- Verify WhiteNoise/S3 configuration

## Support

For more information:
- See `PRODUCTION_SETUP_GUIDE.md` for detailed setup
- See `DEPLOYMENT_CHECKLIST.md` for deployment steps
- See `DEPLOYMENT_TESTING_GUIDE.md` for testing procedures

