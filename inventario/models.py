from django.db import models
from instalaciones.models import Sede

class CategoriaProducto(models.Model):
    categoria_producto_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        db_table = 'categoria_producto'
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    producto_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.CASCADE)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.nombre} ({self.stock} disponibles)"


class Inventario(models.Model):
    inventario_id = models.AutoField(primary_key=True)
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)
    cantidad_actual = models.PositiveIntegerField(default=0)
    minimo = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'inventario'
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'

    def __str__(self):
        return f"{self.producto.nombre} - {self.sede.nombre}"

    def save(self, *args, **kwargs):
        # Al guardar, iguala la cantidad actual al stock del producto
        self.cantidad_actual = self.producto.stock
        super().save(*args, **kwargs)
