from django.db import models
from clientes.models import Cliente          
from inventario.models import Producto


# ===============================
# 🔹 ENUMS: Estado y Método de Pago
# ===============================
class EstadoPago(models.TextChoices):
    PENDIENTE = 'pendiente', 'Pendiente'
    PAGADA = 'pagada', 'Pagada'
    ANULADA = 'anulada', 'Anulada'


class MetodoPago(models.TextChoices):
    EFECTIVO = 'efectivo', 'Efectivo'
    TARJETA = 'tarjeta', 'Tarjeta'
    TRANSFERENCIA = 'transferencia', 'Transferencia'
    OTRO = 'otro', 'Otro'


# ===============================
# 🔹 FACTURA
# ===============================
class Factura(models.Model):
    factura_id = models.AutoField(primary_key=True)

    # 🔹 Relación con la tabla de clientes
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        related_name='facturas'
    )

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
        ordering = ['-fecha_emision']

    def __str__(self):
        if self.cliente and self.cliente.persona:
            nombre = self.cliente.persona.nombre
            apellido = self.cliente.persona.apellido_paterno
            return f"Factura #{self.factura_id} - {nombre} {apellido}"
        return f"Factura #{self.factura_id} - Sin cliente"

    # ✅ Calcular total automáticamente al modificar detalles
    def actualizar_total(self):
        total = sum(detalle.subtotal() for detalle in self.detalles.all())
        self.total = total
        self.save(update_fields=['total'])


# ===============================
# 🔹 DETALLE FACTURA
# ===============================
class DetalleFactura(models.Model):
    detalle_id = models.AutoField(primary_key=True)
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True
    )
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'detalle_factura'
        verbose_name = 'Detalle de Factura'
        verbose_name_plural = 'Detalles de Factura'

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    # ✅ Subtotal del detalle
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    # ✅ Cada vez que se guarda un detalle, actualiza el total de la factura
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.factura:
            self.factura.actualizar_total()


# ===============================
# 🔹 PAGO
# ===============================
class Pago(models.Model):
    pago_id = models.AutoField(primary_key=True)
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices
    )
    fecha_pago = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'pago'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"Pago #{self.pago_id} - {self.metodo_pago}"

    # ✅ Si se realiza un pago, verificar si la factura ya está pagada
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total_pagado = sum(p.monto for p in self.factura.pagos.all())
        if total_pagado >= self.factura.total:
            self.factura.estado_pago = EstadoPago.PAGADA
        else:
            self.factura.estado_pago = EstadoPago.PENDIENTE
        self.factura.save(update_fields=['estado_pago'])
