from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .decorators import permiso_requerido_api
from .utils import obtener_permisos_usuario, obtener_roles_usuario


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permiso_requerido_api('gestionar_empleados')
def dashboard_admin(request):
    """
    Dashboard para administradores con permiso de gestionar empleados.
    """
    permisos = obtener_permisos_usuario(request.user)
    roles = obtener_roles_usuario(request.user)

    # Verificar si la persona existe y no es None
    persona_data = None
    if hasattr(request.user, 'persona') and request.user.persona:
        persona_data = {
            'nombre': request.user.persona.nombre,
            'apellido_paterno': request.user.persona.apellido_paterno,
            'apellido_materno': request.user.persona.apellido_materno,
        }

    return Response({
        'dashboard': 'Administrador',
        'mensaje': 'Bienvenido al panel de administración',
        'user': {
            'email': request.user.email,
            'persona': persona_data
        },
        'roles': [rol.nombre for rol in roles],
        'permisos': [permiso.nombre for permiso in permisos],
        'accesos': {
            'gestionar_empleados': True,
            'gestionar_roles': True,
            'ver_reportes': True,
            'configuracion_sistema': True,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permiso_requerido_api('gestionar_entrenamientos')
def dashboard_entrenador(request):
    """
    Dashboard para entrenadores con permiso de gestionar entrenamientos.
    """
    permisos = obtener_permisos_usuario(request.user)
    roles = obtener_roles_usuario(request.user)

    # Verificar si la persona existe y no es None
    persona_data = None
    if hasattr(request.user, 'persona') and request.user.persona:
        persona_data = {
            'nombre': request.user.persona.nombre,
            'apellido_paterno': request.user.persona.apellido_paterno,
            'apellido_materno': request.user.persona.apellido_materno,
        }

    return Response({
        'dashboard': 'Entrenador',
        'mensaje': 'Bienvenido al panel de entrenador',
        'user': {
            'email': request.user.email,
            'persona': persona_data
        },
        'roles': [rol.nombre for rol in roles],
        'permisos': [permiso.nombre for permiso in permisos],
        'accesos': {
            'gestionar_entrenamientos': True,
            'ver_clientes': True,
            'gestionar_rutinas': True,
            'ver_horarios': True,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permiso_requerido_api('gestionar_acceso')
def dashboard_recepcion(request):
    """
    Dashboard para recepcionistas con permiso de gestionar acceso.
    """
    permisos = obtener_permisos_usuario(request.user)
    roles = obtener_roles_usuario(request.user)

    # Verificar si la persona existe y no es None
    persona_data = None
    if hasattr(request.user, 'persona') and request.user.persona:
        persona_data = {
            'nombre': request.user.persona.nombre,
            'apellido_paterno': request.user.persona.apellido_paterno,
            'apellido_materno': request.user.persona.apellido_materno,
        }

    return Response({
        'dashboard': 'Recepción',
        'mensaje': 'Bienvenido al panel de recepción',
        'user': {
            'email': request.user.email,
            'persona': persona_data
        },
        'roles': [rol.nombre for rol in roles],
        'permisos': [permiso.nombre for permiso in permisos],
        'accesos': {
            'gestionar_acceso': True,
            'registrar_visitas': True,
            'ver_membresias': True,
            'procesar_pagos': True,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permiso_requerido_api('gestionar_instalaciones')
def dashboard_supervisor(request):
    """
    Dashboard para supervisores con permiso de gestionar instalaciones.
    """
    permisos = obtener_permisos_usuario(request.user)
    roles = obtener_roles_usuario(request.user)

    # Verificar si la persona existe y no es None
    persona_data = None
    if hasattr(request.user, 'persona') and request.user.persona:
        persona_data = {
            'nombre': request.user.persona.nombre,
            'apellido_paterno': request.user.persona.apellido_paterno,
            'apellido_materno': request.user.persona.apellido_materno,
        }

    return Response({
        'dashboard': 'Supervisor',
        'mensaje': 'Bienvenido al panel de supervisión',
        'user': {
            'email': request.user.email,
            'persona': persona_data
        },
        'roles': [rol.nombre for rol in roles],
        'permisos': [permiso.nombre for permiso in permisos],
        'accesos': {
            'gestionar_instalaciones': True,
            'ver_mantenimiento': True,
            'gestionar_espacios': True,
            'asignar_personal': True,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permiso_requerido_api('gestionar_limpieza')
def dashboard_limpieza(request):
    """
    Dashboard para personal de limpieza con permiso de gestionar limpieza.
    """
    permisos = obtener_permisos_usuario(request.user)
    roles = obtener_roles_usuario(request.user)

    # Verificar si la persona existe y no es None
    persona_data = None
    if hasattr(request.user, 'persona') and request.user.persona:
        persona_data = {
            'nombre': request.user.persona.nombre,
            'apellido_paterno': request.user.persona.apellido_paterno,
            'apellido_materno': request.user.persona.apellido_materno,
        }

    return Response({
        'dashboard': 'Personal de Limpieza',
        'mensaje': 'Bienvenido al panel de limpieza',
        'user': {
            'email': request.user.email,
            'persona': persona_data
        },
        'roles': [rol.nombre for rol in roles],
        'permisos': [permiso.nombre for permiso in permisos],
        'accesos': {
            'gestionar_limpieza': True,
            'ver_areas_asignadas': True,
            'reportar_mantenimiento': True,
            'ver_horarios': True,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_default(request):
    """
    Dashboard por defecto para usuarios sin permisos específicos.
    """
    permisos = obtener_permisos_usuario(request.user)
    roles = obtener_roles_usuario(request.user)

    # Verificar si la persona existe y no es None
    persona_data = None
    if hasattr(request.user, 'persona') and request.user.persona:
        persona_data = {
            'nombre': request.user.persona.nombre,
            'apellido_paterno': request.user.persona.apellido_paterno,
            'apellido_materno': request.user.persona.apellido_materno,
        }

    return Response({
        'dashboard': 'Usuario',
        'mensaje': 'Bienvenido al sistema',
        'user': {
            'email': request.user.email,
            'persona': persona_data
        },
        'roles': [rol.nombre for rol in roles],
        'permisos': [permiso.nombre for permiso in permisos],
    }, status=status.HTTP_200_OK)
