from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    EmpleadoUserCreateSerializer,
    EmpleadoRegistroSerializer,
    EmpleadoUserDetailSerializer,
    UserListSerializer
)
from .permissions import TienePermisoGestionarEmpleados
from .models import User

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
