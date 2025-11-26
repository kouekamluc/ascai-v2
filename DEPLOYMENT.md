# Deployment Guide for ASCAI Lazio Platform

This document provides deployment instructions for various platforms.

## Environment Variables Required

Set these environment variables in your deployment platform:

### Required
- `SECRET_KEY`: Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Comma-separated list of your domain(s)
- `DATABASE_URL`: PostgreSQL connection string (or individual DB_* variables)
- `DJANGO_ENV`: Set to `production`

### Optional (for production features)
- `USE_S3`: Set to `True` to use AWS S3 for media storage
- `AWS_ACCESS_KEY_ID`: AWS access key
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_STORAGE_BUCKET_NAME`: S3 bucket name
- `AWS_S3_REGION_NAME`: AWS region (e.g., `us-east-1`)

### Email Configuration
- `EMAIL_HOST`: SMTP server
- `EMAIL_PORT`: SMTP port
- `EMAIL_USE_TLS`: `True` or `False`
- `EMAIL_HOST_USER`: Email username
- `EMAIL_HOST_PASSWORD`: Email password
- `DEFAULT_FROM_EMAIL`: Sender email address

## Railway Deployment (Docker)

1. Create a new project on Railway and select the Docker builder (Railway detects the `Dockerfile` automatically).
2. Attach a PostgreSQL service; Railway injects `DATABASE_URL` for you.
3. Configure environment variables:
   - `DJANGO_ENV=production` (default in Dockerfile but keep it visible in the dashboard)
   - `SECRET_KEY=<your-generated-key>`
   - `ALLOWED_HOSTS=your-app-name.railway.app,your-custom-domain`
   - `DEBUG=False`
   - Optional `USE_S3` + AWS credentials if using S3
4. Ensure the deploy start command is `./scripts/entrypoint.sh` (pre-configured in `railway.json`).
5. Trigger a deploy. The entrypoint automatically runs migrations, collects static files, and starts Gunicorn.

## Render Deployment

1. Create a new Web Service on Render
2. Connect your repository
3. Add a PostgreSQL database
4. The `render.yaml` file will configure most settings automatically
5. Set additional environment variables in Render dashboard:
   - `SECRET_KEY`
   - `ALLOWED_HOSTS`
   - `DEBUG=False`
6. Deploy

## DigitalOcean App Platform

1. Create a new App in DigitalOcean
2. Connect your GitHub repository
3. Add a PostgreSQL database
4. Configure environment variables
5. Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
6. Set run command: `gunicorn config.wsgi:application`

## PythonAnywhere

1. Upload your project files via Git or SFTP
2. Create a web app
3. Edit WSGI file to point to your Django app
4. Create a MySQL/PostgreSQL database (or use SQLite for testing)
5. Set up virtual environment and install requirements
6. Run migrations: `python manage.py migrate`
7. Collect static files: `python manage.py collectstatic --noinput`
8. Configure environment variables via `.env` file

## Post-Deployment Steps

1. Run migrations:
```bash
python manage.py migrate
```

2. Create superuser:
```bash
python manage.py createsuperuser
```

3. Collect static files (if not using S3):
```bash
python manage.py collectstatic --noinput
```

4. Create translation files (if needed):
```bash
python manage.py makemessages -l fr
python manage.py compilemessages
```

5. Set up admin approval for initial users

## Health Check

The platform includes a root URL health check endpoint. Ensure your deployment platform uses `/` for health checks.

## Troubleshooting

- **Static files not loading**: Ensure `STATIC_ROOT` is set and `python manage.py collectstatic` has been run
- **Media files not working**: Check AWS S3 configuration or local media directory permissions
- **Database connection errors**: Verify `DATABASE_URL` or individual database environment variables
- **500 errors**: Check `DEBUG=False` and review logs for specific error messages

