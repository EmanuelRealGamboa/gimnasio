from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db import models as django_models
from django.db.models import Avg, Count, Sum
from inventario.models import Inventario
from .models import VentaProducto
from .serializers import (
    VentaProductoSerializer,
    CrearVentaProductoSerializer,
)
from .permissions import EsAdministradorOCajero
from .services import venta_producto_cancelar, venta_producto_crear


class VentaProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar ventas de productos con sistema de carrito.
    Solo accesible por Administrador y Cajero.

    Endpoints principales:
    - GET  /api/ventas-productos/                    - Listar ventas
    - GET  /api/ventas-productos/{id}/               - Detalle de venta
    - POST /api/ventas-productos/crear_venta/        - Crear venta con carrito
    - POST /api/ventas-productos/{id}/cancelar/      - Cancelar venta
    - GET  /api/ventas-productos/productos-disponibles/ - Productos con stock
    - GET  /api/ventas-productos/estadisticas/       - Estadísticas agregadas
    """

    queryset = (
        VentaProducto.objects.select_related("cliente", "empleado", "sede")
        .prefetch_related("detalles__producto")
        .all()
    )
    serializer_class = VentaProductoSerializer
    permission_classes = [EsAdministradorOCajero]

    def get_queryset(self):
        """Filtra ventas por rol, sede, estado, cliente y rango de fechas.

        Los cajeros solo pueden ver ventas de su sede asignada.
        Los administradores pueden filtrar opcionalmente por sede.
        """
        queryset = super().get_queryset()
        user = self.request.user
        from roles.models import PersonaRol

        roles = PersonaRol.objects.filter(
            persona=user.persona
        ).values_list("rol__nombre", flat=True)

        if "Cajero" in roles:
            try:
                cajero_sede = getattr(user.persona.empleado.cajero, "sede", None)
                if cajero_sede:
                    queryset = queryset.filter(sede=cajero_sede)
                else:
                    queryset = queryset.none()
            except Exception:
                queryset = queryset.none()

        elif "Administrador" in roles:
            sede_id = self.request.query_params.get("sede")
            if sede_id:
                queryset = queryset.filter(sede_id=sede_id)

        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado=estado)

        cliente_id = self.request.query_params.get("cliente")
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        fecha_desde = self.request.query_params.get("fecha_desde")
        fecha_hasta = self.request.query_params.get("fecha_hasta")
        if fecha_desde:
            queryset = queryset.filter(fecha_venta__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_venta__lte=fecha_hasta)

        return queryset.order_by("-fecha_venta")

    @action(detail=False, methods=["post"])
    def crear_venta(self, request):
        """Crea una venta con múltiples productos (carrito). Todo o nada.

        POST /api/ventas-productos/crear_venta/
        """
        serializer = CrearVentaProductoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Datos inválidos", "detalles": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        try:
            venta = venta_producto_crear(
                empleado=request.user,
                sede_id=data["sede_id"],
                metodo_pago=data["metodo_pago"],
                productos=data["productos"],
                cliente_id=data.get("cliente_id"),
                descuento_global=data.get("descuento_global", 0),
                notas=data.get("notas", ""),
            )
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Error al crear la venta: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Venta creada exitosamente", "venta": VentaProductoSerializer(venta).data},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """Cancela una venta y restaura el stock de los productos.

        POST /api/ventas-productos/{id}/cancelar/
        """
        venta = self.get_object()
        try:
            venta = venta_producto_cancelar(venta=venta)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Error al cancelar la venta: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": "Venta cancelada y stock restaurado", "venta": VentaProductoSerializer(venta).data},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="productos-disponibles")
    def productos_disponibles(self, request):
        """Lista productos con stock disponible en una sede para el POS.

        GET /api/ventas-productos/productos-disponibles/?sede=<id>[&search=...][&categoria=<id>]
        """
        sede_id = request.query_params.get("sede")
        if not sede_id:
            return Response(
                {"error": 'Parámetro "sede" es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        inventarios = (
            Inventario.objects.filter(sede_id=sede_id, cantidad_actual__gt=0)
            .select_related("producto", "producto__categoria", "sede")
        )

        search = request.query_params.get("search")
        if search:
            inventarios = inventarios.filter(
                django_models.Q(producto__nombre__icontains=search)
                | django_models.Q(producto__codigo__icontains=search)
            )

        categoria_id = request.query_params.get("categoria")
        if categoria_id:
            inventarios = inventarios.filter(producto__categoria_id=categoria_id)

        data = []
        for inv in inventarios:
            prod = inv.producto
            data.append(
                {
                    "producto_id": prod.producto_id,
                    "codigo": prod.codigo or "",
                    "nombre": prod.nombre or "Sin nombre",
                    "categoria": prod.categoria.nombre if prod.categoria else "Sin categoría",
                    "precio_unitario": str(prod.precio_unitario) if prod.precio_unitario else "0.00",
                    "stock": inv.cantidad_actual,
                    "sede_nombre": inv.sede.nombre,
                    "estado_stock": inv.estado_stock,
                }
            )

        return Response(data)

    @action(detail=False, methods=["get"])
    def estadisticas(self, request):
        """Devuelve estadísticas agregadas de ventas completadas.

        GET /api/ventas-productos/estadisticas/?[sede=<id>][&fecha_desde=...][&fecha_hasta=...]
        """
        queryset = VentaProducto.objects.filter(estado="completada")

        sede_id = request.query_params.get("sede")
        if sede_id:
            queryset = queryset.filter(sede_id=sede_id)

        fecha_desde = request.query_params.get("fecha_desde")
        fecha_hasta = request.query_params.get("fecha_hasta")
        if fecha_desde:
            queryset = queryset.filter(fecha_venta__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_venta__lte=fecha_hasta)

        stats = queryset.aggregate(
            total_ventas=Count("venta_id"),
            ingresos_totales=Sum("total"),
            ticket_promedio=Avg("total"),
        )

        return Response(
            {
                "total_ventas": stats["total_ventas"] or 0,
                "ingresos_totales": float(stats["ingresos_totales"] or 0),
                "ticket_promedio": float(stats["ticket_promedio"] or 0),
            }
        )
