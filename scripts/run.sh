#!/bin/bash
set -e
cd /app

export DJANGO_SETTINGS_MODULE=config.settings.prod

echo "=== Running Django migrations ==="
$POETRY_BIN run python manage.py makemigrations --noinput || true
$POETRY_BIN run python manage.py migrate --noinput

echo "=== Collecting static files ==="
$POETRY_BIN run python manage.py collectstatic --noinput

echo "=== Starting Gunicorn server ==="
WORKERS=$(nproc)
$POETRY_BIN run gunicorn config.wsgi:application \
--bind 0.0.0.0:8000 \
--workers $WORKERS \
--threads 2 \
--timeout 120