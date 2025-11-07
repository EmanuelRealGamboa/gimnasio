#!/usr/bin/env python
"""
Script simple para crear datos de prueba básicos
"""
import os
import django
from datetime import date, time, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from horarios.models import TipoActividad, Horario, SesionClase

def crear_datos_basicos():
    print("🚀 Creando datos básicos de prueba...")
    
    # 1. Crear tipos de actividades
    print("\n📋 Creando tipos de actividades...")
    actividades = [
        {
            'nombre': 'Yoga Matutino',
            'descripcion': 'Clase de yoga para empezar el día con energía',
            'duracion_default': timedelta(hours=1),
            'color_hex': '#8B5CF6'
        },
        {
            'nombre': 'CrossFit Intensivo',
            'descripcion': 'Entrenamiento funcional de alta intensidad',
            'duracion_default': timedelta(hours=1, minutes=30),
            'color_hex': '#EF4444'
        },
        {
            'nombre': 'Spinning Cardio',
            'descripcion': 'Clase de ciclismo indoor energético',
            'duracion_default': timedelta(minutes=45),
            'color_hex': '#10B981'
        }
    ]
    
    for act_data in actividades:
        tipo, created = TipoActividad.objects.get_or_create(
            nombre=act_data['nombre'],
            defaults=act_data
        )
        print(f"  ✓ {tipo.nombre} {'(creado)' if created else '(ya existe)'}")
    
    print(f"\n✅ Datos básicos creados!")
    print(f"📊 Total de tipos de actividades: {TipoActividad.objects.count()}")
    
    print("\n🎯 SIGUIENTE PASO:")
    print("Ve al Django Admin para:")
    print("1. Crear entrenadores desde Empleados > Entrenadores")
    print("2. Crear horarios desde Horarios > Horarios")
    print("3. Generar sesiones automáticamente")

if __name__ == '__main__':
    crear_datos_basicos()
