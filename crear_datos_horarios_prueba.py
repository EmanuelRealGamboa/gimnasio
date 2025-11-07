#!/usr/bin/env python
"""
Script para crear datos de prueba del sistema de horarios y reservas
"""
import os
import django
from datetime import date, time, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from horarios.models import (
    TipoActividad, Horario, SesionClase, EquipoActividad, 
    ClienteMembresia, ReservaClase
)
from clientes.models import Cliente
from membresias.models import Membresia
from empleados.models import Entrenador, Empleado
from instalaciones.models import Sede, Espacio
from gestion_equipos.models import Activo, CategoriaActivo
from authentication.models import Persona, User

def crear_datos_prueba():
    print("🚀 Creando datos de prueba para horarios y reservas...")
    
    # 1. Crear tipos de actividades
    print("\n📋 Creando tipos de actividades...")
    actividades = [
        {
            'nombre': 'Yoga',
            'descripcion': 'Clase de yoga para relajación y flexibilidad',
            'duracion_default': timedelta(hours=1),
            'color_hex': '#8B5CF6'
        },
        {
            'nombre': 'CrossFit',
            'descripcion': 'Entrenamiento funcional de alta intensidad',
            'duracion_default': timedelta(hours=1, minutes=30),
            'color_hex': '#EF4444'
        },
        {
            'nombre': 'Spinning',
            'descripcion': 'Clase de ciclismo indoor',
            'duracion_default': timedelta(minutes=45),
            'color_hex': '#10B981'
        },
        {
            'nombre': 'Pilates',
            'descripcion': 'Ejercicios de fortalecimiento del core',
            'duracion_default': timedelta(hours=1),
            'color_hex': '#F59E0B'
        },
        {
            'nombre': 'Zumba',
            'descripcion': 'Baile fitness divertido',
            'duracion_default': timedelta(minutes=50),
            'color_hex': '#EC4899'
        }
    ]
    
    tipos_creados = {}
    for act_data in actividades:
        tipo, created = TipoActividad.objects.get_or_create(
            nombre=act_data['nombre'],
            defaults=act_data
        )
        tipos_creados[act_data['nombre']] = tipo
        print(f"  ✓ {tipo.nombre} {'(creado)' if created else '(ya existe)'}")
    
    # 2. Crear sedes y espacios si no existen
    print("\n🏢 Verificando sedes y espacios...")
    sede, created = Sede.objects.get_or_create(
        nombre='Sede Principal',
        defaults={
            'direccion': 'Av. Principal 123',
            'telefono': '555-0123'
        }
    )
    print(f"  ✓ Sede: {sede.nombre} {'(creada)' if created else '(ya existe)'}")
    
    espacios_data = [
        {'nombre': 'Salón de Yoga', 'capacidad': 20},
        {'nombre': 'Box de CrossFit', 'capacidad': 15},
        {'nombre': 'Salón de Spinning', 'capacidad': 25},
        {'nombre': 'Área de Pilates', 'capacidad': 12},
        {'nombre': 'Salón Principal', 'capacidad': 30}
    ]
    
    espacios_creados = {}
    for esp_data in espacios_data:
        espacio, created = Espacio.objects.get_or_create(
            nombre=esp_data['nombre'],
            sede=sede,
            defaults={
                'descripcion': f"Espacio dedicado para {esp_data['nombre'].lower()}",
                'capacidad': esp_data['capacidad']
            }
        )
        espacios_creados[esp_data['nombre']] = espacio
        print(f"  ✓ Espacio: {espacio.nombre} {'(creado)' if created else '(ya existe)'}")
    
    # 3. Crear entrenadores si no existen
    print("\n👨‍🏫 Verificando entrenadores...")
    entrenadores_data = [
        {
            'nombre': 'Ana', 'apellido': 'García', 'especialidad': 'Yoga y Pilates',
            'email': 'ana.garcia@gimnasio.com'
        },
        {
            'nombre': 'Carlos', 'apellido': 'Rodríguez', 'especialidad': 'CrossFit',
            'email': 'carlos.rodriguez@gimnasio.com'
        },
        {
            'nombre': 'María', 'apellido': 'López', 'especialidad': 'Spinning y Cardio',
            'email': 'maria.lopez@gimnasio.com'
        }
    ]
    
    entrenadores_creados = {}
    for ent_data in entrenadores_data:
        # Verificar si ya existe el usuario
        user, user_created = User.objects.get_or_create(
            email=ent_data['email'],
            defaults={'is_active': True}
        )
        
        if user_created:
            user.set_password('entrenador123')
            user.save()
        
        # Crear persona si no existe
        persona, persona_created = Persona.objects.get_or_create(
            defaults={
                'nombre': ent_data['nombre'],
                'apellido_paterno': ent_data['apellido'],
                'apellido_materno': 'Trainer',
                'telefono': '555-0000'
            }
        )
        
        # Asociar persona con usuario
        if persona_created:
            user.persona = persona
            user.save()
        
        # Crear empleado si no existe
        empleado, emp_created = Empleado.objects.get_or_create(
            persona=persona,
            defaults={
                'puesto': 'Entrenador',
                'departamento': 'Fitness',
                'fecha_contratacion': date.today() - timedelta(days=365),
                'tipo_contrato': 'Tiempo completo',
                'salario': Decimal('25000.00'),
                'estado': 'Activo',
                'sede': sede
            }
        )
        
        # Crear entrenador si no existe
        entrenador, created = Entrenador.objects.get_or_create(
            empleado=empleado,
            defaults={
                'especialidad': ent_data['especialidad'],
                'certificaciones': 'Certificado Nacional de Fitness',
                'turno': 'Matutino',
                'sede': sede
            }
        )
        
        # Asignar espacios al entrenador
        if ent_data['especialidad'] == 'Yoga y Pilates':
            entrenador.espacio.add(espacios_creados['Salón de Yoga'], espacios_creados['Área de Pilates'])
        elif ent_data['especialidad'] == 'CrossFit':
            entrenador.espacio.add(espacios_creados['Box de CrossFit'])
        elif ent_data['especialidad'] == 'Spinning y Cardio':
            entrenador.espacio.add(espacios_creados['Salón de Spinning'])
        
        entrenadores_creados[ent_data['nombre']] = entrenador
        print(f"  ✓ Entrenador: {persona.nombre} {persona.apellido_paterno} {'(creado)' if created else '(ya existe)'}")
    
    # 4. Crear horarios
    print("\n⏰ Creando horarios...")
    horarios_data = [
        # Ana - Yoga
        {
            'tipo': 'Yoga', 'entrenador': 'Ana', 'espacio': 'Salón de Yoga',
            'dia': 'lunes', 'inicio': time(8, 0), 'fin': time(9, 0), 'cupo': 20
        },
        {
            'tipo': 'Yoga', 'entrenador': 'Ana', 'espacio': 'Salón de Yoga',
            'dia': 'miercoles', 'inicio': time(8, 0), 'fin': time(9, 0), 'cupo': 20
        },
        {
            'tipo': 'Pilates', 'entrenador': 'Ana', 'espacio': 'Área de Pilates',
            'dia': 'martes', 'inicio': time(18, 0), 'fin': time(19, 0), 'cupo': 12
        },
        # Carlos - CrossFit
        {
            'tipo': 'CrossFit', 'entrenador': 'Carlos', 'espacio': 'Box de CrossFit',
            'dia': 'lunes', 'inicio': time(17, 0), 'fin': time(18, 30), 'cupo': 15
        },
        {
            'tipo': 'CrossFit', 'entrenador': 'Carlos', 'espacio': 'Box de CrossFit',
            'dia': 'jueves', 'inicio': time(17, 0), 'fin': time(18, 30), 'cupo': 15
        },
        # María - Spinning
        {
            'tipo': 'Spinning', 'entrenador': 'María', 'espacio': 'Salón de Spinning',
            'dia': 'martes', 'inicio': time(7, 0), 'fin': time(7, 45), 'cupo': 25
        },
        {
            'tipo': 'Spinning', 'entrenador': 'María', 'espacio': 'Salón de Spinning',
            'dia': 'viernes', 'inicio': time(7, 0), 'fin': time(7, 45), 'cupo': 25
        }
    ]
    
    for hor_data in horarios_data:
        horario, created = Horario.objects.get_or_create(
            tipo_actividad=tipos_creados[hor_data['tipo']],
            entrenador=entrenadores_creados[hor_data['entrenador']],
            espacio=espacios_creados[hor_data['espacio']],
            dia_semana=hor_data['dia'],
            hora_inicio=hor_data['inicio'],
            defaults={
                'hora_fin': hor_data['fin'],
                'fecha_inicio': date.today(),
                'cupo_maximo': hor_data['cupo'],
                'estado': 'activo'
            }
        )
        print(f"  ✓ {horario} {'(creado)' if created else '(ya existe)'}")
    
    # 5. Generar sesiones para la próxima semana
    print("\n📅 Generando sesiones para la próxima semana...")
    fecha_inicio = date.today()
    fecha_fin = fecha_inicio + timedelta(days=7)
    
    # Mapeo de días
    dias_mapping = {
        'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3,
        'viernes': 4, 'sabado': 5, 'domingo': 6
    }
    
    sesiones_creadas = 0
    for horario in Horario.objects.filter(estado='activo'):
        dia_objetivo = dias_mapping[horario.dia_semana]
        fecha_actual = fecha_inicio
        
        while fecha_actual <= fecha_fin:
            if fecha_actual.weekday() == dia_objetivo:
                sesion, created = SesionClase.objects.get_or_create(
                    horario=horario,
                    fecha=fecha_actual
                )
                if created:
                    sesiones_creadas += 1
            fecha_actual += timedelta(days=1)
    
    print(f"  ✓ {sesiones_creadas} sesiones creadas")
    
    # 6. Crear clientes de prueba
    print("\n👥 Creando clientes de prueba...")
    clientes_data = [
        {'nombre': 'Juan', 'apellido': 'Pérez', 'email': 'juan.perez@email.com'},
        {'nombre': 'Laura', 'apellido': 'Martínez', 'email': 'laura.martinez@email.com'},
        {'nombre': 'Pedro', 'apellido': 'González', 'email': 'pedro.gonzalez@email.com'}
    ]
    
    clientes_creados = []
    for cli_data in clientes_data:
        # Crear usuario
        user, created = User.objects.get_or_create(
            email=cli_data['email'],
            defaults={'is_active': True}
        )
        if created:
            user.set_password('cliente123')
            user.save()
        
        # Crear persona
        persona, created = Persona.objects.get_or_create(
            defaults={
                'nombre': cli_data['nombre'],
                'apellido_paterno': cli_data['apellido'],
                'apellido_materno': 'Cliente',
                'telefono': '555-1234'
            }
        )
        
        # Asociar persona con usuario
        if created:
            user.persona = persona
            user.save()
        
        # Crear cliente
        cliente, created = Cliente.objects.get_or_create(
            persona=persona,
            defaults={
                'objetivo_fitness': 'Mantenerse en forma',
                'nivel_experiencia': 'intermedio',
                'estado': 'activo'
            }
        )
        
        clientes_creados.append(cliente)
        print(f"  ✓ Cliente: {persona.nombre} {persona.apellido_paterno} {'(creado)' if created else '(ya existe)'}")
    
    # 7. Crear membresías
    print("\n💳 Creando membresías...")
    membresia, created = Membresia.objects.get_or_create(
        nombre_plan='Plan Básico Mensual',
        defaults={
            'tipo': 'mensual',
            'precio': Decimal('500.00'),
            'descripcion': 'Acceso completo al gimnasio por un mes',
            'duracion_dias': 30,
            'beneficios': 'Acceso a todas las clases grupales, uso de equipos',
            'activo': True
        }
    )
    print(f"  ✓ Membresía: {membresia.nombre_plan} {'(creada)' if created else '(ya existe)'}")
    
    # 8. Asignar membresías a clientes
    print("\n🎫 Asignando membresías a clientes...")
    for cliente in clientes_creados:
        cliente_membresia, created = ClienteMembresia.objects.get_or_create(
            cliente=cliente,
            membresia=membresia,
            defaults={
                'fecha_inicio': date.today(),
                'fecha_fin': date.today() + timedelta(days=30),
                'estado': 'activa'
            }
        )
        print(f"  ✓ {cliente.persona.nombre}: Membresía {'asignada' if created else 'ya existe'}")
    
    print("\n🎉 ¡Datos de prueba creados exitosamente!")
    print("\n📋 RESUMEN:")
    print(f"  • {TipoActividad.objects.count()} tipos de actividades")
    print(f"  • {Horario.objects.count()} horarios configurados")
    print(f"  • {SesionClase.objects.count()} sesiones programadas")
    print(f"  • {Cliente.objects.count()} clientes registrados")
    print(f"  • {ClienteMembresia.objects.filter(estado='activa').count()} membresías activas")
    
    print("\n🚀 ¡Ahora puedes probar el sistema!")

if __name__ == '__main__':
    crear_datos_prueba()
