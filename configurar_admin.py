#!/usr/bin/env python
"""
Script para configurar el usuario administrador con todos los permisos necesarios.
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from authentication.models import User, Persona
from roles.models import Rol, Permiso, RolPermiso, PersonaRol
from datetime import date

def configurar_admin():
    print("=" * 60)
    print("CONFIGURACIÓN DEL SISTEMA DE GIMNASIO")
    print("=" * 60)
    
    # 1. Crear Permisos
    print("\n[1/5] Creando permisos...")
    permisos_data = [
        {'nombre': 'gestionar_empleados', 'descripcion': 'Puede gestionar empleados'},
        {'nombre': 'gestionar_entrenamientos', 'descripcion': 'Puede gestionar entrenamientos'},
        {'nombre': 'gestionar_acceso', 'descripcion': 'Puede gestionar el acceso al gimnasio'},
        {'nombre': 'gestionar_instalaciones', 'descripcion': 'Puede gestionar instalaciones'},
        {'nombre': 'gestionar_limpieza', 'descripcion': 'Puede gestionar limpieza'},
    ]
    
    permisos_creados = {}
    for p_data in permisos_data:
        permiso, created = Permiso.objects.get_or_create(
            nombre=p_data['nombre'],
            defaults={'descripcion': p_data['descripcion']}
        )
        permisos_creados[p_data['nombre']] = permiso
        status = "✓ Creado" if created else "✓ Ya existe"
        print(f"  {status}: {permiso.nombre}")
    
    # 2. Crear Roles
    print("\n[2/5] Creando roles...")
    roles_config = {
        'Administrador': ['gestionar_empleados'],
        'Entrenador': ['gestionar_entrenamientos'],
        'Recepcionista': ['gestionar_acceso'],
        'Supervisor de Instalaciones': ['gestionar_instalaciones'],
        'Personal de Limpieza': ['gestionar_limpieza'],
    }
    
    roles_creados = {}
    for rol_nombre, permisos_nombres in roles_config.items():
        rol, created = Rol.objects.get_or_create(
            nombre=rol_nombre,
            defaults={'descripcion': f'Rol de {rol_nombre}'}
        )
        roles_creados[rol_nombre] = rol
        status = "✓ Creado" if created else "✓ Ya existe"
        print(f"  {status}: {rol.nombre}")
        
        # Asignar permisos al rol
        for permiso_nombre in permisos_nombres:
            permiso = permisos_creados[permiso_nombre]
            RolPermiso.objects.get_or_create(rol=rol, permiso=permiso)
            print(f"    → Permiso asignado: {permiso_nombre}")
    
    # 3. Obtener o crear el usuario administrador
    print("\n[3/5] Configurando usuario administrador...")
    try:
        user = User.objects.get(email='admin@gimnasio.com')
        print(f"  ✓ Usuario encontrado: {user.email}")
    except User.DoesNotExist:
        print("  ✗ Usuario no encontrado")
        return
    
    # 4. Crear Persona para el usuario si no existe
    print("\n[4/5] Creando registro de Persona...")
    if not hasattr(user, 'persona') or user.persona is None:
        persona = Persona.objects.create(
            nombre='Administrador',
            apellido_paterno='Sistema',
            apellido_materno='Gimnasio',
            telefono='0000000000',
        )
        user.persona = persona
        user.save()
        print(f"  ✓ Persona creada: {persona.nombre} {persona.apellido_paterno}")
    else:
        persona = user.persona
        print(f"  ✓ Persona ya existe: {persona.nombre} {persona.apellido_paterno}")
    
    # 5. Asignar rol de Administrador
    print("\n[5/5] Asignando rol de Administrador...")
    rol_admin = roles_creados['Administrador']
    persona_rol, created = PersonaRol.objects.get_or_create(
        persona=persona,
        rol=rol_admin
    )
    status = "✓ Asignado" if created else "✓ Ya estaba asignado"
    print(f"  {status}: Rol {rol_admin.nombre} → {persona.nombre}")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("✓ CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("\n📋 CREDENCIALES DE ACCESO:")
    print(f"   Email:    admin@gimnasio.com")
    print(f"   Password: admin123")
    print(f"   Rol:      Administrador")
    print(f"\n🚀 ACCESO AL SISTEMA:")
    print(f"   Frontend: http://localhost:3000")
    print(f"   Backend:  http://localhost:8000")
    print(f"   Admin:    http://localhost:8000/admin")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        configurar_admin()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

