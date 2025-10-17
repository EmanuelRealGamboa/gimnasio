from rest_framework import serializers
from .models import Sede, Espacio


class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = ['id', 'nombre', 'direccion', 'telefono']


class EspacioSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)

    class Meta:
        model = Espacio
        fields = ['id', 'nombre', 'descripcion', 'capacidad', 'sede', 'sede_nombre', 'imagen']
