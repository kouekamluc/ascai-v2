# Gmail Authentication Error Troubleshooting

## Error: "Username and Password not accepted" (535)

If you're getting this error, follow these steps:

### ✅ Step 1: Verify Email Address is Complete

**Fixed:** Your email was `kouekamkamgouluc@gmail` (missing `.com`)
**Now:** `kouekamkamgouluc@gmail.com` ✓

Make sure your `.env.example` has:
```bash
EMAIL_HOST_USER=kouekamkamgouluc@gmail.com
```

### ✅ Step 2: Verify App Password Format

Your App Password should be:
- **16 characters** (no spaces)
- Example: `qcwbngtyhcufpiby` ✓ (looks correct)

**Common mistakes:**
- ❌ `qcwb ngty hcuf piby` (with spaces)
- ❌ `qcwb-ngty-hcuf-piby` (with dashes)
- ✅ `qcwbngtyhcufpiby` (no spaces, 16 chars)

### ✅ Step 3: Regenerate App Password

The App Password might be expired or revoked. Generate a new one:

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in with your Gmail account
3. **Delete the old App Password** (if it exists)
4. **Create a new App Password:**
   - App: "Mail" or "Other (Custom name)" → "ASCAI Lazio Django"
   - Device: "Other (Custom name)" → "Django"
   - Click "Generate"
5. **Copy the 16-character password** (remove ALL spaces!)
6. **Update `.env.example`:**
   ```bash
   EMAIL_HOST_PASSWORD=your-new-16-char-password-no-spaces
   ```

### ✅ Step 4: Verify 2FA is Enabled

App Passwords only work if 2-Factor Authentication is enabled:

1. Go to: https://myaccount.google.com/security
2. Check that **"2-Step Verification"** is **ON**
3. If not, enable it first, then generate App Password

### ✅ Step 5: Check Account Type

- **Personal Gmail** ✅ - App Passwords work
- **Google Workspace** ⚠️ - May need admin approval
- **School/Organization** ⚠️ - May be restricted

### ✅ Step 6: Test Again

After fixing the issues above:

```bash
python manage.py test_email your-email@gmail.com
```

## Quick Fix Checklist

- [ ] Email address is complete: `yourname@gmail.com` (not missing `.com`)
- [ ] App Password is 16 characters with NO spaces
- [ ] 2FA is enabled on Google account
- [ ] App Password was generated recently (not expired)
- [ ] Updated `.env.example` with correct credentials
- [ ] Restarted Django server (if running)

## Still Not Working?

1. **Try generating a completely new App Password**
2. **Double-check for hidden spaces** in the password
3. **Verify the email address** matches your Gmail account exactly
4. **Check Gmail security settings** - make sure "Less secure app access" is not blocking (though App Passwords should bypass this)
5. **Try a different email provider** (SendGrid, Mailgun) for testing

## Alternative: Use SendGrid (Easier)

If Gmail continues to give issues, SendGrid is often easier:

1. Sign up at https://sendgrid.com (free tier: 100 emails/day)
2. Get API key from dashboard
3. Update `.env.example`:
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key-here
   ```

