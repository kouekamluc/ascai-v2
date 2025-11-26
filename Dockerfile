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

RUN chmod +x scripts/entrypoint.sh

EXPOSE 8000

CMD ["bash", "-c", "./scripts/entrypoint.sh"]

