# Gmail SMTP Setup Guide for ASCAI Lazio

This guide will walk you through setting up Gmail SMTP to send emails from your Django application.

## Prerequisites

- A Gmail account
- Access to your Google Account settings

## Step-by-Step Instructions

### Step 1: Enable 2-Factor Authentication

Gmail requires 2-Factor Authentication (2FA) to generate App Passwords. If you don't have 2FA enabled:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Sign in with your Gmail account
3. Under **"Signing in to Google"**, find **"2-Step Verification"**
4. Click **"Get started"** (or **"Turn on"** if you see it)
5. Follow the prompts to set up 2FA:
   - Choose your verification method (phone number, authenticator app, etc.)
   - Complete the verification process
6. Once enabled, you'll see **"2-Step Verification"** is **ON**

### Step 2: Generate an App Password

> **Quick Summary:** You need to create an App Password (not your regular Gmail password). Just enter any name when prompted and copy the 16-character password that Google generates.
> 
> **⚠️ CRITICAL:** When Google shows you the password like `abcd efgh ijkl mnop` (with spaces), you **MUST REMOVE ALL SPACES** when using it. Use it as `abcdefghijklmnop` (16 characters, no spaces)!

**Method 1: Direct Link (Easiest)**
1. Go directly to: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. You may be asked to sign in again

**Method 2: Navigation Path**
1. Go to [Google Account](https://myaccount.google.com)
2. Click **"Security"** in the left sidebar (or top menu)
3. Under **"Signing in to Google"**, find **"2-Step Verification"**
4. Click on **"2-Step Verification"**
5. Scroll down to find **"App passwords"** (near the bottom of the page)
6. Click **"App passwords"**

**Creating the App Password:**

Once you're on the App Passwords page, you'll see a form. Here's what to do:

**Option A: If you see dropdown menus:**
1. **"Select app"** dropdown → Choose **"Mail"** (or **"Other (Custom name)"** if Mail isn't listed)
2. **"Select device"** dropdown → Choose **"Other (Custom name)"**
3. Enter a custom name: **"ASCAI Lazio Django"** (or any name you prefer)
4. Click **"Generate"**

**Option B: If you only see a text field for "App name" or "Name":**
1. Simply enter a name like: **"ASCAI Lazio Django"** or **"Django Email"**
2. Click **"Generate"** or **"Create"**

**Option C: If the interface looks different:**
- Look for a button that says **"Create"**, **"Generate"**, or **"Add"**
- You might see a form with just one field asking for a name
- Enter: **"ASCAI Lazio Django"**
- Click the button to create it

**After Generating:**
7. **IMPORTANT**: Google will show you a 16-character password
   - It will look like: `abcd efgh ijkl mnop` (with spaces, grouped in 4s)
   - **Copy this password immediately** - you won't be able to see it again!
   - **⚠️ REMOVE ALL SPACES when using it** - The password should be 16 characters with NO spaces
   - Example: Google shows `abcd efgh ijkl mnop` → Use `abcdefghijklmnop` (no spaces!)

**If you can't find App Passwords:**
- Make sure 2-Step Verification is **ON** (Step 1)
- Some Google Workspace accounts might not have App Passwords available
- Try the direct link: https://myaccount.google.com/apppasswords
- If still not visible, your account type might not support App Passwords

**What the Interface Might Look Like:**

The App Passwords page can show different interfaces:

- **Version 1 (Older):** Two dropdowns for "Select app" and "Select device" → Just choose "Other (Custom name)" for both
- **Version 2 (Newer):** Single text field for "App name" → Just type any name
- **Version 3 (Simplified):** Single text field for "Name" → Just type any name

**Important:** The exact interface doesn't matter - just:
1. Enter any name you want (e.g., "ASCAI Lazio Django")
2. Click Generate/Create
3. Copy the 16-character password shown

### Step 3: Configure Your Django Settings

Now you have everything you need:

- **EMAIL_HOST_USER**: Your Gmail email address (e.g., `yourname@gmail.com`)
- **EMAIL_HOST_PASSWORD**: The 16-character App Password you just generated

### Step 4: Set Environment Variables

#### For Local Development (.env file):

Create or update your `.env` file in the project root:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=yourname@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=ASCAI Lazio <yourname@gmail.com>
CONTACT_EMAIL=info@ascailazio.org
```

**Replace:**
- `yourname@gmail.com` with your actual Gmail address
- `abcdefghijklmnop` with your actual 16-character App Password **WITHOUT SPACES**
  - If Google shows: `abcd efgh ijkl mnop`
  - Use in config: `abcdefghijklmnop` (remove all spaces!)

#### For Railway (Production):

1. Go to your Railway project dashboard
2. Click on your project
3. Go to the **"Variables"** tab
4. Add these variables:

```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=yourname@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=ASCAI Lazio <yourname@gmail.com>
CONTACT_EMAIL=info@ascailazio.org
```

**⚠️ Important:** When setting `EMAIL_HOST_PASSWORD` in Railway, use the App Password **WITHOUT SPACES**:
- Google shows: `abcd efgh ijkl mnop` (with spaces)
- Use in Railway: `abcdefghijklmnop` (no spaces!)

### Step 5: Test Your Configuration

Test that everything works:

```bash
python manage.py test_email your-email@example.com
```

Replace `your-email@example.com` with an email address where you want to receive the test email.

## Important Notes

### Gmail Limitations

⚠️ **Daily Sending Limits:**
- **Free Gmail accounts**: 500 emails per day
- If you exceed this limit, Gmail will temporarily block sending
- For production with high volume, consider using SendGrid or Mailgun instead

### Security Best Practices

✅ **DO:**
- Use App Passwords (not your regular Gmail password)
- Keep your App Password secret
- Store it in environment variables (never commit to code)
- Use a dedicated Gmail account for your application if possible

❌ **DON'T:**
- Use your regular Gmail password
- Hardcode credentials in your code
- Share your App Password publicly
- Commit credentials to version control

### Troubleshooting

#### Can't find "Mail" or "App" dropdown options
**If you only see a text field:**
- Just enter a name like "ASCAI Lazio Django" in the text field
- Click "Generate" or "Create"
- The app type doesn't matter - any App Password will work for SMTP

**If you see a different interface:**
- Look for any button that says "Create", "Generate", "Add", or "New"
- Enter any name you want (e.g., "Django Email", "ASCAI App")
- The important part is getting the 16-character password, not the name

**If App Passwords option is missing:**
- Verify 2-Step Verification is enabled (go back to Step 1)
- Some Google Workspace accounts have App Passwords in a different location
- Try: Google Admin Console → Security → App Passwords (for Workspace accounts)
- If using a personal Gmail account, App Passwords should be available

#### "Username and Password not accepted"
- Make sure you're using the **App Password**, not your regular Gmail password
- **⚠️ REMOVE ALL SPACES from the App Password** - Google shows it with spaces like `abcd efgh ijkl mnop`, but you must use it as `abcdefghijklmnop` (no spaces!)
- Verify 2-Factor Authentication is enabled
- Generate a new App Password if needed
- Double-check you copied all 16 characters correctly (without spaces)

#### "Connection refused" or "Connection timeout"
- Check your firewall isn't blocking port 587
- Verify `EMAIL_HOST=smtp.gmail.com` and `EMAIL_PORT=587`
- Try port 465 with SSL (requires `EMAIL_USE_TLS=False` and `EMAIL_USE_SSL=True`)

#### "Daily sending quota exceeded"
- You've hit Gmail's 500 emails/day limit
- Wait 24 hours or switch to a professional email service

#### "Less secure app access" error
- This shouldn't appear if you're using App Passwords correctly
- If it does, make sure you generated an App Password (not using regular password)

## Alternative: Using Port 465 with SSL

If port 587 doesn't work, you can try port 465 with SSL:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=yourname@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=ASCAI Lazio <yourname@gmail.com>
```

**Note:** `EMAIL_USE_SSL` is already supported in your settings. Just set it to `True` when using port 465.

## Quick Reference

| Setting | Value |
|---------|-------|
| **EMAIL_HOST_USER** | Your Gmail address (e.g., `yourname@gmail.com`) |
| **EMAIL_HOST_PASSWORD** | 16-character App Password from Google |
| **EMAIL_HOST** | `smtp.gmail.com` |
| **EMAIL_PORT** | `587` (TLS) or `465` (SSL) |
| **EMAIL_USE_TLS** | `True` (for port 587) |

## Next Steps

1. ✅ Enable 2-Factor Authentication
2. ✅ Generate App Password
3. ✅ Set environment variables
4. ✅ Test email sending
5. ✅ Test user registration email flow
6. ✅ Test password reset email flow

## Need Help?

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all environment variables are set correctly
3. Test with the management command: `python manage.py test_email your-email@example.com`
4. Check Django logs for error messages
5. Review the full [EMAIL_IMPLEMENTATION_GUIDE.md](EMAIL_IMPLEMENTATION_GUIDE.md)

---

**Remember**: Gmail is great for testing and small projects, but for production with high email volume, consider upgrading to SendGrid or Mailgun for better reliability and higher limits.

