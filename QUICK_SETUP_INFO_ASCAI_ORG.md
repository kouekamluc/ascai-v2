# Quick Setup: info@ascai.org

## 🎯 Goal
- Clients see `info@ascai.org` as your contact email
- You receive emails at your existing email address (via forwarding)

## ✅ What You Need to Do

### 1. Set Up Email Forwarding (5 minutes)

**Where:** Your domain registrar or hosting provider (where you manage `ascai.org`)

**What to do:**
- Create email forward: `info@ascai.org` → `your-actual-email@gmail.com`
- Test it: Send an email to `info@ascai.org` and check if it arrives at your actual email

**Common places to find this:**
- GoDaddy: Email & Office → Email Forwarding
- Namecheap: Domain List → Manage → Email Forwarding
- Cloudflare: Email → Email Routing
- Google Domains: Email → Email Forwarding

---

### 2. Verify in Brevo (2 minutes)

1. Log in to Brevo: https://www.brevo.com/
2. Go to **Settings** → **Senders & IP**
3. Click **"Add a sender"**
4. Enter: `info@ascai.org`
5. Brevo will send a verification email to `info@ascai.org`
6. Since you set up forwarding, it will arrive at your actual email
7. Click the verification link

---

### 3. Update Railway Variables (1 minute)

Go to Railway → Your Project → Variables tab:

```bash
CONTACT_EMAIL=info@ascai.org
DEFAULT_FROM_EMAIL=ASCAI Associazione <info@ascai.org>
SERVER_EMAIL=info@ascai.org
```

(Keep your existing `BREVO_API_KEY` - don't change it)

---

### 4. Test It

```bash
python manage.py test_email info@ascai.org
```

Then check your actual email inbox (where forwarding goes).

---

## 📋 Full Guide

See [INFO_ASCAI_ORG_SETUP.md](INFO_ASCAI_ORG_SETUP.md) for detailed instructions and troubleshooting.

---

**That's it!** Once forwarding is set up and Brevo is verified, contact form emails will go to `info@ascai.org` and forward to your actual email.
