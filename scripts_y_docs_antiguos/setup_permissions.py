"""
Script para configurar roles y permisos del sistema
Ejecutar con: python manage.py shell < setup_permissions.py
"""

from roles.models import Permiso, Rol, RolPermiso, PersonaRol
from authentication.models import User, Persona
from django.utils import timezone

print("=" * 60)
print("CONFIGURACIÓN DE ROLES Y PERMISOS DEL SISTEMA DE GIMNASIO")
print("=" * 60)

# 1. CREAR PERMISOS
print("\n1. Creando permisos...")

permisos_data = [
    {
        'nombre': 'gestionar_empleados',
        'descripcion': 'Puede gestionar empleados del sistema'
    },
    {
        'nombre': 'gestionar_entrenamientos',
        'descripcion': 'Puede gestionar entrenamientos y rutinas'
    },
    {
        'nombre': 'gestionar_acceso',
        'descripcion': 'Puede gestionar el acceso al gimnasio'
    },
    {
        'nombre': 'gestionar_instalaciones',
        'descripcion': 'Puede gestionar instalaciones y equipamiento'
    },
    {
        'nombre': 'gestionar_limpieza',
        'descripcion': 'Puede gestionar tareas de limpieza'
    },
]

permisos_creados = {}
for p_data in permisos_data:
    permiso, created = Permiso.objects.get_or_create(
        nombre=p_data['nombre'],
        defaults={'descripcion': p_data['descripcion']}
    )
    permisos_creados[p_data['nombre']] = permiso
    status = "✓ Creado" if created else "✓ Ya existe"
    print(f"  {status}: {p_data['nombre']}")

# 2. CREAR ROLES
print("\n2. Creando roles...")

roles_config = {
    'Administrador': {
        'descripcion': 'Administrador del sistema con acceso total a gestión de empleados',
        'permisos': ['gestionar_empleados']
    },
    'Entrenador': {
        'descripcion': 'Entrenador personal con acceso a gestión de entrenamientos',
        'permisos': ['gestionar_entrenamientos']
    },
    'Recepcionista': {
        'descripcion': 'Personal de recepción con control de acceso',
        'permisos': ['gestionar_acceso']
    },
    'Supervisor de Instalaciones': {
        'descripcion': 'Supervisor de instalaciones y equipamiento',
        'permisos': ['gestionar_instalaciones']
    },
    'Personal de Limpieza': {
        'descripcion': 'Personal encargado de limpieza y mantenimiento',
        'permisos': ['gestionar_limpieza']
    },
}

roles_creados = {}
for rol_nombre, rol_data in roles_config.items():
    # Crear rol
    rol, created = Rol.objects.get_or_create(
        nombre=rol_nombre,
        defaults={'descripcion': rol_data['descripcion']}
    )
    roles_creados[rol_nombre] = rol
    status = "✓ Creado" if created else "✓ Ya existe"
    print(f"  {status}: {rol_nombre}")

    # Asignar permisos al rol
    for permiso_nombre in rol_data['permisos']:
        permiso = permisos_creados[permiso_nombre]
        RolPermiso.objects.get_or_create(rol=rol, permiso=permiso)
        print(f"    → Permiso asignado: {permiso_nombre}")

# 3. MOSTRAR RESUMEN
print("\n" + "=" * 60)
print("RESUMEN DE CONFIGURACIÓN")
print("=" * 60)

print(f"\nPermisos totales: {Permiso.objects.count()}")
for permiso in Permiso.objects.all():
    print(f"  • {permiso.nombre}: {permiso.descripcion}")

print(f"\nRoles totales: {Rol.objects.count()}")
for rol in Rol.objects.all():
    permisos = [rp.permiso.nombre for rp in RolPermiso.objects.filter(rol=rol)]
    print(f"  • {rol.nombre}")
    print(f"    Permisos: {', '.join(permisos)}")

# 4. VERIFICAR/CREAR USUARIO ADMIN
print("\n" + "=" * 60)
print("CONFIGURACIÓN DE USUARIO ADMINISTRADOR")
print("=" * 60)

# Buscar superusuario
superuser = User.objects.filter(is_superuser=True).first()

if superuser:
    print(f"\n✓ Superusuario encontrado: {superuser.email}")

    # Verificar si tiene Persona
    if not hasattr(superuser, 'persona') or superuser.persona is None:
        print("  → Creando registro de Persona...")
        persona = Persona.objects.create(
            nombre='Admin',
            apellido_paterno='Sistema',
            apellido_materno='Principal',
            telefono='0000000000',
            puesto='Administrador del Sistema',
            departamento='Tecnología',
            fecha_contratacion=timezone.now().date(),
            salario=50000.00,
            rfc='XAXX010101000',
            user=superuser
        )
        print(f"  ✓ Persona creada: {persona.nombre} {persona.apellido_paterno}")
    else:
        persona = superuser.persona
        print(f"  ✓ Persona existente: {persona.nombre} {persona.apellido_paterno}")

    # Asignar rol de Administrador
    rol_admin = roles_creados['Administrador']
    persona_rol, created = PersonaRol.objects.get_or_create(
        persona=persona,
        rol=rol_admin
    )
    status = "asignado" if created else "ya estaba asignado"
    print(f"  ✓ Rol Administrador {status}")

else:
    print("\n⚠ No se encontró superusuario.")
    print("  Crear uno con: python manage.py createsuperuser")
    print("  Luego ejecutar este script nuevamente.")

# 5. INSTRUCCIONES FINALES
print("\n" + "=" * 60)
print("CONFIGURACIÓN COMPLETADA")
print("=" * 60)
print("\nSistema de Roles Configurado:")
print("\n┌─────────────────────────────┬──────────────────────────┐")
print("│ ROL                         │ PERMISO                  │")
print("├─────────────────────────────┼──────────────────────────┤")
print("│ Administrador               │ gestionar_empleados      │")
print("│ Entrenador                  │ gestionar_entrenamientos │")
print("│ Recepcionista               │ gestionar_acceso         │")
print("│ Supervisor de Instalaciones│ gestionar_instalaciones  │")
print("│ Personal de Limpieza        │ gestionar_limpieza       │")
print("└─────────────────────────────┴──────────────────────────┘")

print("\nDashboards por Rol:")
print("  • Administrador → /dashboard-admin")
print("  • Entrenador → /dashboard-entrenador")
print("  • Recepcionista → /dashboard-recepcion")
print("  • Supervisor de Instalaciones → /dashboard-supervisor")
print("  • Personal de Limpieza → /dashboard-limpieza")

print("\nPróximos pasos:")
print("  1. Iniciar el backend: python manage.py runserver")
print("  2. Iniciar el frontend: cd frontend && npm start")
print("  3. Acceder a http://localhost:3000")
print("  4. Iniciar sesión con el superusuario")
print("\n✓ El sistema redirigirá automáticamente al dashboard según el rol")
print("=" * 60)
