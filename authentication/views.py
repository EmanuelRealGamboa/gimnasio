from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .serializers import (
    EmpleadoUserCreateSerializer,
    EmpleadoRegistroSerializer,
    EmpleadoUserDetailSerializer,
    UserListSerializer
)
from .permissions import TienePermisoGestionarEmpleados
from .models import User
from empleados.models import Empleado

class EmpleadoUserCreateView(APIView):
    """
    Endpoint para que el administrador cree, liste, actualice, elimine y consulte empleados.
    """
    permission_classes = [TienePermisoGestionarEmpleados]
    
    def get(self, request, pk=None):
        if pk:
            # Detalle de usuario con la información personalizada
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = EmpleadoUserDetailSerializer(user, context={'request': request})
            return Response(serializer.data)
        else:
            # Listado de usuarios con información completa - SOLO EMPLEADOS
            # Filtrar solo usuarios que tengan un registro de Empleado asociado a través de persona
            users = User.objects.select_related('persona').filter(
                persona__empleado__isnull=False
            ).all()
            serializer = UserListSerializer(users, many=True)
            return Response(serializer.data) 
 
    def post(self, request):
        serializer = EmpleadoUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'success': True, 'user_id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpleadoUserCreateSerializer(user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'user_id': user.id, 'email': user.email})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpleadoUserCreateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'user_id': user.id, 'email': user.email})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'success': True, 'detail': 'Usuario eliminado.'}, status=status.HTTP_204_NO_CONTENT)
    
    def retrieve(self, request, pk):
        """
        Consulta la información completa de un usuario por su ID.
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpleadoUserDetailSerializer(user)
        return Response(serializer.data)
	   



class EmpleadoRegistroView(APIView):
    """
    Endpoint para registrar empleados desde el navegador (solo admins con permiso).
    """
    permission_classes = [TienePermisoGestionarEmpleados]

    def post(self, request):
        serializer = EmpleadoRegistroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'success': True, 'user_id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmpleadoEstadisticasView(APIView):
    """
    Endpoint para obtener estadísticas de empleados
    GET /api/admin/empleados/estadisticas/?sede={id}
    """
    permission_classes = [TienePermisoGestionarEmpleados]

    def get(self, request):
        # Filtrar por sede si se proporciona
        queryset = Empleado.objects.all()
        sede = request.query_params.get('sede', None)

        if sede:
            queryset = queryset.filter(sede_id=sede)

        # Total de empleados
        total_empleados = queryset.count()

        # Estadísticas por estado
        activos = queryset.filter(estado='Activo').count()
        inactivos = queryset.filter(estado='Inactivo').count()

        # Estadísticas por tipo de contrato
        por_contrato = {}
        contratos = queryset.values('tipo_contrato').annotate(total=Count('persona')).order_by('-total')
        for contrato in contratos:
            por_contrato[contrato['tipo_contrato']] = contrato['total']

        # Estadísticas por puesto
        por_puesto = {}
        puestos = queryset.values('puesto').annotate(total=Count('persona')).order_by('-total')
        for puesto in puestos:
            por_puesto[puesto['puesto']] = puesto['total']

        # Estadísticas por departamento
        por_departamento = {}
        departamentos = queryset.values('departamento').annotate(total=Count('persona')).order_by('-total')
        for depto in departamentos:
            if depto['departamento']:  # Ignorar departamentos vacíos
                por_departamento[depto['departamento']] = depto['total']

        # Estadísticas por sede (si no se filtra por sede específica)
        por_sede = []
        if not sede:
            por_sede = list(Empleado.objects.values('sede__nombre').annotate(
                total=Count('persona')
            ).order_by('-total'))

        response_data = {
            'total_empleados': total_empleados,
            'por_estado': {
                'activos': activos,
                'inactivos': inactivos,
            },
            'por_contrato': por_contrato,
            'por_puesto': por_puesto,
            'por_departamento': por_departamento,
        }

        if not sede:
            response_data['por_sede'] = por_sede

        return Response(response_data)
