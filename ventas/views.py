from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db import transaction
from inventario.models import Inventario, Producto
from instalaciones.models import Sede
from .models import Venta, PasarelaPago, DetallePasarela, VentaProducto, DetalleVentaProducto
from .serializers import (
    VentaSerializer, PasarelaPagoSerializer, VentaProductoSerializer,
    CrearVentaProductoSerializer, DetalleVentaProductoSerializer
)
from .permissions import EsAdministradorOCajero


class VentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar ventas.
    Solo accesible por Administrador y Cajero.
    """
    queryset = Venta.objects.all().order_by('-venta_id')
    serializer_class = VentaSerializer
    permission_classes = [EsAdministradorOCajero] 


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
    """
    ViewSet para gestionar pasarelas de pago.
    Solo accesible por Administrador y Cajero.
    """
    queryset = PasarelaPago.objects.all().order_by('-pasarela_id')
    serializer_class = PasarelaPagoSerializer
    permission_classes = [EsAdministradorOCajero]

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


# =====================================================
# NUEVO VIEWSET: SISTEMA DE VENTAS CON CARRITO
# =====================================================

class VentaProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar ventas de productos con sistema de carrito.
    Solo accesible por Administrador y Cajero.

    Endpoints principales:
    - GET /api/ventas-productos/ - Listar ventas
    - GET /api/ventas-productos/{id}/ - Detalle de venta
    - POST /api/ventas-productos/crear_venta/ - Crear venta con carrito
    - POST /api/ventas-productos/{id}/cancelar/ - Cancelar venta
    - GET /api/ventas-productos/productos_disponibles/ - Productos con stock
    """
    queryset = VentaProducto.objects.select_related('cliente', 'empleado', 'sede').prefetch_related('detalles__producto').all()
    serializer_class = VentaProductoSerializer
    permission_classes = [EsAdministradorOCajero]

    def get_queryset(self):
        """
        Permite filtrar ventas por fecha, sede, estado, cliente, etc.
        Si el usuario es cajero, solo puede ver ventas de su sede.
        """
        queryset = super().get_queryset()
        user = self.request.user
        from roles.models import PersonaRol
        roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol__nombre', flat=True)
        if 'Cajero' in roles:
            try:
                cajero_sede = getattr(user.persona.empleado.cajero, 'sede', None)
                if cajero_sede:
                    queryset = queryset.filter(sede=cajero_sede)
            except Exception:
                queryset = queryset.none()

        # Filtrar por sede (solo admins pueden ver otras sedes)
        elif 'Administrador' in roles:
            sede_id = self.request.query_params.get('sede', None)
            if sede_id:
                queryset = queryset.filter(sede_id=sede_id)

        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)

        # Filtrar por cliente
        cliente_id = self.request.query_params.get('cliente', None)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        # Filtrar por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            queryset = queryset.filter(fecha_venta__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_venta__lte=fecha_hasta)

        return queryset.order_by('-fecha_venta')

    @action(detail=False, methods=['post'])
    def crear_venta(self, request):
        """
        Endpoint para crear una venta con múltiples productos (carrito).
        Usa transacción atómica: todo o nada.

        POST /api/ventas-productos/crear_venta/
        Body: {
            "cliente_id": 1,  // opcional
            "sede_id": 1,
            "metodo_pago": "efectivo",
            "productos": [
                {"producto_id": 1, "cantidad": 2, "descuento": 0},
                {"producto_id": 5, "cantidad": 1, "descuento": 10.00}
            ],
            "descuento_global": 0,
            "notas": ""
        }
        """
        serializer = CrearVentaProductoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {'error': 'Datos inválidos', 'detalles': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        try:
            with transaction.atomic():
                # 1. Crear la venta principal
                venta = VentaProducto.objects.create(
                    cliente_id=data.get('cliente_id'),
                    empleado=request.user,
                    sede_id=data['sede_id'],
                    metodo_pago=data['metodo_pago'],
                    descuento_global=data.get('descuento_global', 0),
                    notas=data.get('notas', ''),
                    subtotal=0,  # Se calculará después
                    iva=0,
                    total=0
                )

                # 2. Crear detalles y descontar stock del inventario de la sede
                from inventario.models import Inventario

                for item in data['productos']:
                    producto = Producto.objects.select_for_update().get(pk=item['producto_id'])

                    # Buscar el inventario de la sede específica
                    try:
                        inventario = Inventario.objects.select_for_update().get(
                            producto=producto,
                            sede_id=data['sede_id']
                        )
                    except Inventario.DoesNotExist:
                        raise ValidationError(
                            f"El producto '{producto.nombre}' no está disponible en esta sede"
                        )

                    # Validar stock del inventario de la sede
                    if inventario.cantidad_actual < item['cantidad']:
                        raise ValidationError(
                            f"Stock insuficiente de '{producto.nombre}' en esta sede. "
                            f"Disponible: {inventario.cantidad_actual}, Solicitado: {item['cantidad']}"
                        )

                    # Crear detalle
                    DetalleVentaProducto.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=item['cantidad'],
                        precio_unitario=producto.precio_unitario,
                        descuento=item.get('descuento', 0)
                    )

                    # Descontar del inventario de la sede
                    inventario.cantidad_actual -= item['cantidad']
                    inventario.save(update_fields=['cantidad_actual', 'ultima_actualizacion'])

                # 3. Calcular totales
                totales = venta.calcular_totales()
                venta.subtotal = totales['subtotal']
                venta.iva = totales['iva']
                venta.total = totales['total']
                venta.save(update_fields=['subtotal', 'iva', 'total'])

                # 4. Retornar venta creada
                response_serializer = VentaProductoSerializer(venta)
                return Response(
                    {
                        'message': 'Venta creada exitosamente',
                        'venta': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )

        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al crear la venta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancela una venta y restaura el stock de los productos.

        POST /api/ventas-productos/{id}/cancelar/
        """
        venta = self.get_object()

        if venta.estado == 'cancelada':
            return Response(
                {'error': 'Esta venta ya está cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                from inventario.models import Inventario

                # Restaurar stock en el inventario de la sede
                for detalle in venta.detalles.all():
                    try:
                        inventario = Inventario.objects.select_for_update().get(
                            producto=detalle.producto,
                            sede=venta.sede
                        )
                        inventario.cantidad_actual += detalle.cantidad
                        inventario.save(update_fields=['cantidad_actual', 'ultima_actualizacion'])
                    except Inventario.DoesNotExist:
                        # Si no existe inventario, crearlo con la cantidad restaurada
                        Inventario.objects.create(
                            producto=detalle.producto,
                            sede=venta.sede,
                            cantidad_actual=detalle.cantidad,
                            cantidad_minima=5,
                            cantidad_maxima=1000
                        )

                # Marcar venta como cancelada
                venta.estado = 'cancelada'
                venta.save(update_fields=['estado'])

                serializer = VentaProductoSerializer(venta)
                return Response(
                    {
                        'message': 'Venta cancelada y stock restaurado',
                        'venta': serializer.data
                    },
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {'error': f'Error al cancelar la venta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='productos-disponibles')
    def productos_disponibles(self, request):
        """
        Obtiene productos con stock disponible en una sede específica para el POS.
        Permite búsqueda por nombre, código o categoría.

        GET /api/ventas-productos/productos-disponibles/
        Query params:
        - sede: ID de la sede (REQUERIDO)
        - search: búsqueda por nombre o código
        - categoria: filtrar por categoría
        """
        from inventario.models import Inventario
        from django.db import models as django_models

        # Validar que se proporcione sede
        sede_id = request.query_params.get('sede', None)
        if not sede_id:
            return Response(
                {'error': 'Parámetro "sede" es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener inventarios con stock > 0 de la sede específica
        inventarios = Inventario.objects.filter(
            sede_id=sede_id,
            cantidad_actual__gt=0
        ).select_related('producto', 'producto__categoria', 'sede')

        # Filtrar por búsqueda
        search = request.query_params.get('search', None)
        if search:
            inventarios = inventarios.filter(
                django_models.Q(producto__nombre__icontains=search) |
                django_models.Q(producto__codigo__icontains=search)
            )

        # Filtrar por categoría
        categoria_id = request.query_params.get('categoria', None)
        if categoria_id:
            inventarios = inventarios.filter(producto__categoria_id=categoria_id)

        # Serializar respuesta
        data = []
        for inv in inventarios:
            prod = inv.producto
            data.append({
                'producto_id': prod.producto_id,
                'codigo': prod.codigo if prod.codigo else '',
                'nombre': prod.nombre if prod.nombre else 'Sin nombre',
                'categoria': prod.categoria.nombre if prod.categoria else 'Sin categoría',
                'precio_unitario': str(prod.precio_unitario) if prod.precio_unitario else '0.00',
                'stock': inv.cantidad_actual,  # Stock de la sede específica
                'sede_nombre': inv.sede.nombre,
                'estado_stock': inv.estado_stock
            })

        return Response(data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadísticas de ventas.

        GET /api/ventas-productos/estadisticas/
        Query params:
        - sede: filtrar por sede
        - fecha_desde, fecha_hasta: rango de fechas
        """
        from django.db.models import Sum, Count, Avg
        import django.db.models as models

        queryset = VentaProducto.objects.filter(estado='completada')

        # Filtros
        sede_id = request.query_params.get('sede', None)
        if sede_id:
            queryset = queryset.filter(sede_id=sede_id)

        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)
        if fecha_desde:
            queryset = queryset.filter(fecha_venta__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_venta__lte=fecha_hasta)

        # Calcular estadísticas
        stats = queryset.aggregate(
            total_ventas=Count('venta_id'),
            ingresos_totales=Sum('total'),
            ticket_promedio=Avg('total')
        )

        return Response({
            'total_ventas': stats['total_ventas'] or 0,
            'ingresos_totales': float(stats['ingresos_totales'] or 0),
            'ticket_promedio': float(stats['ticket_promedio'] or 0)
        })
