from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from inventario.models import Inventario
from .models import Venta, PasarelaPago, DetallePasarela
from .serializers import VentaSerializer, PasarelaPagoSerializer



class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all().order_by('-venta_id')
    serializer_class = VentaSerializer
    permission_classes = [AllowAny] 


    @action(detail=False, methods=['get'], url_path='buscar_producto')
    def buscar_producto(self, request):
        valor = request.GET.get('valor', None)
        tipo = request.GET.get('tipo', 'nombre')

        if not valor:
            return Response(
                {'error': 'Debe ingresar un valor para buscar.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if tipo == 'codigo':
            inventarios = Inventario.objects.select_related('producto', 'sede').filter(
                producto__codigo__exact=valor
            )
        else:

            inventarios = Inventario.objects.select_related('producto', 'sede').filter(
                producto__nombre__icontains=valor
            )

        if not inventarios.exists():
            return Response(
                {'error': 'No se encontraron productos con ese valor.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = []
        for inv in inventarios:
            data.append({
                'inventario_id': inv.inventario_id,
                'codigo_producto': inv.producto.codigo,
                'nombre': inv.producto.nombre,
                'precio': inv.producto.precio_unitario,
                'cantidad_actual': inv.cantidad_actual,
                'minimo': inv.minimo,
                'sede': inv.sede.nombre,
            })

        return Response(data)



class PasarelaPagoViewSet(viewsets.ModelViewSet):
    queryset = PasarelaPago.objects.all().order_by('-pasarela_id')
    serializer_class = PasarelaPagoSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        Crea la pasarela de pago y ejecuta las validaciones de cada detalle.
        Si algo falla, se cancela toda la operación.
        """
        pasarela = serializer.save()
        errores = []

        for detalle in pasarela.detalles.all():
            try:
                detalle.save()  
            except ValidationError as e:
                errores.extend(e.messages)

        if errores:
            pasarela.delete()
            raise ValidationError(errores)

        pasarela.total_general = sum(d.total for d in pasarela.detalles.all())
        pasarela.save()
