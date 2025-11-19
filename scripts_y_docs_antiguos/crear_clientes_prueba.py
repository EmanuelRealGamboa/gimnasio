"""
Script para crear clientes de prueba en la base de datos
Ejecutar con: python manage.py shell < crear_clientes_prueba.py
O: python crear_clientes_prueba.py
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

from authentication.models import Persona, User, ContactoEmergencia
from clientes.models import Cliente
from roles.models import Rol, PersonaRol
from datetime import date, timedelta
import random

def crear_clientes_prueba():
    """Crear varios clientes de prueba con datos realistas"""

    # Asegurar que existe el rol Cliente
    rol_cliente, created = Rol.objects.get_or_create(
        nombre='Cliente',
        defaults={'descripcion': 'Cliente del gimnasio'}
    )
    if created:
        print("✓ Rol 'Cliente' creado")
    else:
        print("✓ Rol 'Cliente' ya existe")

    clientes_data = [
        {
            'nombre': 'Juan',
            'apellido_paterno': 'García',
            'apellido_materno': 'López',
            'fecha_nacimiento': date(1990, 5, 15),
            'sexo': 'Masculino',
            'direccion': 'Av. Insurgentes Sur 1234, Col. Del Valle, CDMX',
            'telefono': '5551234567',
            'email': 'juan.garcia@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Pérdida de peso y mejorar resistencia cardiovascular',
            'nivel_experiencia': 'principiante',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'María García',
                'telefono': '5559876543',
                'parentesco': 'Esposa'
            }
        },
        {
            'nombre': 'María',
            'apellido_paterno': 'Rodríguez',
            'apellido_materno': 'Sánchez',
            'fecha_nacimiento': date(1985, 8, 22),
            'sexo': 'Femenino',
            'direccion': 'Calle Reforma 567, Col. Juárez, CDMX',
            'telefono': '5552345678',
            'email': 'maria.rodriguez@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Tonificación muscular y flexibilidad',
            'nivel_experiencia': 'intermedio',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Carlos Rodríguez',
                'telefono': '5558765432',
                'parentesco': 'Esposo'
            }
        },
        {
            'nombre': 'Carlos',
            'apellido_paterno': 'Martínez',
            'apellido_materno': 'Hernández',
            'fecha_nacimiento': date(1988, 3, 10),
            'sexo': 'Masculino',
            'direccion': 'Av. Universidad 890, Col. Narvarte, CDMX',
            'telefono': '5553456789',
            'email': 'carlos.martinez@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Ganancia de masa muscular',
            'nivel_experiencia': 'avanzado',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Ana Martínez',
                'telefono': '5557654321',
                'parentesco': 'Hermana'
            }
        },
        {
            'nombre': 'Ana',
            'apellido_paterno': 'López',
            'apellido_materno': 'Pérez',
            'fecha_nacimiento': date(1995, 11, 5),
            'sexo': 'Femenino',
            'direccion': 'Calle Madero 123, Col. Centro, CDMX',
            'telefono': '5554567890',
            'email': 'ana.lopez@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Mejorar condición física general y salud',
            'nivel_experiencia': 'principiante',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Pedro López',
                'telefono': '5556543210',
                'parentesco': 'Padre'
            }
        },
        {
            'nombre': 'Luis',
            'apellido_paterno': 'González',
            'apellido_materno': 'Ramírez',
            'fecha_nacimiento': date(1992, 7, 18),
            'sexo': 'Masculino',
            'direccion': 'Av. Patriotismo 456, Col. San Pedro de los Pinos, CDMX',
            'telefono': '5555678901',
            'email': 'luis.gonzalez@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Preparación para maratón',
            'nivel_experiencia': 'intermedio',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Laura González',
                'telefono': '5555432109',
                'parentesco': 'Madre'
            }
        },
        {
            'nombre': 'Laura',
            'apellido_paterno': 'Fernández',
            'apellido_materno': 'Torres',
            'fecha_nacimiento': date(1987, 12, 30),
            'sexo': 'Femenino',
            'direccion': 'Calle Amsterdam 789, Col. Condesa, CDMX',
            'telefono': '5556789012',
            'email': 'laura.fernandez@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Yoga y meditación, equilibrio mente-cuerpo',
            'nivel_experiencia': 'avanzado',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Roberto Fernández',
                'telefono': '5554321098',
                'parentesco': 'Hermano'
            }
        },
        {
            'nombre': 'Roberto',
            'apellido_paterno': 'Díaz',
            'apellido_materno': 'Morales',
            'fecha_nacimiento': date(1993, 4, 25),
            'sexo': 'Masculino',
            'direccion': 'Av. Revolución 321, Col. San Ángel, CDMX',
            'telefono': '5557890123',
            'email': 'roberto.diaz@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Entrenamiento funcional para deportes',
            'nivel_experiencia': 'intermedio',
            'estado': 'inactivo',
            'contacto_emergencia': {
                'nombre': 'Carmen Díaz',
                'telefono': '5553210987',
                'parentesco': 'Esposa'
            }
        },
        {
            'nombre': 'Carmen',
            'apellido_paterno': 'Ruiz',
            'apellido_materno': 'Castro',
            'fecha_nacimiento': date(1991, 9, 12),
            'sexo': 'Femenino',
            'direccion': 'Calle Orizaba 654, Col. Roma Norte, CDMX',
            'telefono': '5558901234',
            'email': 'carmen.ruiz@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Rehabilitación post-lesión',
            'nivel_experiencia': 'principiante',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Jorge Ruiz',
                'telefono': '5552109876',
                'parentesco': 'Padre'
            }
        },
        {
            'nombre': 'Jorge',
            'apellido_paterno': 'Vargas',
            'apellido_materno': 'Mendoza',
            'fecha_nacimiento': date(1989, 6, 8),
            'sexo': 'Masculino',
            'direccion': 'Av. Cuauhtémoc 987, Col. Doctores, CDMX',
            'telefono': '5559012345',
            'email': 'jorge.vargas@email.com',
            'password': 'password123',
            'objetivo_fitness': 'CrossFit y levantamiento de pesas',
            'nivel_experiencia': 'avanzado',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Diana Vargas',
                'telefono': '5551098765',
                'parentesco': 'Hermana'
            }
        },
        {
            'nombre': 'Diana',
            'apellido_paterno': 'Ortiz',
            'apellido_materno': 'Flores',
            'fecha_nacimiento': date(1994, 2, 14),
            'sexo': 'Femenino',
            'direccion': 'Calle Puebla 147, Col. Roma Sur, CDMX',
            'telefono': '5550123456',
            'email': 'diana.ortiz@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Bailoterapia y cardio',
            'nivel_experiencia': 'intermedio',
            'estado': 'suspendido',
            'contacto_emergencia': {
                'nombre': 'Miguel Ortiz',
                'telefono': '5559876540',
                'parentesco': 'Esposo'
            }
        },
        {
            'nombre': 'Miguel',
            'apellido_paterno': 'Jiménez',
            'apellido_materno': 'Reyes',
            'fecha_nacimiento': date(1986, 10, 20),
            'sexo': 'Masculino',
            'direccion': 'Av. Chapultepec 258, Col. Juárez, CDMX',
            'telefono': '5551234560',
            'email': 'miguel.jimenez@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Natación y triatlón',
            'nivel_experiencia': 'avanzado',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Elena Jiménez',
                'telefono': '5558765401',
                'parentesco': 'Esposa'
            }
        },
        {
            'nombre': 'Elena',
            'apellido_paterno': 'Moreno',
            'apellido_materno': 'Silva',
            'fecha_nacimiento': date(1996, 1, 3),
            'sexo': 'Femenino',
            'direccion': 'Calle Durango 369, Col. Roma Norte, CDMX',
            'telefono': '5552345601',
            'email': 'elena.moreno@email.com',
            'password': 'password123',
            'objetivo_fitness': 'Pilates y estiramiento',
            'nivel_experiencia': 'principiante',
            'estado': 'activo',
            'contacto_emergencia': {
                'nombre': 'Patricia Moreno',
                'telefono': '5557654302',
                'parentesco': 'Madre'
            }
        },
    ]

    print("\n" + "="*60)
    print("CREANDO CLIENTES DE PRUEBA")
    print("="*60 + "\n")

    clientes_creados = 0
    clientes_existentes = 0

    for data in clientes_data:
        # Verificar si el email ya existe
        if User.objects.filter(email=data['email']).exists():
            print(f"⚠ Cliente con email {data['email']} ya existe. Saltando...")
            clientes_existentes += 1
            continue

        try:
            # 1. Crear Persona
            persona = Persona.objects.create(
                nombre=data['nombre'],
                apellido_paterno=data['apellido_paterno'],
                apellido_materno=data['apellido_materno'],
                fecha_nacimiento=data['fecha_nacimiento'],
                sexo=data['sexo'],
                direccion=data['direccion'],
                telefono=data['telefono']
            )

            # 2. Crear User
            user = User.objects.create_user(
                email=data['email'],
                password=data['password'],
                persona=persona
            )

            # 3. Crear Cliente
            cliente = Cliente.objects.create(
                persona=persona,
                objetivo_fitness=data['objetivo_fitness'],
                nivel_experiencia=data['nivel_experiencia'],
                estado=data['estado']
            )

            # 4. Asignar rol Cliente
            PersonaRol.objects.create(persona=persona, rol=rol_cliente)

            # 5. Crear Contacto de Emergencia
            if 'contacto_emergencia' in data:
                ContactoEmergencia.objects.create(
                    persona=persona,
                    nombre_contacto=data['contacto_emergencia']['nombre'],
                    telefono_contacto=data['contacto_emergencia']['telefono'],
                    parentesco=data['contacto_emergencia']['parentesco']
                )

            clientes_creados += 1
            print(f"✓ Cliente creado: {data['nombre']} {data['apellido_paterno']} ({data['email']}) - {data['nivel_experiencia']} - {data['estado']}")

        except Exception as e:
            print(f"✗ Error al crear cliente {data['email']}: {str(e)}")

    print("\n" + "="*60)
    print(f"RESUMEN:")
    print(f"  Clientes creados: {clientes_creados}")
    print(f"  Clientes ya existentes: {clientes_existentes}")
    print(f"  Total procesados: {len(clientes_data)}")
    print("="*60 + "\n")

    # Mostrar estadísticas finales
    total_clientes = Cliente.objects.count()
    activos = Cliente.objects.filter(estado='activo').count()
    inactivos = Cliente.objects.filter(estado='inactivo').count()
    suspendidos = Cliente.objects.filter(estado='suspendido').count()

    print("ESTADÍSTICAS DE LA BASE DE DATOS:")
    print(f"  Total de clientes: {total_clientes}")
    print(f"  Activos: {activos}")
    print(f"  Inactivos: {inactivos}")
    print(f"  Suspendidos: {suspendidos}")
    print("\n")

    # Mostrar por nivel
    principiantes = Cliente.objects.filter(nivel_experiencia='principiante').count()
    intermedios = Cliente.objects.filter(nivel_experiencia='intermedio').count()
    avanzados = Cliente.objects.filter(nivel_experiencia='avanzado').count()

    print("POR NIVEL DE EXPERIENCIA:")
    print(f"  Principiantes: {principiantes}")
    print(f"  Intermedios: {intermedios}")
    print(f"  Avanzados: {avanzados}")
    print("\n")

if __name__ == '__main__':
    crear_clientes_prueba()
    print("✓ Script completado exitosamente!")
