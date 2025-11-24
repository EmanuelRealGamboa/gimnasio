# -*- coding: utf-8 -*-
"""
Script para crear un empleado de limpieza de prueba con tareas asignadas.
Ejecutar: python crear_empleado_limpieza_test.py
"""
import os
import django
from datetime import date, time, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from authentication.models import User, Persona
from empleados.models import Empleado, PersonalLimpieza, TareaLimpieza, AsignacionTarea
from instalaciones.models import Sede, Espacio

def crear_empleado_limpieza_test():
    """Crear un empleado de limpieza de prueba con tareas asignadas."""

    print('=' * 60)
    print('CREANDO EMPLEADO DE LIMPIEZA DE PRUEBA')
    print('=' * 60)

    # 1. Obtener o crear sede
    sede, created = Sede.objects.get_or_create(
        nombre='Sede Central',
        defaults={
            'direccion': 'Av. Principal 123',
            'telefono': '1234567890'
        }
    )
    print(f"[OK] Sede: {sede.nombre} {'(creada)' if created else '(existente)'}")

    # 2. Crear espacios de prueba si no existen
    espacios = []
    tipos_espacios = [
        ('Recepcion', 'recepcion'),
        ('Vestidores', 'vestidores'),
        ('Area de Cardio', 'area_cardio'),
        ('Area de Pesas', 'area_pesas'),
    ]

    for nombre, tipo in tipos_espacios:
        espacio, created = Espacio.objects.get_or_create(
            nombre=nombre,
            sede=sede,
            defaults={
                'descripcion': f'Espacio de {nombre}',
                'capacidad': 20
            }
        )
        espacios.append(espacio)
        print(f"  [+] Espacio: {espacio.nombre} {'(creado)' if created else '(existente)'}")

    # 3. Crear usuario para empleado de limpieza
    email_test = 'limpieza@gmail.com'
    password_test = '123456'

    # Verificar si el usuario ya existe
    user = User.objects.filter(email=email_test).first()

    if user:
        print(f"\n[!] El usuario {email_test} ya existe")
        print(f"    Contrasena: {password_test}")

        # Verificar si tiene persona y empleado
        try:
            persona = user.persona
            empleado = persona.empleado
            personal_limpieza = empleado.personallimpieza
            print(f"    [+] Personal de limpieza existente: {persona.nombre} {persona.apellido_paterno}")
        except Exception as e:
            print(f"    [X] Error: El usuario existe pero no tiene datos completos de empleado")
            print(f"    {str(e)}")
            return
    else:
        # Crear nuevo usuario
        user = User.objects.create_user(
            email=email_test,
            password=password_test
        )
        print(f"\n[OK] Usuario creado: {email_test}")
        print(f"     Contrasena: {password_test}")

        # Crear persona
        persona = Persona.objects.create(
            usuario=user,
            nombre='Juan',
            apellido_paterno='Perez',
            apellido_materno='Garcia',
            fecha_nacimiento=date(1990, 5, 15),
            telefono='5551234567',
            sexo='M'
        )
        print(f"[OK] Persona creada: {persona.nombre} {persona.apellido_paterno}")

        # Crear empleado
        empleado = Empleado.objects.create(
            persona=persona,
            sede=sede,
            fecha_contratacion=date.today(),
            salario=8000.00,
            puesto='Personal de Limpieza',
            activo=True
        )
        print(f"[OK] Empleado creado - Puesto: {empleado.puesto}")

        # Crear personal de limpieza
        personal_limpieza = PersonalLimpieza.objects.create(
            empleado=empleado,
            sede=sede,
            turno='Matutino (6:00 - 14:00)',
            activo=True
        )
        personal_limpieza.espacio.set(espacios[:2])  # Asignar recepcion y vestidores
        print(f"[OK] Personal de limpieza creado - Turno: {personal_limpieza.turno}")
        print(f"     Espacios asignados: {', '.join([e.nombre for e in espacios[:2]])}")

    # 4. Crear tareas de limpieza si no existen
    tareas_catalogo = [
        {
            'nombre': 'Limpieza General',
            'descripcion': 'Barrer, trapear y limpiar superficies',
            'tipo_espacio': 'recepcion',
            'duracion_estimada': 30,
            'prioridad': 'media'
        },
        {
            'nombre': 'Desinfeccion de Vestidores',
            'descripcion': 'Desinfectar lockers, bancas y pisos',
            'tipo_espacio': 'vestidores',
            'duracion_estimada': 45,
            'prioridad': 'alta'
        },
        {
            'nombre': 'Limpieza de Maquinas',
            'descripcion': 'Limpiar y desinfectar equipos de cardio',
            'tipo_espacio': 'area_cardio',
            'duracion_estimada': 40,
            'prioridad': 'alta'
        },
        {
            'nombre': 'Reabastecimiento de Insumos',
            'descripcion': 'Reabastecer papel, jabon y toallas',
            'tipo_espacio': 'vestidores',
            'duracion_estimada': 15,
            'prioridad': 'baja'
        }
    ]

    print(f"\nCreando catalogo de tareas...")
    tareas_creadas = []
    for tarea_data in tareas_catalogo:
        tarea, created = TareaLimpieza.objects.get_or_create(
            nombre=tarea_data['nombre'],
            defaults=tarea_data
        )
        tareas_creadas.append(tarea)
        print(f"  [+] Tarea: {tarea.nombre} {'(creada)' if created else '(existente)'}")

    # 5. Crear asignaciones de tareas para hoy y manana
    print(f"\nCreando asignaciones de tareas...")
    fechas = [date.today(), date.today() + timedelta(days=1)]

    for fecha in fechas:
        print(f"\n  Fecha: {fecha.strftime('%Y-%m-%d')}")

        # Asignar tareas en espacios del empleado
        for i, espacio in enumerate(espacios[:2]):  # Solo recepcion y vestidores
            # Buscar tareas compatibles con el tipo de espacio
            tareas_espacio = [t for t in tareas_creadas if t.tipo_espacio == espacio.tipo]

            if not tareas_espacio:
                # Si no hay tareas especificas, usar la primera tarea generica
                tareas_espacio = [tareas_creadas[0]]

            for tarea in tareas_espacio:
                # Verificar si ya existe la asignacion
                asignacion_existente = AsignacionTarea.objects.filter(
                    personal_limpieza=personal_limpieza,
                    tarea=tarea,
                    espacio=espacio,
                    fecha=fecha
                ).first()

                if not asignacion_existente:
                    hora_inicio = time(8 + i * 2, 0)  # 8:00, 10:00, etc.

                    asignacion = AsignacionTarea.objects.create(
                        personal_limpieza=personal_limpieza,
                        tarea=tarea,
                        espacio=espacio,
                        fecha=fecha,
                        hora_inicio=hora_inicio,
                        estado='pendiente',
                        asignado_por=empleado
                    )
                    print(f"    [+] {espacio.nombre} - {tarea.nombre} a las {hora_inicio.strftime('%H:%M')}")
                else:
                    print(f"    [*] {espacio.nombre} - {tarea.nombre} (ya existe)")

    print(f"\n{'=' * 60}")
    print('DATOS DE PRUEBA CREADOS EXITOSAMENTE')
    print('=' * 60)
    print(f"\nCREDENCIALES PARA APP MOVIL:")
    print(f"  Email: {email_test}")
    print(f"  Contrasena: {password_test}")
    print(f"\nEMPLEADO:")
    print(f"  Nombre: {persona.nombre} {persona.apellido_paterno}")
    print(f"  Sede: {sede.nombre}")
    print(f"  Turno: {personal_limpieza.turno}")
    print(f"  Espacios: {', '.join([e.nombre for e in espacios[:2]])}")
    print(f"\nTAREAS ASIGNADAS:")

    total_tareas = AsignacionTarea.objects.filter(
        personal_limpieza=personal_limpieza,
        fecha=date.today()
    ).count()
    print(f"  Hoy: {total_tareas} tareas")

    total_tareas_manana = AsignacionTarea.objects.filter(
        personal_limpieza=personal_limpieza,
        fecha=date.today() + timedelta(days=1)
    ).count()
    print(f"  Manana: {total_tareas_manana} tareas")
    print()

if __name__ == '__main__':
    try:
        crear_empleado_limpieza_test()
    except Exception as e:
        print(f"\n[X] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
