import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from gestion_equipos.models import CategoriaActivo, ProveedorServicio, Activo, Mantenimiento, OrdenMantenimiento
from instalaciones.models import Sede, Espacio
from empleados.models import Empleado
from authentication.models import User

def crear_categorias():
    """Crea categorías de activos"""
    print("\n" + "="*60)
    print("CREANDO CATEGORÍAS DE ACTIVOS")
    print("="*60 + "\n")

    categorias_data = [
        {
            'nombre': 'Máquinas Cardiovasculares',
            'descripcion': 'Equipos para ejercicio cardiovascular (caminadoras, elípticas, bicicletas)'
        },
        {
            'nombre': 'Máquinas de Fuerza',
            'descripcion': 'Equipos de musculación y fuerza (prensas, poleas, multiestaciones)'
        },
        {
            'nombre': 'Pesas Libres',
            'descripcion': 'Mancuernas, barras, discos y racks'
        },
        {
            'nombre': 'Mobiliario',
            'descripcion': 'Muebles, escritorios, sillas, mostradores'
        },
        {
            'nombre': 'Sistemas Electrónicos',
            'descripcion': 'Equipos electrónicos, sistemas de sonido, pantallas'
        },
        {
            'nombre': 'Equipamiento Funcional',
            'descripcion': 'TRX, kettlebells, balones medicinales, bandas de resistencia'
        },
    ]

    categorias_creadas = 0
    categorias_existentes = 0

    for cat_data in categorias_data:
        categoria, created = CategoriaActivo.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults={'descripcion': cat_data['descripcion'], 'activo': True}
        )
        if created:
            categorias_creadas += 1
            print(f"✓ Categoría creada: {categoria.nombre}")
        else:
            categorias_existentes += 1
            print(f"○ Categoría ya existe: {categoria.nombre}")

    return categorias_creadas, categorias_existentes


def crear_proveedores():
    """Crea proveedores de servicio"""
    print("\n" + "="*60)
    print("CREANDO PROVEEDORES DE SERVICIO")
    print("="*60 + "\n")

    proveedores_data = [
        {
            'nombre_empresa': 'TechnoGym Service México',
            'nombre_contacto': 'Carlos Rodríguez',
            'telefono': '5551234567',
            'email': 'servicio@technogym.mx',
            'direccion': 'Av. Insurgentes Sur 1234, CDMX',
            'servicios_ofrecidos': 'Mantenimiento preventivo y correctivo de equipos cardiovasculares y de fuerza TechnoGym'
        },
        {
            'nombre_empresa': 'Life Fitness Mantenimiento',
            'nombre_contacto': 'Ana García',
            'telefono': '5559876543',
            'email': 'ana.garcia@lifefitness.com.mx',
            'direccion': 'Blvd. Manuel Ávila Camacho 36, Naucalpan',
            'servicios_ofrecidos': 'Servicio técnico especializado para equipos Life Fitness'
        },
        {
            'nombre_empresa': 'Electrónica y Sonido Pro',
            'nombre_contacto': 'Miguel Hernández',
            'telefono': '5554445566',
            'email': 'contacto@electronicapro.mx',
            'direccion': 'Calle 5 de Mayo 789, CDMX',
            'servicios_ofrecidos': 'Instalación y mantenimiento de sistemas de audio, video y control de acceso'
        },
        {
            'nombre_empresa': 'Mantenimiento Integral del Valle',
            'nombre_contacto': 'Laura Martínez',
            'telefono': '5552223344',
            'email': 'lmartinez@mivsa.com.mx',
            'direccion': 'Av. Universidad 456, Coyoacán',
            'servicios_ofrecidos': 'Mantenimiento de mobiliario, pintura, plomería y electricidad'
        },
        {
            'nombre_empresa': 'Servicios Técnicos Deportivos',
            'nombre_contacto': 'Roberto Sánchez',
            'telefono': '5558889999',
            'email': 'rsanchez@stdmexico.com',
            'direccion': 'Calz. de Tlalpan 2000, CDMX',
            'servicios_ofrecidos': 'Reparación y calibración de equipos deportivos y de gimnasio'
        },
    ]

    proveedores_creados = 0
    proveedores_existentes = 0

    for prov_data in proveedores_data:
        proveedor, created = ProveedorServicio.objects.get_or_create(
            nombre_empresa=prov_data['nombre_empresa'],
            defaults=prov_data
        )
        if created:
            proveedores_creados += 1
            print(f"✓ Proveedor creado: {proveedor.nombre_empresa}")
            print(f"  Contacto: {proveedor.nombre_contacto} | Tel: {proveedor.telefono}")
        else:
            proveedores_existentes += 1
            print(f"○ Proveedor ya existe: {proveedor.nombre_empresa}")

    return proveedores_creados, proveedores_existentes


def crear_activos():
    """Crea activos de ejemplo"""
    print("\n" + "="*60)
    print("CREANDO ACTIVOS")
    print("="*60 + "\n")

    # Obtener datos necesarios
    try:
        sede = Sede.objects.first()
        if not sede:
            print("⚠ No hay sedes disponibles. Crea una sede primero.")
            return 0, 0

        espacio = Espacio.objects.filter(sede=sede).first()
        usuario = User.objects.filter(is_superuser=True).first()

        cat_cardio = CategoriaActivo.objects.get(nombre='Máquinas Cardiovasculares')
        cat_fuerza = CategoriaActivo.objects.get(nombre='Máquinas de Fuerza')
        cat_mobiliario = CategoriaActivo.objects.get(nombre='Mobiliario')
        cat_electronica = CategoriaActivo.objects.get(nombre='Sistemas Electrónicos')

    except Exception as e:
        print(f"⚠ Error al obtener datos necesarios: {e}")
        return 0, 0

    activos_data = [
        # Máquinas cardiovasculares
        {
            'codigo': 'CARDIO-001',
            'nombre': 'Caminadora TechnoGym Run 700',
            'categoria': cat_cardio,
            'fecha_compra': date(2023, 1, 15),
            'valor': Decimal('89999.00'),
            'estado': 'activo',
            'ubicacion': 'Área cardiovascular - Fila 1',
            'marca': 'TechnoGym',
            'modelo': 'Run 700',
            'numero_serie': 'TG-RUN700-2023-001',
            'descripcion': 'Caminadora profesional con pantalla táctil y programas predefinidos'
        },
        {
            'codigo': 'CARDIO-002',
            'nombre': 'Elíptica Life Fitness E5',
            'categoria': cat_cardio,
            'fecha_compra': date(2023, 2, 20),
            'valor': Decimal('67500.00'),
            'estado': 'activo',
            'ubicacion': 'Área cardiovascular - Fila 2',
            'marca': 'Life Fitness',
            'modelo': 'E5 Track Connect',
            'numero_serie': 'LF-E5-2023-002',
            'descripcion': 'Elíptica con monitor Track Connect y 20 niveles de resistencia'
        },
        {
            'codigo': 'CARDIO-003',
            'nombre': 'Bicicleta Estacionaria Spinning',
            'categoria': cat_cardio,
            'fecha_compra': date(2023, 3, 10),
            'valor': Decimal('25000.00'),
            'estado': 'mantenimiento',
            'ubicacion': 'Salón de Spinning',
            'marca': 'Schwinn',
            'modelo': 'IC8',
            'numero_serie': 'SCH-IC8-2023-003',
            'descripcion': 'Bicicleta de spinning con resistencia magnética y monitor'
        },
        # Máquinas de fuerza
        {
            'codigo': 'FUERZA-001',
            'nombre': 'Multiestación Smith Machine',
            'categoria': cat_fuerza,
            'fecha_compra': date(2022, 11, 5),
            'valor': Decimal('125000.00'),
            'estado': 'activo',
            'ubicacion': 'Área de pesas - Zona central',
            'marca': 'Cybex',
            'modelo': 'Smith Machine Pro',
            'numero_serie': 'CYB-SM-2022-001',
            'descripcion': 'Máquina Smith con barra guiada y sistema de seguridad'
        },
        {
            'codigo': 'FUERZA-002',
            'nombre': 'Prensa de Piernas 45°',
            'categoria': cat_fuerza,
            'fecha_compra': date(2023, 1, 20),
            'valor': Decimal('98000.00'),
            'estado': 'activo',
            'ubicacion': 'Área de piernas',
            'marca': 'Hammer Strength',
            'modelo': 'Plate Loaded Leg Press',
            'numero_serie': 'HS-LP45-2023-002',
            'descripcion': 'Prensa de piernas a 45 grados con capacidad para 400kg'
        },
        {
            'codigo': 'FUERZA-003',
            'nombre': 'Polea Doble Crossover',
            'categoria': cat_fuerza,
            'fecha_compra': date(2023, 4, 15),
            'valor': Decimal('85000.00'),
            'estado': 'activo',
            'ubicacion': 'Área funcional',
            'marca': 'Matrix',
            'modelo': 'G3 FW12',
            'numero_serie': 'MTX-FW12-2023-003',
            'descripcion': 'Polea doble ajustable con múltiples accesorios'
        },
        # Mobiliario
        {
            'codigo': 'MOB-001',
            'nombre': 'Mostrador de Recepción',
            'categoria': cat_mobiliario,
            'fecha_compra': date(2022, 8, 1),
            'valor': Decimal('35000.00'),
            'estado': 'activo',
            'ubicacion': 'Recepción principal',
            'marca': 'Oficina Plus',
            'modelo': 'Recepción Moderna',
            'numero_serie': 'OP-REC-2022-001',
            'descripcion': 'Mostrador de recepción de madera con cubierta de granito'
        },
        {
            'codigo': 'MOB-002',
            'nombre': 'Lockers Metálicos (Set 20 unidades)',
            'categoria': cat_mobiliario,
            'fecha_compra': date(2022, 9, 10),
            'valor': Decimal('28000.00'),
            'estado': 'activo',
            'ubicacion': 'Vestidores',
            'marca': 'MetalPro',
            'modelo': 'Locker Estándar',
            'numero_serie': 'MP-LOCK-2022-002',
            'descripcion': 'Set de 20 lockers metálicos con cerradura de llave'
        },
        # Sistemas electrónicos
        {
            'codigo': 'ELEC-001',
            'nombre': 'Sistema de Sonido Profesional',
            'categoria': cat_electronica,
            'fecha_compra': date(2023, 5, 20),
            'valor': Decimal('45000.00'),
            'estado': 'activo',
            'ubicacion': 'Salón de clases grupales',
            'marca': 'Bose',
            'modelo': 'FreeSpace IZA',
            'numero_serie': 'BSE-IZA-2023-001',
            'descripcion': 'Sistema de audio completo con amplificador y 6 bocinas'
        },
        {
            'codigo': 'ELEC-002',
            'nombre': 'Smart TV 55 pulgadas',
            'categoria': cat_electronica,
            'fecha_compra': date(2023, 6, 1),
            'valor': Decimal('18000.00'),
            'estado': 'activo',
            'ubicacion': 'Área de descanso',
            'marca': 'Samsung',
            'modelo': 'QLED 55Q80B',
            'numero_serie': 'SAM-Q80-2023-002',
            'descripcion': 'Smart TV QLED 4K para área de descanso de clientes'
        },
    ]

    activos_creados = 0
    activos_existentes = 0

    for act_data in activos_data:
        act_data['sede'] = sede
        act_data['espacio'] = espacio
        act_data['creado_por'] = usuario

        activo, created = Activo.objects.get_or_create(
            codigo=act_data['codigo'],
            defaults=act_data
        )
        if created:
            activos_creados += 1
            print(f"✓ Activo creado: {activo.codigo} - {activo.nombre}")
            print(f"  Categoría: {activo.categoria.nombre} | Valor: ${activo.valor:,.2f}")
        else:
            activos_existentes += 1
            print(f"○ Activo ya existe: {activo.codigo}")

    return activos_creados, activos_existentes


def crear_mantenimientos():
    """Crea mantenimientos de ejemplo"""
    print("\n" + "="*60)
    print("CREANDO MANTENIMIENTOS")
    print("="*60 + "\n")

    try:
        # Obtener datos necesarios
        usuario = User.objects.filter(is_superuser=True).first()
        empleado = Empleado.objects.first()
        proveedor_techno = ProveedorServicio.objects.filter(nombre_empresa__icontains='TechnoGym').first()
        proveedor_life = ProveedorServicio.objects.filter(nombre_empresa__icontains='Life Fitness').first()
        proveedor_electronica = ProveedorServicio.objects.filter(nombre_empresa__icontains='Electrónica').first()

        activo_caminadora = Activo.objects.filter(codigo='CARDIO-001').first()
        activo_eliptica = Activo.objects.filter(codigo='CARDIO-002').first()
        activo_bicicleta = Activo.objects.filter(codigo='CARDIO-003').first()
        activo_smith = Activo.objects.filter(codigo='FUERZA-001').first()
        activo_prensa = Activo.objects.filter(codigo='FUERZA-002').first()
        activo_sonido = Activo.objects.filter(codigo='ELEC-001').first()

    except Exception as e:
        print(f"⚠ Error al obtener datos: {e}")
        return 0, 0

    hoy = date.today()

    mantenimientos_data = [
        # Mantenimientos completados (históricos)
        {
            'activo': activo_caminadora,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': hoy - timedelta(days=90),
            'fecha_ejecucion': hoy - timedelta(days=88),
            'proveedor_servicio': proveedor_techno,
            'costo': Decimal('2500.00'),
            'descripcion': 'Revisión trimestral: lubricación de banda, ajuste de tensión, limpieza general',
            'observaciones': 'Equipo en excelente estado. Se reemplazó banda de rodamiento por desgaste normal.',
            'estado': 'completado'
        },
        {
            'activo': activo_eliptica,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': hoy - timedelta(days=60),
            'fecha_ejecucion': hoy - timedelta(days=60),
            'proveedor_servicio': proveedor_life,
            'costo': Decimal('1800.00'),
            'descripcion': 'Mantenimiento preventivo bimestral: revisión de rodamientos, ajuste de resistencia',
            'observaciones': 'Todo funcionando correctamente. Se realizó actualización de firmware.',
            'estado': 'completado'
        },
        {
            'activo': activo_smith,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': hoy - timedelta(days=45),
            'fecha_ejecucion': hoy - timedelta(days=43),
            'empleado_responsable': empleado,
            'costo': Decimal('800.00'),
            'descripcion': 'Lubricación de guías y revisión de sistema de seguridad',
            'observaciones': 'Mantenimiento realizado por personal interno. Equipo funcionando correctamente.',
            'estado': 'completado'
        },
        # Mantenimiento en proceso
        {
            'activo': activo_bicicleta,
            'tipo_mantenimiento': 'correctivo',
            'fecha_programada': hoy - timedelta(days=5),
            'proveedor_servicio': ProveedorServicio.objects.filter(nombre_empresa__icontains='Técnicos').first(),
            'costo': Decimal('3500.00'),
            'descripcion': 'Reparación de sistema de resistencia magnética - No ajusta niveles correctamente',
            'observaciones': 'Se identificó problema en controlador electrónico. Pieza en pedido.',
            'estado': 'en_proceso'
        },
        # Mantenimientos pendientes
        {
            'activo': activo_caminadora,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': hoy + timedelta(days=5),
            'proveedor_servicio': proveedor_techno,
            'costo': Decimal('2500.00'),
            'descripcion': 'Mantenimiento preventivo trimestral programado',
            'estado': 'pendiente'
        },
        {
            'activo': activo_prensa,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': hoy + timedelta(days=10),
            'empleado_responsable': empleado,
            'costo': Decimal('500.00'),
            'descripcion': 'Revisión de sistema hidráulico y lubricación de rieles',
            'estado': 'pendiente'
        },
        {
            'activo': activo_eliptica,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': hoy + timedelta(days=30),
            'proveedor_servicio': proveedor_life,
            'costo': Decimal('1800.00'),
            'descripcion': 'Mantenimiento preventivo bimestral',
            'estado': 'pendiente'
        },
        {
            'activo': activo_sonido,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': hoy + timedelta(days=60),
            'proveedor_servicio': proveedor_electronica,
            'costo': Decimal('1200.00'),
            'descripcion': 'Revisión de cableado, conectores y calibración de audio',
            'estado': 'pendiente'
        },
        # Mantenimiento vencido (alerta)
        {
            'activo': activo_smith,
            'tipo_mantenimiento': 'preventivo',
            'fecha_programada': hoy - timedelta(days=3),
            'empleado_responsable': empleado,
            'costo': Decimal('600.00'),
            'descripcion': 'Mantenimiento mensual de lubricación (VENCIDO - Requiere atención)',
            'estado': 'pendiente'
        },
    ]

    mantenimientos_creados = 0
    mantenimientos_existentes = 0

    for mant_data in mantenimientos_data:
        mant_data['creado_por'] = usuario

        # Verificar si ya existe un mantenimiento similar
        exists = Mantenimiento.objects.filter(
            activo=mant_data['activo'],
            fecha_programada=mant_data['fecha_programada'],
            tipo_mantenimiento=mant_data['tipo_mantenimiento']
        ).exists()

        if not exists:
            mantenimiento = Mantenimiento.objects.create(**mant_data)
            mantenimientos_creados += 1
            estado_icon = "⚠" if mantenimiento.estado == 'en_proceso' else ("✓" if mantenimiento.estado == 'completado' else "○")
            alerta = " [VENCIDO]" if mantenimiento.dias_para_mantenimiento and mantenimiento.dias_para_mantenimiento < 0 else ""
            print(f"{estado_icon} Mantenimiento creado: {mantenimiento.activo.codigo} - {mantenimiento.get_tipo_mantenimiento_display()}{alerta}")
            print(f"  Fecha: {mantenimiento.fecha_programada} | Estado: {mantenimiento.get_estado_display()} | Costo: ${mantenimiento.costo:,.2f}")
        else:
            mantenimientos_existentes += 1

    return mantenimientos_creados, mantenimientos_existentes


def crear_ordenes():
    """Crea órdenes de mantenimiento"""
    print("\n" + "="*60)
    print("CREANDO ÓRDENES DE MANTENIMIENTO")
    print("="*60 + "\n")

    try:
        usuario = User.objects.filter(is_superuser=True).first()

        # Obtener mantenimientos sin orden
        mantenimientos_pendientes = Mantenimiento.objects.filter(
            estado__in=['pendiente', 'en_proceso']
        ).exclude(orden__isnull=False)[:5]

    except Exception as e:
        print(f"⚠ Error: {e}")
        return 0, 0

    ordenes_creadas = 0

    for mantenimiento in mantenimientos_pendientes:
        # Determinar prioridad basada en días para mantenimiento
        dias = mantenimiento.dias_para_mantenimiento
        if dias is None:
            prioridad = 'media'
        elif dias < 0:
            prioridad = 'urgente'
        elif dias <= 7:
            prioridad = 'alta'
        elif dias <= 15:
            prioridad = 'media'
        else:
            prioridad = 'baja'

        # Determinar estado de orden
        estado_orden = 'en_ejecucion' if mantenimiento.estado == 'en_proceso' else 'aprobada'

        orden_data = {
            'mantenimiento': mantenimiento,
            'prioridad': prioridad,
            'tiempo_estimado': Decimal('2.5'),
            'materiales_necesarios': 'Lubricantes, herramientas básicas, kit de limpieza',
            'estado_orden': estado_orden,
            'creado_por': usuario
        }

        orden = OrdenMantenimiento.objects.create(**orden_data)
        ordenes_creadas += 1
        print(f"✓ Orden creada: {orden.numero_orden}")
        print(f"  Activo: {orden.mantenimiento.activo.codigo} | Prioridad: {orden.get_prioridad_display()}")

    return ordenes_creadas, 0


def main():
    print("\n" + "="*60)
    print("SCRIPT DE CREACIÓN DE DATOS DE PRUEBA")
    print("Módulo: Gestión de Equipos y Mantenimiento")
    print("="*60)

    # Crear datos
    cat_creadas, cat_existentes = crear_categorias()
    prov_creados, prov_existentes = crear_proveedores()
    act_creados, act_existentes = crear_activos()
    mant_creados, mant_existentes = crear_mantenimientos()
    ord_creadas, ord_existentes = crear_ordenes()

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE CREACIÓN")
    print("="*60)
    print(f"\nCategorías de Activos:")
    print(f"  ✓ Creadas: {cat_creadas}")
    print(f"  ○ Ya existían: {cat_existentes}")

    print(f"\nProveedores de Servicio:")
    print(f"  ✓ Creados: {prov_creados}")
    print(f"  ○ Ya existían: {prov_existentes}")

    print(f"\nActivos:")
    print(f"  ✓ Creados: {act_creados}")
    print(f"  ○ Ya existían: {act_existentes}")

    print(f"\nMantenimientos:")
    print(f"  ✓ Creados: {mant_creados}")
    print(f"  ○ Ya existían: {mant_existentes}")

    print(f"\nÓrdenes de Mantenimiento:")
    print(f"  ✓ Creadas: {ord_creadas}")
    print(f"  ○ Ya existían: {ord_existentes}")

    # Estadísticas finales
    print("\n" + "="*60)
    print("ESTADÍSTICAS DE LA BASE DE DATOS")
    print("="*60)

    total_activos = Activo.objects.count()
    activos_activos = Activo.objects.filter(estado='activo').count()
    activos_mantenimiento = Activo.objects.filter(estado='mantenimiento').count()

    print(f"\nActivos totales: {total_activos}")
    print(f"  Activos: {activos_activos}")
    print(f"  En mantenimiento: {activos_mantenimiento}")

    total_mant = Mantenimiento.objects.count()
    mant_pendientes = Mantenimiento.objects.filter(estado='pendiente').count()
    mant_proceso = Mantenimiento.objects.filter(estado='en_proceso').count()
    mant_completados = Mantenimiento.objects.filter(estado='completado').count()

    print(f"\nMantenimientos totales: {total_mant}")
    print(f"  Pendientes: {mant_pendientes}")
    print(f"  En proceso: {mant_proceso}")
    print(f"  Completados: {mant_completados}")

    # Alertas
    hoy = date.today()
    from datetime import timedelta
    fecha_limite = hoy + timedelta(days=15)
    alertas = Mantenimiento.objects.filter(
        estado='pendiente',
        fecha_programada__lte=fecha_limite,
        fecha_programada__gte=hoy
    ).count()

    vencidos = Mantenimiento.objects.filter(
        estado='pendiente',
        fecha_programada__lt=hoy
    ).count()

    print(f"\n⚠ ALERTAS:")
    print(f"  Mantenimientos próximos (15 días): {alertas}")
    print(f"  Mantenimientos vencidos: {vencidos}")

    print("\n" + "="*60)
    print("✓ Script completado exitosamente!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
