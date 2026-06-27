#!/usr/bin/env bash
#
# Setup completo del Sistema de Gimnasio desde una clonación nueva.
#
# Hace TODO de un solo paso:
#   - crea el entorno virtual e instala dependencias de Python
#   - genera el archivo .env (con una SECRET_KEY nueva) si no existe
#   - crea la base de datos PostgreSQL si no existe
#   - aplica migraciones
#   - crea el admin y un usuario por cada rol (credenciales conocidas)
#   - puebla la base con datos de demostración
#   - instala las dependencias del frontend
#
# Requisitos previos: Python 3.11+, Node 18+, PostgreSQL corriendo.
#
# Uso:
#   ./setup.sh
#
# Variables opcionales (con valores por defecto entre paréntesis):
#   PGUSER (postgres)  PGPASSWORD (postgres)  PGHOST (localhost)
#   PGPORT (5432)  PGDATABASE (gimnasio)  PORT (8000, puerto del backend)
#
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8000}"

echo "=================================================="
echo "  Setup del Sistema de Gimnasio"
echo "=================================================="

echo "==> [1/7] Entorno virtual + dependencias de Python..."
if [ ! -d venv ]; then python3 -m venv venv; fi
venv/bin/python -m pip install --upgrade pip >/dev/null
venv/bin/python -m pip install -r requirements.txt

echo "==> [2/7] Archivo .env..."
if [ ! -f .env ]; then
  SECRET="$(venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(64))')"
  cat > .env <<EOF
# Generado por setup.sh - NO subir a git
DEBUG=True
DJANGO_SECRET_KEY=${SECRET}
PGDATABASE=${PGDATABASE:-gimnasio}
PGUSER=${PGUSER:-postgres}
PGPASSWORD=${PGPASSWORD:-postgres}
PGHOST=${PGHOST:-localhost}
PGPORT=${PGPORT:-5432}
EOF
  echo "    .env creado. Si tu PostgreSQL usa otro usuario/clave, edita el .env y vuelve a correr."
else
  echo "    .env ya existe, se respeta."
fi

echo "==> [3/7] Base de datos PostgreSQL..."
venv/bin/python - <<'PY'
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv(".env")
name = os.getenv("PGDATABASE", "gimnasio")
conn = psycopg2.connect(
    dbname="postgres",
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    host=os.getenv("PGHOST"),
    port=os.getenv("PGPORT"),
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
if cur.fetchone():
    print(f"    Base '{name}' ya existe.")
else:
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    print(f"    Base '{name}' creada.")
cur.close()
conn.close()
PY

echo "==> [4/7] Migraciones..."
venv/bin/python manage.py migrate --noinput

echo "==> [5/7] Usuarios y roles (admin + uno por rol)..."
venv/bin/python manage.py crear_usuarios_demo

echo "==> [6/7] Datos de demostración..."
venv/bin/python manage.py seed_demo

echo "==> [7/7] Dependencias del frontend..."
if [ -d frontend ]; then ( cd frontend && npm install ); fi

echo ""
echo "=================================================="
echo "  LISTO. Para arrancar el sistema:"
echo "=================================================="
echo "  1) Backend:   venv/bin/python manage.py runserver ${PORT}"
if [ "$PORT" = "8000" ]; then
  echo "  2) Frontend:  cd frontend && npm start"
else
  echo "  2) Frontend:  cd frontend && REACT_APP_API_URL=http://localhost:${PORT}/api npm start"
fi
echo ""
echo "  Abre:  http://localhost:3000"
echo ""
echo "  CREDENCIALES:"
echo "    Administrador  ->  admin@gimnasio.com       / admin123"
echo "    Entrenador     ->  entrenador@gimnasio.com  / entrenador123"
echo "    Recepcionista  ->  recepcion@gimnasio.com   / recepcion123"
echo "    Supervisor     ->  supervisor@gimnasio.com  / supervisor123"
echo "    Limpieza       ->  limpieza@gimnasio.com    / limpieza123"
echo "=================================================="
