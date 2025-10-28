"""
Script para crear membresías de prueba en la base de datos
Ejecutar con: python crear_membresias_prueba.py
"""

import os
import sys
import django

# Configurar encoding para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from membresias.models import Membresia
from decimal import Decimal

def crear_membresias_prueba():
    """Crear varias membresías de prueba con datos realistas"""

    membresias_data = [
        {
            'nombre_plan': 'Plan Básico Mensual',
            'tipo': 'mensual',
            'precio': Decimal('499.00'),
            'descripcion': 'Acceso ilimitado al área de pesas y cardio',
            'duracion_dias': 30,
            'beneficios': '''- Acceso ilimitado al gimnasio
- Área de pesas y cardio
- Vestidores y regaderas
- Wi-Fi gratuito''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Premium Mensual',
            'tipo': 'mensual',
            'precio': Decimal('899.00'),
            'descripcion': 'Todo incluido con clases grupales y asesoría personalizada',
            'duracion_dias': 30,
            'beneficios': '''- Todo lo del Plan Básico
- Clases grupales ilimitadas (Yoga, Spinning, Zumba)
- 2 sesiones de asesoría nutricional
- Evaluación física mensual
- Acceso prioritario a eventos''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Trimestral',
            'tipo': 'trimestral',
            'precio': Decimal('1299.00'),
            'descripcion': 'Ahorra un 15% con el plan de 3 meses',
            'duracion_dias': 90,
            'beneficios': '''- Acceso ilimitado al gimnasio
- Clases grupales ilimitadas
- 4 sesiones de asesoría nutricional
- Evaluación física inicial y final
- 10% descuento en productos''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Semestral Premium',
            'tipo': 'semestral',
            'precio': Decimal('2499.00'),
            'descripcion': 'El mejor valor con 6 meses de acceso completo',
            'duracion_dias': 180,
            'beneficios': '''- Acceso VIP al gimnasio
- Todas las clases grupales
- Plan nutricional personalizado
- Evaluación física mensual
- Entrenador personal (2 sesiones/mes)
- 15% descuento en productos
- Invitación a eventos exclusivos''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Anual Elite',
            'tipo': 'anual',
            'precio': Decimal('4299.00'),
            'descripcion': 'Membresía anual con todos los beneficios y máximo ahorro',
            'duracion_dias': 365,
            'beneficios': '''- Todo lo del Plan Semestral
- Entrenador personal ilimitado
- Spa y sauna incluidos
- Nutriólogo personal
- Evaluaciones médicas trimestrales
- Kit de bienvenida premium
- Pase de invitado (2 al mes)
- 20% descuento en productos
- Garantía de satisfacción''',
            'activo': True
        },
        {
            'nombre_plan': 'Pase del Día',
            'tipo': 'pase_dia',
            'precio': Decimal('80.00'),
            'descripcion': 'Acceso por un día al gimnasio',
            'duracion_dias': 1,
            'beneficios': '''- Acceso completo por 1 día
- Área de pesas y cardio
- Vestidores y regaderas''',
            'activo': True
        },
        {
            'nombre_plan': 'Pase Semanal',
            'tipo': 'pase_semana',
            'precio': Decimal('350.00'),
            'descripcion': 'Pase de 7 días para visitantes o prueba',
            'duracion_dias': 7,
            'beneficios': '''- Acceso completo por 7 días
- Todas las áreas del gimnasio
- 1 clase grupal incluida
- Evaluación física gratuita''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Estudiante',
            'tipo': 'mensual',
            'precio': Decimal('399.00'),
            'descripcion': 'Descuento especial para estudiantes',
            'duracion_dias': 30,
            'beneficios': '''- Acceso ilimitado al gimnasio
- Clases grupales seleccionadas
- Requiere credencial vigente
- Horario preferencial (6am-4pm)''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Familiar Mensual',
            'tipo': 'mensual',
            'precio': Decimal('1599.00'),
            'descripcion': 'Membresía para 2-4 familiares',
            'duracion_dias': 30,
            'beneficios': '''- Hasta 4 miembros de la familia
- Acceso ilimitado para todos
- Clases grupales incluidas
- Evaluación física para todos
- Descuentos en productos''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Corporativo',
            'tipo': 'mensual',
            'precio': Decimal('699.00'),
            'descripcion': 'Membresía empresarial por empleado',
            'duracion_dias': 30,
            'beneficios': '''- Precio especial corporativo
- Facturación centralizada
- Reportes de asistencia
- Eventos wellness empresariales
- Mínimo 10 empleados''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Senior',
            'tipo': 'mensual',
            'precio': Decimal('449.00'),
            'descripcion': 'Especial para adultos mayores (+60 años)',
            'duracion_dias': 30,
            'beneficios': '''- Acceso ilimitado
- Clases adaptadas para seniors
- Horario preferencial matutino
- Seguimiento médico mensual
- Área de bajo impacto''',
            'activo': True
        },
        {
            'nombre_plan': 'Plan Black Friday',
            'tipo': 'anual',
            'precio': Decimal('3599.00'),
            'descripcion': 'Oferta especial limitada - Solo válido en promoción',
            'duracion_dias': 365,
            'beneficios': '''- Precio promocional único
- Todos los beneficios del Plan Anual
- No acumulable con otras promociones
- Vigencia limitada''',
            'activo': False  # Desactivado porque es promoción pasada
        }
    ]

    print("\n" + "="*60)
    print("CREANDO MEMBRESÍAS DE PRUEBA")
    print("="*60 + "\n")

    membresias_creadas = 0
    membresias_existentes = 0

    for data in membresias_data:
        # Verificar si la membresía ya existe
        if Membresia.objects.filter(nombre_plan=data['nombre_plan']).exists():
            print(f"⚠ Membresía '{data['nombre_plan']}' ya existe. Saltando...")
            membresias_existentes += 1
            continue

        try:
            membresia = Membresia.objects.create(**data)
            membresias_creadas += 1
            estado_str = "✓ Activa" if data['activo'] else "✗ Inactiva"
            print(f"✓ Membresía creada: {data['nombre_plan']}")
            print(f"  Tipo: {data['tipo']} | Precio: ${data['precio']} | {estado_str}")

        except Exception as e:
            print(f"✗ Error al crear membresía '{data['nombre_plan']}': {str(e)}")

    print("\n" + "="*60)
    print(f"RESUMEN:")
    print(f"  Membresías creadas: {membresias_creadas}")
    print(f"  Membresías ya existentes: {membresias_existentes}")
    print(f"  Total procesadas: {len(membresias_data)}")
    print("="*60 + "\n")

    # Mostrar estadísticas finales
    total_membresias = Membresia.objects.count()
    activas = Membresia.objects.filter(activo=True).count()
    inactivas = Membresia.objects.filter(activo=False).count()

    print("ESTADÍSTICAS DE LA BASE DE DATOS:")
    print(f"  Total de membresías: {total_membresias}")
    print(f"  Activas: {activas}")
    print(f"  Inactivas: {inactivas}")
    print("\n")

    # Mostrar por tipo
    print("POR TIPO DE MEMBRESÍA:")
    for tipo_key, tipo_label in Membresia.TIPO_CHOICES:
        count = Membresia.objects.filter(tipo=tipo_key).count()
        if count > 0:
            print(f"  {tipo_label}: {count}")

    # Estadísticas de precio
    from django.db.models import Avg, Min, Max
    stats = Membresia.objects.aggregate(
        promedio=Avg('precio'),
        minimo=Min('precio'),
        maximo=Max('precio')
    )

    print("\n")
    print("ESTADÍSTICAS DE PRECIOS:")
    print(f"  Precio mínimo: ${stats['minimo']}")
    print(f"  Precio máximo: ${stats['maximo']}")
    print(f"  Precio promedio: ${stats['promedio']:.2f}")
    print("\n")

if __name__ == '__main__':
    crear_membresias_prueba()
    print("✓ Script completado exitosamente!")
