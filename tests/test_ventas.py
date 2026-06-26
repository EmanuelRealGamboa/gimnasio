"""
Tests de la app ventas (VentaProducto / DetalleVentaProducto).

Cubre:
1. Crear venta descuenta el stock del Inventario de la sede correctamente
2. Crear venta con múltiples productos — todos descontados
3. La operación de creación es ATÓMICA: si falla un producto, el stock no cambia
4. Rechaza venta si stock insuficiente en la sede (400)
5. Rechaza venta si producto no existe en la sede (400)
6. Cancelar una venta restaura el stock
7. Cancelar una venta ya cancelada devuelve 400
8. DetalleVentaProducto.calcular_totales() calcula correctamente con descuento
9. VentaProducto.calcular_totales() suma detalles y aplica descuento global
"""
import decimal
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from ventas.models import VentaProducto, DetalleVentaProducto
from inventario.models import Inventario
from tests.factories import (
    SedeFactory,
    ProductoFactory,
    InventarioFactory,
    VentaProductoFactory,
    DetalleVentaProductoFactory,
    ClienteFactory,
    make_admin_user,
    make_cajero_user,
)


def _auth_client(user):
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


# =========================================================
# 1. DetalleVentaProducto.calcular_totales()
# =========================================================

class TestDetalleVentaProductoCalculo:
    def test_calcula_subtotal_sin_descuento(self, db):
        # Arrange
        detalle = DetalleVentaProductoFactory.build(
            cantidad=3,
            precio_unitario=decimal.Decimal("100.00"),
            descuento=decimal.Decimal("0.00"),
        )
        # Act
        detalle.calcular_totales()
        # Assert
        assert detalle.subtotal == decimal.Decimal("300.00")
        assert detalle.total == decimal.Decimal("300.00")

    def test_calcula_total_restando_descuento(self, db):
        detalle = DetalleVentaProductoFactory.build(
            cantidad=2,
            precio_unitario=decimal.Decimal("200.00"),
            descuento=decimal.Decimal("50.00"),
        )
        detalle.calcular_totales()
        assert detalle.subtotal == decimal.Decimal("400.00")
        assert detalle.total == decimal.Decimal("350.00")

    def test_total_no_puede_ser_negativo(self, db):
        """Descuento mayor al subtotal → total debe quedar en 0."""
        detalle = DetalleVentaProductoFactory.build(
            cantidad=1,
            precio_unitario=decimal.Decimal("10.00"),
            descuento=decimal.Decimal("999.00"),
        )
        detalle.calcular_totales()
        assert detalle.total == decimal.Decimal("0")


# =========================================================
# 2. VentaProducto.calcular_totales()
# =========================================================

class TestVentaProductoCalculoTotales:
    def test_calcula_total_desde_detalles(self, db):
        # Arrange — venta con dos detalles
        sede = SedeFactory()
        user, _ = make_admin_user(email="vtcalc@test.com")
        venta = VentaProductoFactory(sede=sede, empleado=user, subtotal=0, total=0)
        DetalleVentaProductoFactory(
            venta=venta,
            cantidad=2,
            precio_unitario=decimal.Decimal("100.00"),
            descuento=decimal.Decimal("0.00"),
        )
        DetalleVentaProductoFactory(
            venta=venta,
            cantidad=1,
            precio_unitario=decimal.Decimal("50.00"),
            descuento=decimal.Decimal("0.00"),
        )
        # Act
        totales = venta.calcular_totales()
        # Assert
        assert totales["subtotal"] == decimal.Decimal("250.00")
        assert totales["total"] == decimal.Decimal("250.00")

    def test_aplica_descuento_global(self, db):
        sede = SedeFactory()
        user, _ = make_admin_user(email="vtdesc@test.com")
        venta = VentaProductoFactory(
            sede=sede, empleado=user,
            subtotal=0, total=0,
            descuento_global=decimal.Decimal("50.00"),
        )
        DetalleVentaProductoFactory(
            venta=venta,
            cantidad=1,
            precio_unitario=decimal.Decimal("300.00"),
            descuento=decimal.Decimal("0.00"),
        )
        totales = venta.calcular_totales()
        assert totales["total"] == decimal.Decimal("250.00")

    def test_descuento_global_no_genera_total_negativo(self, db):
        sede = SedeFactory()
        user, _ = make_admin_user(email="vtdescneg@test.com")
        venta = VentaProductoFactory(
            sede=sede, empleado=user,
            subtotal=0, total=0,
            descuento_global=decimal.Decimal("9999.00"),
        )
        DetalleVentaProductoFactory(
            venta=venta,
            cantidad=1,
            precio_unitario=decimal.Decimal("100.00"),
            descuento=decimal.Decimal("0.00"),
        )
        totales = venta.calcular_totales()
        assert totales["total"] == decimal.Decimal("0")


# =========================================================
# 3 & 4. API crear_venta — descuento de stock
# =========================================================

class TestCrearVentaAPI:
    URL = "/api/ventas/ventas-productos/crear_venta/"

    def _payload(self, sede, producto, cantidad=2):
        return {
            "sede_id": sede.id,
            "metodo_pago": "efectivo",
            "productos": [
                {"producto_id": producto.producto_id, "cantidad": cantidad, "descuento": 0}
            ],
            "descuento_global": 0,
        }

    def test_crear_venta_descuenta_stock_inventario(self, db):
        # Arrange
        sede = SedeFactory()
        producto = ProductoFactory(precio_unitario=decimal.Decimal("100.00"))
        inventario = InventarioFactory(producto=producto, sede=sede, cantidad_actual=10)
        user, _ = make_admin_user(email="venta1@test.com")
        client = _auth_client(user)
        # Act
        response = client.post(self.URL, self._payload(sede, producto, cantidad=3), format="json")
        # Assert
        assert response.status_code == 201
        inventario.refresh_from_db()
        assert inventario.cantidad_actual == 7  # 10 - 3

    def test_crear_venta_requiere_autenticacion(self, db):
        sede = SedeFactory()
        producto = ProductoFactory()
        InventarioFactory(producto=producto, sede=sede, cantidad_actual=10)
        response = APIClient().post(self.URL, self._payload(sede, producto), format="json")
        assert response.status_code == 401

    def test_crear_venta_rechaza_si_stock_insuficiente(self, db):
        # Arrange — stock de 1, solicitamos 5
        sede = SedeFactory()
        producto = ProductoFactory()
        InventarioFactory(producto=producto, sede=sede, cantidad_actual=1)
        user, _ = make_admin_user(email="venta2@test.com")
        client = _auth_client(user)
        # Act
        response = client.post(self.URL, self._payload(sede, producto, cantidad=5), format="json")
        # Assert
        assert response.status_code == 400
        # El stock no debe haber cambiado (transacción atómica)
        inv = Inventario.objects.get(producto=producto, sede=sede)
        assert inv.cantidad_actual == 1

    def test_crear_venta_rechaza_si_producto_no_disponible_en_sede(self, db):
        # Arrange — el producto tiene inventario en otra sede
        sede_a = SedeFactory()
        sede_b = SedeFactory()
        producto = ProductoFactory()
        InventarioFactory(producto=producto, sede=sede_a, cantidad_actual=10)
        user, _ = make_admin_user(email="venta3@test.com")
        client = _auth_client(user)
        payload = {
            "sede_id": sede_b.id,  # sede donde NO hay inventario
            "metodo_pago": "efectivo",
            "productos": [{"producto_id": producto.producto_id, "cantidad": 1, "descuento": 0}],
            "descuento_global": 0,
        }
        # Act
        response = client.post(self.URL, payload, format="json")
        # Assert
        assert response.status_code == 400

    def test_crear_venta_atomica_multiples_productos_rollback(self, db):
        """
        Si el segundo producto no tiene stock, toda la transacción debe revertirse
        y el primer producto no debe perder stock.
        """
        sede = SedeFactory()
        prod1 = ProductoFactory(precio_unitario=decimal.Decimal("50.00"))
        prod2 = ProductoFactory(precio_unitario=decimal.Decimal("50.00"))
        inv1 = InventarioFactory(producto=prod1, sede=sede, cantidad_actual=10)
        InventarioFactory(producto=prod2, sede=sede, cantidad_actual=0)  # sin stock
        user, _ = make_admin_user(email="venta4@test.com")
        client = _auth_client(user)
        payload = {
            "sede_id": sede.id,
            "metodo_pago": "efectivo",
            "productos": [
                {"producto_id": prod1.producto_id, "cantidad": 2, "descuento": 0},
                {"producto_id": prod2.producto_id, "cantidad": 1, "descuento": 0},  # falla
            ],
            "descuento_global": 0,
        }
        response = client.post(self.URL, payload, format="json")
        # La transacción debe revertirse: status 400 o 500
        assert response.status_code in (400, 500)
        # El stock del primer producto NO debe haber cambiado
        inv1.refresh_from_db()
        assert inv1.cantidad_actual == 10

    def test_crear_venta_con_cajero_funciona(self, db):
        """Los cajeros también pueden crear ventas."""
        sede = SedeFactory()
        producto = ProductoFactory(precio_unitario=decimal.Decimal("100.00"))
        InventarioFactory(producto=producto, sede=sede, cantidad_actual=20)
        user, cajero = make_cajero_user(sede=sede)
        client = _auth_client(user)
        response = client.post(self.URL, self._payload(sede, producto, cantidad=1), format="json")
        assert response.status_code == 201


# =========================================================
# 5. Cancelar venta — restaurar stock
# =========================================================

class TestCancelarVentaAPI:
    def test_cancelar_venta_restaura_stock(self, db):
        # Arrange — crear venta con stock 10, comprar 3
        sede = SedeFactory()
        producto = ProductoFactory(precio_unitario=decimal.Decimal("100.00"))
        inv = InventarioFactory(producto=producto, sede=sede, cantidad_actual=7)
        user, _ = make_admin_user(email="cancel1@test.com")
        # Crear venta directamente en BD (bypass API para simplificar arranque)
        venta = VentaProductoFactory(sede=sede, empleado=user, estado="completada")
        DetalleVentaProductoFactory(venta=venta, producto=producto, cantidad=3)
        client = _auth_client(user)
        url = f"/api/ventas/ventas-productos/{venta.venta_id}/cancelar/"
        # Act
        response = client.post(url, format="json")
        # Assert
        assert response.status_code == 200
        venta.refresh_from_db()
        assert venta.estado == "cancelada"
        inv.refresh_from_db()
        assert inv.cantidad_actual == 10  # 7 + 3 devueltos

    def test_cancelar_venta_ya_cancelada_devuelve_400(self, db):
        # Arrange
        sede = SedeFactory()
        user, _ = make_admin_user(email="cancel2@test.com")
        venta = VentaProductoFactory(sede=sede, empleado=user, estado="cancelada")
        client = _auth_client(user)
        url = f"/api/ventas/ventas-productos/{venta.venta_id}/cancelar/"
        # Act
        response = client.post(url, format="json")
        # Assert
        assert response.status_code == 400
