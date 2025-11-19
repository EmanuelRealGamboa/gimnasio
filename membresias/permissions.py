from rest_framework import permissions
from roles.models import PersonaRol


class EsAdministradorOCajero(permissions.BasePermission):
    """
    Permiso personalizado para permitir acceso solo a Administradores y Cajeros.
    """

    def has_permission(self, request, view):
        # Verificar si el usuario está autenticado
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Superusuarios siempre tienen acceso
        if user.is_superuser:
            return True

        # Verificar si el usuario tiene una persona asociada
        if not hasattr(user, 'persona') or not user.persona:
            return False

        # Obtener los roles del usuario
        roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol__nombre', flat=True)

        # Permitir acceso si tiene rol de Administrador o Cajero
        return 'Administrador' in roles or 'Cajero' in roles
