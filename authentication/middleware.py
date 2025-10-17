from django.shortcuts import redirect
from django.urls import reverse, resolve
from roles.models import Permiso, RolPermiso, PersonaRol


class RoleDashboardMiddleware:
    """
    Middleware que redirige a los usuarios autenticados al dashboard correspondiente
    según sus roles y permisos asignados.
    """
    def __init__(self, get_response):
        self.get_response = get_response

        # Mapeo de permisos a URLs de dashboard
        self.permission_dashboard_map = {
            'gestionar_empleados': 'dashboard_admin',
            'gestionar_entrenamientos': 'dashboard_entrenador',
            'gestionar_acceso': 'dashboard_recepcion',
            'gestionar_instalaciones': 'dashboard_supervisor',
            'gestionar_limpieza': 'dashboard_limpieza',
        }

        # URLs que no deben ser redirigidas
        self.excluded_paths = [
            '/api/',
            '/admin/',
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # Este middleware está deshabilitado porque el frontend de React
        # maneja sus propias redirecciones basadas en roles
        # El backend solo provee APIs REST
        return self.get_response(request)

    def _get_user_dashboard(self, user):
        """
        Determina el dashboard apropiado basado en los permisos del usuario.
        Retorna el nombre de la URL del dashboard o None.
        """
        # Superusuarios van al dashboard de admin
        if user.is_superuser:
            return 'dashboard_admin'

        # Verificar que el usuario tenga una persona asociada
        if not hasattr(user, 'persona') or not user.persona:
            return None

        # Obtener todos los roles de la persona
        persona_roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol', flat=True)

        if not persona_roles:
            return None

        # Obtener todos los permisos de esos roles
        permisos = Permiso.objects.filter(
            roles__rol__in=persona_roles
        ).distinct().values_list('nombre', flat=True)

        # Determinar dashboard basado en prioridad de permisos
        # (el orden importa: admin > supervisor > entrenador > recepción > limpieza)
        priority_order = [
            'gestionar_empleados',
            'gestionar_instalaciones',
            'gestionar_entrenamientos',
            'gestionar_acceso',
            'gestionar_limpieza',
        ]

        for permiso_nombre in priority_order:
            if permiso_nombre in permisos:
                return self.permission_dashboard_map.get(permiso_nombre)

        return None
