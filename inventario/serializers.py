from rest_framework import serializers
from .models import CategoriaProducto, Producto, Inventario

class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaProducto
        fields = '__all__'


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = Producto
        fields = ['producto_id', 'nombre', 'categoria', 'categoria_nombre', 'precio_unitario', 'stock']


class InventarioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)

    class Meta:
        model = Inventario
        fields = ['inventario_id', 'producto', 'producto_nombre', 'sede', 'sede_nombre', 'cantidad_actual', 'minimo']
