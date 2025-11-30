FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_ENV=production \
    DJANGO_SETTINGS_MODULE=config.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gettext curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN chmod +x scripts/entrypoint.sh scripts/predeploy.sh

# Compile translation files during build
RUN echo "Compiling translation files during build..." && \
    (python compile_translations.py || python manage.py compilemessages --noinput) && \
    echo "Verifying compiled translation files..." && \
    find locale -name "*.mo" -type f | head -1 || (echo "ERROR: No .mo files found after compilation!" && exit 1)

# Collect static files during build
# IMPORTANT: This only collects to local staticfiles/ directory for WhiteNoise (when USE_S3=False)
# If USE_S3=True, collectstatic will be run in entrypoint.sh with real AWS credentials
# We disable S3 during build by not setting USE_S3, so files are collected locally
# This ensures WhiteNoise has files to serve, and S3 upload happens at runtime
RUN echo "Collecting static files during build (local storage for WhiteNoise)..." && \
    SECRET_KEY=django-build-time-temp-key-for-collectstatic \
    DEBUG=False \
    ALLOWED_HOSTS=localhost \
    DATABASE_URL=postgresql://dummy:dummy@localhost:5432/dummy \
    USE_S3=False \
    python manage.py collectstatic --noinput --clear && \
    echo "Verifying static files collection..." && \
    test -d staticfiles/admin && echo "✓ Admin static files collected locally" || (echo "ERROR: Admin static files not found!" && exit 1)

EXPOSE 8000

CMD ["bash", "-c", "./scripts/entrypoint.sh"]

