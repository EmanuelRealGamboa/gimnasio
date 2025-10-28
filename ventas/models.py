from django.db import models
from django.core.exceptions import ValidationError
from inventario.models import Producto


# =====================================================
# MODELO: VENTA
# =====================================================
class Venta(models.Model):
    venta_id = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[('PENDIENTE', 'Pendiente'), ('FINALIZADA', 'Finalizada')],
        default='PENDIENTE'
    )

    class Meta:
        db_table = 'venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def clean(self):
        # ⚠️ Validar que haya producto
        if not self.producto_id:
            raise ValidationError("Debes seleccionar un producto antes de guardar la venta.")

        # ⚠️ Validar cantidad
        if not self.cantidad or self.cantidad <= 0:
            raise ValidationError("Debes ingresar una cantidad válida.")

        # ⚠️ Validar stock disponible
        if self.producto and self.producto.stock is not None:
            if self.cantidad > self.producto.stock:
                raise ValidationError(f"No hay suficiente stock para {self.producto.nombre}.")
            if self.producto.stock <= 0:
                raise ValidationError(f"El producto {self.producto.nombre} no tiene stock disponible.")

    def save(self, *args, **kwargs):
        # 🧮 Calcular total
        self.total = self.producto.precio_unitario * self.cantidad

        # ⚙️ Si la venta se finaliza, poner cantidad en cero
        if self.estado == 'FINALIZADA':
            # Primero asegurar que ya se descontó el stock, y luego poner cantidad en 0
            self.cantidad = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta #{self.venta_id} - {self.producto.nombre}"


# =====================================================
# MODELO: PASARELA DE PAGO
# =====================================================
METODOS_PAGO = [
    ('Efectivo', 'Efectivo'),
    ('Transferencia', 'Transferencia'),
    ('Tarjeta', 'Tarjeta'),
]


class PasarelaPago(models.Model):
    pasarela_id = models.AutoField(primary_key=True)
    metodo_pago = models.CharField(max_length=50, choices=METODOS_PAGO)
    total_general = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_pago = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pasarela_pago'
        verbose_name = 'Pasarela de Pago'
        verbose_name_plural = 'Pasarelas de Pago'

    def __str__(self):
        return f"Pasarela #{self.pasarela_id} - {self.metodo_pago}"

    def recalcular_total_general(self):
        """
        Calcula el total general sumando los totales de los detalles.
        (Evita recursión infinita, no vuelve a llamar a save()).
        """
        total = sum(detalle.total for detalle in self.detalles.all())
        self.total_general = total


# =====================================================
# MODELO: DETALLE PASARELA
# =====================================================
class DetallePasarela(models.Model):
    pasarela = models.ForeignKey(PasarelaPago, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'detalle_pasarela'
        verbose_name = 'Detalle de Pasarela'
        verbose_name_plural = 'Detalles de Pasarela'

    def clean(self):
        from ventas.models import Venta

        # ⚠️ Validar producto
        if not self.producto:
            raise ValidationError("Debe seleccionar un producto válido.")

        # ⚠️ Buscar venta pendiente
        venta = Venta.objects.filter(producto=self.producto, estado='PENDIENTE').order_by('-venta_id').first()
        if not venta:
            raise ValidationError(f"No hay venta registrada para el producto '{self.producto.nombre}'.")

        # ⚙️ Igualar cantidad con la venta
        self.cantidad = venta.cantidad

        # ⚠️ Validar stock del producto
        if self.producto.stock <= 0:
            raise ValidationError(f"El producto '{self.producto.nombre}' no tiene stock disponible.")
        if self.cantidad > self.producto.stock:
            raise ValidationError(
                f"Stock insuficiente para '{self.producto.nombre}'. "
                f"Venta: {self.cantidad}, Disponible: {self.producto.stock}"
            )

    def save(self, *args, **kwargs):
        from ventas.models import Venta

        # Validaciones previas
        self.clean()

        # Buscar venta asociada
        venta = Venta.objects.filter(producto=self.producto, estado='PENDIENTE').order_by('-venta_id').first()
        if not venta:
            raise ValidationError(f"No se encontró una venta válida para '{self.producto.nombre}'.")

        # 🧮 Calcular total según venta
        self.total = self.producto.precio_unitario * venta.cantidad

        # 🔻 Restar del stock del producto
        self.producto.stock -= venta.cantidad
        if self.producto.stock < 0:
            self.producto.stock = 0
        self.producto.save()

        # ✅ Marcar la venta como finalizada
        venta.estado = 'FINALIZADA'
        venta.save()

        # Guardar el detalle
        super().save(*args, **kwargs)

        # 🔄 Recalcular total general de la pasarela
        self.pasarela.recalcular_total_general()
        self.pasarela.save(update_fields=['total_general'])
