# Railway SMTP Connection Timeout - Alternative Solutions

## Problem

Even with correct SendGrid configuration, Railway is timing out when trying to connect to SMTP servers. This suggests Railway may be blocking outbound SMTP connections.

## Solution 1: Use SendGrid API (Recommended)

Instead of SMTP, use SendGrid's HTTP API which is more reliable and not blocked:

### Install SendGrid Python Library

Add to `requirements.txt`:
```
sendgrid>=6.10.0
```

### Create SendGrid Email Backend

Create `apps/core/email_backends.py`:

```python
"""
Custom email backend using SendGrid API instead of SMTP.
This bypasses Railway's SMTP blocking issues.
"""
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

logger = logging.getLogger(__name__)


class SendGridBackend(BaseEmailBackend):
    """
    SendGrid API email backend to bypass SMTP blocking.
    """
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError('SENDGRID_API_KEY setting is required')
    
    def send_messages(self, email_messages):
        """
        Send messages using SendGrid API.
        """
        if not email_messages:
            return 0
        
        sg = SendGridAPIClient(self.api_key)
        sent_count = 0
        
        for message in email_messages:
            try:
                mail = Mail(
                    from_email=message.from_email,
                    to_emails=message.to,
                    subject=message.subject,
                    html_content=message.body if message.content_subtype == 'html' else None,
                    plain_text_content=message.body if message.content_subtype == 'plain' else None,
                )
                
                # Add CC and BCC if present
                if message.cc:
                    mail.add_cc(message.cc)
                if message.bcc:
                    mail.add_bcc(message.bcc)
                
                # Add reply-to if present
                if message.reply_to:
                    mail.reply_to = message.reply_to[0]
                
                response = sg.send(mail)
                
                if response.status_code in [200, 202]:
                    sent_count += 1
                    logger.info(f"Email sent successfully via SendGrid API: {message.to}")
                else:
                    logger.error(f"SendGrid API error: {response.status_code} - {response.body}")
                    if not self.fail_silently:
                        raise Exception(f"SendGrid API error: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Failed to send email via SendGrid API: {str(e)}")
                if not self.fail_silently:
                    raise
        
        return sent_count
```

### Update Settings

In `config/settings/base.py`, add:

```python
# SendGrid API Configuration (alternative to SMTP)
SENDGRID_API_KEY = config('SENDGRID_API_KEY', default='')

# Use SendGrid API backend if API key is set, otherwise use SMTP
if SENDGRID_API_KEY:
    EMAIL_BACKEND = 'apps.core.email_backends.SendGridBackend'
else:
    EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
```

### Update Railway Variables

Remove SMTP variables, add:
```bash
SENDGRID_API_KEY=SG.your-full-api-key-here
DEFAULT_FROM_EMAIL=ASCAI Lazio <your-verified-email@example.com>
CONTACT_EMAIL=info@ascailazio.org
```

## Solution 2: Increase Timeout and Try Port 465

If you want to keep using SMTP, try:

### Update Railway Variables:
```bash
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_TIMEOUT=30
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-api-key
```

## Solution 3: Use Mailgun (Alternative Provider)

Mailgun might work better with Railway:

1. Sign up at https://mailgun.com (free tier: 5,000 emails/month)
2. Get SMTP credentials from dashboard
3. Update Railway:
```bash
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
```

## Solution 4: Check Railway Network Settings

1. Railway → Your Service → Settings
2. Check if there are network/firewall restrictions
3. Verify outbound connections are allowed
4. Some Railway regions may block SMTP ports

## Recommended: Use SendGrid API (Solution 1)

The API approach is:
- ✅ More reliable
- ✅ Not blocked by firewalls
- ✅ Faster than SMTP
- ✅ Better error handling
- ✅ Designed for production use

This is what most production apps use instead of SMTP.

