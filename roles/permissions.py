from rest_framework.permissions import BasePermission
from roles.models import PersonaRol, RolPermiso, Permiso

class HasCustomPermission(BasePermission):
    def has_permission(self, request, view):
        required_perm = getattr(view, 'permission_required', None)
        if not required_perm:
            return True
        # Recuperar la persona asociada al usuario
        persona = getattr(request.user, 'persona', None)
        if not persona:
            return False
        # Verificar si la persona tiene el permiso requerido
        roles = PersonaRol.objects.filter(persona=persona).values_list('rol', flat=True)
        permiso = Permiso.objects.filter(nombre=required_perm).first()
        return RolPermiso.objects.filter(rol_id__in=roles, permiso=permiso).exists()