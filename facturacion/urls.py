from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaViewSet, DetalleFacturaViewSet, PagoViewSet

# =====================================================
# 🔹 RUTAS PRINCIPALES DE LA APP DE FACTURACIÓN (API)
# =====================================================

router = DefaultRouter()
router.register(r'facturas', FacturaViewSet, basename='factura')
router.register(r'detalles', DetalleFacturaViewSet, basename='detallefactura')
router.register(r'pagos', PagoViewSet, basename='pago')

urlpatterns = [
    # Incluye todas las rutas generadas por el router
    path('', include(router.urls)),
]
