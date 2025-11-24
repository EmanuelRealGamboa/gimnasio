from rest_framework import permissions
from roles.models import PersonaRol

class EsAdministradorOCajeroAcceso(permissions.BasePermission):
    """
    Permite acceso solo a administradores y cajeros.
    Si es cajero, solo permite acceso a registros de su sede.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if not hasattr(user, 'persona') or not user.persona:
            return False
        roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol__nombre', flat=True)
        return 'Administrador' in roles or 'Cajero' in roles

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol__nombre', flat=True)
        if 'Administrador' in roles:
            return True
        if 'Cajero' in roles:
            try:
                cajero_sede = getattr(user.persona.empleado.cajero, 'sede', None)
                return hasattr(obj, 'sede') and obj.sede == cajero_sede
            except Exception:
                return False
        return False
