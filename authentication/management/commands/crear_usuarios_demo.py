"""
Crea (de forma idempotente) el usuario administrador y un usuario por cada rol
del sistema, con credenciales conocidas. Pensado para entornos de demo/desarrollo
y para que un colega que clona el repo entre directo.

Uso:
    python manage.py crear_usuarios_demo
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from authentication.models import Persona, User
from empleados.models import Empleado
from instalaciones.models import Sede
from roles.models import Permiso, PersonaRol, Rol, RolPermiso

PERMISOS = {
    "gestionar_empleados": "Puede gestionar empleados",
    "gestionar_entrenamientos": "Puede gestionar entrenamientos",
    "gestionar_acceso": "Puede gestionar el acceso al gimnasio",
    "gestionar_instalaciones": "Puede gestionar instalaciones",
    "gestionar_limpieza": "Puede gestionar limpieza",
}

ROLES = {
    "Administrador": ["gestionar_empleados"],
    "Entrenador": ["gestionar_entrenamientos"],
    "Recepcionista": ["gestionar_acceso"],
    "Supervisor de Instalaciones": ["gestionar_instalaciones"],
    "Personal de Limpieza": ["gestionar_limpieza"],
}

# email, password, rol, nombre, apellido, puesto, es_superusuario
USUARIOS = [
    ("admin@gimnasio.com", "admin123", "Administrador", "Admin", "Sistema", "Administrador del Sistema", True),
    ("entrenador@gimnasio.com", "entrenador123", "Entrenador", "Carlos", "Entrenador", "Entrenador Personal", False),
    ("recepcion@gimnasio.com", "recepcion123", "Recepcionista", "Maria", "Recepcion", "Recepcionista", False),
    ("supervisor@gimnasio.com", "supervisor123", "Supervisor de Instalaciones", "Jorge", "Supervisor", "Supervisor de Instalaciones", False),
    ("limpieza@gimnasio.com", "limpieza123", "Personal de Limpieza", "Ana", "Limpieza", "Personal de Limpieza", False),
]


class Command(BaseCommand):
    help = "Crea el admin y un usuario por cada rol con credenciales conocidas (idempotente)."

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Permisos
        permisos = {}
        for nombre, desc in PERMISOS.items():
            permisos[nombre], _ = Permiso.objects.get_or_create(
                nombre=nombre, defaults={"descripcion": desc}
            )

        # 2. Roles + asignacion de permisos
        roles = {}
        for rol_nombre, perms in ROLES.items():
            rol, _ = Rol.objects.get_or_create(
                nombre=rol_nombre, defaults={"descripcion": f"Rol de {rol_nombre}"}
            )
            roles[rol_nombre] = rol
            for p in perms:
                RolPermiso.objects.get_or_create(rol=rol, permiso=permisos[p])

        sede = Sede.objects.first()

        # 3. Usuarios (uno por rol)
        self.stdout.write("Creando/actualizando usuarios por rol:")
        for email, password, rol_nombre, nombre, apellido, puesto, es_super in USUARIOS:
            user, created = User.objects.get_or_create(
                email=email, defaults={"is_active": True}
            )
            user.is_active = True
            user.is_staff = es_super
            user.is_superuser = es_super
            user.set_password(password)

            if user.persona is None:
                user.persona = Persona.objects.create(
                    nombre=nombre,
                    apellido_paterno=apellido,
                    apellido_materno="Demo",
                    telefono="0000000000",
                )
            user.save()
            persona = user.persona

            # Registro de empleado base (idempotente)
            Empleado.objects.get_or_create(
                persona=persona,
                defaults={
                    "puesto": puesto,
                    "departamento": "General",
                    "fecha_contratacion": timezone.now().date(),
                    "tipo_contrato": "Indefinido",
                    "salario": Decimal("10000.00"),
                    "estado": "Activo",
                    "sede": sede,
                },
            )

            # Asignacion de rol
            PersonaRol.objects.get_or_create(persona=persona, rol=roles[rol_nombre])

            estado = "creado" if created else "actualizado"
            self.stdout.write(
                self.style.SUCCESS(f"  [{estado}] {email}  /  {password}  ->  {rol_nombre}")
            )

        self.stdout.write(self.style.SUCCESS("\nUsuarios de demo listos."))
