# Deployment Testing Guide

This guide provides instructions for testing the ASCAI Lazio platform before and after deployment.

## Pre-Deployment Testing

### 1. Run All Tests

```bash
# Run all test commands
python manage.py run_all_tests

# Or run individual test suites
python manage.py test_auth_flows
python manage.py test_core_functionality
python manage.py test_workflows
```

### 2. Populate Initial Data

```bash
# Populate all initial data
python manage.py populate_all_initial_data

# Or populate individually
python manage.py populate_forum_categories
python manage.py populate_initial_content
python manage.py populate_universities
python manage.py populate_scholarships

# Clear and repopulate
python manage.py populate_all_initial_data --clear
```

### 3. Test Email Configuration

```bash
# Test email sending
python manage.py test_email
```

### 4. Run Django Tests

```bash
# Run all Django unit tests
python manage.py test --settings=config.settings.test

# Run tests for specific app
python manage.py test apps.accounts
```

## Post-Deployment Testing

### 1. Health Check

```bash
# Check health endpoint
curl https://your-domain.com/health/
```

### 2. Test Authentication Flows

1. **User Registration**
   - Visit `/accounts/signup/`
   - Register a new user
   - Verify email verification is sent
   - Check admin panel for pending approval

2. **Admin Approval**
   - Login as admin
   - Go to Users section
   - Approve the new user
   - Verify user can now login

3. **Password Reset**
   - Visit `/accounts/password/reset/`
   - Enter email address
   - Check email for reset link
   - Reset password and login

4. **Google OAuth** (if configured)
   - Visit login page
   - Click "Sign in with Google"
   - Complete OAuth flow
   - Verify user is created/connected

### 3. Test Core Functionality

1. **Language Switching**
   - Use language switcher
   - Verify content changes language
   - Check URL includes language prefix

2. **Search and Filtering**
   - Visit universities page
   - Test HTMX filters (city, degree, field, etc.)
   - Visit scholarships page
   - Test scholarship filters

3. **File Uploads**
   - Upload profile avatar
   - Upload document in dashboard
   - Verify files are saved correctly

4. **Email Sending**
   - Submit contact form
   - Verify email is sent
   - Check email backend logs

### 4. Test Workflows

1. **Mentorship**
   - Create mentor profile
   - Approve mentor (as admin)
   - Create mentorship request
   - Send messages

2. **Support Tickets**
   - Create support ticket
   - Add replies
   - Mark as resolved

3. **Event Registration**
   - Register for an event
   - Verify QR code is generated
   - Check registration in dashboard

4. **Community Forum**
   - Create forum thread
   - Add posts
   - Test upvoting
   - Test moderation (as admin)

5. **Governance** (if accessible)
   - Test member management
   - Test assembly creation
   - Test financial transactions
   - Test approval workflows

### 5. Test Production Features

1. **Static Files**
   - Verify CSS/JS load correctly
   - Check admin static files
   - Verify images display

2. **Media Files**
   - Upload file
   - Verify file is accessible
   - Check S3/local storage

3. **Database**
   - Verify migrations applied
   - Check data integrity
   - Test database connections

4. **Performance**
   - Check page load times
   - Test with multiple users
   - Monitor database queries

## Automated Testing Script

Create a script to run all tests:

```bash
#!/bin/bash
# test_deployment.sh

echo "Running Pre-Deployment Tests..."

# Run test commands
python manage.py run_all_tests

# Run Django tests
python manage.py test --settings=config.settings.test

# Check migrations
python manage.py showmigrations

# Check Django system
python manage.py check --deploy

echo "Tests completed!"
```

## Common Issues and Solutions

### Issue: Email Not Sending

**Solution:**
- Check email backend configuration
- Verify email credentials
- Test with `python manage.py test_email`
- Check email backend logs

### Issue: Static Files Not Loading

**Solution:**
- Run `python manage.py collectstatic`
- Check STATIC_URL configuration
- Verify WhiteNoise/S3 configuration
- Check file permissions

### Issue: Media Files Not Accessible

**Solution:**
- Check S3 credentials (if using S3)
- Verify media directory permissions
- Check MEDIA_URL configuration
- Verify file upload limits

### Issue: Database Connection Errors

**Solution:**
- Verify DATABASE_URL or DB settings
- Check database is running
- Verify connection credentials
- Check database migrations

### Issue: Authentication Not Working

**Solution:**
- Check AUTHENTICATION_BACKENDS
- Verify user approval status
- Check email verification
- Verify OAuth configuration

## Monitoring

After deployment, monitor:

1. **Error Logs**
   - Check application logs
   - Monitor error rates
   - Set up error tracking (Sentry)

2. **Performance**
   - Monitor response times
   - Check database query performance
   - Monitor server resources

3. **User Activity**
   - Track user registrations
   - Monitor active users
   - Check feature usage

4. **System Health**
   - Monitor server uptime
   - Check database connections
   - Monitor email delivery

## Next Steps

After successful testing:

1. Set up monitoring/alerting
2. Configure backups
3. Set up CI/CD pipeline
4. Document any issues found
5. Plan for future improvements

