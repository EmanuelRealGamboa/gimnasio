from rest_framework import permissions
from roles.models import PersonaRol


class EsAdministradorOSupervisor(permissions.BasePermission):
    """
    Permiso que solo permite acceso a administradores y supervisores.
    """
    message = "Solo los administradores y supervisores pueden realizar esta acción."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.is_staff:
            return True

        # Verificar si tiene rol de administrador o supervisor
        persona = getattr(request.user, 'persona', None)
        if not persona:
            return False

        roles_permitidos = ['Administrador', 'Supervisor de Espacio']
        roles_usuario = PersonaRol.objects.filter(
            persona=persona,
            rol__nombre__in=roles_permitidos
        ).exists()

        return roles_usuario


class PuedeGestionarHorarios(permissions.BasePermission):
    """
    Permiso para gestionar horarios.
    - Administradores: acceso completo
    - Supervisores: solo su sede
    - Entrenadores: solo lectura de sus horarios
    """
    message = "No tiene permisos para gestionar horarios."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        persona = getattr(request.user, 'persona', None)
        if not persona:
            return False

        # Administradores tienen acceso completo
        if PersonaRol.objects.filter(
            persona=persona,
            rol__nombre='Administrador'
        ).exists():
            return True

        # Supervisores y entrenadores pueden ver
        if request.method in permissions.SAFE_METHODS:
            roles_lectura = ['Supervisor de Espacio', 'Entrenador']
            return PersonaRol.objects.filter(
                persona=persona,
                rol__nombre__in=roles_lectura
            ).exists()

        # Solo admin y supervisor pueden modificar
        return PersonaRol.objects.filter(
            persona=persona,
            rol__nombre__in=['Administrador', 'Supervisor de Espacio']
        ).exists()


class PuedeHacerReservas(permissions.BasePermission):
    """
    Permiso para hacer reservas.
    - Clientes con membresía activa pueden reservar
    - Staff puede reservar para clientes
    """
    message = "Debe tener una membresía activa para hacer reservas."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Staff siempre puede
        if request.user.is_superuser or request.user.is_staff:
            return True

        persona = getattr(request.user, 'persona', None)
        if not persona:
            return False

        # Verificar si es staff
        if PersonaRol.objects.filter(
            persona=persona,
            rol__nombre__in=['Administrador', 'Recepcionista', 'Supervisor de Espacio']
        ).exists():
            return True

        # Verificar si es cliente con membresía activa
        try:
            from clientes.models import Cliente
            cliente = Cliente.objects.get(persona=persona)

            # Verificar si tiene suscripción activa
            from membresias.models import SuscripcionMembresia
            tiene_membresia_activa = SuscripcionMembresia.objects.filter(
                cliente=cliente,
                estado='activa'
            ).exists()

            return tiene_membresia_activa
        except Cliente.DoesNotExist:
            return False
