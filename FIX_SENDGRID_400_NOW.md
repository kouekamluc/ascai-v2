# URGENT: Fix SendGrid 400 Bad Request Error

## Current Status
✅ SendGrid API backend is configured  
❌ Getting 400 Bad Request when sending emails  
❌ Sender email is **most likely NOT verified** in SendGrid

## The Problem

SendGrid returns 400 Bad Request when:
1. **Sender email is not verified** (MOST COMMON - 95% of cases)
2. Invalid API key
3. API key missing permissions
4. Email format issues (already fixed in code)

## Immediate Fix Required

### Step 1: Verify Sender Email in SendGrid (CRITICAL!)

1. **Go to SendGrid Dashboard**
   - Visit: https://app.sendgrid.com/
   - Log in with your SendGrid account

2. **Navigate to Sender Authentication**
   - Click **Settings** (left sidebar)
   - Click **Sender Authentication**
   - Click **Verify a Single Sender**

3. **Fill in the Form**
   - **From Email**: Use the EXACT email from your `DEFAULT_FROM_EMAIL` setting
     - Example: If `DEFAULT_FROM_EMAIL=ASCAI Lazio <noreply@ascailazio.org>`, use `noreply@ascailazio.org`
   - **From Name**: `ASCAI Lazio`
   - **Reply To**: Your reply-to email
   - Fill in all other required fields (Address, City, State, etc.)

4. **Verify the Email**
   - SendGrid will send a verification email
   - Check your inbox (and spam folder)
   - Click the verification link in the email
   - Wait for "Verification Complete" message

5. **Important:** The email address MUST match exactly what's in `DEFAULT_FROM_EMAIL`!

### Step 2: Check Your Railway Variables

Make sure these are set correctly:

```bash
SENDGRID_API_KEY=SG.your-full-api-key-here
DEFAULT_FROM_EMAIL=ASCAI Lazio <your-verified-email@example.com>
```

**Replace:**
- `SG.your-full-api-key-here` → Your actual SendGrid API key
- `your-verified-email@example.com` → The email you just verified in Step 1

### Step 3: Verify API Key Has Permissions

1. Go to SendGrid Dashboard → **Settings** → **API Keys**
2. Find your API key
3. Make sure it has **"Mail Send"** permission enabled
4. If not, create a new API key with "Mail Send" permission

### Step 4: Redeploy

1. Save all Railway variables
2. Railway will auto-redeploy
3. Wait for deployment to complete

### Step 5: Test

1. Try signing up a new user
2. Check Railway logs - you should see:
   ```
   INFO: Email sent successfully via SendGrid API to ['email@example.com']
   ```

## How to Check Current Settings

In Railway, check your variables:
- `DEFAULT_FROM_EMAIL` - This email MUST be verified in SendGrid
- `SENDGRID_API_KEY` - Must be a valid API key with Mail Send permission

## Still Getting 400 Error?

After verifying the sender email, if you still get 400:

1. **Check SendGrid Activity Feed**
   - Go to SendGrid Dashboard → **Activity**
   - Look for failed emails
   - Click on a failed email to see detailed error message

2. **Updated Error Logging**
   - The updated backend code will now log detailed error messages
   - Check Railway logs after next deployment for specific error details

3. **Common Issues:**
   - Email address mismatch (from_email doesn't match verified sender)
   - API key missing Mail Send permission
   - Invalid API key format

## Quick Checklist

- [ ] Sender email verified in SendGrid Dashboard
- [ ] `DEFAULT_FROM_EMAIL` uses the verified email address
- [ ] API key has "Mail Send" permissions
- [ ] `SENDGRID_API_KEY` is set correctly in Railway
- [ ] Service redeployed after changes

## What Changed in Code

The backend now:
- ✅ Extracts email from "Name <email>" format
- ✅ Provides better error logging
- ✅ Handles content properly
- ✅ Shows detailed error messages

**But the #1 issue is still: Unverified sender email!**

---

**Next Steps:** Verify your sender email in SendGrid, then test again. This fixes 95% of 400 errors.

