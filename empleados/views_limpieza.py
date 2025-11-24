from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    PersonalLimpieza,
    TareaLimpieza,
    HorarioLimpieza,
    AsignacionTarea,
    ChecklistLimpieza
)
from .serializers_limpieza import (
    PersonalLimpiezaListSerializer,
    TareaLimpiezaSerializer,
    HorarioLimpiezaSerializer,
    AsignacionTareaSerializer,
    AsignacionTareaCreateSerializer,
    ChecklistLimpiezaSerializer,
    EstadisticasLimpiezaSerializer
)


class TareaLimpiezaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el catálogo de tareas de limpieza.
    Endpoints:
    - GET /api/limpieza/tareas/ - Listar tareas
    - POST /api/limpieza/tareas/ - Crear tarea
    - GET /api/limpieza/tareas/{id}/ - Detalle de tarea
    - PUT/PATCH /api/limpieza/tareas/{id}/ - Actualizar tarea
    - DELETE /api/limpieza/tareas/{id}/ - Eliminar tarea
    """
    queryset = TareaLimpieza.objects.all()
    serializer_class = TareaLimpiezaSerializer
    permission_classes = []  # Ajustar según tus necesidades

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo_bool = activo.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(activo=activo_bool)

        # Filtrar por tipo de espacio
        tipo_espacio = self.request.query_params.get('tipo_espacio', None)
        if tipo_espacio:
            queryset = queryset.filter(tipo_espacio=tipo_espacio)

        # Filtrar por prioridad
        prioridad = self.request.query_params.get('prioridad', None)
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)

        return queryset


class PersonalLimpiezaViewSet(viewsets.ViewSet):
    """
    ViewSet para gestionar el personal de limpieza.
    """
    permission_classes = []

    def list(self, request):
        """
        Listar todo el personal de limpieza.
        """
        queryset = PersonalLimpieza.objects.select_related(
            'empleado',
            'empleado__persona',
            'sede'
        ).prefetch_related('espacio')

        # Filtrar por sede
        sede_id = request.query_params.get('sede', None)
        if sede_id:
            queryset = queryset.filter(sede_id=sede_id)

        # Filtrar por turno
        turno = request.query_params.get('turno', None)
        if turno:
            queryset = queryset.filter(turno__icontains=turno)

        serializer = PersonalLimpiezaListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Obtener detalle de un personal de limpieza.
        """
        try:
            personal = PersonalLimpieza.objects.select_related(
                'empleado',
                'empleado__persona',
                'sede'
            ).prefetch_related('espacio').get(empleado_id=pk)

            serializer = PersonalLimpiezaListSerializer(personal)
            return Response(serializer.data)
        except PersonalLimpieza.DoesNotExist:
            return Response(
                {'error': 'Personal de limpieza no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Obtener información del personal de limpieza logueado actualmente.
        Endpoint: GET /api/limpieza/personal/me/
        """
        try:
            # Obtener el empleado del usuario autenticado
            user = request.user

            # Buscar si el usuario tiene un registro de Personal de Limpieza
            personal = PersonalLimpieza.objects.select_related(
                'empleado',
                'empleado__persona',
                'sede'
            ).prefetch_related('espacio').get(empleado__persona__usuario=user)

            serializer = PersonalLimpiezaListSerializer(personal)
            return Response(serializer.data)
        except PersonalLimpieza.DoesNotExist:
            return Response(
                {'error': 'El usuario autenticado no es personal de limpieza'},
                status=status.HTTP_404_NOT_FOUND
            )


class HorarioLimpiezaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar horarios de limpieza.
    """
    queryset = HorarioLimpieza.objects.all()
    serializer_class = HorarioLimpiezaSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por personal
        personal_id = self.request.query_params.get('personal', None)
        if personal_id:
            queryset = queryset.filter(personal_limpieza_id=personal_id)

        # Filtrar por sede
        sede_id = self.request.query_params.get('sede', None)
        if sede_id:
            queryset = queryset.filter(espacio__sede_id=sede_id)

        # Filtrar por día de la semana
        dia_semana = self.request.query_params.get('dia_semana', None)
        if dia_semana:
            queryset = queryset.filter(dia_semana=dia_semana)

        # Filtrar por activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo_bool = activo.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(activo=activo_bool)

        return queryset.select_related(
            'personal_limpieza',
            'personal_limpieza__empleado',
            'personal_limpieza__empleado__persona',
            'espacio',
            'espacio__sede'
        )


class AsignacionTareaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar asignaciones de tareas de limpieza.
    """
    queryset = AsignacionTarea.objects.all()
    permission_classes = []

    def get_serializer_class(self):
        if self.action == 'create':
            return AsignacionTareaCreateSerializer
        return AsignacionTareaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Si el usuario está autenticado y es personal de limpieza, filtrar automáticamente por él
        if self.request.user.is_authenticated:
            try:
                personal = PersonalLimpieza.objects.get(empleado__persona__usuario=self.request.user)
                # Filtrar solo las tareas asignadas a este personal
                queryset = queryset.filter(personal_limpieza=personal)
            except PersonalLimpieza.DoesNotExist:
                # Si no es personal de limpieza, no filtrar (administrador)
                pass

        # Filtrar por fecha
        fecha = self.request.query_params.get('fecha', None)
        if fecha:
            queryset = queryset.filter(fecha=fecha)
        else:
            # Por defecto, mostrar solo las de hoy
            queryset = queryset.filter(fecha=date.today())

        # Filtrar por rango de fechas
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        if fecha_inicio and fecha_fin:
            queryset = queryset.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin)

        # Filtrar por personal (solo si no es personal de limpieza autenticado)
        personal_id = self.request.query_params.get('personal', None)
        if personal_id:
            queryset = queryset.filter(personal_limpieza_id=personal_id)

        # Filtrar por sede
        sede_id = self.request.query_params.get('sede', None)
        if sede_id:
            queryset = queryset.filter(espacio__sede_id=sede_id)

        # Filtrar por espacio
        espacio_id = self.request.query_params.get('espacio', None)
        if espacio_id:
            queryset = queryset.filter(espacio_id=espacio_id)

        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset.select_related(
            'personal_limpieza',
            'personal_limpieza__empleado',
            'personal_limpieza__empleado__persona',
            'tarea',
            'espacio',
            'espacio__sede',
            'completada_por',
            'asignado_por'
        ).prefetch_related('checklist')

    @action(detail=True, methods=['post'])
    def marcar_completada(self, request, pk=None):
        """
        Marcar una tarea como completada (será llamado desde app móvil).
        POST /api/limpieza/asignaciones/{id}/marcar_completada/
        Body: {
            "observaciones_completado": "texto opcional"
        }

        Se guardará automáticamente:
        - hora_fin: hora actual cuando empleado confirma
        - fecha_completada: timestamp completo
        - completada_por: usuario autenticado
        """
        asignacion = self.get_object()

        if asignacion.estado == 'completada':
            return Response(
                {'error': 'Esta tarea ya está completada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        observaciones = request.data.get('observaciones_completado', '')

        # Obtener el personal de limpieza del usuario autenticado
        try:
            personal = PersonalLimpieza.objects.get(empleado__persona__usuario=request.user)
        except PersonalLimpieza.DoesNotExist:
            return Response(
                {'error': 'El usuario autenticado no es personal de limpieza'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verificar que la tarea esté asignada a este personal
        if asignacion.personal_limpieza != personal:
            return Response(
                {'error': 'No tienes permiso para completar esta tarea'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Guardar hora_fin automáticamente cuando empleado confirma
        from datetime import datetime
        asignacion.estado = 'completada'
        asignacion.fecha_completada = timezone.now()
        asignacion.hora_fin = datetime.now().time()  # Guardar hora de finalización automáticamente
        asignacion.completada_por = personal
        asignacion.observaciones_completado = observaciones
        asignacion.save()

        serializer = self.get_serializer(asignacion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_en_progreso(self, request, pk=None):
        """
        Marcar una tarea como en progreso.
        POST /api/limpieza/asignaciones/{id}/marcar_en_progreso/
        """
        asignacion = self.get_object()

        if asignacion.estado == 'completada':
            return Response(
                {'error': 'Esta tarea ya está completada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        asignacion.estado = 'en_progreso'
        asignacion.save()

        serializer = self.get_serializer(asignacion)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancelar una tarea.
        POST /api/limpieza/asignaciones/{id}/cancelar/
        Body: {
            "notas": "motivo de cancelación"
        }
        """
        asignacion = self.get_object()

        if asignacion.estado == 'completada':
            return Response(
                {'error': 'No se puede cancelar una tarea completada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notas = request.data.get('notas', '')
        asignacion.estado = 'cancelada'
        asignacion.notas = notas
        asignacion.save()

        serializer = self.get_serializer(asignacion)
        return Response(serializer.data)


class ChecklistLimpiezaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar checklists de limpieza.
    """
    queryset = ChecklistLimpieza.objects.all()
    serializer_class = ChecklistLimpiezaSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por asignación
        asignacion_id = self.request.query_params.get('asignacion', None)
        if asignacion_id:
            queryset = queryset.filter(asignacion_id=asignacion_id)

        return queryset.select_related('asignacion', 'verificado_por')

    @action(detail=True, methods=['post'])
    def verificar(self, request, pk=None):
        """
        Verificar un checklist.
        POST /api/limpieza/checklists/{id}/verificar/
        Body: {
            "verificado_por": empleado_id,
            "observaciones": "texto opcional",
            "calificacion": 1-5
        }
        """
        checklist = self.get_object()

        verificado_por_id = request.data.get('verificado_por')
        observaciones = request.data.get('observaciones', '')
        calificacion = request.data.get('calificacion')

        from empleados.models import Empleado
        try:
            empleado = Empleado.objects.get(persona_id=verificado_por_id)
        except Empleado.DoesNotExist:
            return Response(
                {'error': 'Empleado no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        checklist.verificado = True
        checklist.verificado_por = empleado
        checklist.fecha_verificacion = timezone.now()
        checklist.observaciones = observaciones
        checklist.calificacion = calificacion
        checklist.save()

        serializer = self.get_serializer(checklist)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([])
def estadisticas_limpieza(request):
    """
    Endpoint para obtener estadísticas del módulo de limpieza.
    GET /api/limpieza/estadisticas/?sede=1&fecha_inicio=2025-01-01&fecha_fin=2025-01-31
    """
    sede_id = request.query_params.get('sede', None)
    fecha_inicio = request.query_params.get('fecha_inicio', None)
    fecha_fin = request.query_params.get('fecha_fin', None)

    # Por defecto, últimos 7 días
    if not fecha_inicio or not fecha_fin:
        fecha_fin = date.today()
        fecha_inicio = fecha_fin - timedelta(days=7)

    queryset = AsignacionTarea.objects.filter(
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin
    )

    if sede_id:
        queryset = queryset.filter(espacio__sede_id=sede_id)

    # Contar tareas por estado
    tareas_completadas = queryset.filter(estado='completada').count()
    tareas_pendientes = queryset.filter(estado='pendiente').count()
    tareas_en_progreso = queryset.filter(estado='en_progreso').count()
    tareas_canceladas = queryset.filter(estado='cancelada').count()

    total_tareas = queryset.count()
    tasa_cumplimiento = (tareas_completadas / total_tareas * 100) if total_tareas > 0 else 0

    # Calificación promedio
    checklists = ChecklistLimpieza.objects.filter(
        asignacion__in=queryset,
        calificacion__isnull=False
    )
    calificacion_promedio = checklists.aggregate(promedio=Avg('calificacion'))['promedio'] or 0

    # Total de personal
    total_personal = PersonalLimpieza.objects.count()
    if sede_id:
        total_personal = PersonalLimpieza.objects.filter(sede_id=sede_id).count()

    # Espacios únicos limpiados hoy
    espacios_limpios_hoy = AsignacionTarea.objects.filter(
        fecha=date.today(),
        estado='completada'
    ).values('espacio').distinct().count()

    if sede_id:
        espacios_limpios_hoy = AsignacionTarea.objects.filter(
            fecha=date.today(),
            estado='completada',
            espacio__sede_id=sede_id
        ).values('espacio').distinct().count()

    estadisticas = {
        'tareas_completadas': tareas_completadas,
        'tareas_pendientes': tareas_pendientes,
        'tareas_en_progreso': tareas_en_progreso,
        'tareas_canceladas': tareas_canceladas,
        'tasa_cumplimiento': round(tasa_cumplimiento, 2),
        'calificacion_promedio': round(float(calificacion_promedio), 2) if calificacion_promedio else 0,
        'total_personal': total_personal,
        'espacios_limpios_hoy': espacios_limpios_hoy,
    }

    serializer = EstadisticasLimpiezaSerializer(estadisticas)
    return Response(serializer.data)
