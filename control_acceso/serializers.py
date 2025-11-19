from rest_framework import serializers
from .models import RegistroAcceso, Credencial
from clientes.models import Cliente
from membresias.models import SuscripcionMembresia


class RegistroAccesoSerializer(serializers.ModelSerializer):
    """Serializer completo para RegistroAcceso"""
    cliente_nombre = serializers.SerializerMethodField()
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    tiempo_permanencia_minutos = serializers.SerializerMethodField()

    class Meta:
        model = RegistroAcceso
        fields = '__all__'
        read_only_fields = ['fecha_hora_entrada', 'registrado_por']

    def get_cliente_nombre(self, obj):
        """Retorna el nombre completo del cliente"""
        if obj.cliente and obj.cliente.persona:
            persona = obj.cliente.persona
            return f"{persona.nombre} {persona.apellido_paterno} {persona.apellido_materno or ''}".strip()
        return 'N/A'

    def get_tiempo_permanencia_minutos(self, obj):
        """Retorna el tiempo de permanencia en minutos"""
        return obj.tiempo_permanencia


class ValidarAccesoSerializer(serializers.Serializer):
    """Serializer para validar el acceso de un cliente"""
    search_term = serializers.CharField(
        required=True,
        help_text="Nombre, apellido, email o teléfono del cliente"
    )
    sede_id = serializers.IntegerField(
        required=True,
        help_text="ID de la sede donde se intenta el acceso"
    )


class RegistrarAccesoSerializer(serializers.Serializer):
    """Serializer para registrar un nuevo acceso"""
    cliente_id = serializers.IntegerField(required=True)
    sede_id = serializers.IntegerField(required=True)
    notas = serializers.CharField(required=False, allow_blank=True)


class ClienteAccesoInfoSerializer(serializers.Serializer):
    """Serializer para devolver información del cliente para validación de acceso"""
    cliente_id = serializers.IntegerField()
    persona_id = serializers.IntegerField()
    nombre_completo = serializers.CharField()
    email = serializers.EmailField(allow_null=True)
    telefono = serializers.CharField(allow_null=True)
    foto_url = serializers.URLField(allow_null=True)

    # Información de membresía
    tiene_membresia_activa = serializers.BooleanField()
    membresia_id = serializers.IntegerField(allow_null=True)
    membresia_nombre = serializers.CharField(allow_null=True)
    membresia_tipo = serializers.CharField(allow_null=True)
    membresia_estado = serializers.CharField(allow_null=True)
    fecha_inicio = serializers.DateField(allow_null=True)
    fecha_fin = serializers.DateField(allow_null=True)
    dias_restantes = serializers.IntegerField(allow_null=True)
    permite_todas_sedes = serializers.BooleanField(allow_null=True)
    sede_suscripcion_id = serializers.IntegerField(allow_null=True)
    sede_suscripcion_nombre = serializers.CharField(allow_null=True)

    # Validación de acceso
    puede_acceder = serializers.BooleanField()
    motivo_denegado = serializers.CharField(allow_null=True)

    # Estadísticas de acceso
    total_accesos = serializers.IntegerField()
    ultimo_acceso = serializers.DateTimeField(allow_null=True)


class CredencialSerializer(serializers.ModelSerializer):
    """Serializer para credenciales"""
    persona_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Credencial
        fields = '__all__'

    def get_persona_nombre(self, obj):
        """Retorna el nombre completo de la persona"""
        if obj.persona:
            return f"{obj.persona.nombre} {obj.persona.apellido_paterno} {obj.persona.apellido_materno or ''}".strip()
        return 'N/A'
