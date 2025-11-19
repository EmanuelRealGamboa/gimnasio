"""Test de la query corregida"""
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
print("TEST: Query CORREGIDA con 'usuario' en lugar de 'user'")
print("="*60)

search_term = 'test'
print(f"\nBuscando: '{search_term}'")

try:
    clientes = Cliente.objects.filter(
        Q(persona__nombre__icontains=search_term) |
        Q(persona__apellido_paterno__icontains=search_term) |
        Q(persona__apellido_materno__icontains=search_term) |
        Q(persona__telefono__icontains=search_term) |
        Q(persona__usuario__email__icontains=search_term)
    ).select_related('persona', 'persona__usuario').distinct()

    print(f"\n✓ Query ejecutada correctamente")
    print(f"✓ Clientes encontrados: {clientes.count()}")

    if clientes.exists():
        print("\nDetalles de los clientes:")
        for i, cliente in enumerate(clientes[:5], 1):
            persona = cliente.persona
            print(f"\n  {i}. ID: {cliente.persona_id}")
            print(f"     Nombre: {persona.nombre} {persona.apellido_paterno} {persona.apellido_materno or ''}")
            print(f"     Teléfono: {persona.telefono}")

            # Obtener email de forma segura
            if hasattr(persona, 'usuario') and persona.usuario:
                print(f"     Email: {persona.usuario.email}")
            else:
                print(f"     Email: (sin usuario)")

    print("\n" + "="*60)
    print("✓ TEST EXITOSO - La query funciona correctamente")
    print("="*60)

except Exception as e:
    print(f"\n❌ ERROR:")
    print(f"   {str(e)}")
    import traceback
    traceback.print_exc()
