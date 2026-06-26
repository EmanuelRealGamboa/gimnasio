"""
Capa de servicios para el módulo de ventas.

Contiene toda la lógica de negocio de escritura:
- venta_producto_crear: crea una venta con carrito de productos
- venta_producto_cancelar: cancela una venta y restaura el stock
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from inventario.models import Inventario, Producto
from .models import DetalleVentaProducto, VentaProducto

User = get_user_model()


def venta_producto_crear(
    *,
    empleado: User,
    sede_id: int,
    metodo_pago: str,
    productos: list[dict[str, Any]],
    cliente_id: int | None = None,
    descuento_global: Decimal = Decimal("0"),
    notas: str = "",
) -> VentaProducto:
    """Crea una venta con carrito de productos, descontando stock del inventario de la sede.

    Ejecuta todo dentro de una transacción atómica con SELECT FOR UPDATE para
    evitar condiciones de carrera en el stock.

    Args:
        empleado: Usuario cajero que realiza la venta.
        sede_id: ID de la sede donde se realiza la venta.
        metodo_pago: 'efectivo', 'tarjeta' o 'transferencia'.
        productos: Lista de dicts con claves 'producto_id', 'cantidad' y 'descuento'.
        cliente_id: ID del cliente (opcional, permite ventas anónimas).
        descuento_global: Descuento aplicado al total de la venta.
        notas: Observaciones adicionales.

    Returns:
        VentaProducto creada con detalles y totales calculados.

    Raises:
        ValidationError: Si algún producto no existe, no tiene inventario en la sede
            o no tiene stock suficiente.
    """
    with transaction.atomic():
        venta = VentaProducto.objects.create(
            cliente_id=cliente_id,
            empleado=empleado,
            sede_id=sede_id,
            metodo_pago=metodo_pago,
            descuento_global=descuento_global,
            notas=notas,
            subtotal=Decimal("0"),
            iva=Decimal("0"),
            total=Decimal("0"),
        )

        for item in productos:
            try:
                producto = (
                    Producto.objects.select_for_update()
                    .get(pk=item["producto_id"])
                )
            except Producto.DoesNotExist:
                raise ValidationError(
                    f"El producto con id {item['producto_id']} no existe"
                )

            try:
                inventario = Inventario.objects.select_for_update().get(
                    producto=producto,
                    sede_id=sede_id,
                )
            except Inventario.DoesNotExist:
                raise ValidationError(
                    f"El producto '{producto.nombre}' no está disponible en esta sede"
                )

            if inventario.cantidad_actual < item["cantidad"]:
                raise ValidationError(
                    f"Stock insuficiente de '{producto.nombre}' en esta sede. "
                    f"Disponible: {inventario.cantidad_actual}, "
                    f"Solicitado: {item['cantidad']}"
                )

            DetalleVentaProducto.objects.create(
                venta=venta,
                producto=producto,
                cantidad=item["cantidad"],
                precio_unitario=producto.precio_unitario,
                descuento=item.get("descuento", Decimal("0")),
            )

            inventario.cantidad_actual -= item["cantidad"]
            inventario.save(update_fields=["cantidad_actual", "ultima_actualizacion"])

        totales = venta.calcular_totales()
        venta.subtotal = totales["subtotal"]
        venta.iva = totales["iva"]
        venta.total = totales["total"]
        venta.save(update_fields=["subtotal", "iva", "total"])

    return venta


def venta_producto_cancelar(*, venta: VentaProducto) -> VentaProducto:
    """Cancela una venta y restaura el stock de cada producto en el inventario de la sede.

    Si el registro de inventario fue eliminado entre la venta y la cancelación,
    lo recrea con la cantidad restaurada y umbrales mínimos por defecto.

    Args:
        venta: Instancia de VentaProducto en estado 'completada'.

    Returns:
        La misma instancia de VentaProducto con estado 'cancelada'.

    Raises:
        ValidationError: Si la venta ya estaba cancelada.
    """
    if venta.estado == "cancelada":
        raise ValidationError("Esta venta ya está cancelada")

    with transaction.atomic():
        for detalle in venta.detalles.select_for_update().select_related("producto"):
            try:
                inventario = Inventario.objects.select_for_update().get(
                    producto=detalle.producto,
                    sede=venta.sede,
                )
                inventario.cantidad_actual += detalle.cantidad
                inventario.save(update_fields=["cantidad_actual", "ultima_actualizacion"])
            except Inventario.DoesNotExist:
                Inventario.objects.create(
                    producto=detalle.producto,
                    sede=venta.sede,
                    cantidad_actual=detalle.cantidad,
                    cantidad_minima=5,
                    cantidad_maxima=1000,
                )

        venta.estado = "cancelada"
        venta.save(update_fields=["estado"])

    return venta
