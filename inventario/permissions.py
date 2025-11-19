from rest_framework import permissions
from roles.models import PersonaRol


class EsAdministradorOCajero(permissions.BasePermission):
    """
    Permiso personalizado que permite el acceso solo a usuarios con rol de Administrador o Cajero.
    """

    def has_permission(self, request, view):
        user = request.user

        # Verificar que el usuario esté autenticado
        if not user or not user.is_authenticated:
            return False

        # Si es superusuario, permitir acceso
        if user.is_superuser:
            return True

        # Verificar que el usuario tenga una persona asociada
        if not hasattr(user, 'persona') or not user.persona:
            return False

        # Obtener los roles de la persona
        roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol__nombre', flat=True)

        # Permitir acceso solo si tiene rol de Administrador o Cajero
        return 'Administrador' in roles or 'Cajero' in roles
