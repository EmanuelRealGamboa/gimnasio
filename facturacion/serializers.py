from rest_framework import serializers
from .models import Factura, DetalleFactura, Pago


# ===========================
# 🔹 FACTURA SERIALIZER
# ===========================
class FacturaSerializer(serializers.ModelSerializer):
    # ✅ Campo solo de lectura para mostrar el nombre completo del cliente
    cliente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Factura
        fields = '__all__'  # incluye 'cliente' (id) + los demás campos + cliente_nombre

    def get_cliente_nombre(self, obj):
        """Obtiene el nombre completo del cliente desde Persona."""
        if obj.cliente and obj.cliente.persona:
            return f"{obj.cliente.persona.nombre} {obj.cliente.persona.apellido_paterno}"
        return None


# ===========================
# 🔹 DETALLE FACTURA SERIALIZER
# ===========================
class DetalleFacturaSerializer(serializers.ModelSerializer):
    # ✅ Campo opcional para mostrar el nombre del producto
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleFactura
        fields = '__all__'


# ===========================
# 🔹 PAGO SERIALIZER
# ===========================
class PagoSerializer(serializers.ModelSerializer):
    # ✅ Mostrar cliente asociado al pago (vía factura)
    cliente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = '__all__'

    def get_cliente_nombre(self, obj):
        if obj.factura and obj.factura.cliente and obj.factura.cliente.persona:
            return f"{obj.factura.cliente.persona.nombre} {obj.factura.cliente.persona.apellido_paterno}"
        return None
