import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from roles.models import Permiso, Rol, RolPermiso, PersonaRol
from authentication.models import User, Persona
from django.utils import timezone

print("=" * 60)
print("ASIGNANDO ROL DE ADMINISTRADOR AL SUPERUSUARIO")
print("=" * 60)

# Buscar superusuario
superuser = User.objects.filter(is_superuser=True).first()

if not superuser:
    print("\nERROR: No se encontró superusuario.")
    print("Crear uno con: python manage.py createsuperuser")
    exit(1)

print(f"\nSuperusuario encontrado: {superuser.email}")

# Verificar si tiene Persona
if not hasattr(superuser, 'persona') or superuser.persona is None:
    print("Creando registro de Persona...")
    persona = Persona.objects.create(
        nombre='Admin',
        apellido_paterno='Sistema',
        apellido_materno='Principal',
        telefono='0000000000'
    )
    # Vincular la persona al usuario
    superuser.persona = persona
    superuser.save()
    print(f"Persona creada: {persona.nombre} {persona.apellido_paterno}")
else:
    persona = superuser.persona
    print(f"Persona existente: {persona.nombre} {persona.apellido_paterno}")

# Buscar o crear el rol de Administrador
rol_admin, created = Rol.objects.get_or_create(
    nombre='Administrador',
    defaults={'descripcion': 'Administrador del sistema con acceso total'}
)

# Buscar o crear el permiso
permiso_empleados, created = Permiso.objects.get_or_create(
    nombre='gestionar_empleados',
    defaults={'descripcion': 'Puede gestionar empleados'}
)

# Asignar permiso al rol
RolPermiso.objects.get_or_create(rol=rol_admin, permiso=permiso_empleados)

# Asignar rol a la persona
persona_rol, created = PersonaRol.objects.get_or_create(
    persona=persona,
    rol=rol_admin
)

status = "asignado correctamente" if created else "ya estaba asignado"
print(f"\nRol Administrador {status}")

print("\n" + "=" * 60)
print("CONFIGURACION COMPLETADA")
print("=" * 60)
print(f"\nUsuario: {superuser.email}")
print(f"Persona: {persona.nombre} {persona.apellido_paterno}")
print(f"Rol: {rol_admin.nombre}")
print(f"Permiso: {permiso_empleados.nombre}")
print("\nPuedes iniciar el servidor con:")
print("  python manage.py runserver")
print("=" * 60)
