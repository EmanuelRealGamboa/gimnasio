from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from .models import Membresia
from .serializers import (
    MembresiaSerializer,
    MembresiaListSerializer,
    MembresiaCreateUpdateSerializer
)


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
