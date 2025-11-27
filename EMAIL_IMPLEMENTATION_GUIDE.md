# Email Implementation Plan — Gmail Relaunch

This document replaces every previous SendGrid-oriented guide. It describes how we will rebuild outbound email using Gmail (standard or Google Workspace) across development, staging, and production (Railway). Follow the checklists in order; once all boxes are checked, the app can send email again via Gmail SMTP.

---

## 1. Objectives & Non‑Goals

- ✅ Provide a single source of truth for Gmail-based email delivery.
- ✅ Define configuration, secrets management, testing, monitoring, and rollout.
- ✅ Identify all code/config changes still required (but do **not** implement them here).
- ❌ No SendGrid/Mailgun instructions.
- ❌ No automation scripts yet (future enhancement).

---

## 2. Gmail Prerequisites

1. **Decide the sender account**
   - Use a Google Workspace mailbox if possible (higher daily quota).
   - Make sure the address belongs to our domain or an acceptable Gmail alias.
2. **Enable 2‑Step Verification** on that Google account.
3. **Create an App Password**
   - Google Account → Security → App Passwords → Select *Mail* / *Other*.
   - Copy the 16-character password; this is the value for `GMAIL_APP_PASSWORD`.
4. **Confirm SMTP access**
   - From the account, send a manual email via Gmail UI to ensure it is not blocked/suspended.
5. **Decide sender identities**
   - `DEFAULT_FROM_EMAIL`: e.g. `Ascai Support <support@yourdomain.com>`
   - `SERVER_EMAIL`: address to receive error emails; often same as `DEFAULT_FROM_EMAIL`.

---

## 3. Required Django Settings (Target State)

These values will be applied once we edit `config/settings/*.py`.

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ["GMAIL_APP_USER"]
EMAIL_HOST_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL
```

Optional but recommended:

- `EMAIL_TIMEOUT = 15`
- `ADMINS = [("Ascai Ops", "ops@yourdomain.com")]` → ensures `mail_admins` works.
- `EMAIL_SUBJECT_PREFIX = "[Ascai]"` for diagnostics.

---

## 4. Environment Variable Matrix

| Variable | Description | Local (.env) | Railway (Production) |
| --- | --- | --- | --- |
| `GMAIL_APP_USER` | Full Gmail address used to send mail | Developer-specific or shared test inbox | Production sender inbox |
| `GMAIL_APP_PASSWORD` | 16-character app password | Created per account; keep in local `.env` (never commit) | Add as Railway secret |
| `DEFAULT_FROM_EMAIL` | Display name + email shown to users | Optional override | Required (match support branding) |
| `SERVER_EMAIL` | Error emails + `ADMINS` target | Usually same as `DEFAULT_FROM_EMAIL` | Optional override |
| `EMAIL_SUBJECT_PREFIX` | String prefix for automated emails | `[Ascai Dev]` | `[Ascai]` |

**Storage Guidance**
- Local: use `.env`, excluded from git.
- Railway: `railway variables set KEY=value`.
- CI (if any): configure equivalent secrets before running email tests.

---

## 5. Implementation Phases

### Phase A — Cleanup (completed in this commit)
- Remove all SendGrid instruction docs to avoid conflicting guidance.
- Reset `EMAIL_IMPLEMENTATION_GUIDE.md` to this Gmail plan.

### Phase B — Code & Settings Updates (still required)
1. Remove `apps.core.email_backends.SendGridBackend` references.
2. Uninstall `sendgrid` package (and any unused logging around it).
3. Update `config/settings/base.py` (and env-specific overrides) to use Gmail settings from Section 3.
4. Update `.env.example`, `env.railway.example`, and docs to include new env vars.

### Phase C — Secrets Provisioning
1. Generate Gmail app password for prod inbox.
2. Update Railway environment variables (`GMAIL_APP_USER`, `GMAIL_APP_PASSWORD`, `DEFAULT_FROM_EMAIL`, `SERVER_EMAIL`).
3. Share credentials securely with relevant team members (e.g., 1Password vault).

### Phase D — Testing
1. **Unit level**: run Django shell + `send_mail` with `console.EmailBackend` to ensure templates render.
2. **Integration (local)**: set local env vars, run `python manage.py sendtestemail you@example.com`.
3. **Staging/Prod smoke test**: trigger user-facing email (e.g., password reset) and verify Gmail “Sent” mailbox + recipient inbox.
4. **Regression**: ensure background tasks (if any) still call `send_mail` and do not rely on SendGrid-specific features.

### Phase E — Monitoring & Rollback
1. Enable Gmail forwarding/filters to capture bounced messages.
2. Add health check command (e.g., cron `manage.py sendtestemail`) if needed.
3. Rollback plan: switch `EMAIL_BACKEND` to Django console backend temporarily if Gmail locks out; document manual unlock steps.

---

## 6. Detailed Configuration Steps

1. **Create/Confirm Gmail Sender**
   - For Workspace: Admin Console → Users → Add user (if needed).
   - For personal Gmail: ensure usage complies with Gmail TOS (low volume transactional only).

2. **Generate App Password**
   - Account → Security → App Passwords → *Select app*: Mail → *Select device*: Other (Ascai Prod) → Generate.
   - Store immediately; Google will not show it again.

3. **Populate Environment Variables**
   - Local `.env` example:
     ```
     GMAIL_APP_USER=support@yourdomain.com
     GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
     DEFAULT_FROM_EMAIL="Ascai Support <support@yourdomain.com>"
     SERVER_EMAIL=errors@yourdomain.com
     EMAIL_SUBJECT_PREFIX="[Ascai Dev]"
     ```
   - Railway CLI:
     ```
     railway variables set GMAIL_APP_USER=support@yourdomain.com
     railway variables set GMAIL_APP_PASSWORD=xxxx....
     railway variables set DEFAULT_FROM_EMAIL="Ascai Support <support@yourdomain.com>"
     railway variables set SERVER_EMAIL=errors@yourdomain.com
     railway variables set EMAIL_SUBJECT_PREFIX="[Ascai]"
     ```

4. **Update Django Settings**
   - Replace custom SendGrid backend with standard SMTP backend.
   - Remove SendGrid-specific logging/error handling.
   - Ensure `DEFAULT_FROM_EMAIL` is referenced wherever emails are sent.

5. **Local Verification**
   - `python manage.py shell`
   - ```
     from django.core.mail import send_mail
     send_mail("Test", "Body", None, ["you@yourdomain.com"])
     ```
   - Check Gmail “Sent” and recipient mailbox.

6. **Production Verification**
   - After deploy, run `python manage.py sendtestemail you@yourdomain.com` via Railway shell.
   - Monitor Gmail account for Google security alerts; mark the server as trusted.
   - Confirm DKIM/SPF alignment (Workspace handles this automatically if domain is verified).

---

## 7. Risk & Mitigation

- **Daily quota exceeded**: Google caps Gmail/Workspace sends (500 for personal, 2k+ for Workspace). Mitigation: monitor send volume dashboards; consider fallback provider if approaching limits.
- **Account lockout**: Wrong password or suspicious activity can block SMTP. Mitigation: use dedicated mailbox, restrict access, enable admin alerts.
- **Emails landing in spam**: Configure SPF, DKIM, DMARC for the sending domain. Keep content clean; avoid link shorteners.
- **Credential leakage**: Store app password only in secrets vaults; rotate quarterly.

---

## 8. Acceptance Checklist

- [ ] Gmail sender mailbox verified and app password created.
- [ ] Environment variables configured locally and in Railway.
- [ ] Django settings switched to Gmail SMTP backend.
- [ ] `sendtestemail` succeeds locally.
- [ ] Production smoke test email received.
- [ ] Monitoring/alerting notes documented (filters, forwarding).
- [ ] Old SendGrid references removed from code, docs, and dependencies.

---

## 9. Future Enhancements

- Automate secret rotation reminders.
- Add management command to send periodic heartbeat emails.
- Consider switching to Google Workspace SMTP relay for higher throughput if needed.
- Introduce feature flag to fall back to console backend during incidents.

---

**Source of Truth:** This file (`EMAIL_IMPLEMENTATION_GUIDE.md`). Update it whenever the plan changes so we never drift again.






