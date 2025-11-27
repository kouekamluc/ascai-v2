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
# This ensures all static files (including Django admin) are collected and included in the image
# Note: collectstatic doesn't require database connection, so it's safe to run during build
RUN echo "Collecting static files during build..." && \
    python manage.py collectstatic --noinput --clear && \
    echo "Verifying static files collection..." && \
    test -d staticfiles/admin && echo "✓ Admin static files collected" || (echo "ERROR: Admin static files not found!" && exit 1)

EXPOSE 8000

CMD ["bash", "-c", "./scripts/entrypoint.sh"]

