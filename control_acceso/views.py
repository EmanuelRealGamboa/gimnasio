from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import EsAdministradorOCajeroAcceso
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta

from .models import RegistroAcceso, Credencial
from .serializers import (
    RegistroAccesoSerializer,
    ValidarAccesoSerializer,
    RegistrarAccesoSerializer,
)
from clientes.models import Cliente
from membresias.models import SuscripcionMembresia
from instalaciones.models import Sede


@api_view(['POST'])
@permission_classes([EsAdministradorOCajeroAcceso])
def validar_acceso(request):
    """
    Endpoint para validar si un cliente puede acceder.
    POST /api/accesos/registros/validar_acceso/
    Body: { "search_term": "nombre/telefono", "sede_id": 1 }
    """
    serializer = ValidarAccesoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    search_term = serializer.validated_data['search_term']
    sede_id = serializer.validated_data['sede_id']

    # Buscar cliente por ID, nombre, apellido, teléfono o email
    query = Q(persona__nombre__icontains=search_term) | \
            Q(persona__apellido_paterno__icontains=search_term) | \
            Q(persona__apellido_materno__icontains=search_term) | \
            Q(persona__telefono__icontains=search_term) | \
            Q(persona__usuario__email__icontains=search_term)

    # Si el término de búsqueda es numérico, buscar también por ID
    if search_term.strip().isdigit():
        query |= Q(persona_id=int(search_term.strip()))

    # Búsqueda por nombre completo (si tiene espacios, buscar como nombre completo)
    if ' ' in search_term.strip():
        palabras = search_term.strip().split()
        # Intentar buscar por combinación de nombre y apellidos
        if len(palabras) >= 2:
            query |= (
                Q(persona__nombre__icontains=palabras[0]) &
                Q(persona__apellido_paterno__icontains=palabras[1])
            )
            if len(palabras) >= 3:
                query |= (
                    Q(persona__nombre__icontains=palabras[0]) &
                    Q(persona__apellido_paterno__icontains=palabras[1]) &
                    Q(persona__apellido_materno__icontains=palabras[2])
                )

    clientes = Cliente.objects.filter(query).select_related('persona', 'persona__usuario').distinct()

    if not clientes.exists():
        return Response({
            'encontrado': False,
            'mensaje': 'No se encontró ningún cliente con ese criterio de búsqueda',
            'clientes': []
        }, status=status.HTTP_200_OK)

    # Si hay múltiples resultados, devolver lista para que el usuario seleccione
    if clientes.count() > 1:
        resultados = []
        for cliente in clientes[:10]:  # Limitar a 10 resultados
            persona = cliente.persona
            resultados.append({
                'cliente_id': cliente.persona_id,
                'nombre_completo': f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno or ''}".strip(),
                'email': persona.usuario.email if hasattr(persona, 'usuario') and persona.usuario else None,
                'telefono': persona.telefono
            })

        return Response({
            'encontrado': True,
            'multiple': True,
            'mensaje': f'Se encontraron {clientes.count()} clientes. Selecciona uno:',
            'clientes': resultados
        })

    # Un solo resultado - validar acceso
    cliente = clientes.first()
    return _validar_cliente_acceso(cliente, sede_id)


@api_view(['POST'])
@permission_classes([EsAdministradorOCajeroAcceso])
def registrar_acceso(request):
    """
    Endpoint para registrar el acceso de un cliente.
    POST /api/accesos/registros/registrar_acceso/
    Body: { "cliente_id": 1, "sede_id": 1, "notas": "..." }
    """
    serializer = RegistrarAccesoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    cliente_id = serializer.validated_data['cliente_id']
    sede_id = serializer.validated_data['sede_id']
    notas = serializer.validated_data.get('notas', '')

    try:
        cliente = Cliente.objects.get(persona_id=cliente_id)
        sede = Sede.objects.get(pk=sede_id)
    except Cliente.DoesNotExist:
        return Response({
            'error': 'Cliente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Sede.DoesNotExist:
        return Response({
            'error': 'Sede no encontrada'
        }, status=status.HTTP_404_NOT_FOUND)

    # Obtener membresía activa
    suscripcion_activa = SuscripcionMembresia.objects.filter(
        cliente=cliente,
        estado='activa'
    ).order_by('-fecha_inicio').first()

    # Validar acceso
    puede_acceder = False
    motivo_denegado = None
    membresia_nombre = None
    membresia_estado = None

    if not suscripcion_activa:
        motivo_denegado = 'No tiene membresía activa'
    else:
        membresia_nombre = suscripcion_activa.membresia.nombre_plan
        membresia_estado = suscripcion_activa.estado

        # Verificar si la membresía permite acceso a esta sede
        if suscripcion_activa.membresia.permite_todas_sedes:
            puede_acceder = True
        elif suscripcion_activa.sede_suscripcion_id == sede_id:
            puede_acceder = True
        else:
            sede_nombre = suscripcion_activa.sede_suscripcion.nombre if suscripcion_activa.sede_suscripcion else 'sede específica'
            motivo_denegado = f'La membresía solo permite acceso a {sede_nombre}'

    # Crear registro de acceso
    registro = RegistroAcceso.objects.create(
        cliente=cliente,
        sede=sede,
        autorizado=puede_acceder,
        motivo_denegado=motivo_denegado,
        membresia_nombre=membresia_nombre,
        membresia_estado=membresia_estado,
        notas=notas,
        registrado_por=request.user.persona if hasattr(request.user, 'persona') else None
    )

    serializer_response = RegistroAccesoSerializer(registro)

    return Response({
        'mensaje': '✓ Acceso autorizado' if puede_acceder else '✗ Acceso denegado',
        'registro': serializer_response.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([EsAdministradorOCajeroAcceso])
def estadisticas_acceso(request):
    """
    Endpoint para obtener estadísticas de accesos.
    GET /api/accesos/registros/estadisticas/?sede=1
    """
    sede_id = request.query_params.get('sede', None)
    queryset = RegistroAcceso.objects.all()

    if sede_id:
        queryset = queryset.filter(sede_id=sede_id)

    # Accesos de hoy
    hoy = timezone.now().date()
    queryset_hoy = queryset.filter(fecha_hora_entrada__date=hoy)

    accesos_hoy = queryset_hoy.count()
    autorizados = queryset_hoy.filter(autorizado=True).count()
    denegados = queryset_hoy.filter(autorizado=False).count()

    # Accesos del mes
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    accesos_mes = queryset.filter(fecha_hora_entrada__gte=inicio_mes).count()

    # Clientes únicos del mes
    clientes_unicos_mes = queryset.filter(
        fecha_hora_entrada__gte=inicio_mes
    ).values('cliente').distinct().count()

    return Response({
        'accesos_hoy': accesos_hoy,
        'autorizados': autorizados,
        'denegados': denegados,
        'accesos_mes': accesos_mes,
        'clientes_unicos_mes': clientes_unicos_mes,
    })


@api_view(['GET'])
@permission_classes([EsAdministradorOCajeroAcceso])
def listar_registros(request):
    """
    Endpoint para listar registros de acceso.
    GET /api/accesos/registros/
    """
    queryset = RegistroAcceso.objects.select_related(
        'cliente',
        'cliente__persona',
        'sede'
    ).all()

    user = request.user
    from roles.models import PersonaRol
    roles = PersonaRol.objects.filter(persona=user.persona).values_list('rol__nombre', flat=True)
    if 'Cajero' in roles:
        try:
            cajero_sede = getattr(user.persona.empleado.cajero, 'sede', None)
            if cajero_sede:
                queryset = queryset.filter(sede=cajero_sede)
        except Exception:
            queryset = queryset.none()
    else:
        # Filtrar por sede (solo admins pueden ver otras sedes)
        sede_id = request.query_params.get('sede', None)
        if sede_id:
            queryset = queryset.filter(sede_id=sede_id)

    # Filtrar por cliente
    cliente_id = request.query_params.get('cliente', None)
    if cliente_id:
        queryset = queryset.filter(cliente_id=cliente_id)

    # Filtrar por autorizado
    autorizado = request.query_params.get('autorizado', None)
    if autorizado is not None:
        autorizado_bool = autorizado.lower() in ['true', '1', 'yes']
        queryset = queryset.filter(autorizado=autorizado_bool)

    # Filtrar por fecha (opcional) - por defecto solo accesos del día
    fecha = request.query_params.get('fecha', None)
    if fecha:
        queryset = queryset.filter(fecha_hora_entrada__date=fecha)
    else:
        # Por defecto mostrar solo accesos de hoy
        hoy = timezone.now().date()
        queryset = queryset.filter(fecha_hora_entrada__date=hoy)

    # Limitar resultados y ordenar por más recientes
    limit = request.query_params.get('limit', 50)
    queryset = queryset.order_by('-fecha_hora_entrada')[:int(limit)]

    serializer = RegistroAccesoSerializer(queryset, many=True)
    return Response(serializer.data)


def _validar_cliente_acceso(cliente, sede_id):
    """
    Método auxiliar para validar el acceso de un cliente específico.
    """
    persona = cliente.persona

    # Buscar membresía activa
    suscripcion_activa = SuscripcionMembresia.objects.filter(
        cliente=cliente,
        estado='activa'
    ).select_related('membresia', 'sede_suscripcion').order_by('-fecha_inicio').first()

    # Datos básicos del cliente
    cliente_info = {
        'cliente_id': cliente.persona_id,
        'persona_id': persona.id,
        'nombre_completo': f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno or ''}".strip(),
        'email': persona.usuario.email if hasattr(persona, 'usuario') and persona.usuario else None,
        'telefono': persona.telefono,
    }

    # Estadísticas de acceso
    total_accesos = RegistroAcceso.objects.filter(cliente=cliente).count()
    ultimo_acceso = RegistroAcceso.objects.filter(
        cliente=cliente
    ).order_by('-fecha_hora_entrada').first()

    cliente_info.update({
        'total_accesos': total_accesos,
        'ultimo_acceso': ultimo_acceso.fecha_hora_entrada if ultimo_acceso else None
    })

    if not suscripcion_activa:
        # No tiene membresía activa
        cliente_info.update({
            'tiene_membresia_activa': False,
            'membresia_id': None,
            'membresia_nombre': None,
            'membresia_tipo': None,
            'membresia_estado': None,
            'fecha_inicio': None,
            'fecha_fin': None,
            'dias_restantes': None,
            'permite_todas_sedes': None,
            'sede_suscripcion_id': None,
            'sede_suscripcion_nombre': None,
            'puede_acceder': False,
            'motivo_denegado': 'No tiene membresía activa'
        })
    else:
        # Tiene membresía activa - validar si puede acceder a esta sede
        puede_acceder = False
        motivo_denegado = None

        if suscripcion_activa.membresia.permite_todas_sedes:
            puede_acceder = True
        elif suscripcion_activa.sede_suscripcion_id == sede_id:
            puede_acceder = True
        else:
            sede_nombre = suscripcion_activa.sede_suscripcion.nombre if suscripcion_activa.sede_suscripcion else 'sede específica'
            motivo_denegado = f'La membresía solo permite acceso a {sede_nombre}'

        cliente_info.update({
            'tiene_membresia_activa': True,
            'membresia_id': suscripcion_activa.id,
            'membresia_nombre': suscripcion_activa.membresia.nombre_plan,
            'membresia_tipo': suscripcion_activa.membresia.get_tipo_display(),
            'membresia_estado': suscripcion_activa.estado,
            'fecha_inicio': suscripcion_activa.fecha_inicio,
            'fecha_fin': suscripcion_activa.fecha_fin,
            'dias_restantes': suscripcion_activa.dias_restantes,
            'permite_todas_sedes': suscripcion_activa.membresia.permite_todas_sedes,
            'sede_suscripcion_id': suscripcion_activa.sede_suscripcion_id,
            'sede_suscripcion_nombre': suscripcion_activa.sede_suscripcion.nombre if suscripcion_activa.sede_suscripcion else None,
            'puede_acceder': puede_acceder,
            'motivo_denegado': motivo_denegado
        })

    return Response({
        'encontrado': True,
        'multiple': False,
        'cliente': cliente_info
    })
