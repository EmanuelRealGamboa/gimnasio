"""
Tests de la app facturacion.

Cubre:
1. Cálculo de total en Factura (actualizar_total)
2. DetalleFactura.subtotal()
3. Estado de pago: PAGADA cuando suma pagos >= total
4. Estado de pago: permanece PENDIENTE cuando faltan pagos
5. Pago parcial no cierra la factura
6. Endpoint generar_pdf: 401 sin token, 200 con Admin, 200 con Cajero
"""
import decimal
import pytest
from django.urls import reverse

from facturacion.models import Factura, DetalleFactura, Pago, EstadoPago, MetodoPago
from tests.factories import (
    ClienteFactory,
    FacturaFactory,
    DetalleFacturaFactory,
    PagoFactory,
    ProductoFactory,
    make_admin_user,
    make_cajero_user,
    SedeFactory,
)
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# =========================================================
# HELPERS
# =========================================================

def _auth_client(user):
    """Devuelve un APIClient autenticado con JWT para el usuario dado."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


# =========================================================
# 1. DetalleFactura.subtotal()
# =========================================================

class TestDetalleFacturaSubtotal:
    def test_subtotal_calcula_precio_por_cantidad(self, db):
        # Arrange
        detalle = DetalleFacturaFactory.build(
            cantidad=3,
            precio_unitario=decimal.Decimal("150.00"),
        )
        # Act
        resultado = detalle.subtotal()
        # Assert
        assert resultado == decimal.Decimal("450.00")

    def test_subtotal_cantidad_uno(self, db):
        detalle = DetalleFacturaFactory.build(
            cantidad=1,
            precio_unitario=decimal.Decimal("99.50"),
        )
        assert detalle.subtotal() == decimal.Decimal("99.50")

    def test_subtotal_con_decimales(self, db):
        detalle = DetalleFacturaFactory.build(
            cantidad=4,
            precio_unitario=decimal.Decimal("33.33"),
        )
        assert detalle.subtotal() == decimal.Decimal("133.32")


# =========================================================
# 2. Factura.actualizar_total()
# =========================================================

class TestFacturaActualizarTotal:
    def test_total_suma_todos_los_detalles(self, db):
        # Arrange — factura con dos líneas de producto distintas
        factura = FacturaFactory()
        DetalleFacturaFactory(factura=factura, cantidad=2, precio_unitario=decimal.Decimal("100.00"))
        DetalleFacturaFactory(factura=factura, cantidad=1, precio_unitario=decimal.Decimal("50.00"))
        # Act — el save() de DetalleFactura ya llama a actualizar_total
        factura.refresh_from_db()
        # Assert
        assert factura.total == decimal.Decimal("250.00")

    def test_total_sin_detalles_es_cero(self, db):
        factura = FacturaFactory()
        factura.actualizar_total()
        factura.refresh_from_db()
        assert factura.total == decimal.Decimal("0.00")

    def test_total_actualiza_al_agregar_detalle(self, db):
        # Arrange
        factura = FacturaFactory(total=decimal.Decimal("0.00"))
        # Act
        DetalleFacturaFactory(factura=factura, cantidad=5, precio_unitario=decimal.Decimal("200.00"))
        factura.refresh_from_db()
        # Assert
        assert factura.total == decimal.Decimal("1000.00")


# =========================================================
# 3 & 4. Estado de pago: PAGADA vs PENDIENTE
# =========================================================

class TestFacturaEstadoPago:
    def test_estado_pago_cambia_a_pagada_cuando_suma_pagos_iguala_total(self, db):
        # Arrange
        factura = FacturaFactory()
        DetalleFacturaFactory(factura=factura, cantidad=1, precio_unitario=decimal.Decimal("300.00"))
        factura.refresh_from_db()
        assert factura.total == decimal.Decimal("300.00")
        # Act — pago exacto
        PagoFactory(factura=factura, monto=decimal.Decimal("300.00"))
        factura.refresh_from_db()
        # Assert
        assert factura.estado_pago == EstadoPago.PAGADA

    def test_estado_pago_cambia_a_pagada_cuando_suma_pagos_supera_total(self, db):
        # Arrange
        factura = FacturaFactory()
        DetalleFacturaFactory(factura=factura, cantidad=1, precio_unitario=decimal.Decimal("200.00"))
        factura.refresh_from_db()
        # Act — pago mayor al total
        PagoFactory(factura=factura, monto=decimal.Decimal("250.00"))
        factura.refresh_from_db()
        # Assert
        assert factura.estado_pago == EstadoPago.PAGADA

    def test_estado_pago_permanece_pendiente_con_pago_parcial(self, db):
        # Arrange
        factura = FacturaFactory()
        DetalleFacturaFactory(factura=factura, cantidad=1, precio_unitario=decimal.Decimal("500.00"))
        factura.refresh_from_db()
        # Act — pago incompleto
        PagoFactory(factura=factura, monto=decimal.Decimal("100.00"))
        factura.refresh_from_db()
        # Assert
        assert factura.estado_pago == EstadoPago.PENDIENTE

    def test_estado_pago_pendiente_cuando_no_hay_pagos(self, db):
        factura = FacturaFactory()
        DetalleFacturaFactory(factura=factura, cantidad=1, precio_unitario=decimal.Decimal("100.00"))
        factura.refresh_from_db()
        assert factura.estado_pago == EstadoPago.PENDIENTE

    def test_multiples_pagos_parciales_suman_y_marcan_pagada(self, db):
        # Arrange — total 300
        factura = FacturaFactory()
        DetalleFacturaFactory(factura=factura, cantidad=3, precio_unitario=decimal.Decimal("100.00"))
        factura.refresh_from_db()
        # Act — dos abonos que en suma igualan el total
        PagoFactory(factura=factura, monto=decimal.Decimal("150.00"))
        factura.refresh_from_db()
        assert factura.estado_pago == EstadoPago.PENDIENTE  # aún parcial
        PagoFactory(factura=factura, monto=decimal.Decimal("150.00"))
        factura.refresh_from_db()
        assert factura.estado_pago == EstadoPago.PAGADA


# =========================================================
# 5. API generar_pdf — permisos HTTP
# =========================================================

class TestFacturaPdfPermisos:
    def _setup_factura(self):
        """Crea factura mínima válida en BD."""
        factura = FacturaFactory()
        DetalleFacturaFactory(factura=factura, cantidad=1, precio_unitario=decimal.Decimal("100.00"))
        return factura

    def test_generar_pdf_sin_autenticacion_devuelve_401(self, db):
        # Arrange
        factura = self._setup_factura()
        client = APIClient()  # sin credenciales
        url = reverse("factura-generar-pdf", kwargs={"pk": factura.factura_id})
        # Act
        response = client.get(url)
        # Assert
        assert response.status_code == 401

    def test_generar_pdf_con_admin_devuelve_200(self, db):
        # Arrange
        factura = self._setup_factura()
        user, _ = make_admin_user(email="adminpdf@test.com")
        client = _auth_client(user)
        url = reverse("factura-generar-pdf", kwargs={"pk": factura.factura_id})
        # Act
        response = client.get(url)
        # Assert
        assert response.status_code == 200
        assert response.get("Content-Type") == "application/pdf"

    def test_generar_pdf_con_cajero_devuelve_200(self, db):
        # Arrange
        factura = self._setup_factura()
        sede = SedeFactory()
        user, _ = make_cajero_user(sede=sede)
        client = _auth_client(user)
        url = reverse("factura-generar-pdf", kwargs={"pk": factura.factura_id})
        # Act
        response = client.get(url)
        # Assert
        assert response.status_code == 200

    def test_generar_pdf_factura_inexistente_devuelve_404(self, db):
        # Arrange
        user, _ = make_admin_user(email="adminpdf2@test.com")
        client = _auth_client(user)
        url = reverse("factura-generar-pdf", kwargs={"pk": 99999})
        # Act
        response = client.get(url)
        # Assert
        assert response.status_code == 404


# =========================================================
# 6. API facturas — listar y crear
# =========================================================

class TestFacturaAPI:
    def test_listar_facturas_requiere_autenticacion(self, db):
        url = reverse("factura-list")
        response = APIClient().get(url)
        assert response.status_code == 401

    def test_listar_facturas_como_admin_devuelve_200(self, db):
        FacturaFactory.create_batch(3)
        user, _ = make_admin_user(email="adminlist@test.com")
        client = _auth_client(user)
        url = reverse("factura-list")
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data) >= 3
