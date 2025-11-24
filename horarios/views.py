from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, Prefetch
from datetime import datetime, timedelta
from .models import (
    TipoActividad, Horario, SesionClase, BloqueoHorario,
    EquipoActividad, ClienteMembresia, ReservaClase,
    ReservaEquipo, ReservaEntrenador
)
from .serializers import (
    TipoActividadSerializer, HorarioSerializer, HorarioCreateSerializer,
    SesionClaseSerializer, SesionClaseCreateSerializer, BloqueoHorarioSerializer,
    HorarioCalendarioSerializer, SesionCalendarioSerializer, SesionDisponibleSerializer,
    HorarioDisponibilidadSerializer, ReservaClaseSerializer, ReservaClaseCreateSerializer,
    ReservaEquipoSerializer, ReservaEntrenadorSerializer
)
from .permissions import EsAdministradorOSupervisor, PuedeGestionarHorarios, PuedeHacerReservas
from clientes.models import Cliente
from gestion_equipos.models import Activo
from empleados.models import Entrenador


class TipoActividadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tipos de actividades
    """
    queryset = TipoActividad.objects.select_related('sede').all()
    serializer_class = TipoActividadSerializer
    permission_classes = [IsAuthenticated]  # Cambiado para permitir a clientes ver actividades
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo', 'sede']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'duracion_default']
    ordering = ['nombre']

    def get_queryset(self):
        """Filtrar tipos de actividad según el usuario y sede"""
        queryset = super().get_queryset()

        # Si el usuario es un cliente, filtrar automáticamente por su sede
        if hasattr(self.request.user, 'persona') and hasattr(self.request.user.persona, 'cliente'):
            cliente = self.request.user.persona.cliente
            queryset = queryset.filter(sede=cliente.sede)

        return queryset

    def get_permissions(self):
        """Solo admins pueden crear/editar/eliminar, todos pueden leer"""
        if self.action in ['list', 'retrieve', 'equipos_necesarios']:
            return [IsAuthenticated()]
        return [PuedeGestionarHorarios()]

    @action(detail=True, methods=['get'])
    def equipos_necesarios(self, request, pk=None):
        """Obtener equipos necesarios para esta actividad"""
        tipo_actividad = self.get_object()
        equipos = EquipoActividad.objects.filter(tipo_actividad=tipo_actividad)
        data = []
        for equipo_actividad in equipos:
            data.append({
                'activo_id': equipo_actividad.activo.activo_id,
                'activo_nombre': equipo_actividad.activo.nombre,
                'activo_codigo': equipo_actividad.activo.codigo,
                'cantidad_necesaria': equipo_actividad.cantidad_necesaria,
                'obligatorio': equipo_actividad.obligatorio
            })
        return Response(data)


class HorarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar horarios base
    Permisos: Admin y Supervisor pueden crear/editar, otros solo leer
    Filtrado automático por sede para supervisores
    """
    queryset = Horario.objects.select_related(
        'tipo_actividad', 'entrenador__empleado__persona', 'espacio__sede'
    ).all()
    permission_classes = [PuedeGestionarHorarios]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'estado', 'dia_semana', 'tipo_actividad', 'entrenador', 'espacio', 'espacio__sede'
    ]
    search_fields = [
        'tipo_actividad__nombre', 'entrenador__empleado__persona__nombre',
        'espacio__nombre'
    ]
    ordering_fields = ['dia_semana', 'hora_inicio', 'fecha_inicio']
    ordering = ['dia_semana', 'hora_inicio']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HorarioCreateSerializer
        return HorarioSerializer

    @action(detail=False, methods=['get'])
    def calendario_semanal(self, request):
        """Obtener horarios para vista de calendario semanal"""
        sede_id = request.query_params.get('sede_id')
        queryset = self.get_queryset()
        
        if sede_id:
            queryset = queryset.filter(espacio__sede_id=sede_id)
        
        # Filtrar solo horarios activos y vigentes
        queryset = queryset.filter(
            estado='activo',
            fecha_inicio__lte=timezone.now().date()
        ).filter(
            Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=timezone.now().date())
        )
        
        serializer = HorarioCalendarioSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def disponibilidad(self, request):
        """Verificar disponibilidad de horarios en un rango de fechas"""
        serializer = HorarioDisponibilidadSerializer(data=request.query_params)
        if serializer.is_valid():
            data = serializer.validated_data
            fecha_inicio = data['fecha_inicio']
            fecha_fin = data['fecha_fin']
            
            queryset = self.get_queryset().filter(
                estado='activo',
                fecha_inicio__lte=fecha_fin
            ).filter(
                Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha_inicio)
            )
            
            # Aplicar filtros opcionales
            if 'sede_id' in data:
                queryset = queryset.filter(espacio__sede_id=data['sede_id'])
            if 'entrenador_id' in data:
                queryset = queryset.filter(entrenador_id=data['entrenador_id'])
            if 'espacio_id' in data:
                queryset = queryset.filter(espacio_id=data['espacio_id'])
            
            serializer = HorarioSerializer(queryset, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def generar_sesiones(self, request, pk=None):
        """Generar sesiones automáticamente para un horario en un rango de fechas"""
        horario = self.get_object()
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return Response(
                {'error': 'Se requieren fecha_inicio y fecha_fin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mapeo de días de la semana
        dias_mapping = {
            'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3,
            'viernes': 4, 'sabado': 5, 'domingo': 6
        }
        
        dia_objetivo = dias_mapping[horario.dia_semana]
        sesiones_creadas = 0
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            if fecha_actual.weekday() == dia_objetivo:
                # Verificar si ya existe una sesión para esta fecha
                if not SesionClase.objects.filter(horario=horario, fecha=fecha_actual).exists():
                    SesionClase.objects.create(
                        horario=horario,
                        fecha=fecha_actual
                    )
                    sesiones_creadas += 1
            
            fecha_actual += timedelta(days=1)
        
        return Response({
            'mensaje': f'Se crearon {sesiones_creadas} sesiones',
            'sesiones_creadas': sesiones_creadas
        })

    @action(detail=False, methods=['get'])
    def entrenadores(self, request):
        """Obtener lista de entrenadores disponibles, opcionalmente filtrados por sede"""
        sede_id = request.query_params.get('sede')

        queryset = Entrenador.objects.select_related(
            'empleado__persona', 'sede'
        ).filter(empleado__estado='Activo')

        if sede_id:
            queryset = queryset.filter(sede_id=sede_id)

        data = []
        for entrenador in queryset:
            persona = entrenador.empleado.persona
            data.append({
                'id': entrenador.empleado_id,
                'nombre_completo': f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}",
                'nombre': persona.nombre,
                'especialidad': entrenador.especialidad,
                'sede_id': entrenador.sede_id,
                'sede_nombre': entrenador.sede.nombre
            })

        return Response(data)

    @action(detail=False, methods=['get'])
    def espacios(self, request):
        """Obtener lista de espacios disponibles, opcionalmente filtrados por sede"""
        from instalaciones.models import Espacio

        sede_id = request.query_params.get('sede')

        queryset = Espacio.objects.select_related('sede').all()

        if sede_id:
            queryset = queryset.filter(sede_id=sede_id)

        data = []
        for espacio in queryset:
            data.append({
                'id': espacio.id,
                'espacio_id': espacio.id,
                'nombre': espacio.nombre,
                'descripcion': espacio.descripcion or '',
                'capacidad': espacio.capacidad,
                'sede_id': espacio.sede_id,
                'sede_nombre': espacio.sede.nombre
            })

        return Response(data)


class SesionClaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar sesiones específicas de clases
    """
    queryset = SesionClase.objects.select_related(
        'horario__tipo_actividad',
        'horario__entrenador__empleado__persona',
        'horario__espacio__sede',
        'entrenador_override__empleado__persona',
        'espacio_override__sede'
    ).prefetch_related('reservas__cliente__persona').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'estado', 'fecha', 'horario__tipo_actividad', 'horario__espacio__sede'
    ]
    search_fields = [
        'horario__tipo_actividad__nombre',
        'horario__entrenador__empleado__persona__nombre'
    ]
    ordering_fields = ['fecha', 'horario__hora_inicio']
    ordering = ['fecha', 'horario__hora_inicio']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SesionClaseCreateSerializer
        return SesionClaseSerializer

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Obtener sesiones disponibles para reservar.
        Para clientes autenticados, filtra automáticamente por su sede.
        """
        queryset = self.get_queryset()

        # Si el usuario es un cliente, filtrar por su sede
        if hasattr(request.user, 'persona') and hasattr(request.user.persona, 'cliente'):
            cliente = request.user.persona.cliente
            queryset = queryset.filter(horario__espacio__sede=cliente.sede)

        # Filtrar solo sesiones programadas (disponibles para reservar)
        queryset = queryset.filter(
            estado='programada',
            fecha__gte=timezone.now().date()
        )

        # Filtros opcionales
        tipo_actividad = request.query_params.get('tipo_actividad')
        if tipo_actividad:
            queryset = queryset.filter(horario__tipo_actividad_id=tipo_actividad)

        fecha_desde = request.query_params.get('fecha_desde')
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)

        fecha_hasta = request.query_params.get('fecha_hasta')
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)

        serializer = SesionDisponibleSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def calendario_mensual(self, request):
        """Obtener sesiones para vista de calendario mensual"""
        año = request.query_params.get('año', timezone.now().year)
        mes = request.query_params.get('mes', timezone.now().month)
        sede_id = request.query_params.get('sede_id')
        
        try:
            año = int(año)
            mes = int(mes)
        except ValueError:
            return Response(
                {'error': 'Año y mes deben ser números enteros'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener primer y último día del mes
        primer_dia = datetime(año, mes, 1).date()
        if mes == 12:
            ultimo_dia = datetime(año + 1, 1, 1).date() - timedelta(days=1)
        else:
            ultimo_dia = datetime(año, mes + 1, 1).date() - timedelta(days=1)
        
        queryset = self.get_queryset().filter(
            fecha__gte=primer_dia,
            fecha__lte=ultimo_dia
        )
        
        if sede_id:
            queryset = queryset.filter(horario__espacio__sede_id=sede_id)
        
        serializer = SesionCalendarioSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reservas(self, request, pk=None):
        """Obtener todas las reservas de una sesión"""
        sesion = self.get_object()
        reservas = ReservaClase.objects.filter(sesion_clase=sesion).select_related(
            'cliente__persona'
        )
        
        data = []
        for reserva in reservas:
            data.append({
                'id': reserva.id,
                'cliente_id': reserva.cliente.persona_id,
                'cliente_nombre': f"{reserva.cliente.persona.nombre} {reserva.cliente.persona.apellido_paterno}",
                'estado': reserva.estado,
                'fecha_reserva': reserva.fecha_reserva,
                'observaciones': reserva.observaciones
            })
        
        return Response(data)

    @action(detail=True, methods=['post'])
    def marcar_asistencia(self, request, pk=None):
        """Marcar asistencia masiva para una sesión"""
        sesion = self.get_object()
        asistencias = request.data.get('asistencias', [])
        
        if not isinstance(asistencias, list):
            return Response(
                {'error': 'asistencias debe ser una lista'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        actualizadas = 0
        for asistencia in asistencias:
            reserva_id = asistencia.get('reserva_id')
            asistio = asistencia.get('asistio', False)
            
            try:
                reserva = ReservaClase.objects.get(
                    id=reserva_id,
                    sesion_clase=sesion
                )
                reserva.estado = 'asistio' if asistio else 'no_asistio'
                reserva.save()
                actualizadas += 1
            except ReservaClase.DoesNotExist:
                continue
        
        return Response({
            'mensaje': f'Se actualizaron {actualizadas} asistencias',
            'actualizadas': actualizadas
        })


class BloqueoHorarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar bloqueos de horarios
    """
    queryset = BloqueoHorario.objects.select_related(
        'entrenador__empleado__persona', 'espacio__sede'
    ).all()
    serializer_class = BloqueoHorarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo_bloqueo', 'entrenador', 'espacio']
    search_fields = ['motivo', 'descripcion']
    ordering_fields = ['fecha_inicio', 'fecha_fin']
    ordering = ['-fecha_inicio']

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Obtener bloqueos activos (que afectan fechas futuras)"""
        ahora = timezone.now()
        queryset = self.get_queryset().filter(fecha_fin__gte=ahora)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ReservaClaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reservas de clases
    """
    queryset = ReservaClase.objects.select_related(
        'cliente__persona',
        'sesion_clase__horario__tipo_actividad',
        'sesion_clase__horario__entrenador__empleado__persona'
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReservaClaseCreateSerializer
        return ReservaClaseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'estado', 'cliente', 'sesion_clase__fecha',
        'sesion_clase__horario__tipo_actividad'
    ]
    search_fields = [
        'cliente__persona__nombre',
        'cliente__persona__apellido_paterno',
        'sesion_clase__horario__tipo_actividad__nombre'
    ]
    ordering_fields = ['fecha_reserva', 'sesion_clase__fecha']
    ordering = ['-fecha_reserva']

    def get_queryset(self):
        """Filtrar reservas según el usuario"""
        queryset = super().get_queryset()

        # Si el usuario tiene una persona asociada y es cliente
        if hasattr(self.request.user, 'persona') and hasattr(self.request.user.persona, 'cliente'):
            # Los clientes solo ven sus propias reservas
            cliente = self.request.user.persona.cliente
            queryset = queryset.filter(cliente=cliente)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Crear nueva reserva de clase.
        Si el usuario autenticado es un cliente, se infiere automáticamente:
        - cliente: del usuario autenticado

        Body requerido para clientes:
        {
            "sesion_clase": <id>,
            "observaciones": "opcional"
        }
        """
        # Verificar si el usuario es un cliente
        if hasattr(request.user, 'persona') and hasattr(request.user.persona, 'cliente'):
            cliente = request.user.persona.cliente

            # Validar que la sesión existe
            sesion_id = request.data.get('sesion_clase')
            if not sesion_id:
                return Response(
                    {'error': 'El campo sesion_clase es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                sesion = SesionClase.objects.get(id=sesion_id)
            except SesionClase.DoesNotExist:
                return Response(
                    {'error': 'La sesión especificada no existe'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar que la sesión esté disponible
            if sesion.estado != 'programada':
                return Response(
                    {'error': 'La sesión no está disponible para reservas'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar que haya cupo disponible
            if sesion.asistentes_registrados >= sesion.cupo_efectivo:
                return Response(
                    {'error': 'La sesión ya alcanzó su cupo máximo'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validar que el cliente no tenga ya una reserva para esta sesión
            reserva_existente = ReservaClase.objects.filter(
                cliente=cliente,
                sesion_clase=sesion,
                estado__in=['activa', 'confirmada']
            ).exists()

            if reserva_existente:
                return Response(
                    {'error': 'Ya tienes una reserva para esta sesión'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear reserva automáticamente
            reserva = ReservaClase.objects.create(
                cliente=cliente,
                sesion_clase=sesion,
                observaciones=request.data.get('observaciones', '')
            )

            return Response(
                {
                    'message': 'Reserva creada exitosamente',
                    'data': ReservaClaseSerializer(reserva).data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            # Si no es cliente (ej: admin/cajero), usar el método por defecto
            return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def mis_reservas(self, request):
        """Obtener reservas del cliente autenticado"""
        if not hasattr(request.user, 'persona') or not hasattr(request.user.persona, 'cliente'):
            return Response(
                {'error': 'Usuario no es un cliente'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cliente = request.user.persona.cliente
        reservas = self.get_queryset().filter(cliente=cliente)
        
        # Filtros opcionales
        estado = request.query_params.get('estado')
        if estado:
            reservas = reservas.filter(estado=estado)
        
        fecha_desde = request.query_params.get('fecha_desde')
        if fecha_desde:
            reservas = reservas.filter(sesion_clase__fecha__gte=fecha_desde)
        
        serializer = self.get_serializer(reservas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar una reserva"""
        reserva = self.get_object()
        motivo = request.data.get('motivo', 'Cancelado por el cliente')
        
        try:
            reserva.cancelar(motivo)
            return Response({
                'mensaje': 'Reserva cancelada exitosamente',
                'estado': reserva.estado
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReservaEquipoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reservas de equipos
    """
    queryset = ReservaEquipo.objects.select_related(
        'cliente__persona', 'activo__categoria'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'estado', 'cliente', 'activo', 'fecha_reserva'
    ]
    search_fields = [
        'cliente__persona__nombre',
        'activo__nombre', 'activo__codigo'
    ]
    ordering_fields = ['fecha_reserva', 'hora_inicio']
    ordering = ['fecha_reserva', 'hora_inicio']

    def get_queryset(self):
        """Filtrar reservas según el usuario"""
        queryset = super().get_queryset()
        
        # Si el usuario es cliente, solo ve sus reservas
        if hasattr(self.request.user, 'persona') and hasattr(self.request.user.persona, 'cliente'):
            cliente = self.request.user.persona.cliente
            queryset = queryset.filter(cliente=cliente)
        
        return queryset

    @action(detail=False, methods=['get'])
    def disponibilidad_equipo(self, request):
        """Verificar disponibilidad de un equipo en una fecha específica"""
        activo_id = request.query_params.get('activo_id')
        fecha = request.query_params.get('fecha')
        
        if not activo_id or not fecha:
            return Response(
                {'error': 'Se requieren activo_id y fecha'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtener reservas existentes para ese equipo en esa fecha
        reservas = ReservaEquipo.objects.filter(
            activo_id=activo_id,
            fecha_reserva=fecha,
            estado__in=['activa', 'en_uso']
        ).order_by('hora_inicio')
        
        horarios_ocupados = []
        for reserva in reservas:
            horarios_ocupados.append({
                'hora_inicio': reserva.hora_inicio,
                'hora_fin': reserva.hora_fin,
                'cliente': f"{reserva.cliente.persona.nombre} {reserva.cliente.persona.apellido_paterno}"
            })
        
        return Response({
            'fecha': fecha,
            'activo_id': activo_id,
            'horarios_ocupados': horarios_ocupados
        })

    @action(detail=True, methods=['post'])
    def iniciar_uso(self, request, pk=None):
        """Iniciar el uso de un equipo reservado"""
        reserva = self.get_object()
        
        try:
            reserva.iniciar_uso()
            return Response({
                'mensaje': 'Uso del equipo iniciado',
                'estado': reserva.estado
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def finalizar_uso(self, request, pk=None):
        """Finalizar el uso de un equipo"""
        reserva = self.get_object()
        
        try:
            reserva.finalizar_uso()
            return Response({
                'mensaje': 'Uso del equipo finalizado',
                'estado': reserva.estado,
                'tiempo_uso_real': reserva.tiempo_uso_real
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReservaEntrenadorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reservas de entrenadores personalizados
    """
    queryset = ReservaEntrenador.objects.select_related(
        'cliente__persona',
        'entrenador__empleado__persona',
        'espacio'
    ).prefetch_related('clientes_adicionales__persona').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'estado', 'tipo_sesion', 'cliente', 'entrenador', 'fecha_sesion'
    ]
    search_fields = [
        'cliente__persona__nombre',
        'entrenador__empleado__persona__nombre',
        'objetivo'
    ]
    ordering_fields = ['fecha_sesion', 'hora_inicio', 'fecha_creacion']
    ordering = ['fecha_sesion', 'hora_inicio']

    def get_queryset(self):
        """Filtrar reservas según el usuario"""
        queryset = super().get_queryset()
        
        # Si el usuario es cliente, solo ve sus reservas
        if hasattr(self.request.user, 'persona') and hasattr(self.request.user.persona, 'cliente'):
            cliente = self.request.user.persona.cliente
            queryset = queryset.filter(
                Q(cliente=cliente) | Q(clientes_adicionales=cliente)
            ).distinct()
        
        return queryset

    @action(detail=False, methods=['get'])
    def pendientes_aprobacion(self, request):
        """Obtener sesiones pendientes de aprobación para entrenadores"""
        # Solo entrenadores pueden ver esto
        if not hasattr(request.user, 'persona') or not hasattr(request.user.persona, 'empleado'):
            return Response(
                {'error': 'Usuario no es un empleado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            entrenador = request.user.persona.empleado.entrenador
        except:
            return Response(
                {'error': 'Usuario no es un entrenador'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reservas = self.get_queryset().filter(
            entrenador=entrenador,
            estado='pendiente'
        )
        
        serializer = self.get_serializer(reservas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        """Aprobar una sesión personalizada"""
        reserva = self.get_object()
        
        try:
            reserva.aprobar()
            return Response({
                'mensaje': 'Sesión aprobada exitosamente',
                'estado': reserva.estado
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def iniciar_sesion(self, request, pk=None):
        """Iniciar una sesión personalizada"""
        reserva = self.get_object()
        
        try:
            reserva.iniciar_sesion()
            return Response({
                'mensaje': 'Sesión iniciada',
                'estado': reserva.estado
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def completar_sesion(self, request, pk=None):
        """Completar una sesión personalizada"""
        reserva = self.get_object()
        notas = request.data.get('notas_entrenador')
        
        try:
            reserva.completar_sesion(notas)
            return Response({
                'mensaje': 'Sesión completada exitosamente',
                'estado': reserva.estado
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# Vistas adicionales para reportes y estadísticas
class EstadisticasHorariosViewSet(viewsets.ViewSet):
    """
    ViewSet para obtener estadísticas y reportes de horarios
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def ocupacion_semanal(self, request):
        """Obtener estadísticas de ocupación semanal"""
        sede_id = request.query_params.get('sede_id')
        fecha_inicio = request.query_params.get('fecha_inicio')
        
        if not fecha_inicio:
            fecha_inicio = timezone.now().date()
        else:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha inválido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        fecha_fin = fecha_inicio + timedelta(days=6)
        
        # Obtener sesiones de la semana
        sesiones = SesionClase.objects.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        ).select_related('horario__tipo_actividad')
        
        if sede_id:
            sesiones = sesiones.filter(horario__espacio__sede_id=sede_id)
        
        # Calcular estadísticas
        estadisticas = []
        for sesion in sesiones:
            ocupacion_porcentaje = (
                sesion.asistentes_registrados / sesion.cupo_efectivo * 100
                if sesion.cupo_efectivo > 0 else 0
            )
            
            estadisticas.append({
                'fecha': sesion.fecha,
                'actividad': sesion.horario.tipo_actividad.nombre,
                'hora_inicio': sesion.hora_inicio_efectiva,
                'cupo_total': sesion.cupo_efectivo,
                'asistentes': sesion.asistentes_registrados,
                'ocupacion_porcentaje': round(ocupacion_porcentaje, 2)
            })
        
        return Response({
            'periodo': f"{fecha_inicio} a {fecha_fin}",
            'estadisticas': estadisticas
        })

    @action(detail=False, methods=['get'])
    def actividades_populares(self, request):
        """Obtener actividades más populares por número de reservas"""
        dias = int(request.query_params.get('dias', 30))
        fecha_desde = timezone.now().date() - timedelta(days=dias)
        
        actividades = TipoActividad.objects.annotate(
            total_reservas=Count(
                'horarios__sesiones__reservas',
                filter=Q(horarios__sesiones__fecha__gte=fecha_desde)
            )
        ).filter(total_reservas__gt=0).order_by('-total_reservas')[:10]
        
        data = []
        for actividad in actividades:
            data.append({
                'nombre': actividad.nombre,
                'total_reservas': actividad.total_reservas,
                'color': actividad.color_hex
            })
        
        return Response({
            'periodo_dias': dias,
            'actividades_populares': data
        })