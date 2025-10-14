from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacturaViewSet, DetalleFacturaViewSet, PagoViewSet

router = DefaultRouter()
router.register(r'facturas', FacturaViewSet)
router.register(r'detalles', DetalleFacturaViewSet)
router.register(r'pagos', PagoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
