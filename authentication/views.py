from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Count
from django.db import transaction
from .serializers import (
    EmpleadoUserCreateSerializer,
    EmpleadoRegistroSerializer,
    EmpleadoUserDetailSerializer,
    UserListSerializer
)
from .permissions import TienePermisoGestionarEmpleados
from .models import User, Persona
from empleados.models import Empleado
from clientes.models import Cliente

class EmpleadoUserCreateView(APIView):
    """
    Endpoint para que el administrador cree, liste, actualice, elimine y consulte empleados.
    """
    permission_classes = [TienePermisoGestionarEmpleados]
    
    def get(self, request, pk=None):
        if pk:
            # Detalle de usuario con la información personalizada
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            serializer = EmpleadoUserDetailSerializer(user, context={'request': request})
            return Response(serializer.data)
        else:
            # Listado de usuarios con información completa - SOLO EMPLEADOS
            # Filtrar solo usuarios que tengan un registro de Empleado asociado a través de persona
            users = User.objects.select_related('persona').filter(
                persona__empleado__isnull=False
            ).all()
            serializer = UserListSerializer(users, many=True)
            return Response(serializer.data) 
 
    def post(self, request):
        serializer = EmpleadoUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'success': True, 'user_id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpleadoUserCreateSerializer(user, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'user_id': user.id, 'email': user.email})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpleadoUserCreateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'user_id': user.id, 'email': user.email})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({'success': True, 'detail': 'Usuario eliminado.'}, status=status.HTTP_204_NO_CONTENT)
    
    def retrieve(self, request, pk):
        """
        Consulta la información completa de un usuario por su ID.
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmpleadoUserDetailSerializer(user)
        return Response(serializer.data)
	   



class EmpleadoRegistroView(APIView):
    """
    Endpoint para registrar empleados desde el navegador (solo admins con permiso).
    """
    permission_classes = [TienePermisoGestionarEmpleados]

    def post(self, request):
        serializer = EmpleadoRegistroSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'success': True, 'user_id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmpleadoEstadisticasView(APIView):
    """
    Endpoint para obtener estadísticas de empleados
    GET /api/admin/empleados/estadisticas/?sede={id}
    """
    permission_classes = [TienePermisoGestionarEmpleados]

    def get(self, request):
        # Filtrar por sede si se proporciona
        queryset = Empleado.objects.all()
        sede = request.query_params.get('sede', None)

        if sede:
            queryset = queryset.filter(sede_id=sede)

        # Total de empleados
        total_empleados = queryset.count()

        # Estadísticas por estado
        activos = queryset.filter(estado='Activo').count()
        inactivos = queryset.filter(estado='Inactivo').count()

        # Estadísticas por tipo de contrato
        por_contrato = {}
        contratos = queryset.values('tipo_contrato').annotate(total=Count('persona')).order_by('-total')
        for contrato in contratos:
            por_contrato[contrato['tipo_contrato']] = contrato['total']

        # Estadísticas por puesto
        por_puesto = {}
        puestos = queryset.values('puesto').annotate(total=Count('persona')).order_by('-total')
        for puesto in puestos:
            por_puesto[puesto['puesto']] = puesto['total']

        # Estadísticas por departamento
        por_departamento = {}
        departamentos = queryset.values('departamento').annotate(total=Count('persona')).order_by('-total')
        for depto in departamentos:
            if depto['departamento']:  # Ignorar departamentos vacíos
                por_departamento[depto['departamento']] = depto['total']

        # Estadísticas por sede (si no se filtra por sede específica)
        por_sede = []
        if not sede:
            por_sede = list(Empleado.objects.values('sede__nombre').annotate(
                total=Count('persona')
            ).order_by('-total'))

        response_data = {
            'total_empleados': total_empleados,
            'por_estado': {
                'activos': activos,
                'inactivos': inactivos,
            },
            'por_contrato': por_contrato,
            'por_puesto': por_puesto,
            'por_departamento': por_departamento,
        }

        if not sede:
            response_data['por_sede'] = por_sede

        return Response(response_data)


class ClienteRegistroView(APIView):
    """
    Endpoint público para que los clientes se registren desde la app móvil.
    No requiere autenticación.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Registrar un nuevo cliente desde la app móvil
        POST /api/registro/cliente/
        Body: {
            "email": "cliente@email.com",
            "password": "password123",
            "nombre": "Juan",
            "apellido_paterno": "Pérez",
            "apellido_materno": "García",
            "telefono": "5551234567",
            "fecha_nacimiento": "1990-01-01",
            "genero": "masculino",
            "objetivo_fitness": "perder_peso",
            "nivel_experiencia": "principiante",
            "sede_id": 1
        }
        """
        try:
            with transaction.atomic():
                # Validar datos requeridos (AHORA INCLUYE sede_id)
                required_fields = ['email', 'password', 'nombre', 'apellido_paterno', 'telefono', 'sede_id']
                for field in required_fields:
                    if not request.data.get(field):
                        return Response(
                            {'error': f'El campo {field} es requerido'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                email = request.data.get('email')
                sede_id = request.data.get('sede_id')

                # Verificar si el email ya existe
                if User.objects.filter(email=email).exists():
                    return Response(
                        {'error': 'Ya existe un usuario con este email'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Validar que la sede existe
                from instalaciones.models import Sede
                try:
                    sede = Sede.objects.get(id=sede_id)
                except Sede.DoesNotExist:
                    return Response(
                        {'error': 'La sede especificada no existe'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Crear usuario
                user = User.objects.create_user(
                    email=email,
                    password=request.data.get('password')
                )

                # Crear persona
                fecha_nacimiento = request.data.get('fecha_nacimiento')
                if fecha_nacimiento == '' or fecha_nacimiento is None:
                    fecha_nacimiento = None

                persona = Persona.objects.create(
                    nombre=request.data.get('nombre'),
                    apellido_paterno=request.data.get('apellido_paterno'),
                    apellido_materno=request.data.get('apellido_materno', ''),
                    telefono=request.data.get('telefono'),
                    fecha_nacimiento=fecha_nacimiento,
                    sexo=(request.data.get('sexo') or request.data.get('genero') or None)
                )

                # Asociar persona al usuario
                user.persona = persona
                user.save(update_fields=['persona'])

                # Crear cliente con la sede seleccionada por el usuario
                cliente = Cliente.objects.create(
                    persona=persona,
                    sede=sede,
                    objetivo_fitness=request.data.get('objetivo_fitness', 'mantenimiento'),
                    nivel_experiencia=request.data.get('nivel_experiencia', 'principiante'),
                    estado='activo'
                )

                return Response({
                    'message': 'Cliente registrado exitosamente',
                    'cliente_id': cliente.persona.id,
                    'user_id': user.id,
                    'email': user.email,
                    'sede_id': cliente.sede_id,
                    'sede_nombre': cliente.sede.nombre
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': f'Error al registrar cliente: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SedesDisponiblesView(APIView):
    """
    Endpoint público para listar las sedes disponibles.
    Usado por la app móvil durante el registro.
    GET /api/sedes-disponibles/
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """Listar todas las sedes disponibles"""
        from instalaciones.models import Sede

        sedes = Sede.objects.all().order_by('nombre')

        data = [
            {
                'id': sede.id,
                'nombre': sede.nombre,
                'direccion': sede.direccion,
                'telefono': sede.telefono
            }
            for sede in sedes
        ]

        return Response(data, status=status.HTTP_200_OK)


class UsuarioActualView(APIView):
    """
    Endpoint para obtener información del usuario autenticado.
    Usado por la app móvil para obtener datos del cliente.
    GET /api/auth/me/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtener información del usuario autenticado"""
        user = request.user

        # Verificar si el usuario es un cliente
        if hasattr(user, 'persona') and hasattr(user.persona, 'cliente'):
            cliente = user.persona.cliente
            return Response({
                'user_id': user.id,
                'email': user.email,
                'persona_id': user.persona.id,
                'cliente_id': cliente.persona_id,
                'nombre': user.persona.nombre,
                'apellido_paterno': user.persona.apellido_paterno,
                'apellido_materno': user.persona.apellido_materno,
                'telefono': user.persona.telefono,
                'fecha_nacimiento': user.persona.fecha_nacimiento,
                'sexo': user.persona.sexo,
                'sede_id': cliente.sede_id,
                'sede_nombre': cliente.sede.nombre,
                'estado': cliente.estado,
                'nivel_experiencia': cliente.nivel_experiencia,
                'objetivo_fitness': cliente.objetivo_fitness,
                'fecha_registro': cliente.fecha_registro,
            })

        # Si es empleado u otro tipo de usuario
        if hasattr(user, 'persona'):
            return Response({
                'user_id': user.id,
                'email': user.email,
                'persona_id': user.persona.id,
                'nombre': user.persona.nombre,
                'apellido_paterno': user.persona.apellido_paterno,
                'apellido_materno': user.persona.apellido_materno,
            })

        # Usuario sin persona asociada
        return Response({
            'user_id': user.id,
            'email': user.email,
        })


class DashboardStatsView(APIView):
    """
    Endpoint para obtener estadísticas del dashboard de administrador.
    GET /api/dashboard/stats/?sede={id}&fecha_inicio={date}&fecha_fin={date}
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        from datetime import datetime, timedelta
        from django.db.models import Sum, Count, Q, Avg
        from membresias.models import SuscripcionMembresia, Membresia
        from control_acceso.models import RegistroAcceso
        from ventas.models import VentaProducto, DetalleVentaProducto
        from inventario.models import Producto
        from instalaciones.models import Sede
        from clientes.models import Cliente

        # Filtros
        sede_id = request.query_params.get('sede', None)
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)

        # Fechas por defecto: mes actual
        if not fecha_inicio:
            fecha_inicio = timezone.now().replace(day=1).date()
        else:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()

        if not fecha_fin:
            fecha_fin = timezone.now().date()
        else:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

        # =====================================================
        # KPIs PRINCIPALES
        # =====================================================

        # 1. Total de Clientes Activos
        clientes_query = Cliente.objects.filter(estado='activo')
        if sede_id:
            clientes_query = clientes_query.filter(sede_id=sede_id)
        total_clientes_activos = clientes_query.count()

        # Comparar con mes anterior
        fecha_mes_anterior = fecha_inicio - timedelta(days=30)
        clientes_mes_anterior = Cliente.objects.filter(
            estado='activo',
            fecha_registro__lte=fecha_mes_anterior
        )
        if sede_id:
            clientes_mes_anterior = clientes_mes_anterior.filter(sede_id=sede_id)
        clientes_mes_anterior_count = clientes_mes_anterior.count()

        if clientes_mes_anterior_count > 0:
            tendencia_clientes = ((total_clientes_activos - clientes_mes_anterior_count) / clientes_mes_anterior_count) * 100
        else:
            tendencia_clientes = 100 if total_clientes_activos > 0 else 0

        # 2. Membresías Activas
        membresias_query = SuscripcionMembresia.objects.all()
        if sede_id:
            membresias_query = membresias_query.filter(sede_suscripcion_id=sede_id)

        membresias_activas = membresias_query.filter(estado='activa').count()
        membresias_vencidas = membresias_query.filter(estado='vencida').count()
        membresias_por_vencer = membresias_query.filter(
            estado='activa',
            fecha_fin__lte=fecha_fin + timedelta(days=7),
            fecha_fin__gte=fecha_fin
        ).count()

        # 3. Ingresos del Mes
        ingresos_query = VentaProducto.objects.filter(
            fecha_venta__date__gte=fecha_inicio,
            fecha_venta__date__lte=fecha_fin,
            estado='completada'
        )
        if sede_id:
            ingresos_query = ingresos_query.filter(sede_id=sede_id)

        ingresos_mes = ingresos_query.aggregate(total=Sum('total'))['total'] or 0

        # Ingresos por membresías (nuevas suscripciones)
        suscripciones_query = SuscripcionMembresia.objects.filter(
            fecha_suscripcion__date__gte=fecha_inicio,
            fecha_suscripcion__date__lte=fecha_fin
        )
        if sede_id:
            suscripciones_query = suscripciones_query.filter(sede_suscripcion_id=sede_id)

        ingresos_membresias = suscripciones_query.aggregate(total=Sum('precio_pagado'))['total'] or 0
        ingresos_totales = float(ingresos_mes) + float(ingresos_membresias)

        # Comparar con mes anterior
        fecha_fin_mes_anterior = fecha_inicio - timedelta(days=1)
        ingresos_mes_anterior_productos = VentaProducto.objects.filter(
            fecha_venta__date__gte=fecha_mes_anterior,
            fecha_venta__date__lte=fecha_fin_mes_anterior,
            estado='completada'
        )
        if sede_id:
            ingresos_mes_anterior_productos = ingresos_mes_anterior_productos.filter(sede_id=sede_id)

        ingresos_mes_anterior = ingresos_mes_anterior_productos.aggregate(total=Sum('total'))['total'] or 0

        suscripciones_mes_anterior = SuscripcionMembresia.objects.filter(
            fecha_suscripcion__date__gte=fecha_mes_anterior,
            fecha_suscripcion__date__lte=fecha_fin_mes_anterior
        )
        if sede_id:
            suscripciones_mes_anterior = suscripciones_mes_anterior.filter(sede_suscripcion_id=sede_id)

        ingresos_membresias_anterior = suscripciones_mes_anterior.aggregate(total=Sum('precio_pagado'))['total'] or 0
        total_mes_anterior = float(ingresos_mes_anterior) + float(ingresos_membresias_anterior)

        if total_mes_anterior > 0:
            tendencia_ingresos = ((ingresos_totales - total_mes_anterior) / total_mes_anterior) * 100
        else:
            tendencia_ingresos = 100 if ingresos_totales > 0 else 0

        # 4. Accesos Hoy
        hoy = timezone.now().date()
        accesos_query = RegistroAcceso.objects.filter(fecha_hora_entrada__date=hoy)
        if sede_id:
            accesos_query = accesos_query.filter(sede_id=sede_id)

        accesos_hoy = accesos_query.count()
        accesos_autorizados = accesos_query.filter(autorizado=True).count()
        accesos_denegados = accesos_query.filter(autorizado=False).count()

        # =====================================================
        # DATOS PARA GRÁFICAS
        # =====================================================

        # 1. Tendencia de Accesos (últimos 30 días)
        accesos_30_dias = []
        for i in range(30):
            fecha = hoy - timedelta(days=29-i)
            accesos_dia_query = RegistroAcceso.objects.filter(fecha_hora_entrada__date=fecha)
            if sede_id:
                accesos_dia_query = accesos_dia_query.filter(sede_id=sede_id)

            total_dia = accesos_dia_query.count()
            accesos_30_dias.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'dia': fecha.strftime('%d/%m'),
                'total': total_dia
            })

        # 2. Ingresos por Concepto
        ingresos_por_concepto = [
            {
                'concepto': 'Membresías',
                'monto': float(ingresos_membresias)
            },
            {
                'concepto': 'Productos',
                'monto': float(ingresos_mes)
            }
        ]

        # 3. Distribución de Membresías por Tipo
        distribucion_membresias = []
        membresias_activas_obj = membresias_query.filter(estado='activa')
        tipos = membresias_activas_obj.values('membresia__tipo').annotate(
            total=Count('id')
        ).order_by('-total')

        for tipo in tipos:
            tipo_display = dict(Membresia.TIPO_CHOICES).get(tipo['membresia__tipo'], tipo['membresia__tipo'])
            distribucion_membresias.append({
                'tipo': tipo_display,
                'total': tipo['total']
            })

        # 4. Top 10 Productos Más Vendidos
        productos_mas_vendidos = []
        detalles = DetalleVentaProducto.objects.filter(
            venta__fecha_venta__date__gte=fecha_inicio,
            venta__fecha_venta__date__lte=fecha_fin,
            venta__estado='completada'
        )
        if sede_id:
            detalles = detalles.filter(venta__sede_id=sede_id)

        productos_stats = detalles.values('producto__nombre').annotate(
            cantidad_total=Sum('cantidad'),
            ingresos_total=Sum('total')
        ).order_by('-cantidad_total')[:10]

        for producto in productos_stats:
            productos_mas_vendidos.append({
                'nombre': producto['producto__nombre'],
                'cantidad': producto['cantidad_total'],
                'ingresos': float(producto['ingresos_total'])
            })

        # 5. Productos con Stock Bajo
        from inventario.models import Inventario
        productos_stock_bajo = []
        inventarios_query = Inventario.objects.filter(
            cantidad_actual__lt=10,
            cantidad_actual__gt=0
        ).select_related('producto', 'sede', 'producto__categoria')

        if sede_id:
            inventarios_query = inventarios_query.filter(sede_id=sede_id)

        for inventario in inventarios_query[:5]:
            productos_stock_bajo.append({
                'id': inventario.producto.producto_id,
                'nombre': inventario.producto.nombre,
                'stock': inventario.cantidad_actual,
                'categoria': inventario.producto.categoria.nombre if inventario.producto.categoria else 'Sin categoría',
                'sede': inventario.sede.nombre
            })

        # 6. Últimas Ventas
        ultimas_ventas = []
        ventas_recientes = VentaProducto.objects.filter(
            estado='completada'
        ).select_related('sede', 'empleado', 'cliente').order_by('-fecha_venta')

        if sede_id:
            ventas_recientes = ventas_recientes.filter(sede_id=sede_id)

        for venta in ventas_recientes[:10]:
            ultimas_ventas.append({
                'id': venta.venta_id,
                'fecha': venta.fecha_venta.strftime('%Y-%m-%d %H:%M'),
                'total': float(venta.total),
                'sede': venta.sede.nombre if venta.sede else 'N/A',
                'cajero': venta.empleado.email if venta.empleado else 'N/A'
            })

        # Últimas Suscripciones
        ultimas_suscripciones = []
        suscripciones_recientes = SuscripcionMembresia.objects.select_related(
            'cliente__persona', 'membresia', 'sede_suscripcion'
        ).order_by('-fecha_suscripcion')

        if sede_id:
            suscripciones_recientes = suscripciones_recientes.filter(sede_suscripcion_id=sede_id)

        for suscripcion in suscripciones_recientes[:10]:
            ultimas_suscripciones.append({
                'id': suscripcion.id,
                'fecha': suscripcion.fecha_suscripcion.strftime('%Y-%m-%d %H:%M'),
                'cliente': f"{suscripcion.cliente.persona.nombre} {suscripcion.cliente.persona.apellido_paterno}",
                'membresia': suscripcion.membresia.nombre_plan,
                'total': float(suscripcion.precio_pagado),
                'sede': suscripcion.sede_suscripcion.nombre if suscripcion.sede_suscripcion else 'N/A'
            })

        # 7. Evolución de Ingresos Mensuales (últimos 6 meses)
        evolucion_ingresos = []
        for i in range(5, -1, -1):  # 6 meses hacia atrás
            mes_fecha = timezone.now().date().replace(day=1) - timedelta(days=i*30)
            primer_dia_mes = mes_fecha.replace(day=1)

            # Calcular último día del mes
            if mes_fecha.month == 12:
                ultimo_dia_mes = mes_fecha.replace(day=31)
            else:
                siguiente_mes = mes_fecha.replace(month=mes_fecha.month + 1, day=1)
                ultimo_dia_mes = siguiente_mes - timedelta(days=1)

            # Ingresos por productos
            ingresos_productos_mes = VentaProducto.objects.filter(
                fecha_venta__date__gte=primer_dia_mes,
                fecha_venta__date__lte=ultimo_dia_mes,
                estado='completada'
            )
            if sede_id:
                ingresos_productos_mes = ingresos_productos_mes.filter(sede_id=sede_id)

            total_productos = ingresos_productos_mes.aggregate(total=Sum('total'))['total'] or 0

            # Ingresos por membresías
            ingresos_membresias_mes = SuscripcionMembresia.objects.filter(
                fecha_suscripcion__date__gte=primer_dia_mes,
                fecha_suscripcion__date__lte=ultimo_dia_mes
            )
            if sede_id:
                ingresos_membresias_mes = ingresos_membresias_mes.filter(sede_suscripcion_id=sede_id)

            total_membresias = ingresos_membresias_mes.aggregate(total=Sum('precio_pagado'))['total'] or 0

            evolucion_ingresos.append({
                'mes': mes_fecha.strftime('%B %Y'),
                'mes_corto': mes_fecha.strftime('%b'),
                'productos': float(total_productos),
                'membresias': float(total_membresias),
                'total': float(total_productos) + float(total_membresias)
            })

        # 8. Comparativas entre Sedes
        comparativas_sedes = []
        if not sede_id:  # Solo mostrar si no hay filtro de sede
            sedes_list = Sede.objects.all()

            for sede in sedes_list:
                # Ingresos de la sede
                ingresos_sede_productos = VentaProducto.objects.filter(
                    fecha_venta__date__gte=fecha_inicio,
                    fecha_venta__date__lte=fecha_fin,
                    estado='completada',
                    sede_id=sede.id
                ).aggregate(total=Sum('total'))['total'] or 0

                ingresos_sede_membresias = SuscripcionMembresia.objects.filter(
                    fecha_suscripcion__date__gte=fecha_inicio,
                    fecha_suscripcion__date__lte=fecha_fin,
                    sede_suscripcion_id=sede.id
                ).aggregate(total=Sum('precio_pagado'))['total'] or 0

                total_ingresos_sede = float(ingresos_sede_productos) + float(ingresos_sede_membresias)

                # Clientes activos de la sede
                clientes_sede = Cliente.objects.filter(
                    sede_id=sede.id,
                    estado='activo'
                ).count()

                # Membresías activas de la sede
                membresias_sede = SuscripcionMembresia.objects.filter(
                    sede_suscripcion_id=sede.id,
                    estado='activa'
                ).count()

                # Accesos hoy en la sede
                accesos_sede = RegistroAcceso.objects.filter(
                    sede_id=sede.id,
                    fecha_hora_entrada__date=hoy
                ).count()

                comparativas_sedes.append({
                    'sede': sede.nombre,
                    'ingresos': round(total_ingresos_sede, 2),
                    'clientes': clientes_sede,
                    'membresias': membresias_sede,
                    'accesos': accesos_sede
                })

        # =====================================================
        # ALERTAS
        # =====================================================
        alertas = {
            'membresias_por_vencer': membresias_por_vencer,
            'productos_stock_bajo': inventarios_query.count(),
            'accesos_denegados_hoy': accesos_denegados
        }

        # =====================================================
        # RESPUESTA
        # =====================================================
        response_data = {
            'kpis': {
                'total_clientes_activos': total_clientes_activos,
                'tendencia_clientes': round(tendencia_clientes, 1),
                'membresias_activas': membresias_activas,
                'membresias_vencidas': membresias_vencidas,
                'membresias_por_vencer': membresias_por_vencer,
                'ingresos_mes': round(ingresos_totales, 2),
                'ingresos_membresias': round(float(ingresos_membresias), 2),
                'ingresos_productos': round(float(ingresos_mes), 2),
                'tendencia_ingresos': round(tendencia_ingresos, 1),
                'accesos_hoy': accesos_hoy,
                'accesos_autorizados': accesos_autorizados,
                'accesos_denegados': accesos_denegados
            },
            'graficas': {
                'accesos_30_dias': accesos_30_dias,
                'ingresos_por_concepto': ingresos_por_concepto,
                'distribucion_membresias': distribucion_membresias,
                'productos_mas_vendidos': productos_mas_vendidos,
                'evolucion_ingresos': evolucion_ingresos
            },
            'comparativas_sedes': comparativas_sedes,
            'alertas': alertas,
            'productos_stock_bajo': productos_stock_bajo,
            'ultimas_ventas': ultimas_ventas,
            'ultimas_suscripciones': ultimas_suscripciones,
            'periodo': {
                'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
                'fecha_fin': fecha_fin.strftime('%Y-%m-%d')
            }
        }

        return Response(response_data)
