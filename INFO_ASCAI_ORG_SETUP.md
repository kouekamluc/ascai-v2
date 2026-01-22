# Setting Up info@ascai.org Email Address

This guide shows you how to set up `info@ascai.org` so that:
- ✅ Clients see `info@ascai.org` when they contact you
- ✅ You receive emails at your existing email address (via forwarding)
- ✅ Works with your existing Brevo setup

## 🎯 What You Need

1. **Domain control** - You need access to manage DNS/email settings for `ascai.org`
2. **Brevo account** - You already have this set up
3. **Your existing email** - Where you want to receive forwarded emails

## 📋 Step-by-Step Setup

### Step 1: Set Up Email Forwarding (Domain Level)

You need to forward `info@ascai.org` → `your-actual-email@gmail.com` (or whatever email you use).

**Option A: Using Your Domain Registrar/Hosting Provider**

Most domain registrars and hosting providers offer email forwarding:

1. **Log in to your domain registrar/hosting provider**
   - Examples: GoDaddy, Namecheap, Google Domains, Cloudflare, etc.

2. **Find Email Settings**
   - Look for "Email Forwarding", "Email Management", or "Mail Settings"
   - This is usually in your domain management dashboard

3. **Create Email Forward**
   - Create a new email forward: `info@ascai.org`
   - Forward to: `your-actual-email@gmail.com` (your real email)
   - Save the settings

4. **Verify it works**
   - Send a test email to `info@ascai.org` from another email
   - Check if it arrives at `your-actual-email@gmail.com`

**Option B: Using Google Workspace (If You Have It)**

If you have Google Workspace for `ascai.org`:

1. Go to Google Admin Console
2. Users → Add user → Create `info@ascai.org`
3. Set up email forwarding in the user settings
4. Forward to your personal Gmail

**Option C: Using Cloudflare Email Routing (Free)**

If your domain uses Cloudflare:

1. Go to Cloudflare Dashboard → Your Domain
2. Email → Email Routing
3. Create address: `info@ascai.org`
4. Forward to: `your-actual-email@gmail.com`

**Option D: Using a Simple Email Service**

Services like:
- **Zoho Mail** (free for 1 user)
- **ForwardMX** (free email forwarding)
- **ImprovMX** (free email forwarding)

---

### Step 2: Verify info@ascai.org in Brevo

Since you're using Brevo to send emails, you need to verify `info@ascai.org` as a sender:

1. **Log in to Brevo**
   - Go to https://www.brevo.com/
   - Sign in to your account

2. **Go to Sender Management**
   - Navigate to **Settings** → **Senders & IP**
   - Click **"Add a sender"** or **"Verify a sender"**

3. **Add info@ascai.org**
   - Enter: `info@ascai.org`
   - Enter display name: `ASCAI Associazione` (optional)
   - Click **"Save"** or **"Verify"**

4. **Verify the Email**
   - Brevo will send a verification email to `info@ascai.org`
   - Since you set up forwarding, this email will arrive at your actual email
   - Click the verification link in the email
   - Or enter the verification code if provided

5. **Wait for Verification**
   - It may take a few minutes for verification to complete
   - Check the sender status in Brevo dashboard

**Important:** Make sure email forwarding is set up BEFORE verifying in Brevo, so the verification email reaches you!

---

### Step 3: Update Railway Environment Variables

Now update your Railway settings to use `info@ascai.org`:

1. **Go to Railway Dashboard**
   - Railway → Your Project → Variables tab

2. **Update/Create These Variables:**

   ```bash
   # Your existing Brevo API key (keep this)
   BREVO_API_KEY=your-existing-brevo-api-key
   
   # Set contact email to info@ascai.org
   CONTACT_EMAIL=info@ascai.org
   
   # Set sender email to info@ascai.org (clients will see this)
   DEFAULT_FROM_EMAIL=ASCAI Associazione <info@ascai.org>
   
   # Server email for error notifications
   SERVER_EMAIL=info@ascai.org
   ```

3. **Save the Variables**
   - Railway will automatically redeploy with new settings

---

### Step 4: Test the Setup

1. **Test Email Forwarding**
   ```bash
   # Send a test email to info@ascai.org from another email
   # Check if it arrives at your actual email address
   ```

2. **Test Contact Form**
   - Go to your website's contact page
   - Fill out and submit the contact form
   - Check your actual email inbox for the contact form submission
   - The email should appear to come from `info@ascai.org`

3. **Test with Management Command**
   ```bash
   python manage.py test_email info@ascai.org
   ```
   - This will send a test email to `info@ascai.org`
   - Check your actual email inbox (where forwarding goes)

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Email forwarding is set up: `info@ascai.org` → `your-actual-email@gmail.com`
- [ ] Test email to `info@ascai.org` arrives at your actual email
- [ ] `info@ascai.org` is verified in Brevo dashboard
- [ ] Railway variables are set:
  - [ ] `CONTACT_EMAIL=info@ascai.org`
  - [ ] `DEFAULT_FROM_EMAIL=ASCAI Associazione <info@ascai.org>`
  - [ ] `BREVO_API_KEY` is set (your existing key)
- [ ] Contact form sends emails to `info@ascai.org`
- [ ] You receive contact form emails at your actual email address
- [ ] Emails appear to come from `info@ascai.org` (check email headers)

---

## 🔍 How It Works

Here's the flow:

1. **Client submits contact form** → Website sends email to `info@ascai.org`
2. **Email goes to info@ascai.org** → Domain forwards it to your actual email
3. **You receive email** → At your actual email address (Gmail, etc.)
4. **Client sees** → `info@ascai.org` as the contact email on your website

**Email Flow:**
```
Contact Form → Brevo → info@ascai.org → [Email Forwarding] → your-actual-email@gmail.com
```

---

## 🛠️ Troubleshooting

### "Verification email not received" (Brevo)

- **Check email forwarding is working first**
  - Send a test email to `info@ascai.org` from another account
  - Make sure it arrives at your actual email
- **Check spam folder** - Verification emails sometimes go to spam
- **Wait a few minutes** - Email forwarding can have delays
- **Try resending verification** in Brevo dashboard

### "Emails not arriving at my actual email"

- **Verify forwarding is set up correctly**
  - Log in to your domain/hosting provider
  - Check that `info@ascai.org` forwards to your actual email
- **Test forwarding manually**
  - Send an email to `info@ascai.org` from another account
  - See if it arrives at your actual email
- **Check spam folder**
- **Verify forwarding hasn't expired** (some services have expiration)

### "Contact form emails not working"

- **Check Railway variables**
  - Make sure `CONTACT_EMAIL=info@ascai.org` is set
  - Make sure `BREVO_API_KEY` is set
- **Check Brevo sender verification**
  - Make sure `info@ascai.org` shows as "Verified" in Brevo
- **Check Railway logs**
  - Look for email sending errors
  - Look for "Failed to send contact email" messages

### "Emails appear to come from wrong address"

- **Check `DEFAULT_FROM_EMAIL` in Railway**
  - Should be: `ASCAI Associazione <info@ascai.org>`
- **Verify in Brevo**
  - Make sure `info@ascai.org` is set as the verified sender
- **Check email headers** (in received email)
  - "From" field should show `info@ascai.org`

---

## 📝 Quick Reference

### Railway Variables (Final Setup)

```bash
BREVO_API_KEY=your-brevo-api-key
CONTACT_EMAIL=info@ascai.org
DEFAULT_FROM_EMAIL=ASCAI Associazione <info@ascai.org>
SERVER_EMAIL=info@ascai.org
```

### Email Forwarding Setup

- **From:** `info@ascai.org`
- **To:** `your-actual-email@gmail.com` (your real email)

### Test Commands

```bash
# Test email sending
python manage.py test_email info@ascai.org

# Then check your actual email inbox (where forwarding goes)
```

---

## 🎯 Summary

1. ✅ Set up email forwarding: `info@ascai.org` → your actual email
2. ✅ Verify `info@ascai.org` in Brevo
3. ✅ Update Railway variables to use `info@ascai.org`
4. ✅ Test contact form and email forwarding
5. ✅ You're done! Clients see `info@ascai.org`, you receive at your actual email

---

**Need Help?** 
- Check your domain registrar's documentation for email forwarding
- Contact your hosting provider's support
- Check Brevo documentation for sender verification
