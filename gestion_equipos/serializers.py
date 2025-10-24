from rest_framework import serializers
from .models import CategoriaActivo, ProveedorServicio, Activo, Mantenimiento, OrdenMantenimiento
from instalaciones.models import Sede, Espacio
from empleados.models import Empleado
from django.utils import timezone


# ==================== CATEGORIA ACTIVO SERIALIZERS ====================

class CategoriaActivoSerializer(serializers.ModelSerializer):
    """Serializer completo para CategoriaActivo"""
    total_activos = serializers.SerializerMethodField()

    class Meta:
        model = CategoriaActivo
        fields = ['categoria_activo_id', 'nombre', 'descripcion', 'activo', 'total_activos']
        read_only_fields = ['categoria_activo_id']

    def get_total_activos(self, obj):
        """Cuenta total de activos en esta categoría"""
        return obj.activos.count()

    def validate_nombre(self, value):
        """Validar que el nombre sea único (case-insensitive)"""
        if CategoriaActivo.objects.filter(nombre__iexact=value).exists():
            if not self.instance or self.instance.nombre.lower() != value.lower():
                raise serializers.ValidationError("Ya existe una categoría con este nombre.")
        return value


# ==================== PROVEEDOR SERVICIO SERIALIZERS ====================

class ProveedorServicioListSerializer(serializers.ModelSerializer):
    """Serializer para listar proveedores"""
    total_mantenimientos = serializers.SerializerMethodField()

    class Meta:
        model = ProveedorServicio
        fields = [
            'proveedor_id', 'nombre_empresa', 'nombre_contacto',
            'telefono', 'email', 'activo', 'total_mantenimientos'
        ]

    def get_total_mantenimientos(self, obj):
        """Cuenta total de mantenimientos realizados por este proveedor"""
        return obj.mantenimientos.count()


class ProveedorServicioSerializer(serializers.ModelSerializer):
    """Serializer completo para ProveedorServicio"""
    class Meta:
        model = ProveedorServicio
        fields = [
            'proveedor_id', 'nombre_empresa', 'nombre_contacto',
            'telefono', 'email', 'direccion', 'servicios_ofrecidos',
            'activo', 'fecha_registro'
        ]
        read_only_fields = ['proveedor_id', 'fecha_registro']

    def validate_telefono(self, value):
        """Validar formato de teléfono (10 dígitos)"""
        if value and not value.isdigit():
            raise serializers.ValidationError("El teléfono debe contener solo dígitos.")
        if value and len(value) != 10:
            raise serializers.ValidationError("El teléfono debe tener 10 dígitos.")
        return value


# ==================== ACTIVO SERIALIZERS ====================

class ActivoListSerializer(serializers.ModelSerializer):
    """Serializer para listar activos"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    en_mantenimiento = serializers.BooleanField(read_only=True)
    proximo_mantenimiento = serializers.SerializerMethodField()

    class Meta:
        model = Activo
        fields = [
            'activo_id', 'codigo', 'nombre', 'categoria_nombre',
            'sede_nombre', 'espacio_nombre', 'estado', 'estado_display',
            'fecha_compra', 'valor', 'marca', 'modelo',
            'en_mantenimiento', 'proximo_mantenimiento', 'imagen'
        ]

    def get_proximo_mantenimiento(self, obj):
        """Obtiene la fecha del próximo mantenimiento programado"""
        proximo = obj.mantenimientos.filter(
            estado='pendiente',
            fecha_programada__gte=timezone.now().date()
        ).order_by('fecha_programada').first()

        if proximo:
            return {
                'fecha': proximo.fecha_programada,
                'tipo': proximo.get_tipo_mantenimiento_display(),
                'dias_restantes': proximo.dias_para_mantenimiento
            }
        return None


class ActivoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un activo específico"""
    categoria = CategoriaActivoSerializer(read_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    espacio_nombre = serializers.CharField(source='espacio.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    creado_por_email = serializers.CharField(source='creado_por.email', read_only=True)
    historial_mantenimientos = serializers.SerializerMethodField()
    estadisticas = serializers.SerializerMethodField()

    class Meta:
        model = Activo
        fields = [
            'activo_id', 'codigo', 'nombre', 'categoria',
            'fecha_compra', 'valor', 'estado', 'estado_display',
            'ubicacion', 'sede_nombre', 'espacio_nombre',
            'descripcion', 'marca', 'modelo', 'numero_serie',
            'imagen', 'creado_por_email', 'fecha_creacion',
            'fecha_actualizacion', 'historial_mantenimientos', 'estadisticas'
        ]

    def get_historial_mantenimientos(self, obj):
        """Últimos 5 mantenimientos del activo"""
        # Evitar importación circular y optimizar consultas
        mantenimientos = obj.mantenimientos.select_related(
            'proveedor_servicio', 'empleado_responsable', 'empleado_responsable__persona'
        ).all()[:5]
        return MantenimientoListSerializer(mantenimientos, many=True).data

    def get_estadisticas(self, obj):
        """Estadísticas del activo"""
        mantenimientos = obj.mantenimientos.all()
        total = mantenimientos.count()
        completados = mantenimientos.filter(estado='completado').count()
        costo_total = sum(m.costo for m in mantenimientos.filter(estado='completado'))

        return {
            'total_mantenimientos': total,
            'mantenimientos_completados': completados,
            'costo_total_mantenimiento': float(costo_total),
            'ultimo_mantenimiento': mantenimientos.filter(estado='completado').first().fecha_ejecucion if mantenimientos.filter(estado='completado').exists() else None
        }


class ActivoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar activos"""
    class Meta:
        model = Activo
        fields = [
            'activo_id', 'codigo', 'nombre', 'categoria',
            'fecha_compra', 'valor', 'estado', 'ubicacion',
            'sede', 'espacio', 'descripcion', 'marca',
            'modelo', 'numero_serie', 'imagen'
        ]
        read_only_fields = ['activo_id']

    def validate_codigo(self, value):
        """Validar que el código sea único"""
        if Activo.objects.filter(codigo__iexact=value).exists():
            if not self.instance or self.instance.codigo.upper() != value.upper():
                raise serializers.ValidationError("Ya existe un activo con este código.")
        return value.upper()

    def validate_numero_serie(self, value):
        """Validar que el número de serie sea único si se proporciona"""
        if value:
            if Activo.objects.filter(numero_serie=value).exists():
                if not self.instance or self.instance.numero_serie != value:
                    raise serializers.ValidationError("Ya existe un activo con este número de serie.")
        return value

    def validate(self, data):
        """Validaciones cruzadas"""
        # Validar que la sede del espacio coincida con la sede del activo
        if data.get('espacio') and data.get('sede'):
            if data['espacio'].sede != data['sede']:
                raise serializers.ValidationError({
                    'espacio': 'El espacio debe pertenecer a la sede seleccionada.'
                })

        # Validar que la fecha de compra no sea futura
        if data.get('fecha_compra') and data['fecha_compra'] > timezone.now().date():
            raise serializers.ValidationError({
                'fecha_compra': 'La fecha de compra no puede ser futura.'
            })

        return data


# ==================== MANTENIMIENTO SERIALIZERS ====================

class MantenimientoListSerializer(serializers.ModelSerializer):
    """Serializer para listar mantenimientos"""
    activo_nombre = serializers.CharField(source='activo.nombre', read_only=True)
    activo_codigo = serializers.CharField(source='activo.codigo', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_mantenimiento_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    responsable = serializers.SerializerMethodField()
    dias_para_mantenimiento = serializers.IntegerField(read_only=True)
    requiere_atencion = serializers.BooleanField(read_only=True)

    class Meta:
        model = Mantenimiento
        fields = [
            'mantenimiento_id', 'activo_nombre', 'activo_codigo',
            'tipo_mantenimiento', 'tipo_display', 'fecha_programada',
            'fecha_ejecucion', 'estado', 'estado_display', 'responsable',
            'costo', 'dias_para_mantenimiento', 'requiere_atencion'
        ]

    def get_responsable(self, obj):
        """Determina quién es el responsable del mantenimiento"""
        if obj.proveedor_servicio:
            return {
                'tipo': 'externo',
                'nombre': obj.proveedor_servicio.nombre_empresa
            }
        elif obj.empleado_responsable:
            persona = obj.empleado_responsable.persona
            return {
                'tipo': 'interno',
                'nombre': f"{persona.nombre} {persona.apellido_paterno}"
            }
        return None


class MantenimientoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para un mantenimiento específico"""
    activo = ActivoListSerializer(read_only=True)
    proveedor = ProveedorServicioListSerializer(source='proveedor_servicio', read_only=True)
    empleado = serializers.SerializerMethodField()
    tipo_display = serializers.CharField(source='get_tipo_mantenimiento_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    creado_por_email = serializers.CharField(source='creado_por.email', read_only=True)
    orden = serializers.SerializerMethodField()

    class Meta:
        model = Mantenimiento
        fields = [
            'mantenimiento_id', 'activo', 'tipo_mantenimiento', 'tipo_display',
            'fecha_programada', 'fecha_ejecucion', 'proveedor', 'empleado',
            'costo', 'descripcion', 'observaciones', 'estado', 'estado_display',
            'creado_por_email', 'fecha_creacion', 'fecha_actualizacion', 'orden'
        ]

    def get_empleado(self, obj):
        """Información del empleado responsable"""
        if obj.empleado_responsable:
            persona = obj.empleado_responsable.persona
            return {
                'persona_id': persona.id,
                'nombre_completo': f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno}",
                'puesto': obj.empleado_responsable.puesto
            }
        return None

    def get_orden(self, obj):
        """Información de la orden de mantenimiento si existe"""
        try:
            orden = obj.orden
            return {
                'orden_id': orden.orden_id,
                'numero_orden': orden.numero_orden,
                'prioridad': orden.get_prioridad_display(),
                'estado_orden': orden.get_estado_orden_display()
            }
        except OrdenMantenimiento.DoesNotExist:
            return None


class MantenimientoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar mantenimientos"""
    class Meta:
        model = Mantenimiento
        fields = [
            'mantenimiento_id', 'activo', 'tipo_mantenimiento',
            'fecha_programada', 'fecha_ejecucion', 'proveedor_servicio',
            'empleado_responsable', 'costo', 'descripcion',
            'observaciones', 'estado'
        ]
        read_only_fields = ['mantenimiento_id']

    def validate(self, data):
        """Validaciones cruzadas"""
        # Validar que tenga al menos un responsable
        if not data.get('proveedor_servicio') and not data.get('empleado_responsable'):
            raise serializers.ValidationError(
                'Debe asignar un proveedor externo o un empleado responsable.'
            )

        # Validar fechas
        if data.get('fecha_ejecucion') and data.get('fecha_programada'):
            if data['fecha_ejecucion'] < data['fecha_programada']:
                raise serializers.ValidationError({
                    'fecha_ejecucion': 'La fecha de ejecución no puede ser anterior a la fecha programada.'
                })

        # Validar que no haya múltiples mantenimientos en proceso para el mismo activo
        if data.get('estado') == 'en_proceso':
            activo = data.get('activo') or (self.instance.activo if self.instance else None)
            if activo:
                query = Mantenimiento.objects.filter(
                    activo=activo,
                    estado='en_proceso'
                )
                if self.instance:
                    query = query.exclude(mantenimiento_id=self.instance.mantenimiento_id)

                if query.exists():
                    raise serializers.ValidationError({
                        'estado': 'El activo ya tiene un mantenimiento en proceso.'
                    })

        return data


# ==================== ORDEN MANTENIMIENTO SERIALIZERS ====================

class OrdenMantenimientoListSerializer(serializers.ModelSerializer):
    """Serializer para listar órdenes de mantenimiento"""
    activo_nombre = serializers.CharField(source='mantenimiento.activo.nombre', read_only=True)
    activo_codigo = serializers.CharField(source='mantenimiento.activo.codigo', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_orden_display', read_only=True)

    class Meta:
        model = OrdenMantenimiento
        fields = [
            'orden_id', 'numero_orden', 'activo_nombre', 'activo_codigo',
            'fecha_emision', 'prioridad', 'prioridad_display',
            'estado_orden', 'estado_display', 'tiempo_estimado'
        ]


class OrdenMantenimientoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para una orden de mantenimiento"""
    mantenimiento = MantenimientoDetailSerializer(read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_orden_display', read_only=True)
    creado_por_email = serializers.CharField(source='creado_por.email', read_only=True)

    class Meta:
        model = OrdenMantenimiento
        fields = [
            'orden_id', 'mantenimiento', 'numero_orden', 'fecha_emision',
            'prioridad', 'prioridad_display', 'tiempo_estimado',
            'materiales_necesarios', 'estado_orden', 'estado_display',
            'creado_por_email', 'fecha_actualizacion'
        ]


class OrdenMantenimientoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar órdenes de mantenimiento"""
    class Meta:
        model = OrdenMantenimiento
        fields = [
            'orden_id', 'mantenimiento', 'prioridad',
            'tiempo_estimado', 'materiales_necesarios', 'estado_orden'
        ]
        read_only_fields = ['orden_id', 'numero_orden']

    def validate_mantenimiento(self, value):
        """Validar que el mantenimiento no tenga ya una orden"""
        if OrdenMantenimiento.objects.filter(mantenimiento=value).exists():
            if not self.instance or self.instance.mantenimiento != value:
                raise serializers.ValidationError(
                    'Este mantenimiento ya tiene una orden asociada.'
                )
        return value
