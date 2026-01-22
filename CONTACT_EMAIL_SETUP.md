# Contact Form Email Setup Guide

## ✅ Good News!

Your contact form is **already configured** to send emails! You can use **any email address you want** - it doesn't have to be `info@ascai.org`.

## 📋 Quick Overview

When someone submits the contact form on your website, the system will:
1. Save the submission to the database
2. Send an email to the address you configure (see below)
3. Show a success message to the user

The email will include:
- Sender's name
- Sender's email address
- Subject
- Message content
- Submission timestamp

## 🎯 Important: You Can Use ANY Email Address!

**You have 3 options for where to receive contact form emails:**

1. **Use your existing Gmail** (easiest - no setup needed)
   - Example: `yourname@gmail.com`
   - Just set `CONTACT_EMAIL=yourname@gmail.com` in Railway

2. **Use any email you already have**
   - Example: `contact@yourdomain.com`, `hello@company.com`, etc.
   - Just set `CONTACT_EMAIL=your-email@example.com` in Railway

3. **Set up `info@ascai.org`** (only if you want this specific address)
   - Requires email hosting for the `ascai.org` domain
   - See "Setting Up info@ascai.org" section below if you want this

**For now, just use an email address you already have!** You can always change it later.

## 🚀 Setup Options (Choose One)

You have **3 options** to send emails. Choose the one that works best for you:

### Option 1: Brevo (Recommended - Easiest & Most Reliable)

**Why Brevo?**
- ✅ Free tier: 300 emails/day
- ✅ Works reliably on Railway (no SMTP blocking)
- ✅ Easy setup (just an API key)
- ✅ Professional email delivery

**Setup Steps:**

1. **Sign up for Brevo:**
   - Go to https://www.brevo.com/
   - Create a free account
   - Verify your email address

2. **Get your API Key:**
   - Log in to Brevo
   - Go to **Settings** → **SMTP & API** → **API Keys**
   - Click **"Generate a new API key"**
   - Name it: "ASCAI Lazio Contact Form"
   - Copy the API key (it will look like: `xkeysib-xxxxxxxxxxxxx-xxxxxxxxxxxxx`)

3. **Set Environment Variables:**

   **For Railway (Production):**
   - Go to Railway → Your Project → Variables tab
   - Add these variables:
     ```
     BREVO_API_KEY=xkeysib-your-api-key-here
     CONTACT_EMAIL=your-email@gmail.com
     DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
     ```
     **Replace `your-email@gmail.com` with the email address where you want to receive contact form submissions!**

   **For Local Development (.env file):**
   ```bash
   BREVO_API_KEY=xkeysib-your-api-key-here
   CONTACT_EMAIL=your-email@gmail.com
   DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
   ```

4. **Verify sender email in Brevo:**
   - Go to Brevo → **Settings** → **Senders & IP**
   - Click **"Add a sender"**
   - Add the email address you're using (e.g., `your-email@gmail.com`)
   - Verify the email address (Brevo will send a verification email)

5. **Test it:**
   ```bash
   python manage.py test_email your-email@gmail.com
   ```
   (Replace with the email address you set in `CONTACT_EMAIL`)

---

### Option 2: SendGrid (Alternative API Service)

**Why SendGrid?**
- ✅ Free tier: 100 emails/day
- ✅ Works reliably on Railway
- ✅ Professional email delivery

**Setup Steps:**

1. **Sign up for SendGrid:**
   - Go to https://sendgrid.com/
   - Create a free account
   - Verify your email address

2. **Get your API Key:**
   - Go to **Settings** → **API Keys**
   - Click **"Create API Key"**
   - Name it: "ASCAI Lazio Contact Form"
   - Choose **"Full Access"** or **"Mail Send"** permissions
   - Copy the API key (it will look like: `SG.xxxxxxxxxxxxx.xxxxxxxxxxxxx`)

3. **Set Environment Variables:**

   **For Railway (Production):**
   ```
   SENDGRID_API_KEY=SG.your-api-key-here
   CONTACT_EMAIL=your-email@gmail.com
   DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
   ```
   **Replace `your-email@gmail.com` with the email address where you want to receive contact form submissions!**

   **For Local Development (.env file):**
   ```bash
   SENDGRID_API_KEY=SG.your-api-key-here
   CONTACT_EMAIL=your-email@gmail.com
   DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
   ```

4. **Verify sender email in SendGrid:**
   - Go to **Settings** → **Sender Authentication**
   - Add the email address you're using (e.g., `your-email@gmail.com`)
   - Complete the verification process

5. **Test it:**
   ```bash
   python manage.py test_email your-email@gmail.com
   ```
   (Replace with the email address you set in `CONTACT_EMAIL`)

---

### Option 3: Gmail SMTP (Simple but Limited)

**Why Gmail?**
- ✅ Free and easy if you already have Gmail
- ⚠️ Limited to 500 emails/day
- ⚠️ May have issues on Railway (SMTP blocking)

**Setup Steps:**

1. **Enable 2-Factor Authentication:**
   - Go to https://myaccount.google.com/security
   - Enable **"2-Step Verification"**

2. **Generate App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select **"Mail"** and **"Other (Custom name)"**
   - Name it: "ASCAI Lazio Contact Form"
   - Click **"Generate"**
   - **Copy the 16-character password** (remove ALL spaces!)
     - Google shows: `abcd efgh ijkl mnop`
     - Use: `abcdefghijklmnop` (no spaces!)

3. **Set Environment Variables:**

   **For Railway (Production):**
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   CONTACT_EMAIL=your-email@gmail.com
   DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
   ```
   **Note:** `EMAIL_HOST_USER` is the Gmail account used to SEND emails, and `CONTACT_EMAIL` is where you RECEIVE contact form submissions. They can be the same or different!

   **For Local Development (.env file):**
   ```bash
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   CONTACT_EMAIL=your-email@gmail.com
   DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
   ```

4. **Test it:**
   ```bash
   python manage.py test_email your-email@gmail.com
   ```
   (Replace with the email address you set in `CONTACT_EMAIL`)

---

## 🧪 Testing Your Setup

### Step 1: Test Email Sending

Run this command to test if emails are working (replace with your email):

```bash
python manage.py test_email your-email@gmail.com
```

**Expected Output:**
```
✅ Successfully sent test email to your-email@gmail.com
```

**If it fails:**
- Check the error message
- Verify your API key/credentials are correct
- Make sure `CONTACT_EMAIL=your-email@gmail.com` is set (with your actual email)
- Check Railway logs for detailed error messages

### Step 2: Test Contact Form

1. Go to your website's contact page
2. Fill out the contact form
3. Submit it
4. Check your email inbox (the address you set in `CONTACT_EMAIL`)
5. Check spam folder if you don't see it

**What the email will look like:**
```
Subject: ASCAI Lazio Contact: [Subject from form]

New contact form submission from ASCAI Lazio website:

From: [Name]
Email: [Email]
Phone: [Phone if provided]
Subject: [Subject]

Message:
[Message content]

---
This message was sent from the ASCAI Lazio contact form.
Submitted on: 2024-01-21 10:30:00
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Environment variables are set in Railway (or `.env` for local)
- [ ] `CONTACT_EMAIL=your-email@gmail.com` is configured (with your actual email)
- [ ] `DEFAULT_FROM_EMAIL` is set correctly
- [ ] Test email command works: `python manage.py test_email your-email@gmail.com`
- [ ] You received the test email at your configured email address
- [ ] Contact form submission sends email to your configured email address
- [ ] Emails appear in inbox (not spam)

---

## 🔍 Troubleshooting

### "Email not received"

**Check 1: Verify Environment Variables**
- Go to Railway → Variables tab
- Make sure `CONTACT_EMAIL=your-email@gmail.com` is set (with your actual email address)
- Verify your email backend credentials (Brevo API key, SendGrid API key, or Gmail credentials)

**Check 2: Check Railway Logs**
- Go to Railway → Deployments → Latest → Logs
- Look for email-related errors
- Look for "Failed to send contact email" messages

**Check 3: Test Email Command**
```bash
python manage.py test_email info@ascai.org
```
- If this fails, your email backend isn't configured correctly
- Fix the backend configuration first

**Check 4: Check Spam Folder**
- Emails might be going to spam
- Mark as "Not Spam" if found
- Add `info@ascai.org` to your contacts

### "Authentication failed" (Gmail)

- Make sure you're using an **App Password**, not your regular Gmail password
- **Remove ALL spaces** from the App Password
- Verify 2-Factor Authentication is enabled
- Try generating a new App Password

### "API key invalid" (Brevo/SendGrid)

- Verify you copied the entire API key
- Check if the API key is active in your Brevo/SendGrid dashboard
- Make sure there are no extra spaces or characters
- Try generating a new API key

### "Connection timeout" (SMTP)

- Check your internet connection
- Verify SMTP host and port are correct
- Railway may block SMTP connections (use Brevo or SendGrid instead)

---

## 📝 Quick Reference

### Required Environment Variables

**For Brevo:**
```bash
BREVO_API_KEY=your-api-key
CONTACT_EMAIL=your-email@gmail.com
DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
```
**Replace `your-email@gmail.com` with the email where you want to receive contact form submissions!**

**For SendGrid:**
```bash
SENDGRID_API_KEY=your-api-key
CONTACT_EMAIL=your-email@gmail.com
DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
```

**For Gmail SMTP:**
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CONTACT_EMAIL=your-email@gmail.com
DEFAULT_FROM_EMAIL=ASCAI Associazione <your-email@gmail.com>
```

### Test Command
```bash
python manage.py test_email your-email@gmail.com
```
(Replace with your actual email address)

---

## 🎯 Recommendation

**For Production (Railway):** Use **Brevo** (Option 1)
- Most reliable on Railway
- Free tier is sufficient for contact forms
- Easy setup with just an API key
- Professional email delivery

**For Local Development:** Use **Console Backend** (default)
- Emails print to terminal (no setup needed)
- Perfect for development and testing

---

## 📚 Additional Resources

- [Gmail Setup Guide](GMAIL_SETUP_GUIDE.md) - Detailed Gmail configuration
- [Production Email Setup](PRODUCTION_EMAIL_SETUP.md) - Full production email guide
- [Email Implementation Guide](EMAIL_IMPLEMENTATION_GUIDE.md) - Complete email system documentation

---

---

## 📧 Setting Up info@ascai.org (Optional)

**You only need this if you specifically want to use `info@ascai.org` as your contact email.**

If you want to use `info@ascai.org`, you have a few options:

### Option A: Email Forwarding (Easiest)
1. Set up email forwarding with your domain registrar or hosting provider
2. Forward `info@ascai.org` → `your-email@gmail.com`
3. Set `CONTACT_EMAIL=info@ascai.org` in Railway
4. Emails sent to `info@ascai.org` will forward to your Gmail

### Option B: Professional Email Hosting
1. Sign up for email hosting (Google Workspace, Microsoft 365, Zoho, etc.)
2. Create the `info@ascai.org` mailbox
3. Set `CONTACT_EMAIL=info@ascai.org` in Railway
4. Access emails through your email hosting provider

### Option C: Use Your Existing Email (Recommended for Now)
- Just use your existing Gmail or any email you have
- Set `CONTACT_EMAIL=your-email@gmail.com` in Railway
- You can always change it to `info@ascai.org` later when you set it up

**For now, we recommend using Option C** - just use an email address you already have. You can set up `info@ascai.org` later if needed.

---

**Need Help?** Check the troubleshooting section above or review the Railway deployment logs for detailed error messages.
