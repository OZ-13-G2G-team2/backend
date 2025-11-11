#!/bin/bash
set -e
cd /app

export DJANGO_SETTINGS_MODULE=config.settings.prod

echo "=== Running Django migrations ==="
POETRY run python manage.py makemigrations --noinput || true
POETRY run python manage.py migrate --noinput

echo "=== Collecting static files ==="
POETRY run python manage.py collectstatic --noinput

echo "=== Starting Gunicorn server ==="
POETRY run gunicorn config.wsgi:application \
--bind 0.0.0.0:8000 \
--workers 2 \
--threads 2 \
--timeout 120