"""Test directo de la query de clientes"""
import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from django.db.models import Q
from clientes.models import Cliente

print("="*60)
print("TEST: Query de búsqueda de clientes")
print("="*60)

search_term = 'test'
print(f"\nBuscando: '{search_term}'")

try:
    # Esta es la query NUEVA (con email)
    print("\n1. Probando query CON email:")
    clientes = Cliente.objects.filter(
        Q(persona__nombre__icontains=search_term) |
        Q(persona__apellido_paterno__icontains=search_term) |
        Q(persona__apellido_materno__icontains=search_term) |
        Q(persona__telefono__icontains=search_term) |
        Q(persona__user__email__icontains=search_term)
    ).select_related('persona', 'persona__user').distinct()

    print(f"   ✓ Query ejecutada")
    print(f"   ✓ Clientes encontrados: {clientes.count()}")

    if clientes.exists():
        for cliente in clientes[:5]:
            persona = cliente.persona
            print(f"\n   Cliente ID: {cliente.persona_id}")
            print(f"   Nombre: {persona.nombre} {persona.apellido_paterno}")
            print(f"   Teléfono: {persona.telefono}")

            # Intentar obtener email
            try:
                if hasattr(persona, 'user') and persona.user:
                    print(f"   Email: {persona.user.email}")
                else:
                    print(f"   Email: (sin usuario asociado)")
            except Exception as e:
                print(f"   Email: ERROR - {str(e)}")

except Exception as e:
    print(f"\n❌ ERROR al ejecutar query:")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("\n2. Probando query SIN email (original):")

try:
    clientes_sin_email = Cliente.objects.filter(
        Q(persona__nombre__icontains=search_term) |
        Q(persona__apellido_paterno__icontains=search_term) |
        Q(persona__apellido_materno__icontains=search_term) |
        Q(persona__telefono__icontains=search_term)
    ).select_related('persona').distinct()

    print(f"   ✓ Query ejecutada")
    print(f"   ✓ Clientes encontrados: {clientes_sin_email.count()}")

except Exception as e:
    print(f"\n❌ ERROR:")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()
