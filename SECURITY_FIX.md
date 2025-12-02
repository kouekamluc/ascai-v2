# Security Fix: Exposed SMTP Credentials

## ⚠️ CRITICAL: Gmail App Password Exposed

Your Gmail App Password was exposed in the GitHub repository. **You MUST regenerate it immediately.**

## Immediate Actions Required

### 1. Regenerate Gmail App Password (URGENT)

1. Go to: https://myaccount.google.com/apppasswords
2. **Delete the old App Password** that was exposed
3. **Create a new App Password:**
   - App: "Mail" or "Other (Custom name)"
   - Name: "ASCAI Lazio Django Production"
   - Click "Generate"
4. **Copy the new 16-character password** (remove ALL spaces)
5. **Update Railway environment variables** with the new password

### 2. Update Railway Environment Variables

Go to Railway → Your Service → Variables and update:

```bash
EMAIL_HOST_PASSWORD=your-new-16-char-app-password
```

**Replace `your-new-16-char-app-password` with the NEW App Password you just generated.**

### 3. Files Fixed

The following files have been updated to remove exposed credentials:
- `RAILWAY_EMAIL_CONFIG.md` - Replaced with placeholders
- `RAILWAY_DEPLOYMENT_FIX.md` - Replaced with placeholders
- `.env.example` - Replaced with placeholders (if it existed)

### 4. Git History

**Important:** The old password is still in Git history. For complete security:

1. **Regenerate the password** (most important - do this first!)
2. The exposed password will be useless once regenerated
3. If you want to remove it from Git history completely, you'll need to use `git filter-branch` or BFG Repo-Cleaner (advanced)

**However, regenerating the password is the most important step** - once you do that, the exposed password becomes useless.

## Prevention

### ✅ What's Already Done

- `.env` files are gitignored
- Documentation files now use placeholders
- `.env.example` uses placeholders

### 📋 Best Practices Going Forward

1. **Never commit real credentials** to Git
2. **Always use placeholders** in documentation (e.g., `your-password-here`)
3. **Use environment variables** in Railway, never hardcode
4. **Rotate credentials** if accidentally exposed
5. **Use secrets management** for production (Railway Variables are secure)

## Next Steps

1. ✅ **Regenerate Gmail App Password** (do this NOW)
2. ✅ **Update Railway with new password**
3. ✅ **Test email sending** after updating
4. ✅ **Commit the fixed files** (credentials removed)

## Verification

After regenerating and updating:

```bash
# Test email in Railway
railway run python manage.py test_email your-email@gmail.com
```

If the test succeeds, you're all set!












