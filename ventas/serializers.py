from rest_framework import serializers
from .models import Venta, PasarelaPago, DetallePasarela, VentaProducto, DetalleVentaProducto
from inventario.models import Producto

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


# =====================================================
# NUEVOS SERIALIZERS: SISTEMA DE VENTAS CON CARRITO
# =====================================================

class DetalleVentaProductoSerializer(serializers.ModelSerializer):
    """Serializer para los detalles de venta (productos en el carrito)"""
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    categoria_nombre = serializers.CharField(source='producto.categoria.nombre', read_only=True)

    class Meta:
        model = DetalleVentaProducto
        fields = [
            'detalle_id', 'producto', 'producto_nombre', 'producto_codigo',
            'categoria_nombre', 'cantidad', 'precio_unitario', 'descuento',
            'subtotal', 'total'
        ]
        read_only_fields = ['detalle_id', 'subtotal', 'total']


class VentaProductoSerializer(serializers.ModelSerializer):
    """Serializer completo para lectura de ventas"""
    detalles = DetalleVentaProductoSerializer(many=True, read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    empleado_nombre = serializers.SerializerMethodField()
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    metodo_pago_display = serializers.CharField(source='get_metodo_pago_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = VentaProducto
        fields = [
            'venta_id', 'cliente', 'cliente_nombre', 'empleado', 'empleado_nombre',
            'sede', 'sede_nombre', 'subtotal', 'descuento_global', 'iva', 'total',
            'metodo_pago', 'metodo_pago_display', 'fecha_venta', 'estado',
            'estado_display', 'notas', 'detalles'
        ]
        read_only_fields = ['venta_id', 'fecha_venta', 'subtotal', 'iva', 'total']

    def get_cliente_nombre(self, obj):
        if obj.cliente and obj.cliente.persona:
            return f"{obj.cliente.persona.nombre} {obj.cliente.persona.apellido_paterno}"
        return "Cliente Anónimo"

    def get_empleado_nombre(self, obj):
        if obj.empleado:
            return obj.empleado.email
        return None


class ProductoVentaSerializer(serializers.Serializer):
    """Serializer para recibir productos en la petición de venta"""
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
    descuento = serializers.DecimalField(max_digits=10, decimal_places=2, default=0, min_value=0)


class CrearVentaProductoSerializer(serializers.Serializer):
    """
    Serializer para crear una venta con múltiples productos (carrito).
    Se usa en el endpoint POST /api/ventas-productos/crear_venta/
    """
    cliente_id = serializers.IntegerField(required=False, allow_null=True)
    sede_id = serializers.IntegerField()
    metodo_pago = serializers.ChoiceField(choices=['efectivo', 'tarjeta', 'transferencia'])
    productos = ProductoVentaSerializer(many=True)
    descuento_global = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        min_value=0
    )
    notas = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_productos(self, value):
        """Valida que haya al menos un producto"""
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto en la venta")
        return value

    def validate(self, data):
        """Validaciones cruzadas"""
        # Validar que los productos existan y tengan stock suficiente
        from instalaciones.models import Sede
        from inventario.models import Inventario

        sede_id = data.get('sede_id')
        try:
            sede = Sede.objects.get(pk=sede_id)
        except Sede.DoesNotExist:
            raise serializers.ValidationError({'sede_id': 'La sede no existe'})

        productos_data = data.get('productos', [])
        errores_stock = []

        for item in productos_data:
            producto_id = item['producto_id']
            cantidad_solicitada = item['cantidad']

            try:
                producto = Producto.objects.get(pk=producto_id)
            except Producto.DoesNotExist:
                errores_stock.append(f"El producto con ID {producto_id} no existe")
                continue

            # Validar stock disponible en el inventario de la sede específica
            try:
                inventario = Inventario.objects.get(producto=producto, sede=sede)
                stock_disponible = inventario.cantidad_actual
            except Inventario.DoesNotExist:
                errores_stock.append(
                    f"El producto '{producto.nombre}' no está disponible en la sede '{sede.nombre}'"
                )
                continue

            if stock_disponible < cantidad_solicitada:
                errores_stock.append(
                    f"Stock insuficiente para '{producto.nombre}' en '{sede.nombre}'. "
                    f"Solicitado: {cantidad_solicitada}, Disponible: {stock_disponible}"
                )

        if errores_stock:
            raise serializers.ValidationError({'productos': errores_stock})

        return data
