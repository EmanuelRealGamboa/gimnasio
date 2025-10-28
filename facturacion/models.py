from django.db import models
from inventario.models import Producto 

class EstadoPago(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    PAGADA = 'pagada', 'Pagada'
    ANULADA = 'anulada', 'Anulada'


class MetodoPago(models.TextChoices):
    EFECTIVO = 'efectivo', 'Efectivo'
    TARJETA = 'tarjeta', 'Tarjeta'
    TRANSFERENCIA = 'transferencia', 'Transferencia'
    OTRO = 'otro', 'Otro'


class Factura(models.Model):
    factura_id = models.AutoField(primary_key=True)
    # Temporalmente usamos un CharField hasta que exista la app de clientes
    cliente_name = models.CharField(max_length=100,)
    fecha_emision = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado_pago = models.CharField(
        max_length=10,
        choices=EstadoPago.choices,
        default=EstadoPago.PENDIENTE
    )

    class Meta:
        db_table = 'factura'
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return f"Factura #{self.factura_id} - {self.estado_pago}"


class DetalleFactura(models.Model):
    detalle_id = models.AutoField(primary_key=True)
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_factura'
        verbose_name = 'Detalle de Factura'
        verbose_name_plural = 'Detalles de Factura'

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"


class Pago(models.Model):
    pago_id = models.AutoField(primary_key=True)
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices)
    fecha_pago = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'pago'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"Pago #{self.pago_id} - {self.metodo_pago}"
