from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentaProductoViewSet

# NOTA: VentaViewSet y PasarelaPagoViewSet fueron desregistrados (2026-06-26).
# Esos modelos (Venta, PasarelaPago, DetallePasarela) acceden a producto.stock,
# campo que ya no existe en inventario.Producto — truena con AttributeError en runtime.
# El flujo moderno de ventas usa VentaProductoViewSet.
# Los modelos legacy se conservan en models.py y sus migraciones NO se borran;
# su eliminación definitiva requiere una migración controlada (ver PLAN DE REFACTOR).

router = DefaultRouter()
router.register(r'ventas-productos', VentaProductoViewSet, basename='ventas-productos')

urlpatterns = [
    path('', include(router.urls)),
]
