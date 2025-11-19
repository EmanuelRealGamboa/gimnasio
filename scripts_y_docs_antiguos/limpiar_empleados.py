"""
Script para eliminar todos los empleados excepto el administrador
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from authentication.models import User, Persona
from empleados.models import Empleado
from roles.models import PersonaRol

def limpiar_empleados():
    print("🗑️  Iniciando limpieza de empleados...")

    # Obtener todos los usuarios con rol de empleado (que tengan un registro en Empleado)
    empleados = Empleado.objects.select_related('persona').all()

    total_eliminados = 0

    for empleado in empleados:
        persona = empleado.persona

        # Verificar si la persona tiene el rol de Administrador
        persona_rol = PersonaRol.objects.filter(persona=persona).first()

        if persona_rol and persona_rol.rol.nombre.lower() == 'administrador':
            print(f"✅ Manteniendo administrador: {persona.nombre} {persona.apellido_paterno}")
            continue

        # Eliminar el usuario (esto eliminará en cascada Persona, Empleado, etc.)
        try:
            user = User.objects.get(persona=persona)
            nombre_completo = f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"
            user.delete()
            total_eliminados += 1
            print(f"🗑️  Eliminado: {nombre_completo}")
        except User.DoesNotExist:
            # Si no hay usuario, eliminar la persona directamente
            nombre_completo = f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}"
            persona.delete()
            total_eliminados += 1
            print(f"🗑️  Eliminada persona: {nombre_completo}")

    print(f"\n✅ Limpieza completada: {total_eliminados} empleado(s) eliminado(s)")

    # Mostrar cuántos empleados quedan
    empleados_restantes = Empleado.objects.count()
    print(f"📊 Empleados restantes: {empleados_restantes}")

if __name__ == '__main__':
    limpiar_empleados()
