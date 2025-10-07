# Guía de Instalación y Ejecución - Sistema de Gimnasio

Esta guía te ayudará a poner en marcha tanto el backend (Django) como el frontend (React).

## Requisitos Previos

- Python 3.11+
- Node.js 14+
- PostgreSQL
- Git

## Configuración del Backend (Django)

### 1. Instalar dependencias de Python

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

Edita el archivo `.env` con tus credenciales de PostgreSQL:

```env
DATABASE_NAME=gimnasio
DATABASE_USER=tu_usuario
DATABASE_PASSWORD=tu_contraseña
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 3. Ejecutar migraciones

```bash
python manage.py migrate
```

### 4. Crear datos de prueba

#### Crear un superusuario:

```bash
python manage.py createsuperuser
```

Ingresa:
- Email: admin@gimnasio.com
- Password: (tu contraseña segura)

#### Crear roles y permisos desde la consola de Django:

```bash
python manage.py shell
```

Luego ejecuta:

```python
from roles.models import Rol, Permiso, RolPermiso, PersonaRol
from authentication.models import Persona, User

# Crear permiso
permiso = Permiso.objects.create(
    nombre='gestionar_empleados',
    descripcion='Permiso para gestionar empleados'
)

# Crear rol Administrador
rol_admin = Rol.objects.create(
    nombre='Administrador',
    descripcion='Administrador del sistema'
)

# Asignar permiso al rol
RolPermiso.objects.create(rol=rol_admin, permiso=permiso)

# Crear rol Empleado
rol_empleado = Rol.objects.create(
    nombre='Empleado',
    descripcion='Empleado regular'
)

# Obtener tu superusuario y asignarle una persona
user = User.objects.get(email='admin@gimnasio.com')

# Si no tiene persona, crear una
if not hasattr(user, 'persona') or not user.persona:
    persona = Persona.objects.create(
        nombre='Admin',
        apellido_paterno='Sistema',
        apellido_materno='Gimnasio',
        telefono='1234567890'
    )
    user.persona = persona
    user.save()

# Asignar rol de administrador
PersonaRol.objects.create(persona=user.persona, rol=rol_admin)

print("✅ Roles y permisos configurados correctamente")
exit()
```

### 5. Iniciar el servidor Django

```bash
python manage.py runserver
```

El backend estará disponible en `http://localhost:8000`

## Configuración del Frontend (React)

### 1. Navegar a la carpeta frontend

```bash
cd frontend
```

### 2. Instalar dependencias (si aún no están instaladas)

```bash
npm install
```

### 3. Iniciar el servidor de desarrollo

```bash
npm start
```

El frontend se abrirá automáticamente en `http://localhost:3000`

## Probar la Aplicación

### 1. Login

1. Abre `http://localhost:3000`
2. Serás redirigido a `/login`
3. Ingresa:
   - Email: `admin@gimnasio.com`
   - Password: (la contraseña que creaste)

### 2. Crear un empleado

1. Click en "Nuevo Empleado"
2. Llena el formulario:
   - **Datos personales**: Nombre, apellidos, teléfono
   - **Datos de usuario**: Email único, contraseña
   - **Datos laborales**: Puesto, departamento, salario, etc.
   - **Rol ID**: 2 (para rol de Empleado)
3. Click en "Crear Empleado"

### 3. Ver lista de empleados

La lista se actualizará automáticamente después de crear el empleado.

### 4. Ver detalles

Click en el botón "👁️ Ver" de cualquier empleado.

### 5. Editar empleado

Click en "✏️ Editar", modifica los campos y guarda.

### 6. Eliminar empleado

Click en "🗑️ Eliminar" y confirma la acción.

## Ejecutar Tests

### Tests del Backend

```bash
python manage.py test authentication.tests.EmpleadoEndpointTests
```

Deberías ver:
```
Ran 11 tests in X.XXs
OK
```

## Solución de Problemas

### Error de CORS

Si ves errores de CORS en la consola del navegador:
- Verifica que `corsheaders` esté instalado
- Confirma que la configuración de CORS esté en `settings.py`
- Reinicia el servidor Django

### Error 401 Unauthorized

- Verifica que el usuario tenga el permiso `gestionar_empleados`
- Verifica que el usuario tenga un rol asignado con ese permiso
- Revisa que el token JWT sea válido

### Error de conexión a la base de datos

- Verifica que PostgreSQL esté corriendo
- Confirma las credenciales en el archivo `.env`
- Verifica que la base de datos `gimnasio` exista

### Frontend no se conecta al backend

- Verifica que el backend esté corriendo en `http://localhost:8000`
- Revisa la configuración de API_URL en `frontend/src/services/api.js`
- Asegúrate de que CORS esté configurado correctamente

## Endpoints Disponibles

### Autenticación
- `POST /api/token/` - Obtener tokens JWT
- `POST /api/token/refresh/` - Refrescar access token

### Empleados (requiere autenticación)
- `GET /api/admin/empleados/` - Lista de empleados
- `POST /api/admin/empleados/` - Crear empleado
- `GET /api/admin/empleados/<id>/detalle` - Detalle de empleado
- `PUT /api/admin/empleados/<id>/` - Actualizar empleado completo
- `PATCH /api/admin/empleados/<id>/` - Actualizar empleado parcial
- `DELETE /api/admin/empleados/<id>/` - Eliminar empleado

## Próximos Pasos

1. Crear más usuarios con diferentes roles
2. Implementar endpoints para las otras aplicaciones (roles, instalaciones, etc.)
3. Agregar más validaciones y manejo de errores
4. Implementar paginación en la lista de empleados
5. Agregar filtros y búsqueda
6. Mejorar la UI/UX con más feedback visual

## Documentación Adicional

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [React Router](https://reactrouter.com/)
