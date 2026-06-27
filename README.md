# Sistema de Gestión de Gimnasio

Backend **Django REST Framework** + frontend **React**. Gestiona clientes, empleados,
membresías, control de acceso, facturación, ventas, inventario, horarios y equipos,
con roles y permisos.

## Requisitos previos

- **Python 3.11+**
- **Node 18+** (incluye npm)
- **PostgreSQL** corriendo (local, Postgres.app, o Docker)
- **Git**

## Puesta en marcha rápida (un solo comando)

```bash
git clone https://github.com/EmanuelRealGamboa/gimnasio.git
cd gimnasio
./setup.sh
```

`setup.sh` crea el entorno, instala dependencias, genera el `.env`, crea la base de
datos, aplica migraciones, crea los usuarios (admin + uno por rol) y **puebla la base
con datos de demostración**.

> Si tu PostgreSQL usa un usuario/clave distintos a `postgres`/`postgres`, edita el
> `.env` que generó `setup.sh` (o exporta `PGUSER`/`PGPASSWORD` antes de correrlo) y
> vuelve a ejecutar `./setup.sh`.

### Arrancar el sistema (dos terminales)

```bash
# Terminal 1 - Backend
venv/bin/python manage.py runserver 8000

# Terminal 2 - Frontend
cd frontend && npm start
```

Abre **http://localhost:3000**

> Si corres el backend en un puerto distinto a 8000, arranca el frontend con:
> `REACT_APP_API_URL=http://localhost:<PUERTO>/api npm start`

## Credenciales de demostración

| Rol | Email | Contraseña |
|-----|-------|-----------|
| Administrador | `admin@gimnasio.com` | `admin123` |
| Entrenador | `entrenador@gimnasio.com` | `entrenador123` |
| Recepcionista | `recepcion@gimnasio.com` | `recepcion123` |
| Supervisor de Instalaciones | `supervisor@gimnasio.com` | `supervisor123` |
| Personal de Limpieza | `limpieza@gimnasio.com` | `limpieza123` |

Cada rol entra a su propio panel; el administrador (superusuario) ve todo.

## Comandos útiles

```bash
# Repoblar datos de demo (sin duplicar)
venv/bin/python manage.py seed_demo
venv/bin/python manage.py seed_demo --flush   # limpia y repuebla

# Recrear usuarios/roles
venv/bin/python manage.py crear_usuarios_demo

# Correr las pruebas
venv/bin/python -m pytest tests/ authentication/tests.py
```

## Notas

- El `.env` **no** se sube a git (contiene la `SECRET_KEY` y la clave de la base de
  datos). Usa `.env.example` como referencia.
- Para producción (Railway) define `DJANGO_SECRET_KEY`, `DEBUG=False` y
  `DJANGO_ALLOWED_HOSTS` como variables de entorno.
