# ASCAI Lazio Platform - Installation Guide

## Prerequisites

- Python 3.9 or higher
- PostgreSQL 12 or higher
- pip (Python package manager)
- Git (optional, for version control)

## Step-by-Step Installation

### 1. Clone or Navigate to Project Directory

```bash
cd "C:\Users\kouek\kouekam\business\ascai final"
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy the example environment file:
```bash
copy .env.example .env
```

Edit `.env` file with your settings:
- Database credentials
- Secret key (generate a new one)
- Email configuration
- AWS S3 credentials (if using)

**Generate Secret Key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Set Up PostgreSQL Database

Create a PostgreSQL database:
```sql
CREATE DATABASE ascai_lazio;
CREATE USER ascai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ascai_lazio TO ascai_user;
```

Update your `.env` file with database credentials.

### 7. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 9. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 10. Create Translation Files (Optional)

```bash
python manage.py makemessages -l fr
python manage.py makemessages -l en
python manage.py compilemessages
```

### 11. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## Post-Installation Setup

### 1. Access Admin Panel

1. Go to `http://localhost:8000/admin/`
2. Login with your superuser credentials

### 2. Initial Configuration

**Create Forum Categories:**
- Go to Community > Categories
- Create categories like "General Discussion", "Academic Help", etc.

**Configure Settings:**
- Add initial universities
- Add scholarship listings
- Create news articles
- Upload documents

### 3. Test User Registration

1. Go to `/accounts/register/`
2. Register a test user
3. Approve the user in the admin panel
4. Test login functionality

## Troubleshooting

### Database Connection Issues

- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

### Static Files Not Loading

```bash
python manage.py collectstatic --noinput
```

### Migration Issues

```bash
python manage.py makemigrations
python manage.py migrate
```

### Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Permission Errors (Windows)

- Run terminal as Administrator
- Check folder permissions

## Production Deployment

See `DEPLOYMENT.md` for production deployment instructions.

## Next Steps

- Read `QUICK_START.md` for usage instructions
- Review `README.md` for project overview
- Check `DEPLOYMENT.md` for production setup
























