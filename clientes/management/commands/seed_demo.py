"""
Management command idempotente para poblar la base de datos con datos de demostración.

Uso:
    python manage.py seed_demo           # Pobla (idempotente, no duplica)
    python manage.py seed_demo --flush   # Limpia datos demo y repobla
"""

from __future__ import annotations

import random
from datetime import date, time, timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone


class Command(BaseCommand):
    help = "Pobla la base de datos con datos de demostración realistas (idempotente)."

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Elimina los datos demo existentes antes de repoblar.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if options["flush"]:
            self._flush_demo_data()

        self.stdout.write(self.style.MIGRATE_HEADING("Iniciando seed de datos demo..."))

        with transaction.atomic():
            sedes = self._seed_instalaciones()
            admin_user = self._get_admin_user()
            activos_cat = self._seed_categorias_activos()
            activos = self._seed_activos(sedes, activos_cat, admin_user)
            empleados, entrenadores = self._seed_empleados(sedes)
            clientes = self._seed_clientes(sedes)
            membresias = self._seed_membresias(sedes)
            self._seed_suscripciones(clientes, membresias)
            self._seed_control_acceso(clientes, sedes)
            self._seed_inventario(sedes)
            self._seed_ventas(clientes, sedes, admin_user)
            self._seed_facturas(clientes)
            self._seed_horarios(entrenadores, sedes)
            self._seed_limpieza(empleados, sedes)

        self.stdout.write(self.style.SUCCESS("\nSeed completado exitosamente."))

    # ------------------------------------------------------------------
    # FLUSH
    # ------------------------------------------------------------------

    def _flush_demo_data(self) -> None:
        self.stdout.write(self.style.WARNING("Eliminando datos demo..."))

        from authentication.models import Persona, User
        from clientes.models import Cliente
        from control_acceso.models import Credencial, RegistroAcceso
        from empleados.models import (
            AsignacionTarea,
            Cajero,
            ChecklistLimpieza,
            Empleado,
            Entrenador,
            HorarioLimpieza,
            PersonalLimpieza,
            SupervisorEspacio,
            TareaLimpieza,
        )
        from facturacion.models import DetalleFactura, Factura, Pago
        from gestion_equipos.models import Activo, CategoriaActivo, Mantenimiento, OrdenMantenimiento, ProveedorServicio
        from horarios.models import (
            BloqueoHorario,
            ClienteMembresia,
            EquipoActividad,
            Horario,
            ReservaClase,
            ReservaEntrenador,
            ReservaEquipo,
            SesionClase,
            TipoActividad,
        )
        from instalaciones.models import Espacio, Sede
        from inventario.models import CategoriaProducto, Inventario, Producto
        from membresias.models import Membresia, SuscripcionMembresia
        from roles.models import PersonaRol, Permiso, Rol, RolPermiso
        from ventas.models import DetalleVentaProducto, VentaProducto

        # Orden inverso de dependencias
        for model in [
            ChecklistLimpieza, AsignacionTarea, HorarioLimpieza, TareaLimpieza,
            ReservaClase, ReservaEntrenador, ReservaEquipo,
            ClienteMembresia, BloqueoHorario, EquipoActividad, SesionClase, Horario, TipoActividad,
            DetalleVentaProducto, VentaProducto,
            Pago, DetalleFactura, Factura,
            RegistroAcceso, Credencial,
            SuscripcionMembresia,
            OrdenMantenimiento, Mantenimiento, Activo, CategoriaActivo, ProveedorServicio,
            Inventario,
        ]:
            count = model.objects.all().delete()[0]
            if count:
                self.stdout.write(f"  Eliminados {count} registros de {model.__name__}")

        # Eliminar suscripciones y membresías
        SuscripcionMembresia.objects.all().delete()
        Membresia.objects.all().delete()

        # Catálogos de inventario
        Inventario.objects.all().delete()
        Producto.objects.all().delete()
        CategoriaProducto.objects.all().delete()

        # Roles y PersonaRol de empleados demo (conservamos Rol y Permiso — los crea configurar_admin.py)
        PersonaRol.objects.exclude(persona__usuario__email="admin@gimnasio.com").delete()

        # Empleados, clientes y usuarios demo (no admin)
        for model in [SupervisorEspacio, PersonalLimpieza, Cajero, Entrenador, Empleado]:
            model.objects.all().delete()
        Cliente.objects.all().delete()

        # Usuarios demo
        User.objects.exclude(email="admin@gimnasio.com").delete()

        # Espacios y sedes
        Espacio.objects.all().delete()
        Sede.objects.all().delete()

        # Personas huérfanas
        Persona.objects.exclude(usuario__email="admin@gimnasio.com").delete()

        # Roles/permisos demo
        Rol.objects.all().delete()
        Permiso.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Flush completado."))

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _get_admin_user(self):
        from authentication.models import User
        return User.objects.get(email="admin@gimnasio.com")

    def _log(self, msg: str) -> None:
        self.stdout.write(f"  {msg}")

    # ------------------------------------------------------------------
    # INSTALACIONES: Sedes y Espacios
    # ------------------------------------------------------------------

    def _seed_instalaciones(self):
        from instalaciones.models import Espacio, Sede

        sedes_data = [
            {"nombre": "Sede Norte", "direccion": "Av. Insurgentes Norte 450, CDMX", "telefono": "5551234001"},
            {"nombre": "Sede Sur", "direccion": "Blvd. Miguel de Cervantes Saavedra 255, CDMX", "telefono": "5551234002"},
            {"nombre": "Sede Oriente", "direccion": "Calz. Ignacio Zaragoza 1200, CDMX", "telefono": "5551234003"},
            {"nombre": "Sede Poniente", "direccion": "Periférico Poniente 3800, CDMX", "telefono": "5551234004"},
        ]

        sedes = []
        for data in sedes_data:
            sede, created = Sede.objects.get_or_create(nombre=data["nombre"], defaults=data)
            sedes.append(sede)
            if created:
                self._log(f"Sede creada: {sede.nombre}")

        espacios_data = [
            ("Sala Cardio Principal", "Zona de máquinas cardiovasculares", 30),
            ("Sala de Pesas", "Zona de peso libre y máquinas de fuerza", 25),
            ("Estudio Grupal A", "Clases grupales: yoga, pilates, zumba", 20),
            ("Estudio Grupal B", "Clases grupales: spinning, kickboxing", 18),
            ("Alberca", "Alberca olímpica semiolímpica", 40),
            ("Vestidores Hombres", "Vestidores y regaderas para hombres", 50),
            ("Vestidores Mujeres", "Vestidores y regaderas para mujeres", 50),
            ("Recepción", "Área de recepción y control de acceso", 10),
        ]

        all_espacios: dict[str, list] = {sede.nombre: [] for sede in sedes}
        for sede in sedes:
            for nombre, desc, cap in espacios_data:
                espacio, created = Espacio.objects.get_or_create(
                    nombre=nombre,
                    sede=sede,
                    defaults={"descripcion": desc, "capacidad": cap},
                )
                all_espacios[sede.nombre].append(espacio)

        self._log(f"Sedes: {len(sedes)} | Espacios: {Espacio.objects.count()}")
        return sedes

    # ------------------------------------------------------------------
    # EMPLEADOS
    # ------------------------------------------------------------------

    def _seed_empleados(self, sedes):
        from authentication.models import Persona, User
        from empleados.models import (
            Cajero,
            Empleado,
            Entrenador,
            PersonalLimpieza,
            SupervisorEspacio,
        )
        from instalaciones.models import Espacio

        empleados_data = [
            # (nombre, ap, am, sexo, tel, puesto, tipo_contrato, salario, rol_esp)
            ("Carlos", "Mendoza", "Ríos", "M", "5551110001", "Entrenador", "tiempo_completo", 18000, "entrenador"),
            ("Sofía", "Ramírez", "Castro", "F", "5551110002", "Entrenadora", "tiempo_completo", 18000, "entrenador"),
            ("Diego", "Torres", "Vega", "M", "5551110003", "Entrenador Personal", "tiempo_completo", 22000, "entrenador"),
            ("Valentina", "López", "Moreno", "F", "5551110004", "Entrenadora Grupal", "tiempo_completo", 17000, "entrenador"),
            ("Miguel", "Herrera", "Soto", "M", "5551110005", "Recepcionista", "tiempo_completo", 12000, "cajero"),
            ("Fernanda", "García", "Núñez", "F", "5551110006", "Cajera", "tiempo_completo", 12000, "cajero"),
            ("Luis", "Martínez", "Peña", "M", "5551110007", "Auxiliar Limpieza", "tiempo_completo", 9500, "limpieza"),
            ("Patricia", "González", "Ruiz", "F", "5551110008", "Auxiliar Limpieza", "tiempo_completo", 9500, "limpieza"),
            ("Roberto", "Flores", "Díaz", "M", "5551110009", "Supervisor de Piso", "tiempo_completo", 14000, "supervisor"),
            ("Andrea", "Reyes", "Cruz", "F", "5551110010", "Entrenadora Spinning", "medio_tiempo", 10000, "entrenador"),
            ("José", "Jiménez", "Salinas", "M", "5551110011", "Entrenador Cardio", "tiempo_completo", 17500, "entrenador"),
            ("María", "Sánchez", "Vargas", "F", "5551110012", "Recepcionista", "tiempo_completo", 11500, "cajero"),
        ]

        empleados = []
        entrenadores = []
        fecha_base = date(2022, 1, 1)

        for i, (nombre, ap, am, sexo, tel, puesto, contrato, salario, rol_esp) in enumerate(empleados_data):
            sede = sedes[i % len(sedes)]
            email = f"{nombre.lower()}.{ap.lower()}@gimnasio.com"
            persona, _ = Persona.objects.get_or_create(
                telefono=tel,
                defaults={
                    "nombre": nombre,
                    "apellido_paterno": ap,
                    "apellido_materno": am,
                    "fecha_nacimiento": date(1985 + i, (i % 12) + 1, 15),
                    "sexo": sexo,
                    "direccion": f"Calle Demo {i + 1}, CDMX",
                },
            )

            user, _ = User.objects.get_or_create(
                email=email,
                defaults={"persona": persona, "first_name": nombre, "last_name": ap},
            )
            if not user.has_usable_password():
                user.set_password("demo1234!")
                user.save()

            empleado, _ = Empleado.objects.get_or_create(
                persona=persona,
                defaults={
                    "puesto": puesto,
                    "departamento": "Operaciones",
                    "fecha_contratacion": fecha_base + timedelta(days=i * 30),
                    "tipo_contrato": contrato,
                    "salario": salario,
                    "estado": "Activo",
                    "sede": sede,
                },
            )
            empleados.append(empleado)

            # Espacios del empleado en su sede
            espacios_sede = list(Espacio.objects.filter(sede=sede))
            espacios_principales = espacios_sede[:2] if espacios_sede else []

            if rol_esp == "entrenador":
                esp, created = Entrenador.objects.get_or_create(
                    empleado=empleado,
                    defaults={
                        "especialidad": random.choice(["Cardio", "Fuerza", "Yoga", "Spinning", "CrossFit"]),
                        "certificaciones": "ACSM, ACE",
                        "turno": random.choice(["Matutino", "Vespertino"]),
                        "sede": sede,
                    },
                )
                if espacios_principales:
                    esp.espacio.set(espacios_principales)
                entrenadores.append(esp)

            elif rol_esp == "cajero":
                rec_espacios = [e for e in espacios_sede if "Recepción" in e.nombre]
                obj, _ = Cajero.objects.get_or_create(
                    empleado=empleado,
                    defaults={
                        "turno": random.choice(["Matutino", "Vespertino"]),
                        "sede": sede,
                    },
                )
                if rec_espacios:
                    obj.espacio.set(rec_espacios)

            elif rol_esp == "limpieza":
                obj, _ = PersonalLimpieza.objects.get_or_create(
                    empleado=empleado,
                    defaults={
                        "turno": random.choice(["Matutino", "Vespertino", "Nocturno"]),
                        "sede": sede,
                    },
                )
                if espacios_sede:
                    obj.espacio.set(espacios_sede[:3])

            elif rol_esp == "supervisor":
                obj, _ = SupervisorEspacio.objects.get_or_create(
                    empleado=empleado,
                    defaults={
                        "turno": "Matutino",
                        "sede": sede,
                    },
                )
                if espacios_sede:
                    obj.espacio.set(espacios_sede[:4])

        self._log(f"Empleados: {len(empleados)} | Entrenadores: {len(entrenadores)}")
        return empleados, entrenadores

    # ------------------------------------------------------------------
    # CLIENTES
    # ------------------------------------------------------------------

    def _seed_clientes(self, sedes):
        from authentication.models import ContactoEmergencia, Persona
        from clientes.models import Cliente

        nombres_f = ["Ana", "Laura", "Mónica", "Gabriela", "Sandra", "Paola", "Daniela",
                     "Alejandra", "Verónica", "Carmen", "Isabel", "Teresa"]
        nombres_m = ["Juan", "Pedro", "Ricardo", "Héctor", "Eduardo", "Raúl", "Marco",
                     "Andrés", "Felipe", "Sergio", "Emilio", "Iván"]
        apellidos = ["López", "García", "Martínez", "Hernández", "González", "Pérez",
                     "Rodríguez", "Sánchez", "Jiménez", "Díaz", "Torres", "Morales",
                     "Reyes", "Cruz", "Flores", "Gómez", "Ruiz", "Vázquez"]
        objetivos = [
            "Perder peso y tonificar",
            "Ganar masa muscular",
            "Mejorar condición cardiovascular",
            "Rehabilitación y movilidad",
            "Reducir estrés y mejorar flexibilidad",
            "Preparación para competencia",
        ]
        contactos_nombres = ["María", "José", "Roberto", "Patricia", "Alejandro", "Claudia"]
        parentescos = ["Madre", "Padre", "Esposo/a", "Hermano/a", "Amigo/a", "Tutor/a"]

        clientes = []
        telefono_base = 5552000000

        for i in range(35):
            es_mujer = i % 2 == 0
            nombre = nombres_f[i % len(nombres_f)] if es_mujer else nombres_m[i % len(nombres_m)]
            ap = apellidos[i % len(apellidos)]
            am = apellidos[(i + 5) % len(apellidos)]
            tel = str(telefono_base + i)
            sede = sedes[i % len(sedes)]

            persona, _ = Persona.objects.get_or_create(
                telefono=tel,
                defaults={
                    "nombre": nombre,
                    "apellido_paterno": ap,
                    "apellido_materno": am,
                    "fecha_nacimiento": date(1980 + (i % 30), (i % 12) + 1, (i % 28) + 1),
                    "sexo": "F" if es_mujer else "M",
                    "direccion": f"Calle {i + 1}, Colonia Demo, CDMX",
                },
            )

            # Contacto de emergencia
            ContactoEmergencia.objects.get_or_create(
                persona=persona,
                defaults={
                    "nombre_contacto": f"{contactos_nombres[i % len(contactos_nombres)]} {ap}",
                    "telefono_contacto": str(telefono_base + 1000 + i),
                    "parentesco": parentescos[i % len(parentescos)],
                },
            )

            nivel = ["principiante", "intermedio", "avanzado"][i % 3]
            estado = "activo" if i < 28 else ("inactivo" if i < 32 else "suspendido")

            cliente, _ = Cliente.objects.get_or_create(
                persona=persona,
                defaults={
                    "sede": sede,
                    "objetivo_fitness": objetivos[i % len(objetivos)],
                    "nivel_experiencia": nivel,
                    "estado": estado,
                },
            )
            clientes.append(cliente)

        self._log(f"Clientes: {len(clientes)}")
        return clientes

    # ------------------------------------------------------------------
    # MEMBRESÍAS
    # ------------------------------------------------------------------

    def _seed_membresias(self, sedes):
        from instalaciones.models import Espacio
        from membresias.models import Membresia

        planes = [
            # (nombre, tipo, precio, dias, permite_todas, sede_idx)
            ("Mensual Básico Norte", "mensual", 500, 30, False, 0),
            ("Mensual Básico Sur", "mensual", 500, 30, False, 1),
            ("Mensual Básico Oriente", "mensual", 500, 30, False, 2),
            ("Mensual Básico Poniente", "mensual", 500, 30, False, 3),
            ("Trimestral Estándar Norte", "trimestral", 1350, 90, False, 0),
            ("Trimestral Estándar Sur", "trimestral", 1350, 90, False, 1),
            ("Semestral Plus", "semestral", 2400, 180, False, 0),
            ("Anual Premium", "anual", 4200, 365, False, 0),
            ("Plan Corporativo Multi-Sede", "anual", 5500, 365, True, 0),
            ("Pase del Día", "pase_dia", 80, 1, False, 0),
            ("Pase Semanal", "pase_semana", 250, 7, False, 1),
        ]

        membresias = []
        for nombre, tipo, precio, dias, permite_todas, sede_idx in planes:
            sede = sedes[sede_idx] if not permite_todas else None
            m, created = Membresia.objects.get_or_create(
                nombre_plan=nombre,
                defaults={
                    "tipo": tipo,
                    "precio": precio,
                    "duracion_dias": dias,
                    "descripcion": f"Plan {tipo} con acceso a instalaciones",
                    "beneficios": "Acceso a todas las instalaciones incluidas\nVestuarios y regaderas\nClases grupales básicas",
                    "activo": True,
                    "sede": sede,
                    "permite_todas_sedes": permite_todas,
                },
            )
            # Asociar espacios
            if not permite_todas and sede:
                espacios_sede = list(Espacio.objects.filter(sede=sede)[:5])
                if espacios_sede:
                    m.espacios_incluidos.set(espacios_sede)
            membresias.append(m)

        self._log(f"Membresías: {len(membresias)}")
        return membresias

    # ------------------------------------------------------------------
    # SUSCRIPCIONES
    # ------------------------------------------------------------------

    def _seed_suscripciones(self, clientes, membresias):
        from membresias.models import SuscripcionMembresia

        metodos = ["efectivo", "transferencia", "tarjeta"]
        hoy = timezone.now().date()
        count = 0

        for i, cliente in enumerate(clientes):
            if SuscripcionMembresia.objects.filter(cliente=cliente).exists():
                continue

            # La mayoría tiene suscripción activa
            if i < 25:
                membresia = membresias[i % 4]  # planes mensuales por sede
                inicio = hoy - timedelta(days=random.randint(5, 20))
                fin = inicio + timedelta(days=membresia.duracion_dias or 30)
                estado = "activa"
            elif i < 30:
                # Vencidas
                membresia = membresias[i % 4]
                inicio = hoy - timedelta(days=60)
                fin = hoy - timedelta(days=10)
                estado = "vencida"
            else:
                # Canceladas
                membresia = membresias[9]  # pase del día
                inicio = hoy - timedelta(days=90)
                fin = hoy - timedelta(days=89)
                estado = "cancelada"

            SuscripcionMembresia.objects.create(
                cliente=cliente,
                membresia=membresia,
                fecha_inicio=inicio,
                fecha_fin=fin,
                estado=estado,
                precio_pagado=membresia.precio,
                metodo_pago=metodos[i % 3],
                sede_suscripcion=membresia.sede,
                notas="Suscripción creada por seed demo",
            )
            count += 1

        # Algunas suscripciones históricas adicionales (clientes recurrentes)
        for cliente in clientes[:10]:
            membresia = membresias[random.randint(4, 6)]
            inicio_hist = hoy - timedelta(days=random.randint(200, 365))
            fin_hist = inicio_hist + timedelta(days=membresia.duracion_dias or 90)
            if not SuscripcionMembresia.objects.filter(cliente=cliente, fecha_inicio=inicio_hist).exists():
                SuscripcionMembresia.objects.create(
                    cliente=cliente,
                    membresia=membresia,
                    fecha_inicio=inicio_hist,
                    fecha_fin=fin_hist,
                    estado="vencida",
                    precio_pagado=membresia.precio,
                    metodo_pago=metodos[random.randint(0, 2)],
                    sede_suscripcion=membresia.sede,
                )
                count += 1

        self._log(f"Suscripciones: {count}")

    # ------------------------------------------------------------------
    # CONTROL DE ACCESO
    # ------------------------------------------------------------------

    def _seed_control_acceso(self, clientes, sedes):
        from control_acceso.models import Credencial, RegistroAcceso

        hoy = timezone.now()
        count_cred = 0
        count_acc = 0

        for i, cliente in enumerate(clientes[:28]):  # solo clientes activos
            persona = cliente.persona

            # Credencial
            if not Credencial.objects.filter(persona=persona).exists():
                Credencial.objects.create(
                    persona=persona,
                    tipo_credencial=random.choice(["Tarjeta", "QR", "RFID"]),
                    identificador=f"GIM-{2025 + i:04d}-{i:06d}",
                    fecha_emision=date(2024, 1, 1) + timedelta(days=i * 5),
                    fecha_expiracion=date(2026, 12, 31),
                    estado="activa",
                )
                count_cred += 1

            # Registros de acceso: últimos 30 días
            sede = sedes[i % len(sedes)]
            for j in range(random.randint(3, 12)):
                dias_atras = random.randint(1, 30)
                hora_entrada = timezone.make_aware(
                    timezone.datetime(
                        hoy.year, hoy.month, hoy.day,
                        random.randint(6, 20),
                        random.choice([0, 15, 30, 45]),
                    )
                ) - timedelta(days=dias_atras)
                permanencia = timedelta(minutes=random.randint(45, 120))

                RegistroAcceso.objects.create(
                    cliente=cliente,
                    sede=sede,
                    fecha_hora_entrada=hora_entrada,
                    fecha_hora_salida=hora_entrada + permanencia,
                    autorizado=True,
                    membresia_nombre=f"Plan Demo {i % 4 + 1}",
                    membresia_estado="activa",
                )
                count_acc += 1

        # Algunos accesos denegados
        for cliente in clientes[28:32]:
            sede = sedes[0]
            RegistroAcceso.objects.create(
                cliente=cliente,
                sede=sede,
                fecha_hora_entrada=hoy - timedelta(days=5),
                autorizado=False,
                motivo_denegado="Membresía vencida",
                membresia_estado="vencida",
            )
            count_acc += 1

        self._log(f"Credenciales: {count_cred} | Registros de acceso: {count_acc}")

    # ------------------------------------------------------------------
    # CATEGORÍAS DE ACTIVOS Y ACTIVOS (GESTIÓN DE EQUIPOS)
    # ------------------------------------------------------------------

    def _seed_categorias_activos(self):
        from gestion_equipos.models import CategoriaActivo

        categorias_data = [
            ("Máquinas Cardiovasculares", "Cintas, bicicletas, elípticas y similares"),
            ("Máquinas de Fuerza", "Máquinas de pesas y cables"),
            ("Peso Libre", "Mancuernas, barras y discos"),
            ("Equipamiento Grupal", "Colchonetas, pesas rusas, TRX"),
            ("Mobiliario", "Bancas, espejos, locker"),
            ("Sistemas Electrónicos", "Monitores, control de acceso, audio"),
        ]

        cats = []
        for nombre, desc in categorias_data:
            cat, _ = CategoriaActivo.objects.get_or_create(nombre=nombre, defaults={"descripcion": desc})
            cats.append(cat)

        self._log(f"Categorías de activos: {len(cats)}")
        return cats

    def _seed_activos(self, sedes, categorias, admin_user):
        from gestion_equipos.models import Activo, Mantenimiento, OrdenMantenimiento, ProveedorServicio
        from instalaciones.models import Espacio

        # Proveedores de servicio
        proveedores_data = [
            ("TechGym México", "Ing. Ramírez", "5559001001", "techgym@gym.mx", "Mantenimiento de equipos cardio y fuerza"),
            ("Servicio Express SA", "Lic. Gómez", "5559001002", "servicio@express.mx", "Reparaciones eléctricas y mecánicas"),
            ("CleanMaster", "Sr. Morales", "5559001003", "clean@master.mx", "Limpieza especializada de equipos"),
        ]

        proveedores = []
        for nombre, contacto, tel, email, servicios in proveedores_data:
            prov, _ = ProveedorServicio.objects.get_or_create(
                nombre_empresa=nombre,
                defaults={
                    "nombre_contacto": contacto,
                    "telefono": tel,
                    "email": email,
                    "servicios_ofrecidos": servicios,
                },
            )
            proveedores.append(prov)

        activos_spec = [
            # (codigo_prefix, nombre, cat_idx, valor, marca, modelo)
            ("CARD", "Cinta Caminadora", 0, 25000, "LifeFitness", "T5-GO"),
            ("CARD", "Bicicleta Estática", 0, 15000, "Precor", "UBK 835"),
            ("CARD", "Elíptica", 0, 22000, "Matrix", "E50"),
            ("CARD", "Bicicleta Spinning", 0, 12000, "Keiser", "M3i"),
            ("FUER", "Máquina Press Pecho", 1, 35000, "Technogym", "Selection Pro"),
            ("FUER", "Máquina Jalón", 1, 30000, "Hammer Strength", "MTC-LAT"),
            ("FUER", "Máquina Leg Press", 1, 40000, "Nautilus", "LP"),
            ("PESO", "Set Mancuernas 2-40kg", 2, 18000, "Troy", "HEX-SET"),
            ("PESO", "Barra Olímpica 20kg", 2, 8000, "Cap", "OB-86B"),
            ("GRUP", "Colchonetas Yoga (x20)", 3, 6000, "Manduka", "PRO"),
            ("GRUP", "Pesas Rusas Set", 3, 12000, "Onnit", "PRO"),
            ("MOB", "Espejo de Pared 2x4m", 4, 5000, "Cristalería Metro", "CL-2000"),
            ("ELEC", "Sistema de Audio", 5, 20000, "Bose", "Pro FreeSpace"),
        ]

        activos = []
        global_counter = 0

        for sede in sedes:
            espacios_sede = list(Espacio.objects.filter(sede=sede))
            for idx, (prefix, nombre, cat_idx, valor, marca, modelo) in enumerate(activos_spec):
                global_counter += 1
                codigo = f"{prefix}-{sede.id:02d}-{idx + 1:03d}"
                numero_serie = f"SN-{global_counter:06d}"

                if Activo.objects.filter(codigo=codigo).exists():
                    activos.append(Activo.objects.get(codigo=codigo))
                    continue

                # Evitar duplicado de numero_serie si ya existe
                if Activo.objects.filter(numero_serie=numero_serie).exists():
                    numero_serie = f"SN-{global_counter:06d}-{sede.id}"

                espacio = espacios_sede[cat_idx % len(espacios_sede)] if espacios_sede else None
                activo = Activo.objects.create(
                    codigo=codigo,
                    nombre=f"{nombre} - {sede.nombre}",
                    categoria=categorias[cat_idx],
                    fecha_compra=date(2022, 1, 1) + timedelta(days=global_counter * 7),
                    valor=valor,
                    estado="activo",
                    sede=sede,
                    espacio=espacio,
                    marca=marca,
                    modelo=modelo,
                    numero_serie=numero_serie,
                    creado_por=admin_user,
                )
                activos.append(activo)

        # Algunos en mantenimiento
        for activo in activos[:4]:
            if not activo.mantenimientos.exists():
                m = Mantenimiento.objects.create(
                    activo=activo,
                    tipo_mantenimiento="preventivo",
                    fecha_programada=timezone.now().date() + timedelta(days=random.randint(5, 30)),
                    proveedor_servicio=proveedores[0],
                    costo=1500,
                    descripcion="Mantenimiento preventivo trimestral",
                    estado="pendiente",
                    creado_por=admin_user,
                )
                OrdenMantenimiento.objects.get_or_create(
                    mantenimiento=m,
                    defaults={
                        "numero_orden": f"OM-2026-{m.pk:04d}",
                        "prioridad": "media",
                        "tiempo_estimado": 4,
                        "materiales_necesarios": "Lubricante, limpiador industrial",
                        "estado_orden": "aprobada",
                        "creado_por": admin_user,
                    },
                )

        self._log(f"Activos: {len(activos)} | Proveedores: {len(proveedores)}")
        return activos

    # ------------------------------------------------------------------
    # INVENTARIO
    # ------------------------------------------------------------------

    def _seed_inventario(self, sedes):
        from inventario.models import CategoriaProducto, Inventario, Producto

        categorias_prod = [
            "Bebidas Deportivas",
            "Suplementos",
            "Ropa Deportiva",
            "Accesorios",
            "Snacks Saludables",
        ]

        cats = {}
        for nombre in categorias_prod:
            cat, _ = CategoriaProducto.objects.get_or_create(nombre=nombre)
            cats[nombre] = cat

        productos_data = [
            ("Proteína Whey 1kg Chocolate", "Suplementos", 480, "SUPP-001"),
            ("Proteína Whey 1kg Vainilla", "Suplementos", 480, "SUPP-002"),
            ("BCAA 300g", "Suplementos", 320, "SUPP-003"),
            ("Creatina 300g", "Suplementos", 280, "SUPP-004"),
            ("Electrolitos en polvo", "Suplementos", 150, "SUPP-005"),
            ("Agua Natural 600ml", "Bebidas Deportivas", 20, "BEB-001"),
            ("Gatorade 600ml", "Bebidas Deportivas", 25, "BEB-002"),
            ("Isotónico Monster", "Bebidas Deportivas", 35, "BEB-003"),
            ("Guantes de Entrenamiento", "Accesorios", 180, "ACC-001"),
            ("Cuerda para saltar", "Accesorios", 120, "ACC-002"),
            ("Banda de resistencia Kit", "Accesorios", 250, "ACC-003"),
            ("Calcetas Deportivas (par)", "Ropa Deportiva", 90, "ROPA-001"),
            ("Playera Gym Dri-fit", "Ropa Deportiva", 220, "ROPA-002"),
            ("Barra de Proteína", "Snacks Saludables", 45, "SNACK-001"),
            ("Nueces mixtas 100g", "Snacks Saludables", 60, "SNACK-002"),
        ]

        productos = []
        for nombre, cat_nombre, precio, codigo in productos_data:
            prod, _ = Producto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    "nombre": nombre,
                    "categoria": cats[cat_nombre],
                    "precio_unitario": precio,
                    "descripcion": f"{nombre} de alta calidad",
                    "activo": True,
                },
            )
            productos.append(prod)

        # Inventario por sede
        inv_count = 0
        for sede in sedes:
            for prod in productos:
                qty = random.randint(5, 80)
                _, created = Inventario.objects.get_or_create(
                    producto=prod,
                    sede=sede,
                    defaults={
                        "cantidad_actual": qty,
                        "cantidad_minima": 5,
                        "cantidad_maxima": 100,
                        "ubicacion_almacen": f"Almacén {sede.nombre[:3].upper()}-A1",
                    },
                )
                if created:
                    inv_count += 1

        self._log(f"Productos: {len(productos)} | Inventarios: {inv_count}")
        return productos

    # ------------------------------------------------------------------
    # VENTAS (modelo nuevo VentaProducto)
    # ------------------------------------------------------------------

    def _seed_ventas(self, clientes, sedes, admin_user):
        from inventario.models import Producto
        from ventas.models import DetalleVentaProducto, VentaProducto

        if VentaProducto.objects.exists():
            self._log("Ventas ya existen, omitiendo.")
            return

        productos = list(Producto.objects.filter(activo=True))
        if not productos:
            self._log("Sin productos disponibles para ventas.")
            return

        metodos = ["efectivo", "tarjeta", "transferencia"]
        hoy = timezone.now()
        ventas_creadas = 0

        for i in range(40):
            cliente = clientes[i % len(clientes)] if i % 3 != 0 else None
            sede = sedes[i % len(sedes)]

            # Seleccionar 1-3 productos
            prods_venta = random.sample(productos, min(random.randint(1, 3), len(productos)))
            subtotal = sum(p.precio_unitario for p in prods_venta)
            from decimal import Decimal
            descuento = subtotal * (Decimal(str(random.choice([0, 0.05, 0.10]))) if i % 5 == 0 else Decimal("0"))
            total = subtotal - descuento

            fecha_v = hoy - timedelta(days=random.randint(0, 60))

            venta = VentaProducto(
                cliente=cliente,
                empleado=admin_user,
                sede=sede,
                subtotal=subtotal,
                descuento_global=descuento,
                iva=0,
                total=total,
                metodo_pago=metodos[i % 3],
                estado="completada",
                notas="Venta demo",
            )
            venta.save()

            for prod in prods_venta:
                qty = random.randint(1, 3)
                precio = prod.precio_unitario
                sub = precio * qty
                tot = sub
                DetalleVentaProducto.objects.create(
                    venta=venta,
                    producto=prod,
                    cantidad=qty,
                    precio_unitario=precio,
                    descuento=0,
                    subtotal=sub,
                    total=tot,
                )

            ventas_creadas += 1

        self._log(f"Ventas: {ventas_creadas}")

    # ------------------------------------------------------------------
    # FACTURAS
    # ------------------------------------------------------------------

    def _seed_facturas(self, clientes):
        from facturacion.models import DetalleFactura, Factura, MetodoPago, Pago
        from inventario.models import Producto

        if Factura.objects.exists():
            self._log("Facturas ya existen, omitiendo.")
            return

        productos = list(Producto.objects.filter(activo=True))
        if not productos:
            self._log("Sin productos para facturas.")
            return

        facturas_creadas = 0
        metodos = [MetodoPago.EFECTIVO, MetodoPago.TARJETA, MetodoPago.TRANSFERENCIA]

        for i, cliente in enumerate(clientes[:25]):
            factura = Factura.objects.create(
                cliente=cliente,
                estado_pago="pendiente",
                total=0,
            )

            # 1-4 detalles por factura
            prods = random.sample(productos, min(random.randint(1, 4), len(productos)))
            for prod in prods:
                qty = random.randint(1, 5)
                DetalleFactura.objects.create(
                    factura=factura,
                    producto=prod,
                    cantidad=qty,
                    precio_unitario=prod.precio_unitario,
                )
            # El total se actualiza automáticamente por el signal del modelo

            # Pago total o parcial
            if i < 18:
                # Pagadas
                Pago.objects.create(
                    factura=factura,
                    monto=factura.total,
                    metodo_pago=metodos[i % 3],
                )
            elif i < 22:
                # Pago parcial
                Pago.objects.create(
                    factura=factura,
                    monto=factura.total / 2,
                    metodo_pago=MetodoPago.EFECTIVO,
                )

            facturas_creadas += 1

        self._log(f"Facturas: {facturas_creadas}")

    # ------------------------------------------------------------------
    # HORARIOS DE CLASES
    # ------------------------------------------------------------------

    def _seed_horarios(self, entrenadores, sedes):
        from horarios.models import (
            ClienteMembresia,
            Horario,
            ReservaClase,
            ReservaEntrenador,
            SesionClase,
            TipoActividad,
        )
        from instalaciones.models import Espacio
        from membresias.models import SuscripcionMembresia
        from clientes.models import Cliente

        if not entrenadores:
            self._log("Sin entrenadores, omitiendo horarios.")
            return

        # Tipos de actividad por sede
        actividades_data = [
            ("Yoga", "01:00:00", "#22c55e"),
            ("Spinning", "00:45:00", "#ef4444"),
            ("Zumba", "01:00:00", "#f97316"),
            ("CrossFit", "01:00:00", "#6366f1"),
            ("Pilates", "01:00:00", "#ec4899"),
            ("Cardio HIIT", "00:45:00", "#f59e0b"),
        ]

        tipos_por_sede: dict = {}
        for sede in sedes:
            tipos_por_sede[sede.id] = []
            for nombre, duracion, color in actividades_data:
                ta, _ = TipoActividad.objects.get_or_create(
                    nombre=nombre,
                    sede=sede,
                    defaults={
                        "descripcion": f"Clase de {nombre}",
                        "duracion_default": duracion,
                        "color_hex": color,
                        "activo": True,
                    },
                )
                tipos_por_sede[sede.id].append(ta)

        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
        horarios_creados = 0
        sesiones_creadas = 0

        hoy = timezone.now().date()
        # Fecha inicio para todos los horarios: primer lunes de hace 3 semanas
        dias_a_lunes = hoy.weekday()
        fecha_inicio_horario = hoy - timedelta(days=dias_a_lunes + 21)

        for i, entrenador in enumerate(entrenadores):
            sede = entrenador.sede
            espacios_entrenador = list(entrenador.espacio.filter(sede=sede))
            if not espacios_entrenador:
                espacios_entrenador = list(Espacio.objects.filter(sede=sede)[:2])
            if not espacios_entrenador:
                continue

            tipos = tipos_por_sede.get(sede.id, [])
            if not tipos:
                continue

            # Cada entrenador tiene 2 horarios semanales
            for j in range(2):
                dia = dias[(i * 2 + j) % len(dias)]
                hora_inicio = time(6 + (i + j) % 14, 0)
                hora_fin_h = 6 + (i + j) % 14 + 1
                hora_fin = time(hora_fin_h if hora_fin_h < 24 else 23, 0)
                espacio = espacios_entrenador[j % len(espacios_entrenador)]
                tipo = tipos[(i + j) % len(tipos)]

                try:
                    horario, created = Horario.objects.get_or_create(
                        espacio=espacio,
                        dia_semana=dia,
                        hora_inicio=hora_inicio,
                        fecha_inicio=fecha_inicio_horario,
                        defaults={
                            "entrenador": entrenador,
                            "tipo_actividad": tipo,
                            "hora_fin": hora_fin,
                            "cupo_maximo": 20,
                            "estado": "activo",
                            "observaciones": "Clase regular",
                        },
                    )
                    if created:
                        horarios_creados += 1

                        # Crear sesiones para las últimas 3 semanas + 2 futuras
                        dias_mapping = {
                            "lunes": 0, "martes": 1, "miercoles": 2, "jueves": 3,
                            "viernes": 4, "sabado": 5, "domingo": 6,
                        }
                        dia_num = dias_mapping[dia]

                        for semana in range(-3, 3):
                            # Calcular el próximo día_num desde hoy
                            days_to_target = (dia_num - hoy.weekday() + 7) % 7
                            if days_to_target == 0 and semana < 0:
                                days_to_target = 7
                            fecha_sesion = hoy + timedelta(days=days_to_target + semana * 7)

                            if fecha_sesion < fecha_inicio_horario:
                                continue

                            try:
                                sesion, s_created = SesionClase.objects.get_or_create(
                                    horario=horario,
                                    fecha=fecha_sesion,
                                    defaults={
                                        "estado": "completada" if fecha_sesion < hoy else "programada",
                                        "asistentes_registrados": random.randint(5, 18) if fecha_sesion < hoy else 0,
                                    },
                                )
                                if s_created:
                                    sesiones_creadas += 1
                            except Exception:
                                pass
                except Exception:
                    pass

        # Membresías de cliente (ClienteMembresia en horarios)
        clientes_activos = list(Cliente.objects.filter(estado="activo")[:15])
        from membresias.models import Membresia
        membresias = list(Membresia.objects.filter(activo=True)[:4])
        cm_count = 0
        for i, cliente in enumerate(clientes_activos):
            if not ClienteMembresia.objects.filter(cliente=cliente).exists() and membresias:
                mem = membresias[i % len(membresias)]
                ClienteMembresia.objects.create(
                    cliente=cliente,
                    membresia=mem,
                    fecha_inicio=hoy - timedelta(days=15),
                    fecha_fin=hoy + timedelta(days=15),
                    estado="activa",
                )
                cm_count += 1

        # Reservas de clase: solo sesiones futuras
        sesiones_futuras = list(SesionClase.objects.filter(fecha__gte=hoy, estado="programada")[:20])
        reservas_count = 0
        clientes_con_membresia_activa = list(
            Cliente.objects.filter(
                suscripciones__estado="activa",
                suscripciones__fecha_inicio__lte=hoy,
                suscripciones__fecha_fin__gte=hoy,
            ).distinct()[:10]
        )

        for i, sesion in enumerate(sesiones_futuras):
            for cliente in clientes_con_membresia_activa[:3]:
                if not ReservaClase.objects.filter(cliente=cliente, sesion_clase=sesion).exists():
                    try:
                        ReservaClase.objects.create(
                            cliente=cliente,
                            sesion_clase=sesion,
                            estado="confirmada",
                        )
                        reservas_count += 1
                    except Exception:
                        pass

        # Reservas de entrenador personal
        re_count = 0
        clientes_para_reservas = clientes_con_membresia_activa[:5]
        for i, cliente in enumerate(clientes_para_reservas):
            if entrenadores:
                entrenador = entrenadores[i % len(entrenadores)]
                fecha_sesion = hoy + timedelta(days=random.randint(3, 14))
                hi = time(10 + i, 0)
                hf = time(11 + i, 0)
                espacio = entrenador.espacio.filter(sede=entrenador.sede).first()
                try:
                    if not ReservaEntrenador.objects.filter(
                        cliente=cliente,
                        entrenador=entrenador,
                        fecha_sesion=fecha_sesion,
                    ).exists():
                        ReservaEntrenador.objects.create(
                            cliente=cliente,
                            entrenador=entrenador,
                            fecha_sesion=fecha_sesion,
                            hora_inicio=hi,
                            hora_fin=hf,
                            tipo_sesion="individual",
                            estado="confirmada",
                            objetivo="Entrenamiento funcional personalizado",
                            espacio=espacio,
                            precio=500,
                        )
                        re_count += 1
                except Exception:
                    pass

        self._log(
            f"TiposActividad: {TipoActividad.objects.count()} | Horarios: {horarios_creados} | "
            f"Sesiones: {sesiones_creadas} | ClienteMembresia: {cm_count} | "
            f"ReservasClase: {reservas_count} | ReservasEntrenador: {re_count}"
        )

    # ------------------------------------------------------------------
    # LIMPIEZA
    # ------------------------------------------------------------------

    def _seed_limpieza(self, empleados, sedes):
        from empleados.models import (
            AsignacionTarea,
            HorarioLimpieza,
            PersonalLimpieza,
            TareaLimpieza,
        )
        from instalaciones.models import Espacio

        personal_limpieza = list(PersonalLimpieza.objects.all())
        if not personal_limpieza:
            self._log("Sin personal de limpieza, omitiendo.")
            return

        # Tareas de limpieza
        tareas_data = [
            ("Limpieza de baños", "bano", 30, "alta"),
            ("Limpieza de vestidores", "vestidor", 45, "alta"),
            ("Limpieza de área de cardio", "gimnasio", 20, "media"),
            ("Limpieza de área de pesas", "gimnasio", 25, "media"),
            ("Limpieza de recepción", "recepcion", 15, "media"),
            ("Limpieza de alberca", "alberca", 60, "alta"),
            ("Limpieza de áreas comunes", "areas_comunes", 30, "baja"),
        ]

        tareas = []
        for nombre, tipo_esp, duracion, prioridad in tareas_data:
            tarea, _ = TareaLimpieza.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "tipo_espacio": tipo_esp,
                    "duracion_estimada": duracion,
                    "prioridad": prioridad,
                    "activo": True,
                },
            )
            tareas.append(tarea)

        # Horarios de limpieza
        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
        hl_count = 0
        for pl in personal_limpieza:
            espacios = list(Espacio.objects.filter(sede=pl.sede)[:3])
            for i, espacio in enumerate(espacios):
                dia = dias[i % len(dias)]
                hi = time(6 + i * 2, 0)
                hf = time(7 + i * 2, 30)
                if not HorarioLimpieza.objects.filter(personal_limpieza=pl, espacio=espacio, dia_semana=dia).exists():
                    HorarioLimpieza.objects.create(
                        personal_limpieza=pl,
                        espacio=espacio,
                        dia_semana=dia,
                        hora_inicio=hi,
                        hora_fin=hf,
                        activo=True,
                    )
                    hl_count += 1

        # Asignaciones de tarea
        at_count = 0
        hoy = timezone.now().date()
        for i, pl in enumerate(personal_limpieza):
            espacios = list(Espacio.objects.filter(sede=pl.sede)[:2])
            for j, tarea in enumerate(tareas[:4]):
                if not espacios:
                    continue
                espacio = espacios[j % len(espacios)]
                fecha = hoy - timedelta(days=j * 2)
                estado = "completada" if j < 3 else "pendiente"

                if not AsignacionTarea.objects.filter(personal_limpieza=pl, tarea=tarea, fecha=fecha).exists():
                    AsignacionTarea.objects.create(
                        personal_limpieza=pl,
                        tarea=tarea,
                        espacio=espacio,
                        fecha=fecha,
                        hora_inicio=time(7, 0),
                        hora_fin=time(7, 30) if estado == "completada" else None,
                        estado=estado,
                        notas="Asignación demo",
                    )
                    at_count += 1

        self._log(f"Tareas de limpieza: {len(tareas)} | HorariosLimpieza: {hl_count} | Asignaciones: {at_count}")

    # ------------------------------------------------------------------
    # ROLES (idempotente — ya deben existir del configurar_admin.py)
    # ------------------------------------------------------------------

    # Los roles y permisos ya fueron creados por configurar_admin.py
    # Solo asignamos PersonaRol a los empleados si no existen

    def _seed_roles(self) -> None:
        from authentication.models import Persona
        from empleados.models import Empleado
        from roles.models import PersonaRol, Rol

        rol_admin = Rol.objects.filter(nombre__icontains="admin").first()
        if not rol_admin:
            return

        for empleado in Empleado.objects.all():
            rol = Rol.objects.filter(nombre__icontains=empleado.puesto[:5]).first() or rol_admin
            PersonaRol.objects.get_or_create(persona=empleado.persona, rol=rol)
