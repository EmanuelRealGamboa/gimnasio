from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from .models import Membresia, SuscripcionMembresia
from .permissions import EsAdministradorOCajero
from .serializers import (
    MembresiaSerializer,
    MembresiaListSerializer,
    MembresiaCreateUpdateSerializer,
    SuscripcionMembresiaSerializer,
    SuscripcionMembresiaCreateSerializer,
    ClienteConMembresiaSerializer
)
from clientes.models import Cliente


class MembresiaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las membresías del gimnasio.
    Permite crear, leer, actualizar y eliminar membresías.
    """
    queryset = Membresia.objects.all()
    permission_classes = [EsAdministradorOCajero]

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return MembresiaListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MembresiaCreateUpdateSerializer
        return MembresiaSerializer

    def get_queryset(self):
        """
        Permite filtrar membresías por tipo, activo, precio, sede, etc.
        Parámetros de query: tipo, activo, search, sede, permite_todas_sedes
        """
        queryset = Membresia.objects.select_related('sede').prefetch_related('espacios_incluidos').all()

        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        # Filtrar por estado activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo_bool = activo.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(activo=activo_bool)

        # Filtrar por sede
        sede = self.request.query_params.get('sede', None)
        if sede:
            queryset = queryset.filter(Q(sede_id=sede) | Q(permite_todas_sedes=True))

        # Filtrar por permite_todas_sedes
        permite_todas_sedes = self.request.query_params.get('permite_todas_sedes', None)
        if permite_todas_sedes is not None:
            permite_bool = permite_todas_sedes.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(permite_todas_sedes=permite_bool)

        # Búsqueda general
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(nombre_plan__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(beneficios__icontains=search)
            )

        return queryset

    @action(detail=True, methods=['post'])
    def toggle_activo(self, request, pk=None):
        """
        Endpoint para activar/desactivar una membresía
        POST /api/membresias/{id}/toggle_activo/
        """
        membresia = self.get_object()
        membresia.activo = not membresia.activo
        membresia.save()

        serializer = MembresiaSerializer(membresia)
        return Response({
            'message': f'Membresía {"activada" if membresia.activo else "desactivada"} exitosamente',
            'data': serializer.data
        })

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para obtener estadísticas de membresías
        GET /api/membresias/estadisticas/
        Parámetros opcionales: sede (id de sede para filtrar estadísticas)
        """
        from django.db.models import Avg, Min, Max

        # Obtener el filtro de sede si existe
        sede_id = request.query_params.get('sede', None)

        # Base queryset
        queryset = Membresia.objects.all()

        # Aplicar filtro de sede si se proporciona
        if sede_id:
            queryset = queryset.filter(Q(sede_id=sede_id) | Q(permite_todas_sedes=True))

        total_membresias = queryset.count()
        activas = queryset.filter(activo=True).count()
        inactivas = queryset.filter(activo=False).count()
        multi_sede = queryset.filter(permite_todas_sedes=True).count()

        # Contar por tipo
        por_tipo = {}
        for tipo_key, tipo_label in Membresia.TIPO_CHOICES:
            count = queryset.filter(tipo=tipo_key).count()
            por_tipo[tipo_key] = {
                'label': tipo_label,
                'count': count
            }

        # Precio promedio
        stats_precio = queryset.aggregate(
            precio_promedio=Avg('precio'),
            precio_min=Min('precio'),
            precio_max=Max('precio')
        )

        # Estadísticas por sede
        por_sede = []
        from instalaciones.models import Sede
        sedes = Sede.objects.all()
        for sede in sedes:
            membresias_sede = Membresia.objects.filter(
                Q(sede=sede) | Q(permite_todas_sedes=True)
            )
            por_sede.append({
                'sede_id': sede.id,
                'sede_nombre': sede.nombre,
                'total': membresias_sede.count(),
                'activas': membresias_sede.filter(activo=True).count()
            })

        return Response({
            'total_membresias': total_membresias,
            'activas': activas,
            'inactivas': inactivas,
            'multi_sede': multi_sede,
            'por_tipo': por_tipo,
            'precio_promedio': float(stats_precio['precio_promedio'] or 0),
            'precio_minimo': float(stats_precio['precio_min'] or 0),
            'precio_maximo': float(stats_precio['precio_max'] or 0),
            'por_sede': por_sede,
        })

    @action(detail=False, methods=['get'])
    def activas(self, request):
        """
        Endpoint para obtener solo membresías activas
        GET /api/membresias/activas/
        """
        membresias = Membresia.objects.filter(activo=True)
        serializer = MembresiaListSerializer(membresias, many=True)
        return Response(serializer.data)


class SuscripcionMembresiaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las suscripciones de membresías de los clientes.
    Permite crear, leer, actualizar y cancelar suscripciones.
    """
    queryset = SuscripcionMembresia.objects.all()
    permission_classes = [EsAdministradorOCajero]

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action in ['create', 'update', 'partial_update']:
            return SuscripcionMembresiaCreateSerializer
        return SuscripcionMembresiaSerializer

    def get_queryset(self):
        """
        Permite filtrar suscripciones por cliente, estado, fechas, sede, etc.
        Parámetros de query: cliente, estado, membresia, sede, fecha_inicio, fecha_fin
        """
        queryset = SuscripcionMembresia.objects.select_related(
            'cliente', 'cliente__persona', 'membresia', 'sede_suscripcion'
        ).all()

        # Filtrar por cliente
        cliente_id = self.request.query_params.get('cliente', None)
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)

        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)

        # Filtrar por membresía
        membresia_id = self.request.query_params.get('membresia', None)
        if membresia_id:
            queryset = queryset.filter(membresia_id=membresia_id)

        # Filtrar por sede
        sede_id = self.request.query_params.get('sede', None)
        if sede_id:
            queryset = queryset.filter(
                Q(sede_suscripcion_id=sede_id) |
                Q(membresia__permite_todas_sedes=True)
            )

        # Búsqueda por nombre de cliente
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(cliente__persona__nombre__icontains=search) |
                Q(cliente__persona__apellido_paterno__icontains=search) |
                Q(cliente__persona__apellido_materno__icontains=search)
            )

        return queryset

    @action(detail=False, methods=['get'])
    def clientes_con_membresia(self, request):
        """
        Endpoint para obtener todos los clientes con membresía
        GET /api/suscripciones/clientes_con_membresia/
        """
        # Obtener todas las suscripciones únicas de clientes
        clientes_con_suscripcion = SuscripcionMembresia.objects.all(
        ).values_list('cliente_id', flat=True).distinct()

        clientes = Cliente.objects.filter(
            persona_id__in=clientes_con_suscripcion
        ).select_related('persona')

        # Construir respuesta manual con información de cliente y suscripción
        from authentication.models import User

        data = []
        for cliente in clientes:
            # Obtener la suscripción más reciente (puede ser activa, vencida o cancelada)
            suscripcion = SuscripcionMembresia.objects.filter(
                cliente=cliente
            ).select_related('membresia').order_by('-fecha_inicio').first()

            if suscripcion:
                # Obtener email del usuario
                try:
                    user = User.objects.get(persona=cliente.persona)
                    email = user.email
                except User.DoesNotExist:
                    email = None

                data.append({
                    'cliente_id': cliente.persona_id,
                    'nombre': cliente.persona.nombre,
                    'apellido_paterno': cliente.persona.apellido_paterno,
                    'apellido_materno': cliente.persona.apellido_materno,
                    'email': email,
                    'telefono': cliente.persona.telefono,
                    'estado_cliente': cliente.estado,
                    'suscripcion': {
                        'id': suscripcion.id,
                        'membresia_nombre': suscripcion.membresia.nombre_plan,
                        'membresia_tipo': suscripcion.membresia.get_tipo_display(),
                        'precio_pagado': str(suscripcion.precio_pagado),
                        'fecha_inicio': suscripcion.fecha_inicio,
                        'fecha_fin': suscripcion.fecha_fin,
                        'dias_restantes': suscripcion.dias_restantes,
                        'estado': suscripcion.estado,
                        'metodo_pago': suscripcion.get_metodo_pago_display(),
                        'sede_id': suscripcion.sede_suscripcion.id if suscripcion.sede_suscripcion else None,
                        'sede_nombre': suscripcion.sede_suscripcion.nombre if suscripcion.sede_suscripcion else None,
                        'permite_todas_sedes': suscripcion.membresia.permite_todas_sedes
                    }
                })

        return Response(data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Endpoint para cancelar una suscripción
        POST /api/suscripciones/{id}/cancelar/
        """
        suscripcion = self.get_object()

        if suscripcion.estado == 'cancelada':
            return Response(
                {'error': 'Esta suscripción ya está cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        suscripcion.estado = 'cancelada'
        suscripcion.save()

        serializer = SuscripcionMembresiaSerializer(suscripcion)
        return Response({
            'message': 'Suscripción cancelada exitosamente',
            'data': serializer.data
        })

    @action(detail=True, methods=['post'])
    def renovar(self, request, pk=None):
        """
        Endpoint para renovar una suscripción vencida
        POST /api/suscripciones/{id}/renovar/
        Body: { "metodo_pago": "efectivo" }
        """
        suscripcion_anterior = self.get_object()

        # Crear nueva suscripción
        nueva_suscripcion = SuscripcionMembresia.objects.create(
            cliente=suscripcion_anterior.cliente,
            membresia=suscripcion_anterior.membresia,
            fecha_inicio=timezone.now().date(),
            precio_pagado=suscripcion_anterior.membresia.precio,
            metodo_pago=request.data.get('metodo_pago', 'efectivo'),
            notas=f"Renovación de suscripción #{suscripcion_anterior.id}",
            sede_suscripcion=suscripcion_anterior.sede_suscripcion  # Copiar la sede de la suscripción anterior
        )

        serializer = SuscripcionMembresiaSerializer(nueva_suscripcion)
        return Response({
            'message': 'Suscripción renovada exitosamente',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para obtener estadísticas de suscripciones
        GET /api/suscripciones/estadisticas/
        Parámetros opcionales: sede (id de sede para filtrar estadísticas)
        """
        from django.db.models import Sum, Avg

        # Obtener el filtro de sede si existe
        sede_id = request.query_params.get('sede', None)

        # Base queryset
        queryset = SuscripcionMembresia.objects.all()

        # Aplicar filtro de sede si se proporciona
        if sede_id:
            queryset = queryset.filter(
                Q(sede_suscripcion_id=sede_id) |
                Q(membresia__permite_todas_sedes=True)
            )

        total_suscripciones = queryset.count()
        activas = queryset.filter(estado='activa').count()
        vencidas = queryset.filter(estado='vencida').count()
        canceladas = queryset.filter(estado='cancelada').count()

        # Ingresos totales
        ingresos_totales = queryset.aggregate(
            total=Sum('precio_pagado')
        )['total'] or 0

        # Ingresos del mes actual
        mes_actual = timezone.now().replace(day=1)
        ingresos_mes = queryset.filter(
            fecha_suscripcion__gte=mes_actual
        ).aggregate(total=Sum('precio_pagado'))['total'] or 0

        # Estadísticas por sede
        por_sede = []
        from instalaciones.models import Sede
        sedes = Sede.objects.all()
        for sede in sedes:
            suscripciones_sede = SuscripcionMembresia.objects.filter(
                Q(sede_suscripcion=sede) | Q(membresia__permite_todas_sedes=True)
            )
            ingresos_sede = suscripciones_sede.aggregate(
                total=Sum('precio_pagado')
            )['total'] or 0

            por_sede.append({
                'sede_id': sede.id,
                'sede_nombre': sede.nombre,
                'total': suscripciones_sede.count(),
                'activas': suscripciones_sede.filter(estado='activa').count(),
                'ingresos': float(ingresos_sede)
            })

        return Response({
            'total_suscripciones': total_suscripciones,
            'activas': activas,
            'vencidas': vencidas,
            'canceladas': canceladas,
            'ingresos_totales': float(ingresos_totales),
            'ingresos_mes_actual': float(ingresos_mes),
            'por_sede': por_sede
        })
