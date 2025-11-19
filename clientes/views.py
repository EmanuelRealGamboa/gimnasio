from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Cliente
from .serializers import (
    ClienteSerializer,
    ClienteListSerializer,
    ClienteCreateSerializer,
    ClienteDetailSerializer
)


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los clientes del gimnasio.
    Permite crear, leer, actualizar y eliminar clientes.
    """
    queryset = Cliente.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return ClienteListSerializer
        elif self.action == 'retrieve':
            return ClienteDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ClienteCreateSerializer
        return ClienteSerializer

    def get_queryset(self):
        """
        Permite filtrar clientes por estado, nombre, email, sede, etc.
        Parámetros de query: estado, search, sede
        """
        queryset = Cliente.objects.all().select_related('persona', 'sede')

        # Filtrar por sede
        sede = self.request.query_params.get('sede', None)
        if sede:
            queryset = queryset.filter(sede_id=sede)

        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)

        # Filtrar por nivel de experiencia
        nivel = self.request.query_params.get('nivel_experiencia', None)
        if nivel:
            queryset = queryset.filter(nivel_experiencia=nivel)

        # Búsqueda general
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(persona__nombre__icontains=search) |
                Q(persona__apellido_paterno__icontains=search) |
                Q(persona__apellido_materno__icontains=search) |
                Q(persona__telefono__icontains=search) |
                Q(persona__usuario__email__icontains=search)
            )

        return queryset

    def create(self, request, *args, **kwargs):
        """Crear un nuevo cliente"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cliente = serializer.save()

        # Retornar los datos del cliente creado
        detail_serializer = ClienteDetailSerializer(cliente, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Actualizar un cliente existente"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        cliente = serializer.save()

        # Retornar los datos del cliente actualizado
        detail_serializer = ClienteDetailSerializer(cliente, context={'request': request})
        return Response(detail_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Eliminar un cliente"""
        instance = self.get_object()
        # Eliminar en cascada: Cliente -> Persona -> User, ContactoEmergencia
        self.perform_destroy(instance)
        return Response(
            {"message": "Cliente eliminado exitosamente"},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint personalizado para cambiar el estado de un cliente
        POST /api/clientes/{id}/cambiar_estado/
        Body: {"estado": "activo|inactivo|suspendido"}
        """
        cliente = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in dict(Cliente.ESTADO_CHOICES):
            return Response(
                {"error": "Estado no válido. Opciones: activo, inactivo, suspendido"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cliente.estado = nuevo_estado
        cliente.save()

        serializer = ClienteDetailSerializer(cliente, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Endpoint para obtener estadísticas de clientes
        GET /api/clientes/estadisticas/?sede={id}
        """
        # Filtrar por sede si se proporciona
        queryset = Cliente.objects.all()
        sede = request.query_params.get('sede', None)
        if sede:
            queryset = queryset.filter(sede_id=sede)

        total_clientes = queryset.count()
        activos = queryset.filter(estado='activo').count()
        inactivos = queryset.filter(estado='inactivo').count()
        suspendidos = queryset.filter(estado='suspendido').count()

        # Estadísticas por nivel de experiencia
        principiantes = queryset.filter(nivel_experiencia='principiante').count()
        intermedios = queryset.filter(nivel_experiencia='intermedio').count()
        avanzados = queryset.filter(nivel_experiencia='avanzado').count()

        # Estadísticas por sede (si no se filtra por sede específica)
        por_sede = []
        if not sede:
            from django.db.models import Count
            por_sede = list(Cliente.objects.values('sede__nombre').annotate(
                total=Count('persona')
            ).order_by('-total'))

        response_data = {
            'total_clientes': total_clientes,
            'por_estado': {
                'activos': activos,
                'inactivos': inactivos,
                'suspendidos': suspendidos,
            },
            'por_nivel': {
                'principiantes': principiantes,
                'intermedios': intermedios,
                'avanzados': avanzados,
            }
        }

        if not sede:
            response_data['por_sede'] = por_sede

        return Response(response_data)
