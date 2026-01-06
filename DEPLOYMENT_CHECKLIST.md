# Production Deployment Checklist

Use this checklist to ensure a smooth deployment to production.

## Pre-Deployment

### Environment Setup
- [ ] All environment variables configured
- [ ] SECRET_KEY generated and set (not default)
- [ ] DEBUG=False set
- [ ] ALLOWED_HOSTS configured with production domain
- [ ] CSRF_TRUSTED_ORIGINS configured
- [ ] Database connection string configured
- [ ] Email backend configured (Brevo/SendGrid/SMTP)
- [ ] Storage configured (S3 or volume)
- [ ] Google OAuth configured (optional)

### Code Preparation
- [ ] All code committed to repository
- [ ] All migrations created and tested
- [ ] Static files collected locally
- [ ] Tests passing
- [ ] No linting errors
- [ ] Documentation updated

### Verification
- [ ] Run `python scripts/verify_production_setup.py`
- [ ] Run `python manage.py check --deploy`
- [ ] Run `python manage.py run_all_tests`
- [ ] Test email sending locally
- [ ] Verify database connection

## Deployment

### Platform Setup
- [ ] Deployment platform account created
- [ ] Repository connected
- [ ] PostgreSQL database service added
- [ ] Environment variables set in platform
- [ ] Build command configured
- [ ] Start command configured
- [ ] Health check endpoint configured

### Initial Deployment
- [ ] Service deployed
- [ ] Migrations run automatically or manually
- [ ] Static files collected
- [ ] Admin user created
- [ ] Site domain updated
- [ ] Google OAuth configured (if using)

### Data Population
- [ ] Initial data populated (if using POPULATE_DATA)
- [ ] Forum categories created
- [ ] Initial news/events added
- [ ] Universities data populated
- [ ] Scholarships data populated

## Post-Deployment

### Verification
- [ ] Health check endpoint working (`/health/`)
- [ ] Home page loads correctly
- [ ] Static files loading
- [ ] Media files accessible
- [ ] Database queries working
- [ ] Email sending working
- [ ] Authentication flows working

### Testing
- [ ] User registration works
- [ ] Admin approval works
- [ ] Email verification works
- [ ] Password reset works
- [ ] Google OAuth works (if configured)
- [ ] File uploads work
- [ ] All major features accessible

### Security
- [ ] HTTPS enabled
- [ ] Security headers present
- [ ] CSRF protection working
- [ ] Admin panel secured
- [ ] Sensitive data not exposed
- [ ] Environment variables secure

### Monitoring
- [ ] Error tracking set up (Sentry, etc.)
- [ ] Uptime monitoring configured
- [ ] Logs accessible
- [ ] Alerts configured
- [ ] Performance monitoring set up

## Maintenance

### Regular Tasks
- [ ] Database backups configured
- [ ] Backup restoration tested
- [ ] Update procedure documented
- [ ] Rollback procedure documented
- [ ] Monitoring alerts tested

### Documentation
- [ ] Deployment procedure documented
- [ ] Environment variables documented
- [ ] Troubleshooting guide created
- [ ] Admin guide created
- [ ] User guide created (if needed)

## Troubleshooting

If deployment fails:

1. **Check Logs**
   - Review application logs
   - Check database logs
   - Review platform logs

2. **Verify Configuration**
   - Run verification script
   - Check environment variables
   - Verify database connection

3. **Test Locally**
   - Test with production settings
   - Verify all dependencies
   - Check for missing migrations

4. **Common Issues**
   - Static files not loading → Run collectstatic
   - Database errors → Check migrations
   - Email not sending → Verify credentials
   - 500 errors → Check logs for details

## Support

For deployment issues:
- Check platform documentation
- Review Django deployment guide
- Check application logs
- Contact development team

