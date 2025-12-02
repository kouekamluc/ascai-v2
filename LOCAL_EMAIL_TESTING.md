# Local Email Testing Guide

This guide helps you test email sending locally on your development machine.

## Quick Test (Console Backend - Default)

The default development setup uses the **console backend**, which prints emails to your terminal instead of sending them. This is perfect for development!

**Test it:**
```bash
python manage.py test_email your-email@example.com
```

You'll see the email content printed in your terminal. This confirms the email system is working.

## Testing Real Email Sending (SMTP)

To test sending **actual emails** via SMTP, you need to:

### Option 1: Create a `.env` file (Recommended)

Create a `.env` file in your project root with your email credentials:

```bash
# Switch to SMTP backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Gmail SMTP (for testing)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <your-email@gmail.com>
CONTACT_EMAIL=info@ascailazio.org
```

**For Gmail:**
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. **Remove ALL SPACES** from the App Password when pasting it
4. Example: Google shows `abcd efgh ijkl mnop` → Use `abcdefghijklmnop`

### Option 2: Set Environment Variables Temporarily

You can also set environment variables in your current PowerShell session:

```powershell
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST="smtp.gmail.com"
$env:EMAIL_PORT="587"
$env:EMAIL_USE_TLS="True"
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-app-password"
$env:DEFAULT_FROM_EMAIL="ASCAI Lazio <your-email@gmail.com>"
```

Then run:
```bash
python manage.py test_email your-email@example.com
```

### Option 3: Use SendGrid or Mailgun

For production-like testing, use SendGrid or Mailgun:

**SendGrid:**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
```

**Mailgun:**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.com
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
```

## Testing Steps

1. **Configure your email settings** (using one of the options above)
2. **Run the test command:**
   ```bash
   python manage.py test_email your-real-email@gmail.com
   ```
3. **Check the output:**
   - If successful, you'll see: "Successfully sent test email"
   - Check your inbox (and spam folder) for the email
4. **If it fails:**
   - Check the error message
   - Verify your credentials are correct
   - For Gmail: Make sure you're using an App Password (not regular password)
   - Check that 2FA is enabled on your Gmail account

## Switching Back to Console Backend

After testing, you can switch back to console backend by:

1. **Remove EMAIL_BACKEND from .env** (or set it to console backend)
2. **Or delete the .env file** (development.py defaults to console backend)

## Troubleshooting

### "Authentication failed"
- **Gmail:** Make sure you're using an App Password, not your regular password
- **Gmail:** Remove ALL spaces from the App Password
- Verify your email and password are correct

### "Connection timeout"
- Check your internet connection
- Verify SMTP host and port are correct
- Check if firewall is blocking port 587

### "Email not received"
- Check spam/junk folder
- Verify the recipient email address is correct
- Some email providers have delays (wait a few minutes)

## Next Steps

- See `EMAIL_IMPLEMENTATION_GUIDE.md` for detailed provider setup
- See `GMAIL_SETUP_GUIDE.md` for Gmail-specific instructions
- See `PRODUCTION_EMAIL_SETUP.md` for production deployment












