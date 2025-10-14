from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaProductoViewSet, ProductoViewSet, InventarioViewSet
from . import views

router = DefaultRouter()
router.register(r'categorias', CategoriaProductoViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'inventario', InventarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
        path('get_stock_producto/<int:producto_id>/', views.get_stock_producto, name='get_stock_producto'),
]
