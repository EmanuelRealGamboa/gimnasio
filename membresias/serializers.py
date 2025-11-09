import re
from rest_framework import serializers
from .models import Membresia


class MembresiaSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Membresia"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    beneficios_list = serializers.SerializerMethodField()

    class Meta:
        model = Membresia
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']

    def get_beneficios_list(self, obj):
        return parse_beneficios(obj.beneficios)


class MembresiaListSerializer(serializers.ModelSerializer):
    """Serializer para listar membresías (vista resumida)"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    beneficios_list = serializers.SerializerMethodField()

    class Meta:
        model = Membresia
        fields = [
            'id',
            'nombre_plan',
            'tipo',
            'tipo_display',
            'precio',
            'activo',
            'duracion_dias',
            'descripcion',
            'beneficios',
            'beneficios_list',
        ]

    def get_beneficios_list(self, obj):
        return parse_beneficios(obj.beneficios)


class MembresiaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar membresías"""

    class Meta:
        model = Membresia
        fields = ['nombre_plan', 'tipo', 'precio', 'descripcion', 'duracion_dias', 'beneficios', 'activo']

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


def parse_beneficios(beneficios_raw):
    """Convierte el texto plano de beneficios en una lista legible."""
    if not beneficios_raw:
        return []

    # Normalizar saltos de línea y separadores
    normalized = beneficios_raw.replace('\r', '\n')
    parts = re.split(r'[\n;,]+', normalized)

    beneficios = []
    for part in parts:
        cleaned = part.strip("•*- \t")
        if cleaned:
            beneficios.append(cleaned)

    return beneficios
