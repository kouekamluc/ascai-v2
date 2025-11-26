#!/usr/bin/env bash

set -euo pipefail

# Default PORT to 8000 for local usage if Railway does not inject one.
: "${PORT:=8000}"

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}"

