from roles.models import Permiso, RolPermiso, PersonaRol


def tiene_permiso(user, nombre_permiso):
    """
    Verifica si un usuario tiene un permiso específico basado en sus roles.

    Args:
        user: Usuario de Django
        nombre_permiso: Nombre del permiso a verificar (ej: 'gestionar_empleados')

    Returns:
        bool: True si el usuario tiene el permiso, False en caso contrario
    """
    if not user or not user.is_authenticated:
        return False

    # Superusuarios tienen todos los permisos
    if user.is_superuser:
        return True

    # Verificar que tenga persona asociada
    if not hasattr(user, 'persona') or not user.persona:
        return False

    # Buscar el permiso
    try:
        permiso = Permiso.objects.get(nombre=nombre_permiso)
    except Permiso.DoesNotExist:
        return False

    # Obtener roles de la persona
    roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol', flat=True)

    # Verificar si alguno de los roles tiene el permiso
    return RolPermiso.objects.filter(rol__in=roles, permiso=permiso).exists()


def obtener_permisos_usuario(user):
    """
    Obtiene todos los permisos de un usuario basado en sus roles.

    Args:
        user: Usuario de Django

    Returns:
        QuerySet: Lista de permisos del usuario
    """
    if not user or not user.is_authenticated:
        return Permiso.objects.none()

    if user.is_superuser:
        return Permiso.objects.all()

    if not hasattr(user, 'persona') or not user.persona:
        return Permiso.objects.none()

    # Obtener roles de la persona
    roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol', flat=True)

    # Obtener todos los permisos de esos roles
    return Permiso.objects.filter(roles__rol__in=roles).distinct()


def obtener_roles_usuario(user):
    """
    Obtiene todos los roles de un usuario.

    Args:
        user: Usuario de Django

    Returns:
        QuerySet: Lista de roles del usuario
    """
    if not user or not user.is_authenticated:
        return []

    if not hasattr(user, 'persona') or not user.persona:
        return []

    from roles.models import Rol
    return Rol.objects.filter(
        personas__persona=user.persona
    ).distinct()


def tiene_cualquier_permiso(user, lista_permisos):
    """
    Verifica si un usuario tiene al menos uno de los permisos especificados.

    Args:
        user: Usuario de Django
        lista_permisos: Lista de nombres de permisos

    Returns:
        bool: True si el usuario tiene al menos uno de los permisos
    """
    return any(tiene_permiso(user, permiso) for permiso in lista_permisos)


def tiene_todos_permisos(user, lista_permisos):
    """
    Verifica si un usuario tiene todos los permisos especificados.

    Args:
        user: Usuario de Django
        lista_permisos: Lista de nombres de permisos

    Returns:
        bool: True si el usuario tiene todos los permisos
    """
    return all(tiene_permiso(user, permiso) for permiso in lista_permisos)
