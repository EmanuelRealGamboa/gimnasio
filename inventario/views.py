import logging

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import CategoriaProducto, Producto, Inventario
from .serializers import CategoriaProductoSerializer, ProductoSerializer, InventarioSerializer
from .permissions import EsAdministradorOCajero

logger = logging.getLogger(__name__)


# -------------------------------
# CATEGORÍA PRODUCTO
# -------------------------------
class CategoriaProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de productos.
    Solo accesible por Administrador y Cajero.
    """
    queryset = CategoriaProducto.objects.all().order_by('nombre')
    serializer_class = CategoriaProductoSerializer
    permission_classes = [EsAdministradorOCajero]


# -------------------------------
# PRODUCTOS
# -------------------------------
class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar productos.
    Solo accesible por Administrador y Cajero.
    """
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer
    permission_classes = [EsAdministradorOCajero]

    def perform_update(self, serializer):
        """
        Actualiza un producto sin modificar inventarios.
        El stock se gestiona desde el modelo Inventario por sede.
        """
        serializer.save()

    def perform_create(self, serializer):
        """
        Crea un producto. El serializer se encarga de crear el inventario inicial.
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Elimina un producto. Si tiene ventas asociadas, retorna error claro.
        """
        from django.db.models import ProtectedError
        from rest_framework.exceptions import ValidationError

        try:
            instance.delete()
        except ProtectedError:
            raise ValidationError({
                'detail': 'No se puede eliminar este producto porque tiene ventas asociadas. '
                         'Puedes desactivarlo editándolo y cambiando su estado a "Inactivo".'
            })


# -------------------------------
# INVENTARIO
# -------------------------------
class InventarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar inventario.
    Solo accesible por Administrador y Cajero.
    """
    queryset = Inventario.objects.select_related('producto', 'sede').all().order_by('producto__nombre')
    serializer_class = InventarioSerializer
    permission_classes = [EsAdministradorOCajero]

    @action(detail=False, methods=['get'])
    def filtrar(self, request):
        """
        Filtro avanzado:
        /api/inventario/filtrar/?tipo=nombre&valor=proteina&stock=con_stock
        """
        tipo = request.GET.get('tipo', None)
        valor = request.GET.get('valor', None)
        stock = request.GET.get('stock', 'todos')

        inventarios = Inventario.objects.select_related('producto', 'sede')

        if stock == 'con_stock':
            inventarios = inventarios.filter(cantidad_actual__gt=0)
        elif stock == 'sin_stock':
            inventarios = inventarios.filter(cantidad_actual__lte=0)

        if tipo == 'nombre' and valor:
            inventarios = inventarios.filter(producto__nombre__icontains=valor)
        elif tipo == 'codigo' and valor:
            inventarios = inventarios.filter(producto__codigo__icontains=valor)

        serializer = self.get_serializer(inventarios, many=True)
        return Response(serializer.data)
