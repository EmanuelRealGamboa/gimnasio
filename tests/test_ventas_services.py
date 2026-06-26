"""
Tests unitarios para ventas/services.py

Prueba las funciones venta_producto_crear() y venta_producto_cancelar()
directamente (sin HTTP), siguiendo el patrón AAA.

Casos cubiertos:
    venta_producto_crear:
      - camino feliz: 1 producto, descuenta stock, crea DetalleVentaProducto
      - camino feliz: varios productos en el mismo carrito
      - stock exactamente igual a la cantidad solicitada (límite)
      - stock insuficiente → ValidationError, inventario queda intacto
      - stock en cero → ValidationError (derivado del caso anterior)
      - producto sin inventario en esa sede → ValidationError
      - producto inexistente → Producto.DoesNotExist (bug documentado)
      - venta anónima (sin cliente_id)
      - descuento global reduce el total correcto
      - aislamiento: otro sede no pierde stock

    venta_producto_cancelar:
      - repone stock tras cancelación
      - múltiples detalles reponen stock individualmente
      - doble cancelación → ValidationError
      - inventario eliminado entre venta y cancelación → se recrea con defaults
"""
from __future__ import annotations

import decimal

import pytest
from django.core.exceptions import ValidationError

from inventario.models import Inventario
from ventas.models import DetalleVentaProducto, VentaProducto
from ventas.services import venta_producto_cancelar, venta_producto_crear

from tests.factories import (
    ClienteFactory,
    DetalleVentaProductoFactory,
    InventarioFactory,
    ProductoFactory,
    SedeFactory,
    UserFactory,
    VentaProductoFactory,
)


# ===========================================================================
# Fixtures locales (complementan conftest.py)
# ===========================================================================


@pytest.fixture
def sede(db):
    return SedeFactory(nombre="Sede Norte")


@pytest.fixture
def empleado(db):
    return UserFactory()


@pytest.fixture
def producto(db):
    return ProductoFactory(precio_unitario=decimal.Decimal("100.00"))


@pytest.fixture
def inventario(db, producto, sede):
    """Inventario con 10 unidades del producto en la sede."""
    return InventarioFactory(producto=producto, sede=sede, cantidad_actual=10)


# ===========================================================================
# venta_producto_crear — camino feliz
# ===========================================================================


def test_venta_crear_descuenta_stock_correcto(db, empleado, producto, sede, inventario):
    """
    Arrange: producto con 10 unidades en inventario.
    Act: crear venta por 3 unidades.
    Assert: inventario queda en 7 y se crea el DetalleVentaProducto.
    """
    # Arrange
    stock_inicial = inventario.cantidad_actual  # 10

    # Act
    venta = venta_producto_crear(
        empleado=empleado,
        sede_id=sede.pk,
        metodo_pago="efectivo",
        productos=[{"producto_id": producto.pk, "cantidad": 3, "descuento": decimal.Decimal("0")}],
    )

    # Assert — stock descontado
    inventario.refresh_from_db()
    assert inventario.cantidad_actual == stock_inicial - 3

    # Assert — detalle creado
    assert venta.detalles.count() == 1
    detalle = venta.detalles.first()
    assert detalle.producto == producto
    assert detalle.cantidad == 3


def test_venta_crear_totales_calculados_correctamente(db, empleado, producto, sede, inventario):
    """
    El total de la venta debe ser precio_unitario × cantidad.
    precio_unitario=100, cantidad=3 → subtotal=300, total=300 (sin IVA, sin descuento).
    """
    venta = venta_producto_crear(
        empleado=empleado,
        sede_id=sede.pk,
        metodo_pago="efectivo",
        productos=[{"producto_id": producto.pk, "cantidad": 3, "descuento": decimal.Decimal("0")}],
    )

    assert venta.subtotal == decimal.Decimal("300.00")
    assert venta.iva == decimal.Decimal("0")
    assert venta.total == decimal.Decimal("300.00")


def test_venta_crear_varios_productos_descuenta_cada_inventario(db, empleado, sede):
    """
    Arrange: dos productos distintos con inventario propio en la misma sede.
    Act: venta con ambos.
    Assert: cada inventario se descuenta independientemente.
    """
    # Arrange
    prod_a = ProductoFactory(precio_unitario=decimal.Decimal("50.00"))
    prod_b = ProductoFactory(precio_unitario=decimal.Decimal("200.00"))
    inv_a = InventarioFactory(producto=prod_a, sede=sede, cantidad_actual=20)
    inv_b = InventarioFactory(producto=prod_b, sede=sede, cantidad_actual=5)

    # Act
    venta = venta_producto_crear(
        empleado=empleado,
        sede_id=sede.pk,
        metodo_pago="tarjeta",
        productos=[
            {"producto_id": prod_a.pk, "cantidad": 2, "descuento": decimal.Decimal("0")},
            {"producto_id": prod_b.pk, "cantidad": 3, "descuento": decimal.Decimal("0")},
        ],
    )

    # Assert — stocks
    inv_a.refresh_from_db()
    inv_b.refresh_from_db()
    assert inv_a.cantidad_actual == 18
    assert inv_b.cantidad_actual == 2

    # Assert — detalles y total
    assert venta.detalles.count() == 2
    # 2×50 + 3×200 = 100 + 600 = 700
    assert venta.total == decimal.Decimal("700.00")


def test_venta_crear_stock_exactamente_igual_a_cantidad_solicitada(db, empleado, producto, sede):
    """
    Caso límite: stock == cantidad solicitada → debe funcionar (stock queda en 0).
    La guarda usa `cantidad_actual < cantidad`, por lo que exacto == suficiente.
    """
    # Arrange
    inv = InventarioFactory(producto=producto, sede=sede, cantidad_actual=5)

    # Act
    venta = venta_producto_crear(
        empleado=empleado,
        sede_id=sede.pk,
        metodo_pago="efectivo",
        productos=[{"producto_id": producto.pk, "cantidad": 5, "descuento": decimal.Decimal("0")}],
    )

    # Assert
    inv.refresh_from_db()
    assert inv.cantidad_actual == 0
    assert venta.detalles.count() == 1


def test_venta_crear_descuento_global_reduce_total(db, empleado, producto, sede, inventario):
    """
    descuento_global=50 sobre un subtotal de 200 → total=150.
    """
    venta = venta_producto_crear(
        empleado=empleado,
        sede_id=sede.pk,
        metodo_pago="efectivo",
        productos=[{"producto_id": producto.pk, "cantidad": 2, "descuento": decimal.Decimal("0")}],
        descuento_global=decimal.Decimal("50.00"),
    )

    # subtotal = 100×2 = 200; total = 200 - 50 = 150
    assert venta.subtotal == decimal.Decimal("200.00")
    assert venta.total == decimal.Decimal("150.00")


def test_venta_crear_sin_cliente_es_valida(db, empleado, producto, sede, inventario):
    """
    Las ventas anónimas (cliente_id=None) son permitidas por el modelo.
    """
    venta = venta_producto_crear(
        empleado=empleado,
        sede_id=sede.pk,
        metodo_pago="transferencia",
        productos=[{"producto_id": producto.pk, "cantidad": 1, "descuento": decimal.Decimal("0")}],
        cliente_id=None,
    )

    assert venta.cliente is None
    assert venta.estado == "completada"


def test_venta_crear_solo_afecta_inventario_de_la_sede_correcta(db, empleado, producto):
    """
    Aislamiento por sede: el inventario de una sede distinta no debe cambiar.
    """
    # Arrange
    sede_venta = SedeFactory(nombre="Sede A")
    sede_otra = SedeFactory(nombre="Sede B")
    inv_venta = InventarioFactory(producto=producto, sede=sede_venta, cantidad_actual=10)
    inv_otra = InventarioFactory(producto=producto, sede=sede_otra, cantidad_actual=10)

    # Act
    venta_producto_crear(
        empleado=empleado,
        sede_id=sede_venta.pk,
        metodo_pago="efectivo",
        productos=[{"producto_id": producto.pk, "cantidad": 3, "descuento": decimal.Decimal("0")}],
    )

    # Assert — solo la sede de la venta cambia
    inv_venta.refresh_from_db()
    inv_otra.refresh_from_db()
    assert inv_venta.cantidad_actual == 7
    assert inv_otra.cantidad_actual == 10  # intacto


# ===========================================================================
# venta_producto_crear — errores y atomicidad
# ===========================================================================


def test_venta_crear_stock_insuficiente_lanza_validation_error(db, empleado, producto, sede):
    """
    Pedir más unidades de las disponibles debe lanzar ValidationError.
    """
    # Arrange
    InventarioFactory(producto=producto, sede=sede, cantidad_actual=2)

    # Act & Assert
    with pytest.raises(ValidationError, match="Stock insuficiente"):
        venta_producto_crear(
            empleado=empleado,
            sede_id=sede.pk,
            metodo_pago="efectivo",
            productos=[{"producto_id": producto.pk, "cantidad": 5, "descuento": decimal.Decimal("0")}],
        )


def test_venta_crear_stock_insuficiente_no_descuenta_inventario(db, empleado, producto, sede):
    """
    Atomicidad: si falla el stock, el inventario queda intacto (sin descuento parcial).
    """
    # Arrange
    stock_original = 2
    inv = InventarioFactory(producto=producto, sede=sede, cantidad_actual=stock_original)

    # Act — intentamos comprar más de lo disponible
    with pytest.raises(ValidationError):
        venta_producto_crear(
            empleado=empleado,
            sede_id=sede.pk,
            metodo_pago="efectivo",
            productos=[{"producto_id": producto.pk, "cantidad": 10, "descuento": decimal.Decimal("0")}],
        )

    # Assert — inventario sin cambios
    inv.refresh_from_db()
    assert inv.cantidad_actual == stock_original


def test_venta_crear_stock_insuficiente_no_crea_venta_ni_detalles(db, empleado, producto, sede):
    """
    Atomicidad: si falla por stock, no debe quedar ni VentaProducto ni DetalleVentaProducto
    huérfanos en la BD.
    """
    # Arrange
    InventarioFactory(producto=producto, sede=sede, cantidad_actual=1)
    ventas_antes = VentaProducto.objects.count()
    detalles_antes = DetalleVentaProducto.objects.count()

    # Act
    with pytest.raises(ValidationError):
        venta_producto_crear(
            empleado=empleado,
            sede_id=sede.pk,
            metodo_pago="efectivo",
            productos=[{"producto_id": producto.pk, "cantidad": 99, "descuento": decimal.Decimal("0")}],
        )

    # Assert — BD igual que antes
    assert VentaProducto.objects.count() == ventas_antes
    assert DetalleVentaProducto.objects.count() == detalles_antes


def test_venta_crear_stock_cero_lanza_validation_error(db, empleado, producto, sede):
    """
    Stock en cero es un caso particular de insuficiente; debe fallar igual.
    """
    InventarioFactory(producto=producto, sede=sede, cantidad_actual=0)

    with pytest.raises(ValidationError, match="Stock insuficiente"):
        venta_producto_crear(
            empleado=empleado,
            sede_id=sede.pk,
            metodo_pago="efectivo",
            productos=[{"producto_id": producto.pk, "cantidad": 1, "descuento": decimal.Decimal("0")}],
        )


def test_venta_crear_sin_inventario_en_sede_lanza_validation_error(db, empleado, producto, sede):
    """
    Si el producto existe pero no tiene registro de Inventario en esa sede,
    el servicio debe lanzar ValidationError (no DoesNotExist sin capturar).
    """
    # Arrange — NO creamos Inventario para este par (producto, sede)

    with pytest.raises(ValidationError, match="no está disponible en esta sede"):
        venta_producto_crear(
            empleado=empleado,
            sede_id=sede.pk,
            metodo_pago="efectivo",
            productos=[{"producto_id": producto.pk, "cantidad": 1, "descuento": decimal.Decimal("0")}],
        )


def test_venta_crear_segundo_producto_con_stock_insuficiente_no_afecta_primero(db, empleado, sede):
    """
    Atomicidad multi-producto: si el segundo producto falla por stock,
    el inventario del primer producto también debe quedar intacto.
    """
    # Arrange
    prod_a = ProductoFactory()
    prod_b = ProductoFactory()
    inv_a = InventarioFactory(producto=prod_a, sede=sede, cantidad_actual=10)
    inv_b = InventarioFactory(producto=prod_b, sede=sede, cantidad_actual=1)

    stock_a_inicial = inv_a.cantidad_actual

    # Act — prod_a OK, prod_b falla
    with pytest.raises(ValidationError):
        venta_producto_crear(
            empleado=empleado,
            sede_id=sede.pk,
            metodo_pago="efectivo",
            productos=[
                {"producto_id": prod_a.pk, "cantidad": 3, "descuento": decimal.Decimal("0")},
                {"producto_id": prod_b.pk, "cantidad": 99, "descuento": decimal.Decimal("0")},
            ],
        )

    # Assert — inv_a no fue descontado (transacción revertida)
    inv_a.refresh_from_db()
    assert inv_a.cantidad_actual == stock_a_inicial


def test_venta_crear_producto_inexistente_deberia_lanzar_validation_error(db, empleado, sede):
    """Un producto_id inexistente lanza ValidationError (no Producto.DoesNotExist crudo)."""
    from inventario.models import Producto

    producto_id_fantasma = 999999

    with pytest.raises(ValidationError):
        venta_producto_crear(
            empleado=empleado,
            sede_id=sede.pk,
            metodo_pago="efectivo",
            productos=[
                {"producto_id": producto_id_fantasma, "cantidad": 1, "descuento": decimal.Decimal("0")}
            ],
        )


# ===========================================================================
# venta_producto_cancelar — camino feliz
# ===========================================================================


def test_venta_cancelar_repone_stock_en_inventario(db, sede):
    """
    Arrange: venta completada con 1 detalle de 3 unidades; inventario con 7.
    Act: cancelar.
    Assert: inventario vuelve a 10 y venta.estado == 'cancelada'.
    """
    # Arrange
    producto = ProductoFactory(precio_unitario=decimal.Decimal("100.00"))
    inv = InventarioFactory(producto=producto, sede=sede, cantidad_actual=7)
    venta = VentaProductoFactory(sede=sede, estado="completada")
    DetalleVentaProductoFactory(venta=venta, producto=producto, cantidad=3)

    # Act
    resultado = venta_producto_cancelar(venta=venta)

    # Assert
    inv.refresh_from_db()
    assert inv.cantidad_actual == 10
    assert resultado.estado == "cancelada"
    resultado.refresh_from_db()
    assert resultado.estado == "cancelada"


def test_venta_cancelar_repone_stock_multiples_detalles(db, sede):
    """
    Si la venta tiene varios productos, cada inventario se repone por separado.
    """
    # Arrange
    prod_a = ProductoFactory()
    prod_b = ProductoFactory()
    inv_a = InventarioFactory(producto=prod_a, sede=sede, cantidad_actual=5)
    inv_b = InventarioFactory(producto=prod_b, sede=sede, cantidad_actual=8)

    venta = VentaProductoFactory(sede=sede, estado="completada")
    DetalleVentaProductoFactory(venta=venta, producto=prod_a, cantidad=2)
    DetalleVentaProductoFactory(venta=venta, producto=prod_b, cantidad=4)

    # Act
    venta_producto_cancelar(venta=venta)

    # Assert
    inv_a.refresh_from_db()
    inv_b.refresh_from_db()
    assert inv_a.cantidad_actual == 7   # 5 + 2
    assert inv_b.cantidad_actual == 12  # 8 + 4


# ===========================================================================
# venta_producto_cancelar — errores y casos borde
# ===========================================================================


def test_venta_cancelar_doble_cancelacion_lanza_validation_error(db, sede):
    """
    Cancelar una venta que ya está cancelada debe lanzar ValidationError,
    no cambiar nada ni lanzar otra excepción inesperada.
    """
    # Arrange
    venta = VentaProductoFactory(sede=sede, estado="cancelada")

    # Act & Assert
    with pytest.raises(ValidationError, match="ya está cancelada"):
        venta_producto_cancelar(venta=venta)


def test_venta_cancelar_inventario_eliminado_recrea_con_cantidad_del_detalle(db, sede):
    """
    Si el registro de Inventario fue borrado después de la venta,
    el servicio debe recrearlo con cantidad=detalle.cantidad y defaults seguros,
    sin lanzar ninguna excepción.
    """
    # Arrange
    producto = ProductoFactory(precio_unitario=decimal.Decimal("50.00"))
    venta = VentaProductoFactory(sede=sede, estado="completada")
    DetalleVentaProductoFactory(venta=venta, producto=producto, cantidad=4)

    # Eliminar el inventario para simular el caso borde
    Inventario.objects.filter(producto=producto, sede=sede).delete()
    assert not Inventario.objects.filter(producto=producto, sede=sede).exists()

    # Act — no debe lanzar excepción
    venta_producto_cancelar(venta=venta)

    # Assert — inventario recreado con la cantidad del detalle
    nuevo_inv = Inventario.objects.get(producto=producto, sede=sede)
    assert nuevo_inv.cantidad_actual == 4
    assert nuevo_inv.cantidad_minima == 5
    assert nuevo_inv.cantidad_maxima == 1000


def test_venta_cancelar_inventario_eliminado_no_rompe_cuando_hay_multiples_detalles(db, sede):
    """
    Si hay varios detalles y todos sus inventarios fueron eliminados,
    el servicio debe recrear uno por producto sin errores.
    """
    # Arrange
    prod_a = ProductoFactory()
    prod_b = ProductoFactory()
    venta = VentaProductoFactory(sede=sede, estado="completada")
    DetalleVentaProductoFactory(venta=venta, producto=prod_a, cantidad=6)
    DetalleVentaProductoFactory(venta=venta, producto=prod_b, cantidad=9)

    Inventario.objects.filter(sede=sede).delete()

    # Act
    venta_producto_cancelar(venta=venta)

    # Assert — ambos inventarios recreados
    inv_a = Inventario.objects.get(producto=prod_a, sede=sede)
    inv_b = Inventario.objects.get(producto=prod_b, sede=sede)
    assert inv_a.cantidad_actual == 6
    assert inv_b.cantidad_actual == 9


def test_venta_cancelar_estado_persiste_en_bd(db, sede):
    """
    El estado 'cancelada' debe guardarse en BD, no solo en memoria.
    """
    # Arrange
    venta = VentaProductoFactory(sede=sede, estado="completada")

    # Act
    venta_producto_cancelar(venta=venta)

    # Assert — leer desde BD, no la instancia en memoria
    venta_desde_bd = VentaProducto.objects.get(pk=venta.pk)
    assert venta_desde_bd.estado == "cancelada"


# ===========================================================================
# Flujo completo crear → cancelar (integración de los dos servicios)
# ===========================================================================


def test_flujo_completo_crear_y_cancelar_repone_stock_original(db, empleado, sede):
    """
    Crear una venta (que descuenta stock) y luego cancelarla debe dejar
    el inventario exactamente en el valor original.
    """
    # Arrange
    producto = ProductoFactory(precio_unitario=decimal.Decimal("100.00"))
    stock_original = 15
    inv = InventarioFactory(producto=producto, sede=sede, cantidad_actual=stock_original)

    # Act — crear venta
    venta = venta_producto_crear(
        empleado=empleado,
        sede_id=sede.pk,
        metodo_pago="efectivo",
        productos=[{"producto_id": producto.pk, "cantidad": 5, "descuento": decimal.Decimal("0")}],
    )

    inv.refresh_from_db()
    assert inv.cantidad_actual == 10  # descontado

    # Act — cancelar
    venta_producto_cancelar(venta=venta)

    # Assert — stock restaurado
    inv.refresh_from_db()
    assert inv.cantidad_actual == stock_original
