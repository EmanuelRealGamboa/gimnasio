# Frontend - Sistema de Gestión de Gimnasio

Frontend en React para el sistema de gestión de empleados del gimnasio.

## Características

- ✅ Login con autenticación JWT
- ✅ Lista de empleados
- ✅ Crear nuevo empleado
- ✅ Editar empleado existente
- ✅ Ver detalles de empleado
- ✅ Eliminar empleado
- ✅ Rutas protegidas
- ✅ Refresh automático de tokens
- ✅ Interfaz moderna y responsiva

## Requisitos Previos

- Node.js 14+ y npm
- Backend de Django corriendo en `http://localhost:8000`

## Instalación

1. Las dependencias ya están instaladas, pero si necesitas reinstalar:

```bash
npm install
```

## Ejecución

1. Inicia el servidor de desarrollo:

```bash
npm start
```

2. Abre tu navegador en `http://localhost:3000`

## Credenciales de Prueba

Para probar la aplicación necesitas:
- Un usuario con el permiso `gestionar_empleados`
- Email y contraseña del usuario

Puedes crear un superusuario desde Django:
```bash
python manage.py createsuperuser
```

## Estructura del Proyecto

```
src/
├── components/          # Componentes React
│   ├── Login.js        # Página de login
│   ├── EmployeeList.js # Lista de empleados
│   ├── EmployeeForm.js # Formulario crear/editar
│   ├── EmployeeDetail.js # Detalles de empleado
│   └── ProtectedRoute.js # Componente de rutas protegidas
├── services/           # Servicios de API
│   ├── api.js         # Configuración de axios
│   ├── authService.js # Servicio de autenticación
│   └── employeeService.js # Servicio de empleados
├── App.js             # Componente principal con rutas
└── App.css            # Estilos globales
```

## Rutas

- `/login` - Página de inicio de sesión
- `/employees` - Lista de empleados
- `/employees/new` - Crear nuevo empleado
- `/employees/edit/:id` - Editar empleado
- `/employees/:id` - Ver detalles de empleado

## Tecnologías

- React 18
- React Router DOM 6
- Axios
- CSS3 (sin frameworks adicionales)
