"""
Script para probar el endpoint de validar_acceso
"""
import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from control_acceso.views import validar_acceso
from authentication.models import Persona
import json

# Crear factory para requests
factory = RequestFactory()
User = get_user_model()

# Crear usuario de prueba
try:
    user = User.objects.first()
    if not user:
        print("❌ No hay usuarios en la base de datos")
        print("   Crea un usuario primero con: python manage.py createsuperuser")
        exit(1)

    print(f"✓ Usuario de prueba: {user.email}")

    # Crear request POST
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

    # Ejecutar la vista
    print("\n📡 Ejecutando vista validar_acceso...")
    response = validar_acceso(request)

    print(f"\n✓ Status Code: {response.status_code}")
    print(f"✓ Response Data:")
    print(json.dumps(json.loads(response.content), indent=2, ensure_ascii=False))

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
