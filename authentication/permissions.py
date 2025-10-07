from rest_framework import permissions
from roles.models import Permiso, RolPermiso, PersonaRol

class TienePermisoGestionarEmpleados(permissions.BasePermission):
    """
    Permite el acceso solo a usuarios autenticados que tengan el permiso 'gestionar_empleados'.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Si es superusuario, permitir
        if user.is_superuser:
            return True
        # Si no tiene persona asociada, denegar
        if not hasattr(user, 'persona') or not user.persona:
            return False
        # Buscar el permiso 'gestionar_empleados'
        try:
            permiso = Permiso.objects.get(nombre='gestionar_empleados')
        except Permiso.DoesNotExist:
            return False
        # Buscar roles de la persona
        roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol', flat=True)
        # Buscar si alguno de los roles tiene el permiso
        return RolPermiso.objects.filter(rol__in=roles, permiso=permiso).exists()
