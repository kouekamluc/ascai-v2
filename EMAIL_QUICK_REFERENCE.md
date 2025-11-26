# Email Configuration Quick Reference

## Quick Setup Steps

1. **Choose a provider** (SendGrid recommended)
2. **Get credentials** from provider dashboard
3. **Set environment variables** in Railway/local `.env`
4. **Test** using: `python manage.py test_email your-email@example.com`

## Environment Variables Template

### SendGrid (Recommended)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-api-key-here
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

### Mailgun
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@ascailazio.org
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

### Gmail (Testing Only)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <your-email@gmail.com>
CONTACT_EMAIL=info@ascailazio.org
```

## Testing Commands

```bash
# Test email sending
python manage.py test_email your-email@example.com

# Test with custom subject
python manage.py test_email your-email@example.com --subject "My Test Subject"
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Authentication failed | Check credentials, for Gmail use App Password |
| Connection timeout | Verify SMTP host/port, check firewall |
| Emails in spam | Verify domain, add SPF/DKIM records |
| Rate limit exceeded | Check provider limits, upgrade plan |

## Full Documentation

See [EMAIL_IMPLEMENTATION_GUIDE.md](EMAIL_IMPLEMENTATION_GUIDE.md) for complete setup instructions.

