from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import (
    EmpleadoUserCreateSerializer,
    EmpleadoRegistroSerializer,
    EmpleadoUserDetailSerializer,
    UserListSerializer
)
from .permissions import TienePermisoGestionarEmpleados
from .models import User, Persona
from clientes.models import Cliente
from django.db import transaction

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


class ClienteRegistroView(APIView):
    """
    Endpoint público para que los clientes se registren desde la app móvil.
    No requiere autenticación.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registrar un nuevo cliente desde la app móvil
        POST /api/registro/cliente/
        Body: {
            "email": "cliente@email.com",
            "password": "password123",
            "nombre": "Juan",
            "apellido_paterno": "Pérez",
            "apellido_materno": "García",
            "telefono": "5551234567",
            "fecha_nacimiento": "1990-01-01",
            "genero": "masculino",
            "objetivo_fitness": "perder_peso",
            "nivel_experiencia": "principiante"
        }
        """
        try:
            with transaction.atomic():
                # Validar datos requeridos
                required_fields = ['email', 'password', 'nombre', 'apellido_paterno', 'telefono']
                for field in required_fields:
                    if not request.data.get(field):
                        return Response(
                            {'error': f'El campo {field} es requerido'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                email = request.data.get('email')
                
                # Verificar si el email ya existe
                if User.objects.filter(email=email).exists():
                    return Response(
                        {'error': 'Ya existe un usuario con este email'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Crear usuario
                user = User.objects.create_user(
                    email=email,
                    password=request.data.get('password')
                )

                # Crear persona (Persona no tiene campo 'usuario'; User tiene OneToOne a Persona)
                persona = Persona.objects.create(
                    nombre=request.data.get('nombre'),
                    apellido_paterno=request.data.get('apellido_paterno'),
                    apellido_materno=request.data.get('apellido_materno', ''),
                    telefono=request.data.get('telefono'),
                    fecha_nacimiento=request.data.get('fecha_nacimiento'),
                    sexo=(request.data.get('sexo') or request.data.get('genero'))
                )

                # Asociar persona al usuario
                user.persona = persona
                user.save(update_fields=['persona'])

                # Crear cliente
                cliente = Cliente.objects.create(
                    persona=persona,
                    objetivo_fitness=request.data.get('objetivo_fitness', 'mantenimiento'),
                    nivel_experiencia=request.data.get('nivel_experiencia', 'principiante'),
                    estado='activo'
                )

                return Response({
                    'message': 'Cliente registrado exitosamente',
                    'cliente_id': cliente.id,
                    'user_id': user.id,
                    'email': user.email
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Error al registrar cliente: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
