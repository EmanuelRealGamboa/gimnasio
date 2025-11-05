from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import Membresia
from .serializers import (
    MembresiaSerializer,
    MembresiaListSerializer,
    MembresiaCreateUpdateSerializer
)
from horarios.models import ClienteMembresia
from clientes.models import Cliente


class MembresiaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las membresías del gimnasio.
    Permite crear, leer, actualizar y eliminar membresías.
    """
    queryset = Membresia.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return MembresiaListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return MembresiaCreateUpdateSerializer
        return MembresiaSerializer

    def get_queryset(self):
        """
        Permite filtrar membresías por tipo, activo, precio, etc.
        Parámetros de query: tipo, activo, search
        """
        queryset = Membresia.objects.all()

        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        # Filtrar por estado activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo_bool = activo.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(activo=activo_bool)

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
        """
        total_membresias = Membresia.objects.count()
        activas = Membresia.objects.filter(activo=True).count()
        inactivas = Membresia.objects.filter(activo=False).count()

        # Contar por tipo
        por_tipo = {}
        for tipo_key, tipo_label in Membresia.TIPO_CHOICES:
            count = Membresia.objects.filter(tipo=tipo_key).count()
            por_tipo[tipo_key] = {
                'label': tipo_label,
                'count': count
            }

        # Precio promedio
        from django.db.models import Avg, Min, Max
        stats_precio = Membresia.objects.aggregate(
            precio_promedio=Avg('precio'),
            precio_min=Min('precio'),
            precio_max=Max('precio')
        )

        return Response({
            'total_membresias': total_membresias,
            'activas': activas,
            'inactivas': inactivas,
            'por_tipo': por_tipo,
            'precio_promedio': float(stats_precio['precio_promedio'] or 0),
            'precio_minimo': float(stats_precio['precio_min'] or 0),
            'precio_maximo': float(stats_precio['precio_max'] or 0),
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

    @action(detail=True, methods=['post'])
    def adquirir(self, request, pk=None):
        """
        Endpoint para que un cliente adquiera una membresía
        POST /api/membresias/{id}/adquirir/
        Body: {
            "metodo_pago": "efectivo|tarjeta|transferencia",
            "meses_adicionales": 0  // opcional, para extender duración
        }
        """
        try:
            membresia = self.get_object()
            
            if not membresia.activo:
                return Response(
                    {'error': 'Esta membresía no está disponible'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Obtener cliente del usuario autenticado
            try:
                cliente = Cliente.objects.get(persona__usuario=request.user)
            except Cliente.DoesNotExist:
                return Response(
                    {'error': 'Usuario no es un cliente registrado'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verificar si ya tiene una membresía activa
            membresia_activa = ClienteMembresia.objects.filter(
                cliente=cliente,
                estado='activa',
                fecha_fin__gte=timezone.now().date()
            ).first()

            if membresia_activa:
                return Response(
                    {'error': 'Ya tienes una membresía activa. Expira el: ' + str(membresia_activa.fecha_fin)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calcular fechas
            fecha_inicio = timezone.now().date()
            meses_adicionales = request.data.get('meses_adicionales', 0)
            duracion_total = membresia.duracion_dias + (meses_adicionales * 30)
            fecha_fin = fecha_inicio + timedelta(days=duracion_total)

            # Crear la membresía del cliente
            cliente_membresia = ClienteMembresia.objects.create(
                cliente=cliente,
                membresia=membresia,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado='activa'
            )

            # Aquí podrías integrar con sistema de pagos
            # Por ahora solo registramos la adquisición

            return Response({
                'message': 'Membresía adquirida exitosamente',
                'membresia_cliente_id': cliente_membresia.id,
                'membresia': membresia.nombre_plan,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'precio': float(membresia.precio),
                'duracion_dias': duracion_total
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Error al adquirir membresía: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def mis_membresias(self, request):
        """
        Endpoint para que un cliente vea sus membresías
        GET /api/membresias/mis_membresias/
        """
        try:
            cliente = Cliente.objects.get(persona__usuario=request.user)
            
            membresias_cliente = ClienteMembresia.objects.filter(
                cliente=cliente
            ).select_related('membresia').order_by('-fecha_inicio')

            data = []
            for cm in membresias_cliente:
                data.append({
                    'id': cm.id,
                    'membresia': {
                        'id': cm.membresia.id,
                        'nombre_plan': cm.membresia.nombre_plan,
                        'tipo': cm.membresia.get_tipo_display(),
                        'precio': float(cm.membresia.precio),
                        'beneficios': cm.membresia.beneficios
                    },
                    'fecha_inicio': cm.fecha_inicio,
                    'fecha_fin': cm.fecha_fin,
                    'estado': cm.get_estado_display(),
                    'dias_restantes': (cm.fecha_fin - timezone.now().date()).days if cm.fecha_fin >= timezone.now().date() else 0,
                    'activa': cm.estado == 'activa' and cm.fecha_fin >= timezone.now().date()
                })

            return Response(data)

        except Cliente.DoesNotExist:
            return Response(
                {'error': 'Usuario no es un cliente registrado'},
                status=status.HTTP_400_BAD_REQUEST
            )
