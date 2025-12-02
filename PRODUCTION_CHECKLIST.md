# Production Deployment Checklist

This checklist ensures all environment variables and security settings are properly configured for production deployment.

## Pre-Deployment Security Checks

### ✅ Environment Variables

- [ ] **SECRET_KEY**: Generate a new secret key (never use the default)
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- [ ] **DEBUG**: Set to `False` in production
  ```bash
  DEBUG=False
  ```

- [ ] **DJANGO_ENV**: Set to `production`
  ```bash
  DJANGO_ENV=production
  ```

- [ ] **ALLOWED_HOSTS**: Set to your production domain(s)
  ```bash
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
  ```

- [ ] **CSRF_TRUSTED_ORIGINS**: Set to your production domain(s) with https://
  ```bash
  CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
  ```

### ✅ Database Configuration

Choose one of the following:

**Option 1: DATABASE_URL (Recommended)**
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

**Option 2: Individual Settings**
- [ ] **DB_NAME**: Database name
- [ ] **DB_USER**: Database user
- [ ] **DB_PASSWORD**: Database password (strong password)
- [ ] **DB_HOST**: Database host
- [ ] **DB_PORT**: Database port (default: 5432)

### ✅ Email Configuration

- [ ] **EMAIL_BACKEND**: Set to SMTP backend
  ```bash
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  ```

- [ ] **EMAIL_HOST**: SMTP server address
- [ ] **EMAIL_PORT**: SMTP port (usually 587 for TLS)
- [ ] **EMAIL_USE_TLS**: Set to `True`
- [ ] **EMAIL_HOST_USER**: Email account username
- [ ] **EMAIL_HOST_PASSWORD**: Email account password or app password
- [ ] **DEFAULT_FROM_EMAIL**: Sender email address
- [ ] **CONTACT_EMAIL**: Contact email address

### ✅ AWS S3 Configuration (Optional)

If using S3 for media storage:

- [ ] **USE_S3**: Set to `True`
- [ ] **AWS_ACCESS_KEY_ID**: AWS access key
- [ ] **AWS_SECRET_ACCESS_KEY**: AWS secret key
- [ ] **AWS_STORAGE_BUCKET_NAME**: S3 bucket name
- [ ] **AWS_S3_REGION_NAME**: AWS region (e.g., `us-east-1`)
- [ ] **AWS_S3_CUSTOM_DOMAIN**: Custom domain (optional)

### ✅ Security Settings

These are automatically enabled in production, but verify:

- [ ] **SECURE_SSL_REDIRECT**: `True` (redirects HTTP to HTTPS)
- [ ] **SESSION_COOKIE_SECURE**: `True` (cookies only over HTTPS)
- [ ] **CSRF_COOKIE_SECURE**: `True` (CSRF cookies only over HTTPS)
- [ ] **SECURE_HSTS_SECONDS**: `31536000` (1 year)
- [ ] **SECURE_HSTS_INCLUDE_SUBDOMAINS**: `True`
- [ ] **SECURE_HSTS_PRELOAD**: `True`
- [ ] **X_FRAME_OPTIONS**: `DENY`

## Deployment Platform Specific

### Railway

- [ ] Set `DJANGO_ENV=production`
- [ ] Set `DATABASE_URL` (auto-configured from PostgreSQL service)
- [ ] Set `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your Railway domain
- [ ] Set `DEBUG=False`
- [ ] Configure email settings
- [ ] Configure AWS S3 (if using)

### Render

- [ ] Set `DJANGO_ENV=production`
- [ ] Set `DATABASE_URL` (auto-configured from PostgreSQL service)
- [ ] Set `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your Render domain
- [ ] Set `DEBUG=False`
- [ ] Configure email settings
- [ ] Configure AWS S3 (if using)

### Other Platforms

- [ ] Set all required environment variables
- [ ] Ensure `DJANGO_ENV=production` is set
- [ ] Verify database connection
- [ ] Test email sending
- [ ] Test file uploads (if using S3)

## Post-Deployment Verification

- [ ] Application loads without errors
- [ ] HTTPS is working (SSL certificate valid)
- [ ] Database connections are working
- [ ] Static files are being served correctly
- [ ] Media files are accessible (if using S3)
- [ ] Email sending works (test password reset)
- [ ] User registration works
- [ ] User login works
- [ ] Admin panel is accessible
- [ ] No sensitive data in error messages
- [ ] Security headers are present (check with securityheaders.com)

## Security Best Practices

- [ ] Never commit `.env` file to version control
- [ ] Use strong, unique passwords for all services
- [ ] Rotate secrets regularly
- [ ] Use environment-specific secrets (don't reuse dev secrets)
- [ ] Enable database backups
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting (if applicable)
- [ ] Review and update dependencies regularly
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable database connection pooling
- [ ] Set up automated backups

## Monitoring

- [ ] Set up error tracking (e.g., Sentry)
- [ ] Configure logging levels
- [ ] Set up uptime monitoring
- [ ] Configure performance monitoring
- [ ] Set up database monitoring
- [ ] Configure alerting for critical errors

## Backup Strategy

- [ ] Database backups are configured
- [ ] Media file backups (if using S3, enable versioning)
- [ ] Backup retention policy is defined
- [ ] Backup restoration process is tested
- [ ] Backup schedule is documented

## Documentation

- [ ] Environment variables are documented in `.env.example`
- [ ] Deployment process is documented
- [ ] Rollback procedure is documented
- [ ] Emergency contact information is available
- [ ] Access credentials are stored securely (password manager)

## Testing

- [ ] All tests pass in production environment
- [ ] Load testing has been performed
- [ ] Security testing has been performed
- [ ] User acceptance testing is complete
- [ ] Performance benchmarks are met

---

**Important Notes:**

1. **Never** set `DEBUG=True` in production
2. **Always** use a unique `SECRET_KEY` in production
3. **Never** commit secrets to version control
4. **Always** use HTTPS in production
5. **Always** validate environment variables before deployment
6. **Always** test in a staging environment first

---

Last Updated: $(date)

















