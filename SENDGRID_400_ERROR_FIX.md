# Fix: SendGrid API 400 Bad Request Error

## Problem
SendGrid API returns `HTTP Error 400: Bad Request` when trying to send emails.

## Most Common Causes

### 1. **Sender Email Not Verified** (Most Likely!)

SendGrid requires you to verify the sender email address before sending emails.

**Fix:**
1. Go to [SendGrid Dashboard](https://app.sendgrid.com/)
2. Navigate to **Settings** → **Sender Authentication**
3. Click **Verify a Single Sender**
4. Fill in the form:
   - **From Email**: The email address you're using in `DEFAULT_FROM_EMAIL`
   - **From Name**: ASCAI Lazio
   - **Reply To**: Your reply-to email
   - Fill in all other required fields
5. Check your email inbox for the verification email
6. Click the verification link
7. Once verified, the email address is ready to use

**Important:** The email in `DEFAULT_FROM_EMAIL` must match the verified sender email!

### 2. **Invalid API Key**

Make sure your API key is:
- The **full key** (starts with `SG.` and is very long)
- Has **"Mail Send"** permissions
- Is correctly set in Railway as `SENDGRID_API_KEY`

### 3. **Email Format Issues**

The backend now handles:
- Email extraction from "Name <email>" format
- List vs string handling for recipients
- HTML and plain text content

### 4. **Missing Content**

The backend now ensures:
- At least one content type (HTML or plain text) is provided
- Content is not empty

## Quick Checklist

- [ ] Sender email is verified in SendGrid
- [ ] `DEFAULT_FROM_EMAIL` uses the verified email address
- [ ] `SENDGRID_API_KEY` is set correctly in Railway
- [ ] API key has "Mail Send" permissions
- [ ] Email address format is correct (just email, or "Name <email>")

## After Fixing

1. Redeploy your Railway service
2. Try sending a test email
3. Check logs for success message:
   ```
   INFO: Email sent successfully via SendGrid API to ['email@example.com']
   ```

## Test Email

You can test the email configuration using:
```bash
railway run python manage.py test_email your-email@gmail.com
```

## Common Error Messages

### "The from address does not match a verified Sender Identity"
→ **Fix:** Verify the sender email in SendGrid Dashboard

### "Permission denied"
→ **Fix:** Check API key has "Mail Send" permissions

### "Invalid API key"
→ **Fix:** Regenerate API key and update `SENDGRID_API_KEY` in Railway

## Updated Backend Features

The SendGrid backend now:
- ✅ Extracts email from "Name <email>" format
- ✅ Handles list/string recipients properly
- ✅ Ensures at least one content type is provided
- ✅ Provides better error logging with details
- ✅ Handles empty content gracefully

## Need More Help?

Check the SendGrid Activity Feed:
1. Go to SendGrid Dashboard
2. Navigate to **Activity**
3. Look for failed emails
4. Click on a failed email to see detailed error message

This will show exactly what SendGrid rejected!

