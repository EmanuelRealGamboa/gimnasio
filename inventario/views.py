from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import CategoriaProducto, Producto, Inventario
from .serializers import CategoriaProductoSerializer, ProductoSerializer, InventarioSerializer


# -------------------------------
# CATEGORÍA PRODUCTO
# -------------------------------
class CategoriaProductoViewSet(viewsets.ModelViewSet):
    queryset = CategoriaProducto.objects.all().order_by('nombre')
    serializer_class = CategoriaProductoSerializer


# -------------------------------
# PRODUCTOS
# -------------------------------
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all().order_by('nombre')
    serializer_class = ProductoSerializer

    def perform_update(self, serializer):
        """
        Cuando se actualiza un producto, sincroniza el inventario relacionado.
        """
        producto = serializer.save()

        try:
            inventario = Inventario.objects.get(producto=producto)
            inventario.cantidad_actual = producto.stock
            inventario.save(update_fields=['cantidad_actual'])
            print(f"✅ Inventario sincronizado desde API: {producto.nombre} → {producto.stock}")
        except Inventario.DoesNotExist:
            Inventario.objects.create(
                producto=producto,
                cantidad_actual=producto.stock,
                minimo=5
            )
            print(f"🆕 Inventario creado automáticamente para {producto.nombre}")

    def perform_create(self, serializer):
        """
        Cuando se crea un nuevo producto, también crea su inventario automáticamente.
        """
        producto = serializer.save()
        Inventario.objects.create(
            producto=producto,
            cantidad_actual=producto.stock,
            minimo=5
        )
        print(f"🆕 Inventario creado automáticamente (API): {producto.nombre}")


# -------------------------------
# INVENTARIO
# -------------------------------
class InventarioViewSet(viewsets.ModelViewSet):
    queryset = Inventario.objects.select_related('producto', 'sede').all().order_by('producto__nombre')
    serializer_class = InventarioSerializer

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
