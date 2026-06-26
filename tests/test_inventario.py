"""
Tests de la app inventario.

Cubre:
1. Producto.stock_total — suma de inventarios en todas las sedes
2. Producto.get_stock_por_sede — stock en sede específica
3. Producto.get_stock_por_sede — devuelve 0 si no hay inventario en esa sede
4. Inventario.requiere_reabastecimiento — por debajo del mínimo
5. Inventario.porcentaje_disponibilidad
6. Inventario.estado_stock — los 5 estados posibles
7. unique_together (producto, sede) — no puede haber duplicados
8. Producto.save() genera código automáticamente si está vacío
"""
import decimal
import pytest
from django.db import IntegrityError

from inventario.models import Producto, Inventario
from tests.factories import (
    SedeFactory,
    ProductoFactory,
    InventarioFactory,
    CategoriaProductoFactory,
)


# =========================================================
# 1 & 2. stock_total y get_stock_por_sede
# =========================================================

class TestProductoStockMethods:
    def test_stock_total_suma_todas_las_sedes(self, db):
        # Arrange
        producto = ProductoFactory()
        sede_a = SedeFactory()
        sede_b = SedeFactory()
        InventarioFactory(producto=producto, sede=sede_a, cantidad_actual=30)
        InventarioFactory(producto=producto, sede=sede_b, cantidad_actual=20)
        # Act
        total = producto.stock_total
        # Assert
        assert total == 50

    def test_stock_total_sin_inventarios_es_cero(self, db):
        producto = ProductoFactory()
        assert producto.stock_total == 0

    def test_get_stock_por_sede_devuelve_cantidad_correcta(self, db):
        producto = ProductoFactory()
        sede = SedeFactory()
        InventarioFactory(producto=producto, sede=sede, cantidad_actual=15)
        assert producto.get_stock_por_sede(sede) == 15

    def test_get_stock_por_sede_devuelve_cero_si_no_hay_inventario(self, db):
        producto = ProductoFactory()
        sede_sin_inventario = SedeFactory()
        assert producto.get_stock_por_sede(sede_sin_inventario) == 0

    def test_stock_por_sede_no_mezcla_con_otra_sede(self, db):
        """Un producto con inventario en sede_a no debe mostrar stock en sede_b."""
        producto = ProductoFactory()
        sede_a = SedeFactory()
        sede_b = SedeFactory()
        InventarioFactory(producto=producto, sede=sede_a, cantidad_actual=100)
        assert producto.get_stock_por_sede(sede_b) == 0


# =========================================================
# 4. Inventario.requiere_reabastecimiento
# =========================================================

class TestInventarioRequiereReabastecimiento:
    def test_requiere_reabastecimiento_cuando_stock_igual_a_minimo(self, db):
        inv = InventarioFactory(cantidad_actual=5, cantidad_minima=5)
        assert inv.requiere_reabastecimiento is True

    def test_requiere_reabastecimiento_cuando_stock_debajo_de_minimo(self, db):
        inv = InventarioFactory(cantidad_actual=2, cantidad_minima=10)
        assert inv.requiere_reabastecimiento is True

    def test_no_requiere_reabastecimiento_cuando_stock_sobre_minimo(self, db):
        inv = InventarioFactory(cantidad_actual=20, cantidad_minima=5)
        assert inv.requiere_reabastecimiento is False


# =========================================================
# 5. Inventario.porcentaje_disponibilidad
# =========================================================

class TestInventarioPorcentajeDisponibilidad:
    def test_porcentaje_cuando_lleno(self, db):
        inv = InventarioFactory(cantidad_actual=100, cantidad_maxima=100)
        assert inv.porcentaje_disponibilidad == 100.0

    def test_porcentaje_cuando_a_la_mitad(self, db):
        inv = InventarioFactory(cantidad_actual=50, cantidad_maxima=200)
        assert inv.porcentaje_disponibilidad == 25.0

    def test_porcentaje_cuando_maximo_es_cero_devuelve_cero(self, db):
        inv = InventarioFactory(cantidad_actual=10, cantidad_maxima=0)
        assert inv.porcentaje_disponibilidad == 0


# =========================================================
# 6. Inventario.estado_stock
# =========================================================

class TestInventarioEstadoStock:
    def test_estado_agotado_cuando_cantidad_es_cero(self, db):
        inv = InventarioFactory(cantidad_actual=0, cantidad_minima=5)
        assert inv.estado_stock == "agotado"

    def test_estado_critico_cuando_cantidad_igual_a_minimo(self, db):
        inv = InventarioFactory(cantidad_actual=5, cantidad_minima=5, cantidad_maxima=100)
        assert inv.estado_stock == "critico"

    def test_estado_bajo_cuando_cantidad_entre_minimo_y_150_por_ciento_minimo(self, db):
        # minimo=10, 150% de minimo = 15; cantidad_actual=12 → "bajo"
        inv = InventarioFactory(cantidad_actual=12, cantidad_minima=10, cantidad_maxima=100)
        assert inv.estado_stock == "bajo"

    def test_estado_normal_cuando_cantidad_por_encima_del_150_minimo(self, db):
        # minimo=10, 150% = 15; cantidad_actual=50 < 100 (max) → "normal"
        inv = InventarioFactory(cantidad_actual=50, cantidad_minima=10, cantidad_maxima=100)
        assert inv.estado_stock == "normal"

    def test_estado_excedido_cuando_cantidad_igual_o_mayor_a_maximo(self, db):
        inv = InventarioFactory(cantidad_actual=100, cantidad_minima=10, cantidad_maxima=100)
        assert inv.estado_stock == "excedido"


# =========================================================
# 7. Restricción unique_together (producto, sede)
# =========================================================

class TestInventarioUniqueProductoSede:
    def test_no_se_puede_crear_inventario_duplicado_para_misma_sede(self, db):
        producto = ProductoFactory()
        sede = SedeFactory()
        InventarioFactory(producto=producto, sede=sede, cantidad_actual=10)
        with pytest.raises(IntegrityError):
            InventarioFactory(producto=producto, sede=sede, cantidad_actual=5)

    def test_mismo_producto_puede_estar_en_distintas_sedes(self, db):
        producto = ProductoFactory()
        sede_a = SedeFactory()
        sede_b = SedeFactory()
        inv_a = InventarioFactory(producto=producto, sede=sede_a, cantidad_actual=10)
        inv_b = InventarioFactory(producto=producto, sede=sede_b, cantidad_actual=20)
        assert inv_a.pk != inv_b.pk


# =========================================================
# 8. Producto.save() genera código automáticamente
# =========================================================

class TestProductoGeneraCodigo:
    def test_codigo_se_genera_automaticamente_si_esta_vacio(self, db):
        cat = CategoriaProductoFactory()
        producto = Producto.objects.create(
            nombre="Proteína Test",
            categoria=cat,
            precio_unitario=decimal.Decimal("299.00"),
            codigo="",  # vacío → debe auto-generarse
        )
        assert producto.codigo != ""
        assert len(producto.codigo) > 0

    def test_codigo_generado_es_numerico(self, db):
        cat = CategoriaProductoFactory()
        producto = Producto.objects.create(
            nombre="Proteína Numérica",
            categoria=cat,
            precio_unitario=decimal.Decimal("100.00"),
            codigo="",
        )
        assert producto.codigo.isdigit()

    def test_codigo_explicito_se_respeta(self, db):
        cat = CategoriaProductoFactory()
        producto = Producto.objects.create(
            nombre="Producto Codificado",
            categoria=cat,
            precio_unitario=decimal.Decimal("50.00"),
            codigo="PROT-001",
        )
        assert producto.codigo == "PROT-001"
