#!/bin/sh
set -e

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
  echo "==> Creando superusuario (si no existe)..."
  python manage.py createsuperuser \
    --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL" || true
fi

echo "==> Levantando gunicorn..."
exec gunicorn gym.wsgi:application --bind 0.0.0.0:8000
