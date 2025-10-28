from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaProductoViewSet, ProductoViewSet, InventarioViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet)
router.register(r'productos', ProductoViewSet,basename='productos')
router.register(r'inventario', InventarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
