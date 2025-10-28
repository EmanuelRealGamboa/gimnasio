from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaActivoViewSet,
    ProveedorServicioViewSet,
    ActivoViewSet,
    MantenimientoViewSet,
    OrdenMantenimientoViewSet
)

router = DefaultRouter()
router.register(r'categorias-activo', CategoriaActivoViewSet, basename='categoria-activo')
router.register(r'proveedores', ProveedorServicioViewSet, basename='proveedor')
router.register(r'activos', ActivoViewSet, basename='activo')
router.register(r'mantenimientos', MantenimientoViewSet, basename='mantenimiento')
router.register(r'ordenes', OrdenMantenimientoViewSet, basename='orden-mantenimiento')

urlpatterns = [
    path('', include(router.urls)),
]
