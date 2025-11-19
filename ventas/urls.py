from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentaViewSet, PasarelaPagoViewSet, VentaProductoViewSet

router = DefaultRouter()
router.register(r'ventas', VentaViewSet, basename='ventas')
router.register(r'pasarela', PasarelaPagoViewSet, basename='pasarela')
router.register(r'ventas-productos', VentaProductoViewSet, basename='ventas-productos')

urlpatterns = [
    path('', include(router.urls)),
]
