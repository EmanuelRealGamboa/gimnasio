#!/usr/bin/env python
"""
Script para crear membresías de prueba para el gimnasio
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from membresias.models import Membresia
from decimal import Decimal

def crear_membresias():
    """Crear membresías de prueba"""
    
    membresias_data = [
        {
            'nombre_plan': 'Básico',
            'tipo': 'mensual',
            'precio': Decimal('599.00'),
            'duracion_dias': 30,
            'descripcion': 'Acceso completo al gimnasio durante horarios regulares',
            'beneficios': 'Acceso a área de pesas, cardio y clases grupales básicas',
            'activo': True
        },
        {
            'nombre_plan': 'Premium',
            'tipo': 'mensual',
            'precio': Decimal('899.00'),
            'duracion_dias': 30,
            'descripcion': 'Acceso completo + servicios adicionales',
            'beneficios': 'Todo lo del plan básico + acceso a sauna, vapor, clases premium y 2 sesiones de entrenador personal',
            'activo': True
        },
        {
            'nombre_plan': 'VIP',
            'tipo': 'mensual',
            'precio': Decimal('1299.00'),
            'duracion_dias': 30,
            'descripcion': 'Acceso completo con todos los beneficios',
            'beneficios': 'Todo lo del plan premium + casillero personal, toallas, bebidas deportivas y 4 sesiones de entrenador personal',
            'activo': True
        },
        {
            'nombre_plan': 'Anual Básico',
            'tipo': 'anual',
            'precio': Decimal('5999.00'),
            'duracion_dias': 365,
            'descripcion': 'Plan básico con descuento anual (2 meses gratis)',
            'beneficios': 'Acceso a área de pesas, cardio y clases grupales básicas por un año completo',
            'activo': True
        },
        {
            'nombre_plan': 'Anual Premium',
            'tipo': 'anual',
            'precio': Decimal('8999.00'),
            'duracion_dias': 365,
            'descripcion': 'Plan premium con descuento anual (2 meses gratis)',
            'beneficios': 'Todo lo del plan básico + acceso a sauna, vapor, clases premium y 24 sesiones de entrenador personal al año',
            'activo': True
        },
        {
            'nombre_plan': 'Estudiante',
            'tipo': 'mensual',
            'precio': Decimal('399.00'),
            'duracion_dias': 30,
            'descripcion': 'Plan especial para estudiantes con credencial vigente',
            'beneficios': 'Acceso a área de pesas y cardio en horarios específicos (6am-2pm y 8pm-11pm)',
            'activo': True
        },
        {
            'nombre_plan': 'Día Completo',
            'tipo': 'diario',
            'precio': Decimal('50.00'),
            'duracion_dias': 1,
            'descripcion': 'Acceso por un día completo',
            'beneficios': 'Acceso completo al gimnasio por 24 horas',
            'activo': True
        },
        {
            'nombre_plan': 'Semanal',
            'tipo': 'semanal',
            'precio': Decimal('199.00'),
            'duracion_dias': 7,
            'descripcion': 'Acceso por una semana completa',
            'beneficios': 'Acceso completo al gimnasio por 7 días',
            'activo': True
        }
    ]
    
    print("🏋️ Creando membresías de prueba...")
    
    for membresia_data in membresias_data:
        membresia, created = Membresia.objects.get_or_create(
            nombre_plan=membresia_data['nombre_plan'],
            defaults=membresia_data
        )
        
        if created:
            print(f"✅ Creada: {membresia.nombre_plan} - ${membresia.precio}")
        else:
            print(f"⚠️  Ya existe: {membresia.nombre_plan}")
    
    print(f"\n📊 Total de membresías: {Membresia.objects.count()}")
    print(f"📊 Membresías activas: {Membresia.objects.filter(activo=True).count()}")

if __name__ == '__main__':
    crear_membresias()
    print("\n🎉 ¡Membresías de prueba creadas exitosamente!")