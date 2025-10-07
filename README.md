# Sistema de Gestión de Gimnasio

Sistema completo de gestión para gimnasios desarrollado con Django REST Framework y React, que incluye control de acceso basado en roles y permisos, gestión de empleados, instalaciones, entrenamientos y más.

## 🚀 Características

- **Sistema de autenticación JWT** con tokens de acceso y refresh
- **Control de acceso basado en roles (RBAC)** con permisos granulares
- **5 roles predefinidos** con permisos específicos
- **Dashboards personalizados** según el rol del usuario
- **Gestión completa de empleados** con CRUD
- **Interfaz moderna** con tema oscuro
- **Navegación lateral** (sidebar) colapsable
- **Sistema de filtros y búsqueda** en listados
- **Diseño responsive** para dispositivos móviles

## 📋 Requisitos Previos

- Python 3.8 o superior
- Node.js 16 o superior
- PostgreSQL (o SQLite para desarrollo)
- pip (gestor de paquetes de Python)
- npm (gestor de paquetes de Node.js)

## 🛠️ Instalación

### Backend (Django)

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd gimnasio
```

2. **Crear y activar entorno virtual**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**

Editar `gym/settings.py` si es necesario. Por defecto usa SQLite.

5. **Ejecutar migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Configurar roles y permisos** (ver sección más abajo)

8. **Iniciar servidor de desarrollo**
```bash
python manage.py runserver
```

El backend estará disponible en `http://localhost:8000`

### Frontend (React)

1. **Navegar a la carpeta frontend**
```bash
cd frontend
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Iniciar servidor de desarrollo**
```bash
npm start
```

El frontend estará disponible en `http://localhost:3000`

## 🔐 Configuración de Roles y Permisos

### Estructura del Sistema de Permisos

El sistema utiliza una arquitectura de permisos personalizada:

```
Usuario → Persona → PersonaRol → Rol → RolPermiso → Permiso
```

### 1. Crear los Permisos

Desde el shell de Django o el admin panel, crear los siguientes permisos:

```python
python manage.py shell
```

```python
from roles.models import Permiso

# Crear permisos
permisos = [
    {'nombre': 'gestionar_empleados', 'descripcion': 'Puede gestionar empleados'},
    {'nombre': 'gestionar_entrenamientos', 'descripcion': 'Puede gestionar entrenamientos'},
    {'nombre': 'gestionar_acceso', 'descripcion': 'Puede gestionar el acceso al gimnasio'},
    {'nombre': 'gestionar_instalaciones', 'descripcion': 'Puede gestionar instalaciones'},
    {'nombre': 'gestionar_limpieza', 'descripcion': 'Puede gestionar limpieza'},
]

for p in permisos:
    Permiso.objects.get_or_create(nombre=p['nombre'], defaults={'descripcion': p['descripcion']})

print("Permisos creados exitosamente")
```

### 2. Crear los Roles

```python
from roles.models import Rol, RolPermiso, Permiso

# Crear roles
roles_config = {
    'Administrador': ['gestionar_empleados'],
    'Entrenador': ['gestionar_entrenamientos'],
    'Recepcionista': ['gestionar_acceso'],
    'Supervisor de Instalaciones': ['gestionar_instalaciones'],
    'Personal de Limpieza': ['gestionar_limpieza'],
}

for rol_nombre, permisos_nombres in roles_config.items():
    rol, created = Rol.objects.get_or_create(
        nombre=rol_nombre,
        defaults={'descripcion': f'Rol de {rol_nombre}'}
    )

    # Asignar permisos al rol
    for permiso_nombre in permisos_nombres:
        permiso = Permiso.objects.get(nombre=permiso_nombre)
        RolPermiso.objects.get_or_create(rol=rol, permiso=permiso)

    print(f"Rol '{rol_nombre}' creado con permisos: {permisos_nombres}")

print("Roles creados exitosamente")
```

### 3. Asignar Rol a un Usuario

```python
from authentication.models import User, Persona
from roles.models import Rol, PersonaRol

# Ejemplo: Asignar rol de Administrador al superusuario
user = User.objects.get(email='admin@ejemplo.com')

# Si el usuario no tiene Persona, crear una
if not hasattr(user, 'persona') or user.persona is None:
    persona = Persona.objects.create(
        nombre='Admin',
        apellido_paterno='Sistema',
        apellido_materno='Sistema',
        telefono='0000000000',
        puesto='Administrador',
        departamento='TI',
        fecha_contratacion='2025-01-01',
        salario=50000.00,
        rfc='XAXX010101000',
        user=user
    )
else:
    persona = user.persona

# Asignar rol
rol_admin = Rol.objects.get(nombre='Administrador')
PersonaRol.objects.get_or_create(persona=persona, rol=rol_admin)

print(f"Rol asignado a {user.email}")
```

## 🎭 Roles del Sistema

### 1. Administrador
- **Permiso**: `gestionar_empleados`
- **Dashboard**: `/dashboard-admin`
- **Funcionalidades**:
  - Crear, editar, eliminar empleados
  - Asignar roles a empleados
  - Gestión completa del personal

### 2. Entrenador
- **Permiso**: `gestionar_entrenamientos`
- **Dashboard**: `/dashboard-entrenador`
- **Funcionalidades**:
  - Gestionar rutinas de entrenamiento
  - Ver clientes asignados
  - Crear planes de ejercicio

### 3. Recepcionista
- **Permiso**: `gestionar_acceso`
- **Dashboard**: `/dashboard-recepcion`
- **Funcionalidades**:
  - Controlar acceso al gimnasio
  - Registrar entradas y salidas
  - Gestión de visitantes

### 4. Supervisor de Instalaciones
- **Permiso**: `gestionar_instalaciones`
- **Dashboard**: `/dashboard-supervisor`
- **Funcionalidades**:
  - Supervisar estado de instalaciones
  - Reportar mantenimiento
  - Gestionar equipamiento

### 5. Personal de Limpieza
- **Permiso**: `gestionar_limpieza`
- **Dashboard**: `/dashboard-limpieza`
- **Funcionalidades**:
  - Ver áreas asignadas
  - Reportar limpieza completada
  - Gestionar horarios

## 📁 Estructura del Proyecto

```
gimnasio/
├── authentication/          # App de autenticación
│   ├── models.py           # Modelo User
│   ├── views.py            # Login, registro, etc.
│   ├── dashboard_views.py  # Vistas de dashboards
│   ├── utils.py            # Funciones de utilidad (permisos)
│   ├── decorators.py       # Decoradores de permisos
│   └── middleware.py       # Middleware de redirección
├── empleados/              # App de gestión de empleados
│   ├── models.py           # Modelo Persona
│   └── views.py            # CRUD de empleados
├── roles/                  # App de roles y permisos
│   ├── models.py           # Rol, Permiso, PersonaRol, RolPermiso
│   └── views.py            # API de roles
├── control_acceso/         # App de control de acceso
├── instalaciones/          # App de instalaciones
├── gym/                    # Configuración del proyecto
│   ├── settings.py         # Configuración general
│   └── urls.py             # URLs principales
├── frontend/               # Aplicación React
│   ├── public/
│   └── src/
│       ├── components/     # Componentes React
│       │   ├── Login.js
│       │   ├── Sidebar.js
│       │   ├── Layout.js
│       │   ├── Dashboard*.js
│       │   ├── EmployeeList.js
│       │   ├── EmployeeForm.js
│       │   └── EmployeeDetail.js
│       ├── services/       # Servicios de API
│       │   ├── authService.js
│       │   └── employeeService.js
│       ├── App.js          # Componente principal
│       └── index.css       # Estilos globales
├── requirements.txt        # Dependencias Python
└── README.md              # Este archivo
```

## 🔧 Configuración Adicional

### Variables de Entorno (Producción)

Crear archivo `.env` en la raíz:

```env
DEBUG=False
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=postgresql://usuario:contraseña@localhost/gimnasio_db
ALLOWED_HOSTS=tudominio.com,www.tudominio.com
CORS_ALLOWED_ORIGINS=https://tudominio.com
```

### CORS (Cross-Origin Resource Sharing)

Ya configurado en `gym/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

## 🧪 Pruebas

### Backend
```bash
python manage.py test
```

### Frontend
```bash
cd frontend
npm test
```

## 📝 Uso del Sistema

1. **Iniciar sesión**
   - Ir a `http://localhost:3000`
   - Ingresar credenciales
   - El sistema redirige automáticamente al dashboard correspondiente según el rol

2. **Crear un empleado**
   - Desde el dashboard de Administrador
   - Click en "Nuevo Empleado"
   - Llenar formulario con todos los datos
   - Seleccionar rol
   - Guardar

3. **Buscar y filtrar empleados**
   - En la lista de empleados usar el buscador
   - Filtrar por estado (Todos/Activos/Inactivos)
   - Click en acciones para Ver/Editar/Eliminar

## 🎨 Personalización del Tema

Los colores se pueden personalizar en `frontend/src/index.css`:

```css
:root {
  --bg-primary: #0a0a0a;
  --bg-secondary: #1a1a1a;
  --accent-primary: #3b82f6;
  --accent-secondary: #8b5cf6;
  /* ... más variables */
}
```

## 🚢 Despliegue

### Backend (Django)

1. Configurar variables de entorno
2. Ejecutar migraciones en producción
3. Recolectar archivos estáticos: `python manage.py collectstatic`
4. Usar servidor WSGI como Gunicorn
5. Configurar nginx como reverse proxy

### Frontend (React)

1. Crear build de producción: `npm run build`
2. Servir archivos estáticos con nginx o similar
3. Configurar variable de entorno para API URL

## 🐛 Solución de Problemas

### Error: "persona: null"
- Asegúrate de que el usuario tenga un registro de Persona asociado
- Verifica que la Persona tenga un PersonaRol asignado

### Error: "No tienes permisos"
- Verifica que el rol tenga los permisos correctos en RolPermiso
- Revisa que PersonaRol esté correctamente vinculado

### Error de CORS
- Verifica que el frontend esté en la lista de `CORS_ALLOWED_ORIGINS`
- En desarrollo debe incluir `http://localhost:3000`

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto es privado y confidencial.

## 👥 Autores

- **Equipo de Desarrollo** - *Trabajo inicial*

## 📞 Contacto

Para preguntas o soporte, contactar a: [tu-email@ejemplo.com]

---

**Nota**: Este README asume que tienes Git configurado y conocimientos básicos de Django y React. Para más información sobre cada tecnología, consulta sus documentaciones oficiales.
