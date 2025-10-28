from rest_framework import serializers
from .models import Membresia


class MembresiaSerializer(serializers.ModelSerializer):
    """Serializer completo para el modelo Membresia"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Membresia
        fields = '__all__'
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']


class MembresiaListSerializer(serializers.ModelSerializer):
    """Serializer para listar membresías (vista resumida)"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Membresia
        fields = ['id', 'nombre_plan', 'tipo', 'tipo_display', 'precio', 'activo', 'duracion_dias']


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
