from rest_framework import viewsets
from django.http import JsonResponse
from .models import CategoriaProducto, Producto, Inventario
from .serializers import CategoriaProductoSerializer, ProductoSerializer, InventarioSerializer


# ==== VIEWSETS ====
class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all()
    serializer_class = CategoriaProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer


class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.all()
    serializer_class = InventarioSerializer


# ==== FUNCIÓN EXTRA PARA OBTENER EL STOCK ====
def get_stock_producto(request, producto_id):
    try:
        producto = Producto.objects.get(pk=producto_id)
        return JsonResponse({'stock': producto.stock})
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
