from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Sum, Avg
from datetime import timedelta

from .models import CategoriaActivo, ProveedorServicio, Activo, Mantenimiento, OrdenMantenimiento
from .serializers import (
    CategoriaActivoSerializer,
    ProveedorServicioListSerializer, ProveedorServicioSerializer,
    ActivoListSerializer, ActivoDetailSerializer, ActivoCreateUpdateSerializer,
    MantenimientoListSerializer, MantenimientoDetailSerializer, MantenimientoCreateUpdateSerializer,
    OrdenMantenimientoListSerializer, OrdenMantenimientoDetailSerializer, OrdenMantenimientoCreateUpdateSerializer
)


class CategoriaActivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar categorías de activos.
    Permite CRUD completo y filtrado.
    """
    queryset = CategoriaActivo.objects.all()
    serializer_class = CategoriaActivoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    filterset_fields = ['activo']
    ordering_fields = ['nombre', 'categoria_activo_id']
    ordering = ['nombre']

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Obtiene solo las categorías activas"""
        categorias = self.queryset.filter(activo=True)
        serializer = self.get_serializer(categorias, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_activo(self, request, pk=None):
        """Activa o desactiva una categoría"""
        categoria = self.get_object()
        categoria.activo = not categoria.activo
        categoria.save()
        serializer = self.get_serializer(categoria)
        return Response(serializer.data)


class ProveedorServicioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar proveedores de servicios.
    Incluye filtros y acciones personalizadas.
    """
    queryset = ProveedorServicio.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['nombre_empresa', 'nombre_contacto', 'telefono', 'email']
    filterset_fields = ['activo']
    ordering_fields = ['nombre_empresa', 'fecha_registro']
    ordering = ['nombre_empresa']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProveedorServicioListSerializer
        return ProveedorServicioSerializer

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Obtiene solo los proveedores activos"""
        proveedores = self.queryset.filter(activo=True)
        serializer = self.get_serializer(proveedores, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_activo(self, request, pk=None):
        """Activa o desactiva un proveedor"""
        proveedor = self.get_object()
        proveedor.activo = not proveedor.activo
        proveedor.save()
        serializer = self.get_serializer(proveedor)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def mantenimientos(self, request, pk=None):
        """Obtiene los mantenimientos realizados por este proveedor"""
        proveedor = self.get_object()
        mantenimientos = proveedor.mantenimientos.all()
        serializer = MantenimientoListSerializer(mantenimientos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de proveedores"""
        total = self.queryset.count()
        activos = self.queryset.filter(activo=True).count()

        return Response({
            'total_proveedores': total,
            'proveedores_activos': activos,
            'proveedores_inactivos': total - activos
        })


class ActivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar activos del gimnasio.
    Incluye filtros avanzados, búsqueda y acciones personalizadas.
    """
    queryset = Activo.objects.select_related('categoria', 'sede', 'espacio', 'creado_por').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre', 'marca', 'modelo', 'numero_serie']
    filterset_fields = ['categoria', 'estado', 'sede', 'espacio']
    ordering_fields = ['codigo', 'nombre', 'fecha_compra', 'valor', 'fecha_creacion']
    ordering = ['-fecha_creacion']

    def get_serializer_class(self):
        if self.action == 'list':
            return ActivoListSerializer
        elif self.action == 'retrieve':
            return ActivoDetailSerializer
        return ActivoCreateUpdateSerializer

    def perform_create(self, serializer):
        """Asignar el usuario que crea el activo"""
        serializer.save(creado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Obtiene activos agrupados por estado"""
        estado = request.query_params.get('estado', None)
        if estado:
            activos = self.queryset.filter(estado=estado)
            serializer = self.get_serializer(activos, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Debe proporcionar el parámetro estado'}, status=400)

    @action(detail=False, methods=['get'])
    def por_sede(self, request):
        """Obtiene activos de una sede específica"""
        sede_id = request.query_params.get('sede_id', None)
        if sede_id:
            activos = self.queryset.filter(sede_id=sede_id)
            serializer = self.get_serializer(activos, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Debe proporcionar el parámetro sede_id'}, status=400)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado de un activo"""
        activo = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in dict(Activo.ESTADO_CHOICES):
            return Response(
                {'error': 'Estado inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        activo.estado = nuevo_estado
        activo.save()
        serializer = self.get_serializer(activo)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historial_mantenimiento(self, request, pk=None):
        """Obtiene el historial completo de mantenimientos de un activo"""
        activo = self.get_object()
        mantenimientos = activo.mantenimientos.all()
        serializer = MantenimientoListSerializer(mantenimientos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def proximos_mantenimientos(self, request):
        """Obtiene activos con mantenimientos próximos (15 días)"""
        fecha_limite = timezone.now().date() + timedelta(days=15)
        activos_con_mantenimiento = Mantenimiento.objects.filter(
            estado='pendiente',
            fecha_programada__lte=fecha_limite,
            fecha_programada__gte=timezone.now().date()
        ).values_list('activo_id', flat=True)

        activos = self.queryset.filter(activo_id__in=activos_con_mantenimiento)
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas generales de activos"""
        total = self.queryset.count()
        por_estado = self.queryset.values('estado').annotate(count=Count('activo_id'))
        por_categoria = self.queryset.values('categoria__nombre').annotate(count=Count('activo_id'))

        valor_total = self.queryset.aggregate(Sum('valor'))['valor__sum'] or 0
        valor_promedio = self.queryset.aggregate(Avg('valor'))['valor__avg'] or 0

        # Activos con mantenimientos próximos (15 días)
        fecha_limite = timezone.now().date() + timedelta(days=15)
        proximos_mantenimientos = Mantenimiento.objects.filter(
            estado='pendiente',
            fecha_programada__lte=fecha_limite,
            fecha_programada__gte=timezone.now().date()
        ).count()

        return Response({
            'total_activos': total,
            'por_estado': {item['estado']: item['count'] for item in por_estado},
            'por_categoria': {item['categoria__nombre']: item['count'] for item in por_categoria},
            'valor_total': float(valor_total),
            'valor_promedio': float(valor_promedio),
            'alertas_mantenimiento': proximos_mantenimientos
        })


class MantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar mantenimientos.
    Incluye filtros, alertas y acciones personalizadas.
    """
    queryset = Mantenimiento.objects.select_related(
        'activo', 'activo__categoria', 'activo__sede',
        'proveedor_servicio', 'empleado_responsable', 'creado_por'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['activo__codigo', 'activo__nombre', 'descripcion']
    filterset_fields = ['tipo_mantenimiento', 'estado', 'activo', 'proveedor_servicio', 'empleado_responsable']
    ordering_fields = ['fecha_programada', 'fecha_ejecucion', 'costo', 'fecha_creacion']
    ordering = ['-fecha_programada']

    def get_serializer_class(self):
        if self.action == 'list':
            return MantenimientoListSerializer
        elif self.action == 'retrieve':
            return MantenimientoDetailSerializer
        return MantenimientoCreateUpdateSerializer

    def perform_create(self, serializer):
        """Asignar el usuario que crea el mantenimiento"""
        serializer.save(creado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Obtiene mantenimientos pendientes"""
        mantenimientos = self.queryset.filter(estado='pendiente')
        serializer = self.get_serializer(mantenimientos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def en_proceso(self, request):
        """Obtiene mantenimientos en proceso"""
        mantenimientos = self.queryset.filter(estado='en_proceso')
        serializer = self.get_serializer(mantenimientos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def alertas(self, request):
        """Obtiene mantenimientos que requieren atención (próximos 15 días)"""
        fecha_limite = timezone.now().date() + timedelta(days=15)
        mantenimientos = self.queryset.filter(
            estado='pendiente',
            fecha_programada__lte=fecha_limite,
            fecha_programada__gte=timezone.now().date()
        )
        serializer = self.get_serializer(mantenimientos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Obtiene mantenimientos vencidos (fecha programada pasada y aún pendientes)"""
        mantenimientos = self.queryset.filter(
            estado='pendiente',
            fecha_programada__lt=timezone.now().date()
        )
        serializer = self.get_serializer(mantenimientos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        """Cambia el estado del mantenimiento a 'en_proceso'"""
        mantenimiento = self.get_object()

        if mantenimiento.estado != 'pendiente':
            return Response(
                {'error': 'Solo se pueden iniciar mantenimientos pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )

        mantenimiento.estado = 'en_proceso'
        mantenimiento.save()
        serializer = self.get_serializer(mantenimiento)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Completa un mantenimiento"""
        mantenimiento = self.get_object()

        if mantenimiento.estado == 'completado':
            return Response(
                {'error': 'Este mantenimiento ya está completado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        fecha_ejecucion = request.data.get('fecha_ejecucion', timezone.now().date())
        observaciones = request.data.get('observaciones', '')
        costo = request.data.get('costo', mantenimiento.costo)

        mantenimiento.estado = 'completado'
        mantenimiento.fecha_ejecucion = fecha_ejecucion
        mantenimiento.observaciones = observaciones
        mantenimiento.costo = costo
        mantenimiento.save()

        serializer = self.get_serializer(mantenimiento)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancela un mantenimiento"""
        mantenimiento = self.get_object()

        if mantenimiento.estado == 'completado':
            return Response(
                {'error': 'No se puede cancelar un mantenimiento completado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        motivo = request.data.get('motivo', '')
        mantenimiento.estado = 'cancelado'
        mantenimiento.observaciones = f"Cancelado: {motivo}"
        mantenimiento.save()

        serializer = self.get_serializer(mantenimiento)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de mantenimientos"""
        total = self.queryset.count()
        por_estado = self.queryset.values('estado').annotate(count=Count('mantenimiento_id'))
        por_tipo = self.queryset.values('tipo_mantenimiento').annotate(count=Count('mantenimiento_id'))

        costo_total = self.queryset.filter(estado='completado').aggregate(Sum('costo'))['costo__sum'] or 0
        costo_promedio = self.queryset.filter(estado='completado').aggregate(Avg('costo'))['costo__avg'] or 0

        # Alertas
        fecha_limite = timezone.now().date() + timedelta(days=15)
        alertas = self.queryset.filter(
            estado='pendiente',
            fecha_programada__lte=fecha_limite,
            fecha_programada__gte=timezone.now().date()
        ).count()

        vencidos = self.queryset.filter(
            estado='pendiente',
            fecha_programada__lt=timezone.now().date()
        ).count()

        return Response({
            'total_mantenimientos': total,
            'por_estado': {item['estado']: item['count'] for item in por_estado},
            'por_tipo': {item['tipo_mantenimiento']: item['count'] for item in por_tipo},
            'costo_total': float(costo_total),
            'costo_promedio': float(costo_promedio),
            'alertas': alertas,
            'vencidos': vencidos
        })

    @action(detail=False, methods=['get'])
    def por_activo(self, request):
        """Obtiene mantenimientos de un activo específico"""
        activo_id = request.query_params.get('activo_id', None)
        if activo_id:
            mantenimientos = self.queryset.filter(activo_id=activo_id)
            serializer = self.get_serializer(mantenimientos, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Debe proporcionar el parámetro activo_id'}, status=400)


class OrdenMantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar órdenes de mantenimiento.
    Genera números de orden automáticamente.
    """
    queryset = OrdenMantenimiento.objects.select_related(
        'mantenimiento', 'mantenimiento__activo', 'creado_por'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['numero_orden', 'mantenimiento__activo__codigo', 'mantenimiento__activo__nombre']
    filterset_fields = ['prioridad', 'estado_orden', 'mantenimiento']
    ordering_fields = ['fecha_emision', 'prioridad', 'numero_orden']
    ordering = ['-fecha_emision']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrdenMantenimientoListSerializer
        elif self.action == 'retrieve':
            return OrdenMantenimientoDetailSerializer
        return OrdenMantenimientoCreateUpdateSerializer

    def perform_create(self, serializer):
        """Asignar el usuario que crea la orden"""
        serializer.save(creado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def por_prioridad(self, request):
        """Obtiene órdenes filtradas por prioridad"""
        prioridad = request.query_params.get('prioridad', None)
        if prioridad:
            ordenes = self.queryset.filter(prioridad=prioridad)
            serializer = self.get_serializer(ordenes, many=True)
            return Response(serializer.data)
        else:
            return Response({'error': 'Debe proporcionar el parámetro prioridad'}, status=400)

    @action(detail=False, methods=['get'])
    def urgentes(self, request):
        """Obtiene órdenes urgentes y de alta prioridad"""
        ordenes = self.queryset.filter(
            prioridad__in=['urgente', 'alta'],
            estado_orden__in=['creada', 'aprobada', 'en_ejecucion']
        )
        serializer = self.get_serializer(ordenes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambia el estado de una orden"""
        orden = self.get_object()
        nuevo_estado = request.data.get('estado_orden')

        if nuevo_estado not in dict(OrdenMantenimiento.ESTADO_ORDEN_CHOICES):
            return Response(
                {'error': 'Estado inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        orden.estado_orden = nuevo_estado
        orden.save()
        serializer = self.get_serializer(orden)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas de órdenes de mantenimiento"""
        total = self.queryset.count()
        por_estado = self.queryset.values('estado_orden').annotate(count=Count('orden_id'))
        por_prioridad = self.queryset.values('prioridad').annotate(count=Count('orden_id'))

        tiempo_promedio = self.queryset.filter(
            tiempo_estimado__isnull=False
        ).aggregate(Avg('tiempo_estimado'))['tiempo_estimado__avg'] or 0

        return Response({
            'total_ordenes': total,
            'por_estado': {item['estado_orden']: item['count'] for item in por_estado},
            'por_prioridad': {item['prioridad']: item['count'] for item in por_prioridad},
            'tiempo_promedio_estimado': float(tiempo_promedio)
        })
