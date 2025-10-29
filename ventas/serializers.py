from rest_framework import serializers
from .models import Venta, PasarelaPago, DetallePasarela

class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'


class DetallePasarelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePasarela
        fields = '__all__'


class PasarelaPagoSerializer(serializers.ModelSerializer):
    detalles = DetallePasarelaSerializer(many=True, read_only=True)

    class Meta:
        model = PasarelaPago
        fields = '__all__'
