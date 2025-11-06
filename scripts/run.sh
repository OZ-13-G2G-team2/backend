#!/bin/bash
set -e
cd /app

export DJANGO_SETTINGS_MODULE=config.settings.prod

chmod +x /root/.local/bin/poetry
/root/.local/bin/poetry install

echo "=== Running Django migrations ==="
/root/.local/bin/poetry run python manage.py makemigrations --noinput || true
/root/.local/bin/poetry run python manage.py migrate --noinput

echo "=== Collecting static files ==="
/root/.local/bin/poetry run python manage.py collectstatic --noinput

echo "=== Starting Gunicorn server ==="
exec /root/.local/bin/poetry run gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --threads 2 \
    --timeout 120