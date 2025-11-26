# Quick Fix: SendGrid SMTP Timeout on Railway

## Problem
Railway is blocking SMTP connections, causing timeouts when sending emails.

## Solution: Use SendGrid API Instead of SMTP

The SendGrid API backend is already implemented and will bypass Railway's SMTP blocking.

### Step 1: Get Your SendGrid API Key

1. Go to [SendGrid Dashboard](https://app.sendgrid.com/)
2. Navigate to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name it: `ASCAI Lazio Production`
5. Give it **Full Access** or **Restricted Access** with "Mail Send" permission
6. **Copy the API key** (starts with `SG.` - you won't see it again!)

### Step 2: Add to Railway Environment Variables

1. Go to Railway → Your Service → **Variables**
2. Add/Update this variable:

```bash
SENDGRID_API_KEY=SG.your-full-api-key-here
```

**Important:** Replace `SG.your-full-api-key-here` with your actual SendGrid API key.

### Step 3: Verify Sender Email

Make sure `DEFAULT_FROM_EMAIL` uses an email you've verified in SendGrid:

1. Go to SendGrid Dashboard → **Settings** → **Sender Authentication**
2. Verify a single sender email (e.g., `noreply@ascailazio.org`)
3. Set in Railway:

```bash
DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>
CONTACT_EMAIL=info@ascailazio.org
```

### Step 4: Remove/Disable SMTP Variables (Optional)

You can remove these since we're using the API:
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`

**Or** just leave them - the system will automatically use SendGrid API if `SENDGRID_API_KEY` is set.

### Step 5: Redeploy

Railway will automatically redeploy when you save variables. The email backend will automatically switch to SendGrid API.

## How It Works

- ✅ If `SENDGRID_API_KEY` is set → Uses SendGrid API (bypasses SMTP blocking)
- ❌ If `SENDGRID_API_KEY` is NOT set → Falls back to SMTP (may timeout on Railway)

## Verify It's Working

After redeploying, check the logs. You should see:

```
INFO: SendGrid API backend initialized successfully (bypasses SMTP blocking)
```

Instead of:
```
ERROR: Failed to send email... timed out
```

## Test Email

After configuration, signup should send emails successfully without timeouts.

## Why This Works

- SendGrid API uses HTTP/HTTPS (port 443) - not blocked by Railway
- SMTP uses port 587/465 - often blocked by Railway
- API is faster and more reliable than SMTP
- This is the production-standard approach

---

**That's it!** Just set `SENDGRID_API_KEY` and emails will work. 🎉

