# ASCAI Lazio Client Delivery Checklist

Use this before the client walkthrough so the platform feels coherent and lived-in.

## Demo Story

1. A student creates an account and verifies email.
2. The bureau approves the account and reviews the automatically created student profile.
3. The verified student appears as a pending member, not as an active member.
4. The student requests dues payment processing from the member portal.
5. The bureau sees the payment request in admin, marks dues paid, and activates membership after eligibility review.
6. The bureau sends a dashboard message; the email button opens the user's dashboard message section.
7. A mentor account has an automatically created mentor profile and becomes visible only after bureau approval.

## Status Language

- Account pending: user can exist, but bureau has not approved access.
- Email unverified: user should not appear as a dashboard-visible member.
- Profile pending: student or mentor profile exists but needs completion or bureau review.
- Member pending eligibility: email-verified account has a member record, but eligibility or dues are not complete.
- Dues payment requested: user asked the bureau to process payment; finance/admin must confirm it.
- Active member: eligibility is reviewed and current dues are paid.
- Bureau login: staff/admin access, not a membership verification status.

## Client Walkthrough

1. Show public homepage, leadership, services, events, scholarships, and downloads.
2. Sign in as the demo student and show dashboard, messages, dues, events, and mentorship.
3. Sign in as the demo mentor and show mentor profile/workflow.
4. Sign in as the bureau/admin user and show the action center queues:
   - account approvals
   - member eligibility
   - dues payment processing
   - mentor profiles
   - support/questions/messages
5. Process the demo dues request and explain how membership becomes active.
6. Send a bureau message and show the email link opens the dashboard message.

## Production Handoff Checks

- Domain and `SITE_URL` point to the final client URL.
- Email backend is configured and sender identity is verified.
- Admin/bureau credentials are known and temporary passwords are changed.
- Database backup/export process is documented.
- Unverified-account cleanup is enabled or scheduled.
- Demo seed data is removed or clearly labelled if it remains.
- GitHub `main` contains the deployed commit.

## Demo Data Command

Run this before a client demo:

```bash
python manage.py seed_client_demo
```

Run it again safely if needed. It updates the same labelled demo records rather than creating duplicates.
