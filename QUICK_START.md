# Quick Start Guide - ASCAI Lazio Platform

## Initial Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

3. **Create database:**
```bash
# PostgreSQL
createdb ascai_lazio
```

4. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Collect static files:**
```bash
python manage.py collectstatic --noinput
```

7. **Run development server:**
```bash
python manage.py runserver
```

## Initial Admin Setup

1. Login to admin: `http://localhost:8000/admin/`

2. Create forum categories:
   - Go to Community > Categories
   - Create categories like "General Discussion", "Academic Help", etc.

3. Approve initial users:
   - Go to Accounts > Users
   - Approve users who have registered

4. Approve mentors:
   - Go to Mentorship > Mentor Profiles
   - Approve mentor profiles

## Adding Initial Content

1. **Universities:**
   - Go to Universities > Universities
   - Add universities in Lazio region
   - Add programs for each university

2. **Scholarships:**
   - Go to Scholarships > Scholarships
   - Add scholarships including DISCO Lazio
   - Mark DISCO Lazio scholarships with the checkbox

3. **News & Events:**
   - Go to Diaspora > News/Events
   - Create news articles and events
   - Mark as published to make visible

4. **Documents:**
   - Go to Downloads > Documents
   - Upload PDFs and other documents
   - Set category and activate

5. **Gallery:**
   - Go to Gallery > Albums
   - Create albums and add images

## Testing Features

### User Registration Flow
1. Register a new user at `/accounts/register/`
2. User account will be pending approval
3. Admin approves in admin panel
4. User can then login

### University Search
1. Go to `/universities/`
2. Test HTMX filtering by city, degree type, etc.
3. Save universities as favorites (requires login)

### Forum
1. Go to `/community/`
2. Create a thread
3. Reply to threads
4. Test upvote functionality

### Mentorship
1. Create a mentor profile (user with mentor role)
2. Admin approves mentor profile
3. Students can request mentorship
4. Test messaging between mentor and student

## Translation Setup

1. **Extract strings:**
```bash
python manage.py makemessages -l fr
python manage.py makemessages -l en
```

2. **Edit translation files:**
   - Edit `locale/fr/LC_MESSAGES/django.po`
   - Edit `locale/en/LC_MESSAGES/django.po`

3. **Compile translations:**
```bash
python manage.py compilemessages
```

## Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Set `SECRET_KEY` to a secure random value
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up AWS S3 for media storage (or use local)
- [ ] Configure email settings
- [ ] Set up SSL/HTTPS
- [ ] Run `collectstatic`
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Test all features thoroughly

## Common Issues

**Static files not loading:**
- Run `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATIC_URL` settings

**Media files not working:**
- Check `MEDIA_ROOT` and `MEDIA_URL` settings
- Ensure directory permissions are correct
- If using S3, verify AWS credentials

**Database connection errors:**
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

**HTMX not working:**
- Check that HTMX script is loaded in base.html
- Verify CSRF tokens are included in forms
- Check browser console for errors
























