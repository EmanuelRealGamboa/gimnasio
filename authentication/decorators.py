from functools import wraps
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from .utils import tiene_permiso, tiene_cualquier_permiso


def permiso_requerido(permiso_nombre):
    """
    Decorador para vistas que requieren un permiso específico.
    Redirige a login si no está autenticado, o muestra error 403 si no tiene permiso.

    Uso:
        @permiso_requerido('gestionar_empleados')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if not tiene_permiso(request.user, permiso_nombre):
                return JsonResponse(
                    {'error': 'No tienes permisos para acceder a este recurso'},
                    status=403
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permisos_requeridos(*permisos_nombres):
    """
    Decorador para vistas que requieren múltiples permisos (TODOS deben cumplirse).

    Uso:
        @permisos_requeridos('gestionar_empleados', 'gestionar_instalaciones')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            for permiso in permisos_nombres:
                if not tiene_permiso(request.user, permiso):
                    return JsonResponse(
                        {'error': f'No tienes el permiso requerido: {permiso}'},
                        status=403
                    )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def cualquier_permiso_requerido(*permisos_nombres):
    """
    Decorador para vistas que requieren al menos uno de varios permisos.

    Uso:
        @cualquier_permiso_requerido('gestionar_empleados', 'gestionar_entrenamientos')
        def mi_vista(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if not tiene_cualquier_permiso(request.user, permisos_nombres):
                return JsonResponse(
                    {'error': 'No tienes ninguno de los permisos requeridos'},
                    status=403
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permiso_requerido_api(permiso_nombre):
    """
    Decorador para vistas de API (DRF) que requieren un permiso específico.
    Retorna Response en lugar de JsonResponse para compatibilidad con DRF.

    Uso:
        @permiso_requerido_api('gestionar_empleados')
        def mi_vista_api(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Autenticación requerida'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if not tiene_permiso(request.user, permiso_nombre):
                return Response(
                    {'error': 'No tienes permisos para acceder a este recurso'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
