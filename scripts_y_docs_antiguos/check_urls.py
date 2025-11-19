import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from rest_framework.routers import DefaultRouter
from ventas.views import VentaProductoViewSet

router = DefaultRouter()
router.register(r'ventas-productos', VentaProductoViewSet, basename='ventas-productos')

print("URLs registradas:")
for pattern in router.urls:
    print(f"  {pattern.pattern}")
