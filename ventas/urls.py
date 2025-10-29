from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VentaViewSet, PasarelaPagoViewSet

router = DefaultRouter()
router.register(r'ventas', VentaViewSet, basename='ventas')
router.register(r'pasarela', PasarelaPagoViewSet, basename='pasarela')

urlpatterns = [
    path('', include(router.urls)),
]
