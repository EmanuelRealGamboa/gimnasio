#!/usr/bin/env python
"""
Script de migración para convertir el inventario de single-sede a multi-sede.
Migra todo el stock actual de Producto.stock a Inventario de la sede 'central'.

IMPORTANTE: Ejecutar DESPUÉS de aplicar las migraciones con:
    python manage.py makemigrations
    python manage.py migrate

Uso:
    python migrar_inventario_multisede.py
"""

import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from inventario.models import Producto, Inventario
from instalaciones.models import Sede
from django.db import transaction


def migrar_inventario():
    """
    Migra el stock de productos a inventarios por sede.
    Asigna todo el stock actual a la sede 'central'.
    """
    print("="*70)
    print("MIGRACIÓN DE INVENTARIO A SISTEMA MULTI-SEDE")
    print("="*70)
    print()

    # 1. Verificar que existe la sede central
    try:
        sede_central = Sede.objects.get(nombre__iexact='central')
        print(f"✅ Sede central encontrada: {sede_central.nombre} (ID: {sede_central.pk})")
    except Sede.DoesNotExist:
        print("❌ ERROR: No se encontró la sede 'central'.")
        print("   Por favor, crea la sede 'central' antes de ejecutar este script.")
        print()
        print("   Puedes crearla desde el admin de Django o ejecutando:")
        print("   python manage.py shell")
        print("   >>> from instalaciones.models import Sede")
        print("   >>> Sede.objects.create(nombre='central', direccion='Dirección central', telefono='5555555555')")
        return False

    print()

    # 2. Obtener todos los productos
    productos = Producto.objects.all()
    total_productos = productos.count()

    if total_productos == 0:
        print("⚠️  No hay productos en la base de datos.")
        return True

    print(f"📦 Productos encontrados: {total_productos}")
    print()

    # 3. Verificar si ya existen inventarios
    inventarios_existentes = Inventario.objects.count()
    if inventarios_existentes > 0:
        print(f"⚠️  Ya existen {inventarios_existentes} registros de inventario.")
        respuesta = input("   ¿Deseas continuar? Esto puede crear duplicados. (s/n): ")
        if respuesta.lower() != 's':
            print("   Migración cancelada.")
            return False
        print()

    # 4. Migrar stock de cada producto
    print("🔄 Iniciando migración...")
    print("-"*70)

    productos_migrados = 0
    productos_sin_stock = 0
    productos_ya_existentes = 0
    errores = 0

    with transaction.atomic():
        for i, producto in enumerate(productos, 1):
            try:
                # Verificar si ya existe inventario para este producto en sede central
                if Inventario.objects.filter(producto=producto, sede=sede_central).exists():
                    print(f"⏭️  [{i}/{total_productos}] {producto.nombre} - Ya existe inventario en sede central")
                    productos_ya_existentes += 1
                    continue

                # Obtener stock actual (si existe el campo)
                stock_actual = 0
                if hasattr(producto, 'stock'):
                    stock_actual = producto.stock if producto.stock is not None else 0

                # Crear inventario en sede central
                inventario = Inventario.objects.create(
                    producto=producto,
                    sede=sede_central,
                    cantidad_actual=stock_actual,
                    cantidad_minima=5,
                    cantidad_maxima=1000
                )

                if stock_actual > 0:
                    print(f"✅ [{i}/{total_productos}] {producto.nombre} - {stock_actual} unidades migradas")
                    productos_migrados += 1
                else:
                    print(f"📭 [{i}/{total_productos}] {producto.nombre} - Sin stock (0 unidades)")
                    productos_sin_stock += 1

            except Exception as e:
                print(f"❌ [{i}/{total_productos}] {producto.nombre} - ERROR: {str(e)}")
                errores += 1

    print()
    print("="*70)
    print("RESUMEN DE MIGRACIÓN")
    print("="*70)
    print(f"Total de productos:           {total_productos}")
    print(f"✅ Migrados exitosamente:     {productos_migrados}")
    print(f"📭 Sin stock (0 unidades):    {productos_sin_stock}")
    print(f"⏭️  Ya existían:               {productos_ya_existentes}")
    print(f"❌ Errores:                   {errores}")
    print()

    if errores == 0:
        print("✅ ¡Migración completada exitosamente!")
        print()
        print("PRÓXIMOS PASOS:")
        print("1. Verificar inventarios en el admin: /admin/inventario/inventario/")
        print("2. Puedes eliminar el campo 'stock' de Producto si ya no lo necesitas")
        print("3. Agregar inventarios para otras sedes según sea necesario")
        return True
    else:
        print(f"⚠️  Migración completada con {errores} errores.")
        print("   Revisa los errores arriba y corrígelos manualmente.")
        return False


def verificar_migracion():
    """
    Verifica que la migración se haya realizado correctamente.
    """
    print()
    print("="*70)
    print("VERIFICACIÓN DE MIGRACIÓN")
    print("="*70)

    total_productos = Producto.objects.count()
    total_inventarios = Inventario.objects.count()

    print(f"Total productos:   {total_productos}")
    print(f"Total inventarios: {total_inventarios}")

    if total_inventarios == 0:
        print("⚠️  No hay inventarios. La migración no se realizó.")
        return

    # Productos con inventario
    productos_con_inventario = Producto.objects.filter(inventarios__isnull=False).distinct().count()
    productos_sin_inventario = total_productos - productos_con_inventario

    print(f"Productos con inventario: {productos_con_inventario}")
    print(f"Productos sin inventario: {productos_sin_inventario}")

    # Stock total
    from django.db.models import Sum
    stock_total = Inventario.objects.aggregate(total=Sum('cantidad_actual'))['total'] or 0
    print(f"Stock total en inventarios: {stock_total} unidades")

    # Inventarios por sede
    print()
    print("Inventarios por sede:")
    from django.db.models import Count
    inventarios_por_sede = Inventario.objects.values('sede__nombre').annotate(
        total_inventarios=Count('inventario_id'),
        total_stock=Sum('cantidad_actual')
    )

    for item in inventarios_por_sede:
        print(f"  - {item['sede__nombre']}: {item['total_inventarios']} productos, {item['total_stock']} unidades")

    print()


if __name__ == '__main__':
    print()
    print("⚠️  IMPORTANTE: Asegúrate de haber ejecutado las migraciones primero:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    print()

    respuesta = input("¿Deseas continuar con la migración? (s/n): ")
    if respuesta.lower() != 's':
        print("Migración cancelada.")
        sys.exit(0)

    print()

    # Ejecutar migración
    exito = migrar_inventario()

    if exito:
        # Verificar migración
        verificar_migracion()
        print()
        print("="*70)
        print("✅ PROCESO COMPLETADO")
        print("="*70)
    else:
        print()
        print("❌ Migración no completada. Revisa los errores arriba.")
        sys.exit(1)
