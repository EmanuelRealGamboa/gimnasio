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


# =====================================================
# NUEVOS MODELOS: SISTEMA DE VENTAS CON CARRITO
# =====================================================

METODOS_PAGO_CHOICES = [
    ('efectivo', 'Efectivo'),
    ('tarjeta', 'Tarjeta'),
    ('transferencia', 'Transferencia'),
]


class VentaProducto(models.Model):
    """
    Modelo para representar una transacción de venta completa.
    Reemplaza el concepto de PasarelaPago con una estructura más clara.
    """
    venta_id = models.AutoField(primary_key=True)

    # Relaciones
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_productos',
        help_text="Cliente que realiza la compra (opcional para ventas rápidas)"
    )
    empleado = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ventas_realizadas',
        help_text="Cajero que realizó la venta"
    )
    sede = models.ForeignKey(
        'instalaciones.Sede',
        on_delete=models.CASCADE,
        related_name='ventas_productos',
        help_text="Sede donde se realizó la venta"
    )

    # Montos calculados
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Suma de todos los productos antes de descuentos"
    )
    descuento_global = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Descuento aplicado al total de la venta"
    )
    iva = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="IVA calculado (16% en México)"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total final a pagar"
    )

    # Pago
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODOS_PAGO_CHOICES,
        default='efectivo'
    )

    # Control y metadata
    fecha_venta = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de la venta"
    )
    estado = models.CharField(
        max_length=20,
        choices=[
            ('completada', 'Completada'),
            ('cancelada', 'Cancelada'),
        ],
        default='completada'
    )
    notas = models.TextField(
        blank=True,
        help_text="Notas adicionales sobre la venta"
    )

    class Meta:
        db_table = 'venta_producto'
        verbose_name = 'Venta de Producto'
        verbose_name_plural = 'Ventas de Productos'
        ordering = ['-fecha_venta']
        indexes = [
            models.Index(fields=['-fecha_venta']),
            models.Index(fields=['sede', '-fecha_venta']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        cliente_str = f"{self.cliente.persona.nombre}" if self.cliente else "Cliente Anónimo"
        return f"Venta #{self.venta_id} - {cliente_str} - ${self.total}"

    def calcular_totales(self):
        """
        Calcula subtotal, IVA y total basándose en los detalles.
        Este método debe llamarse después de crear los detalles.
        """
        self.subtotal = sum(detalle.total for detalle in self.detalles.all())

        # Aplicar descuento global
        subtotal_con_descuento = self.subtotal - self.descuento_global
        if subtotal_con_descuento < 0:
            subtotal_con_descuento = 0

        # Sin IVA
        self.iva = 0

        # Total final (igual al subtotal con descuento)
        self.total = subtotal_con_descuento

        return {
            'subtotal': self.subtotal,
            'descuento_global': self.descuento_global,
            'iva': self.iva,
            'total': self.total
        }


class DetalleVentaProducto(models.Model):
    """
    Modelo para representar cada producto vendido en una transacción.
    Cada detalle es una línea en el ticket de venta.
    """
    detalle_id = models.AutoField(primary_key=True)

    venta = models.ForeignKey(
        VentaProducto,
        on_delete=models.CASCADE,
        related_name='detalles',
        help_text="Venta a la que pertenece este detalle"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        help_text="Producto vendido (PROTECT para mantener historial)"
    )

    # Cantidades y precios
    cantidad = models.PositiveIntegerField(
        help_text="Cantidad de unidades vendidas"
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Precio unitario al momento de la venta"
    )
    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Descuento aplicado a este producto específico"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="precio_unitario * cantidad"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="subtotal - descuento"
    )

    class Meta:
        db_table = 'detalle_venta_producto'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
        indexes = [
            models.Index(fields=['venta', 'producto']),
        ]

    def __str__(self):
        return f"Detalle #{self.detalle_id} - {self.producto.nombre} x{self.cantidad}"

    def calcular_totales(self):
        """Calcula subtotal y total del detalle"""
        self.subtotal = self.precio_unitario * self.cantidad
        self.total = self.subtotal - self.descuento
        if self.total < 0:
            self.total = 0

    def save(self, *args, **kwargs):
        """Override save para calcular totales automáticamente"""
        self.calcular_totales()
        super().save(*args, **kwargs)
