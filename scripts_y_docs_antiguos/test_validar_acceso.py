"""Test del endpoint validar_acceso"""
import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from control_acceso.views import validar_acceso
from django.test import RequestFactory
from django.contrib.auth import get_user_model
import json

User = get_user_model()
factory = RequestFactory()

# Obtener usuario admin
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.first()

if not user:
    print("❌ No hay usuarios. Crea uno con: python manage.py createsuperuser")
    exit(1)

print(f"Usuario: {user.email}")
print("\n" + "="*60)
print("TEST: Buscar cliente 'test'")
print("="*60)

try:
    # Crear request
    data = {
        'search_term': 'test',
        'sede_id': 1
    }

    request = factory.post(
        '/api/accesos/registros/validar_acceso/',
        data=json.dumps(data),
        content_type='application/json'
    )
    request.user = user

    # Ejecutar vista
    response = validar_acceso(request)

    print(f"\n✓ Status: {response.status_code}")
    print(f"✓ Response:")

    # Renderizar response si es necesario
    if hasattr(response, 'render'):
        response.render()

    response_data = json.loads(response.content.decode('utf-8'))
    print(json.dumps(response_data, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
