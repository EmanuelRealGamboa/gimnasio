from rest_framework import serializers
from .models import Membresia, SuscripcionMembresia
from clientes.models import Cliente
from clientes.serializers import ClienteSerializer


class MembresiaSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Membresia"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True, allow_null=True)
    espacios_incluidos_info = serializers.SerializerMethodField()
    espacios_count = serializers.SerializerMethodField()

    class Meta:
        model = Membresia
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

    def get_espacios_incluidos_info(self, obj):
        """Retorna información detallada de los espacios incluidos"""
        espacios = obj.espacios_incluidos.all()
        return [{'id': e.id, 'nombre': e.nombre, 'sede': e.sede.nombre} for e in espacios]

    def get_espacios_count(self, obj):
        """Retorna el número de espacios incluidos"""
        return obj.espacios_incluidos.count()


class MembresiaListSerializer(serializers.ModelSerializer):
    """Serializer para listar membresías (vista resumida)"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True, allow_null=True)
    espacios_count = serializers.SerializerMethodField()

    class Meta:
        model = Membresia
        fields = ['id', 'nombre_plan', 'tipo', 'tipo_display', 'precio', 'activo', 'duracion_dias',
                  'sede', 'sede_nombre', 'permite_todas_sedes', 'espacios_count']

    def get_espacios_count(self, obj):
        """Retorna el número de espacios incluidos"""
        return obj.espacios_incluidos.count()


class MembresiaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar membresías"""

    class Meta:
        model = Membresia
        fields = ['nombre_plan', 'tipo', 'precio', 'descripcion', 'duracion_dias', 'beneficios', 'activo',
                  'sede', 'espacios_incluidos', 'permite_todas_sedes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Importar aquí para evitar dependencia circular
        from instalaciones.models import Espacio
        # Establecer el queryset para espacios_incluidos
        self.fields['espacios_incluidos'].queryset = Espacio.objects.all()
        self.fields['espacios_incluidos'].required = False

    def validate_precio(self, value):
        """Validar que el precio sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value

    def validate_duracion_dias(self, value):
        """Validar que la duración sea positiva si se proporciona"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("La duración debe ser mayor a 0 días")
        return value

    def validate_nombre_plan(self, value):
        """Validar que el nombre del plan sea único (excepto en actualización)"""
        if self.instance:
            # En actualización, permitir el mismo nombre si es el mismo registro
            if Membresia.objects.filter(nombre_plan=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe una membresía con este nombre")
        else:
            # En creación, validar que no exista
            if Membresia.objects.filter(nombre_plan=value).exists():
                raise serializers.ValidationError("Ya existe una membresía con este nombre")
        return value

    def validate(self, data):
        """Validaciones cruzadas"""
        # Si permite_todas_sedes es False, debe tener una sede
        if not data.get('permite_todas_sedes', False) and not data.get('sede'):
            raise serializers.ValidationError({
                'sede': 'Debe seleccionar una sede o marcar como membresía multi-sede'
            })

        # Si tiene sede, validar que los espacios pertenezcan a esa sede
        if data.get('sede') and data.get('espacios_incluidos'):
            sede = data['sede']
            espacios = data['espacios_incluidos']
            for espacio in espacios:
                if espacio.sede != sede:
                    raise serializers.ValidationError({
                        'espacios_incluidos': f'El espacio "{espacio.nombre}" no pertenece a la sede seleccionada'
                    })

        return data


class SuscripcionMembresiaSerializer(serializers.ModelSerializer):
    """Serializer completo para SuscripcionMembresia con información del cliente y membresía"""
    cliente_info = ClienteSerializer(source='cliente', read_only=True)
    membresia_info = MembresiaSerializer(source='membresia', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)
    esta_activa = serializers.BooleanField(read_only=True)
    sede_nombre = serializers.CharField(source='sede_suscripcion.nombre', read_only=True, allow_null=True)
    espacios_disponibles = serializers.SerializerMethodField()

    # Campos planos para el frontend
    cliente_nombre = serializers.SerializerMethodField()
    membresia_nombre = serializers.CharField(source='membresia.nombre_plan', read_only=True)
    membresia_tipo = serializers.CharField(source='membresia.get_tipo_display', read_only=True)
    permite_todas_sedes = serializers.BooleanField(source='membresia.permite_todas_sedes', read_only=True)

    class Meta:
        model = SuscripcionMembresia
        fields = '__all__'
        read_only_fields = ['fecha_suscripcion']

    def get_espacios_disponibles(self, obj):
        """Retorna los espacios disponibles para esta suscripción"""
        espacios = obj.get_espacios_disponibles()
        return [{'id': e.id, 'nombre': e.nombre, 'sede': e.sede.nombre} for e in espacios]

    def get_cliente_nombre(self, obj):
        """Retorna el nombre completo del cliente"""
        if obj.cliente and obj.cliente.persona:
            persona = obj.cliente.persona
            return f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno or ''}".strip()
        return 'N/A'


class SuscripcionMembresiaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear suscripciones"""

    class Meta:
        model = SuscripcionMembresia
        fields = ['cliente', 'membresia', 'fecha_inicio', 'fecha_fin', 'precio_pagado', 'metodo_pago', 'notas', 'sede_suscripcion']

    def validate(self, data):
        """Validaciones cruzadas"""
        if data.get('fecha_fin') and data.get('fecha_inicio'):
            if data['fecha_fin'] < data['fecha_inicio']:
                raise serializers.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio")

        if data.get('precio_pagado', 0) < 0:
            raise serializers.ValidationError("El precio pagado no puede ser negativo")

        return data


class ClienteConMembresiaSerializer(serializers.ModelSerializer):
    """Serializer para mostrar clientes con su membresía activa"""
    suscripcion_activa = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ['persona', 'objetivo_fitness', 'nivel_experiencia', 'estado', 'fecha_registro', 'suscripcion_activa']

    def get_suscripcion_activa(self, obj):
        """Obtiene la suscripción activa del cliente"""
        suscripcion = obj.suscripciones.filter(estado='activa').order_by('-fecha_inicio').first()
        if suscripcion:
            return SuscripcionMembresiaSerializer(suscripcion).data
        return None
