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
    """
    Catálogo maestro de productos.
    NO almacena stock - el stock se gestiona en el modelo Inventario por sede.
    """
    producto_id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('CategoriaProducto', on_delete=models.CASCADE, related_name='productos')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción del producto")
    activo = models.BooleanField(default=True, help_text="Si el producto está disponible para venta")

    class Meta:
        db_table = 'producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}" if self.codigo else self.nombre

    def save(self, *args, **kwargs):
        if not self.codigo:
            import random
            while True:
                nuevo_codigo = random.randint(100000000000, 999999999999)
                if not Producto.objects.filter(codigo=nuevo_codigo).exists():
                    self.codigo = str(nuevo_codigo)
                    break
        super().save(*args, **kwargs)

    @property
    def stock_total(self):
        """Calcula el stock total sumando todas las sedes"""
        return self.inventarios.aggregate(
            total=models.Sum('cantidad_actual')
        )['total'] or 0

    def get_stock_por_sede(self, sede):
        """Obtiene el stock disponible en una sede específica"""
        try:
            inventario = self.inventarios.get(sede=sede)
            return inventario.cantidad_actual
        except Inventario.DoesNotExist:
            return 0


class Inventario(models.Model):
    """
    Inventario de productos por sede.
    Cada producto puede tener múltiples registros de inventario (uno por sede).
    """
    inventario_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='inventarios',
        help_text="Producto inventariado"
    )
    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='inventarios',
        help_text="Sede donde se encuentra el inventario"
    )
    cantidad_actual = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad disponible en esta sede"
    )
    cantidad_minima = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad mínima antes de reabastecimiento"
    )
    cantidad_maxima = models.PositiveIntegerField(
        default=1000,
        help_text="Capacidad máxima de almacenamiento"
    )
    ubicacion_almacen = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Ubicación física en el almacén (ej: Anaquel A3)"
    )
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inventario'
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        unique_together = [['producto', 'sede']]
        ordering = ['sede', 'producto__nombre']
        indexes = [
            models.Index(fields=['sede', 'producto']),
            models.Index(fields=['cantidad_actual']),
        ]

    def __str__(self):
        return f"{self.producto.nombre} - {self.sede.nombre} (Stock: {self.cantidad_actual})"

    @property
    def requiere_reabastecimiento(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.cantidad_actual <= self.cantidad_minima

    @property
    def porcentaje_disponibilidad(self):
        """Calcula el % de capacidad utilizada"""
        if self.cantidad_maxima == 0:
            return 0
        return (self.cantidad_actual / self.cantidad_maxima) * 100

    @property
    def estado_stock(self):
        """Retorna el estado del stock: critico, bajo, normal, alto"""
        if self.cantidad_actual == 0:
            return 'agotado'
        elif self.cantidad_actual <= self.cantidad_minima:
            return 'critico'
        elif self.cantidad_actual <= (self.cantidad_minima * 1.5):
            return 'bajo'
        elif self.cantidad_actual >= self.cantidad_maxima:
            return 'excedido'
        return 'normal'
