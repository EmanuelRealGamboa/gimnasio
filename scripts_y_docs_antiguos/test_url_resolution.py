"""Test de resolución de URLs"""
import os
import sys
import django

# Configurar encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from django.urls import resolve, reverse
from django.core.exceptions import ViewDoesNotExist

print("="*60)
print("TEST: Resolución de URL de validar_acceso")
print("="*60)

# Test 1: Resolver URL por path
print("\n1. Resolviendo por path:")
try:
    match = resolve('/api/accesos/registros/validar_acceso/')
    print(f"   ✓ URL encontrada")
    print(f"   ✓ View: {match.func.__name__}")
    print(f"   ✓ App: {match.app_name}")
    print(f"   ✓ URL name: {match.url_name}")
except Exception as e:
    print(f"   ✗ ERROR: {str(e)}")

# Test 2: Reverse por nombre
print("\n2. Reverse por nombre:")
try:
    url = reverse('validar-acceso')
    print(f"   ✓ URL generada: {url}")
except Exception as e:
    print(f"   ✗ ERROR: {str(e)}")

# Test 3: Listar todas las URLs de control_acceso
print("\n3. URLs registradas en control_acceso:")
from django.urls import get_resolver
resolver = get_resolver()

for pattern in resolver.url_patterns:
    if 'accesos' in str(pattern.pattern):
        print(f"\n   Patrón: {pattern.pattern}")
        if hasattr(pattern, 'url_patterns'):
            for sub in pattern.url_patterns:
                try:
                    print(f"      - {sub.pattern} → {sub.callback.__name__ if hasattr(sub, 'callback') else 'N/A'}")
                except:
                    print(f"      - {sub.pattern}")

print("\n" + "="*60)
