from rest_framework import serializers
from .models import CategoriaProducto, Producto, Inventario

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    stock_total = serializers.IntegerField(read_only=True, help_text="Stock total en todas las sedes")
    sede = serializers.IntegerField(write_only=True, required=False, help_text="ID de la sede para crear el inventario inicial")

    # Campo adicional para mostrar stock por sede (usado en el endpoint de productos disponibles)
    stock_sede = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ['producto_id', 'codigo', 'nombre', 'categoria', 'categoria_nombre',
                  'precio_unitario', 'descripcion', 'activo', 'stock_total', 'stock_sede', 'sede']

    def get_stock_sede(self, obj):
        """Retorna el stock de la sede especificada en el contexto"""
        sede_id = self.context.get('sede_id')
        if sede_id:
            return obj.get_stock_por_sede(sede_id)
        return None

    def create(self, validated_data):
        # Extraer 'sede' antes de crear el producto
        sede_id = validated_data.pop('sede', None)
        print(f"🔍 DEBUG - Sede ID recibido: {sede_id}")
        print(f"🔍 DEBUG - Validated data: {validated_data}")

        producto = super().create(validated_data)
        print(f"✅ DEBUG - Producto creado: {producto.nombre} (ID: {producto.producto_id})")

        # Crear inventario inicial si se proporcionó sede
        if sede_id:
            from instalaciones.models import Sede
            try:
                sede = Sede.objects.get(pk=sede_id)
                print(f"✅ DEBUG - Sede encontrada: {sede.nombre} (ID: {sede.pk})")

                inventario = Inventario.objects.create(
                    producto=producto,
                    sede=sede,
                    cantidad_actual=0,
                    cantidad_minima=5,
                    cantidad_maxima=1000
                )
                print(f"✅ DEBUG - Inventario creado: Producto={producto.nombre}, Sede={sede.nombre}, ID={inventario.inventario_id}")
            except Sede.DoesNotExist:
                print(f"❌ DEBUG - Sede con ID {sede_id} no existe")
            except Exception as e:
                print(f"❌ DEBUG - Error al crear inventario: {str(e)}")
        else:
            print("⚠️ DEBUG - No se proporcionó sede_id, inventario no creado")

        return producto


class InventarioSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.IntegerField(write_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    estado_stock = serializers.CharField(read_only=True)
    requiere_reabastecimiento = serializers.BooleanField(read_only=True)
    porcentaje_disponibilidad = serializers.FloatField(read_only=True)

    class Meta:
        model = Inventario
        fields = [
            'inventario_id', 'producto', 'producto_id', 'sede', 'sede_nombre',
            'cantidad_actual', 'cantidad_minima', 'cantidad_maxima',
            'ubicacion_almacen', 'estado_stock', 'requiere_reabastecimiento',
            'porcentaje_disponibilidad', 'ultima_actualizacion'
        ]
        read_only_fields = ['ultima_actualizacion']

    def update(self, instance, validated_data):
        """
        Actualiza un registro de inventario.
        El producto_id no se debe cambiar en una actualización.
        """
        # Remover producto_id si viene en los datos (no se debe cambiar)
        validated_data.pop('producto_id', None)

        # Actualizar los campos permitidos
        instance.cantidad_actual = validated_data.get('cantidad_actual', instance.cantidad_actual)
        instance.cantidad_minima = validated_data.get('cantidad_minima', instance.cantidad_minima)
        instance.cantidad_maxima = validated_data.get('cantidad_maxima', instance.cantidad_maxima)
        instance.ubicacion_almacen = validated_data.get('ubicacion_almacen', instance.ubicacion_almacen)

        # Si viene sede en validated_data, actualizarla
        if 'sede' in validated_data:
            instance.sede = validated_data['sede']

        instance.save()
        return instance
