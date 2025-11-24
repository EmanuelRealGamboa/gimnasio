#!/bin/sh
set -e

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

echo "==> Creando superusuario (si no existe)..."
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  # Django leerá DJANGO_SUPERUSER_* automáticamente
  python manage.py createsuperuser --noinput || true
fi

echo "==> Levantando gunicorn..."
exec gunicorn gym.wsgi:application --bind 0.0.0.0:8000
